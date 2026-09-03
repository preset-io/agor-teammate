#!/usr/bin/env python3
"""
Report Execution Watchlist — daily digest generator.

For each watchlist workspace, pulls report_execution_terminal lines over the
last N hours, groups by execution_id, and reports Success/Error counts +
error detail (schedule/dashboard/chart id, terminal_reason, elapsed).

Env: DD_API_KEY, DD_APP_KEY
Usage: ./scripts/watchlist_digest.py [--hours 24]
"""
import sys, os, re, argparse, json
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dd

WATCHLIST = {
    "19afbfef": "ProperBird",
    "26f1fa3e": "stiq.gr",
    "2699c223": "Obrien Garret",
    "2baffc15": "ProperBird #2",
    "9859d4ce": "Paysend",
    "77d21c51": "blueocean",
    "bce906ff": "OpenTable",
}


def gi(msg, key):
    m = re.search(rf"(?:^|[\s\[]){re.escape(key)}=([^\s\]]+)", msg)
    return m.group(1) if m else None


def gf(msg, key):
    v = gi(msg, key)
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def get_state(msg):
    if "state=Not triggered" in msg:
        return "Not triggered"
    if "state=On Grace" in msg:
        return "On Grace"
    if "state=Success" in msg:
        return "Success"
    if "state=Error" in msg:
        return "Error"
    return None


def get_reason(msg):
    m = re.search(r"terminal_reason=(.+?)(?: elapsed_seconds=| execution_id=| \[|$)", msg)
    return m.group(1).strip() if m else None


def search(q, hours, limit=2000):
    to_ts, from_ts = dd.now_and_ago(hours)
    return dd.dd_search(q, from_ts, to_ts, limit=limit)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hours", type=float, default=24)
    args = ap.parse_args()
    dd.check_creds()
    H = args.hours

    results = {}
    for wsid, name in WATCHLIST.items():
        # Scope to capture_kind=report so alert executions (which also emit
        # report_execution_terminal, e.g. screenshot-timeout Errors) don't get
        # miscounted as report errors. See report-execution-investigation.md
        # "Multi-workspace daily digest mode" note 1.
        logs = search(f'@workspace:{wsid} "capture_kind=report" "report_execution_terminal"', H, limit=2000)
        by_exec = defaultdict(list)
        for l in logs:
            msg = l["attributes"].get("message", "")
            if "capture_kind=report" not in msg:
                continue
            state = get_state(msg)
            if state not in ("Success", "Error"):
                continue
            eid = gi(msg, "execution_id")
            rec = dict(
                state=state,
                reason=get_reason(msg),
                sched=gi(msg, "report_schedule_id"),
                dash=gi(msg, "dashboard_id"),
                chart=gi(msg, "chart_id"),
                elapsed=gf(msg, "elapsed_seconds"),
                ts=l["attributes"].get("timestamp", "")[:19],
            )
            by_exec[eid].append(rec)

        execs = []
        for eid, recs in by_exec.items():
            final_state = "Error" if any(r["state"] == "Error" for r in recs) else "Success"
            err = next((r for r in recs if r["state"] == "Error"), recs[0])
            execs.append(dict(eid=eid, state=final_state, **{k: v for k, v in err.items() if k != "state"}))

        results[wsid] = dict(name=name, executions=execs)

    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    main()
