#!/usr/bin/env python3
"""
Blank / Empty Report Watch — daily analysis over report/alert *delivery* executions.

Sources last-24h Datadog report-execution logs and buckets offenders into:
  1) CAPTURE FAILURES (fail-closed): report_capture_terminal terminal_reason=TimeoutError
     and report_execution_terminal state=Error w/ timeout/screenshot reasons — a would-be
     blank that RAISED instead of shipping. Reports #43348 / #43031 working as intended.
  2a) PAINT-TRUTH suspects (silent blank): report_readiness_ready, delivery (has
     report_schedule_id), semantic_success=True, virtualized_holders>0 on a heavy dash.
  2b) LEGACY ALERT NULL-CONTEXT (silent blank): capture_kind=alert readiness with
     mounted_holders=0 that still reached delivery.

Delivery vs thumbnail: DELIVERY lines carry report_schedule_id + execution_id in a
trailing [ ... ] context; UI thumbnails carry only [cache_key=...] (no recipient) and
are EXCLUDED.

Env: DD_API_KEY, DD_APP_KEY
Usage: ./scripts/blank_watch.py [--hours 24]
"""
import sys, os, re, argparse, json
from collections import defaultdict, Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dd

WATCHLIST = {  # workspace short id -> (customer, cluster-hint, note)
    "bce906ff": ("OpenTable", "us1a", "windowing capture-fails; grace/stale re-delivery"),
    "054bbabc": ("OpenTable", "us2a", "windowing capture-fails; grace/stale re-delivery"),
    "cd5866de": ("OpenTable", "us2a", "windowing capture-fails; grace/stale re-delivery"),
    "26f1fa3e": ("StiQ", "us1a", "PAINT-TRUTH; alert 8681767f null-context blank"),
    "8681767f": ("StiQ (alert ws)", "us1a", "alert null-context blank"),
    "6a0814c5": ("O'Brien Garrett", "us2a", "dash 246 sched 63 loud timeout; silent blanks"),
    "3aab4059": ("O'Brien Garrett", "us2a", "silent blanks"),
    "4d041830": ("O'Brien Garrett", "us2a", "silent blanks"),
    "0e5a6f44": ("stonebridge", "eu5a", "reports-only; healthy — flag any new failure"),
    "526cce94": ("stonebridge", "eu5a", "reports-only; healthy — flag any new failure"),
    "ef8cba42": ("Paysend (prod)", "eu5a", "tiled windowing — should be a #43348 win"),
    "5428552e": ("Paysend (test)", "us1a", "tiled windowing — should be a #43348 win"),
    # second tier
    "da308448": ("ESTO", "eu5a", "2nd-tier"),
    "466cbeb3": ("SATEP", "us1a", "2nd-tier"),
    "97b73347": ("Permutive", "eu5a", "2nd-tier"),
    "19afbfef": ("ProperBird", "us2a", "2nd-tier"),
}

NUM = lambda m: None if m in (None, "None", "") else m
def gi(msg, key):
    m = re.search(rf"(?:^|[\s\[]){re.escape(key)}=([^\s\]]+)", msg)
    return m.group(1) if m else None
def gf(msg, key):
    v = gi(msg, key)
    try: return float(v)
    except (TypeError, ValueError): return None
def cluster_of(log):
    return next((t.split(":",1)[1] for t in log["attributes"].get("tags",[])
                 if t.startswith("kube_cluster_name:")), "?")
def sha_of(log):
    v = next((t.split(":",1)[1] for t in log["attributes"].get("tags",[])
              if t.startswith("version:")), None)
    return v[:10] if v else "?"

def search(q, hours, limit=3000):
    to_ts, from_ts = dd.now_and_ago(hours)
    return dd.dd_search(q, from_ts, to_ts, limit=limit)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hours", type=float, default=24)
    args = ap.parse_args()
    dd.check_creds()
    H = args.hours

    # ---- 1. terminals: final verdict per execution (deliveries carry report_schedule_id) ----
    terms = search('service:superset "report_execution_terminal"', H, limit=4000)
    # ---- capture-level timeouts (fail-closed caught blank) ----
    caps = search('service:superset "report_capture_terminal" "terminal_reason=TimeoutError"', H, limit=2000)
    # ---- readiness terminals that failed the gate (unready holder detail) ----
    rterm = search('service:superset "report_readiness_terminal" "semantic_success=False"', H, limit=2000)
    # ---- PAINT-TRUTH candidates ----
    pt = search('service:superset "report_readiness_ready" "semantic_success=True" "virtualized_holders"', H, limit=3000)
    # ---- alert null-context ----
    nullctx = search('service:superset "report_readiness" "mounted_holders=0"', H, limit=2000)

    # index terminals by execution_id and by (ws,sched)
    term_by_exec = {}
    sched_states = defaultdict(list)   # (ws,capture_kind,sched) -> [state,...]
    for l in terms:
        msg = l["attributes"].get("message","")
        ck = gi(msg,"capture_kind"); state = gi(msg,"state")
        # state token may be 'Not'/'On' truncated by space -> normalize from message
        if "state=Not triggered" in msg: state="Not triggered"
        elif "state=On Grace" in msg: state="On Grace"
        elif "state=Success" in msg: state="Success"
        elif "state=Error" in msg: state="Error"
        eid = gi(msg,"execution_id"); sched = gi(msg,"report_schedule_id")
        ws = dd.attr(l,"workspace")
        tr = re.search(r"terminal_reason=(.+?)(?: elapsed_seconds=| execution_id=| \[|$)", msg)
        rec = dict(ws=ws, ck=ck, state=state, sched=sched, eid=eid,
                   dash=gi(msg,"dashboard_id"), chart=gi(msg,"chart_id"),
                   reason=(tr.group(1).strip() if tr else None),
                   cluster=cluster_of(l), sha=sha_of(l), ts=l["attributes"].get("timestamp","")[:19])
        if eid: term_by_exec[eid]=rec
        if sched and ck=="report":
            sched_states[(ws,sched)].append(state)

    # ---- BUCKET 1: capture failures ----
    cap_rows = []
    seen=set()
    for l in caps:
        msg=l["attributes"].get("message","")
        eid=gi(msg,"execution_id"); ws=dd.attr(l,"workspace"); sched=gi(msg,"report_schedule_id")
        if not sched or sched=="None":  # deliveries only
            continue
        key=(ws,sched,eid)
        if key in seen: continue
        seen.add(key)
        # final: did any Success terminal exist for this (ws,sched) in window?
        states=sched_states.get((ws,sched),[])
        recovered = "Success" in states
        cap_rows.append(dict(ws=ws, sched=sched, dash=gi(msg,"dashboard_id"), chart=gi(msg,"chart_id"),
                             exp=gi(msg,"expected_holders"), attempt=gi(msg,"attempt"),
                             elapsed=gf(msg,"elapsed_seconds"), eid=eid,
                             cluster=cluster_of(l), sha=sha_of(l), recovered=recovered,
                             ts=l["attributes"].get("timestamp","")[:19]))
    # attach unready-holder detail from readiness terminals (by execution_id)
    unready_by_exec={}
    for l in rterm:
        msg=l["attributes"].get("message","")
        eid=gi(msg,"execution_id")
        if not eid: continue
        unready_by_exec[eid]=dict(unready=gi(msg,"unready_holders"), mounted=gi(msg,"mounted_holders"),
                                  ready=gi(msg,"ready_holders"), rendered=gi(msg,"rendered_holders"),
                                  virt=gi(msg,"virtualized_holders"))

    # ---- BUCKET 2a: PAINT-TRUTH (delivery, semantic_success=True, virtualized>0) ----
    pt_rows=[]; seen=set()
    for l in pt:
        msg=l["attributes"].get("message","")
        sched=gi(msg,"report_schedule_id"); eid=gi(msg,"execution_id")
        if not sched or sched=="None": continue      # deliveries only (exclude cache_key thumbnails)
        virt=gf(msg,"virtualized_holders")
        if not virt or virt<=0: continue
        key=(dd.attr(l,"workspace"),sched,eid)
        if key in seen: continue
        seen.add(key)
        term=term_by_exec.get(eid,{})
        pt_rows.append(dict(ws=dd.attr(l,"workspace"), sched=sched, dash=gi(msg,"dashboard_id"),
                            rendered=gi(msg,"rendered_holders"), virt=gi(msg,"virtualized_holders"),
                            empty=gi(msg,"empty_holders"), mounted=gi(msg,"mounted_holders"),
                            elapsed=gf(msg,"elapsed_seconds"), eid=eid, ck=gi(msg,"capture_kind"),
                            final=term.get("state"), cluster=cluster_of(l), sha=sha_of(l),
                            ts=l["attributes"].get("timestamp","")[:19]))

    # ---- BUCKET 2b: alert null-context (capture_kind=alert, mounted_holders=0, delivery) ----
    nc_rows=[]; seen=set()
    for l in nullctx:
        msg=l["attributes"].get("message","")
        if gf(msg,"mounted_holders")!=0: continue
        sched=gi(msg,"report_schedule_id"); ck=gi(msg,"capture_kind"); eid=gi(msg,"execution_id")
        if not sched or sched=="None": continue
        if ck!="alert": continue
        key=(dd.attr(l,"workspace"),sched,eid)
        if key in seen: continue
        seen.add(key)
        term=term_by_exec.get(eid,{})
        nc_rows.append(dict(ws=dd.attr(l,"workspace"), sched=sched, eid=eid,
                            final=term.get("state"), reason=term.get("reason"),
                            cluster=cluster_of(l), sha=sha_of(l),
                            ts=l["attributes"].get("timestamp","")[:19]))

    # ---- schedules failing (Error, no Success) — customer got nothing ----
    hard_fail = {k:v for k,v in sched_states.items() if "Error" in v and "Success" not in v}

    out = dict(hours=H, capture_failures=cap_rows, unready=unready_by_exec,
               paint_truth=pt_rows, null_context=nc_rows,
               hard_fail_scheds={f"{k[0]}/{k[1]}":Counter(v) for k,v in hard_fail.items()})
    print(json.dumps(out, indent=2, default=str))

if __name__=="__main__":
    main()
