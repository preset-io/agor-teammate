#!/usr/bin/env python3
"""
Daily report-execution watchlist digest — see skills/report-execution-investigation.md
("Multi-workspace daily digest mode").

For each watchlist workspace, pulls capture_kind=report terminal lines over the
window, groups by execution_id, filters to state in (Success, Error) to drop
alert-condition-check noise that also tags capture_kind=report, and reports
per-workspace counts + error detail.

Env: DD_API_KEY, DD_APP_KEY
Usage: ./scripts/daily_digest.py [--hours 24]
"""
import sys, os, re, argparse, json
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dd

WATCHLIST = [
    ("ProperBird", "19afbfef"),
    ("stiq.gr", "26f1fa3e"),
    ("Obrien Garret", "2699c223"),
    ("ProperBird #2", "2baffc15"),
    ("Paysend", "9859d4ce"),
    ("blueocean", "77d21c51"),
    ("OpenTable", "bce906ff"),
]


def gi(msg, key):
    m = re.search(rf"(?:^|[\s\[]){re.escape(key)}=([^\s\]]+)", msg)
    return m.group(1) if m else None


def gf(msg, key):
    v = gi(msg, key)
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def terminal_reason(msg):
    m = re.search(r"terminal_reason=(.+?)(?: elapsed_seconds=| execution_id=| \[|$)", msg)
    return m.group(1).strip() if m else None


def state_of(msg):
    if "state=Success" in msg:
        return "Success"
    if "state=Error" in msg:
        return "Error"
    if "state=Not triggered" in msg:
        return "Not triggered"
    if "state=On Grace" in msg:
        return "On Grace"
    return gi(msg, "state")


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
    for name, wsid in WATCHLIST:
        logs = search(f'@workspace:{wsid} "capture_kind=report"', H, limit=3000)

        execs = {}
        for l in logs:
            msg = l["attributes"].get("message", "")
            eid = gi(msg, "execution_id")
            if not eid:
                continue
            rec = execs.setdefault(eid, {})
            if "report_execution_start" in msg:
                rec["report_schedule_id"] = gi(msg, "report_schedule_id")
                rec["dashboard_id"] = gi(msg, "dashboard_id")
                rec["chart_id"] = gi(msg, "chart_id")
                rec["expected_holders"] = gi(msg, "expected_holders")
                rec["start_ts"] = l["attributes"].get("timestamp", "")
            if "report_execution_terminal" in msg:
                rec["state"] = state_of(msg)
                rec["terminal_reason"] = terminal_reason(msg)
                rec["elapsed_seconds"] = gf(msg, "elapsed_seconds")
                rec["term_ts"] = l["attributes"].get("timestamp", "")
                if not rec.get("report_schedule_id"):
                    rec["report_schedule_id"] = gi(msg, "report_schedule_id")
                if not rec.get("dashboard_id"):
                    rec["dashboard_id"] = gi(msg, "dashboard_id")
                if not rec.get("chart_id"):
                    rec["chart_id"] = gi(msg, "chart_id")

        # keep only real report executions (drop alert-condition-check noise)
        real = {eid: r for eid, r in execs.items() if r.get("state") in ("Success", "Error")}
        results[name] = dict(wsid=wsid, total_logs=len(logs), executions=real)

    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    main()
