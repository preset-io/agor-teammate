#!/usr/bin/env python3
"""
Datadog log query helper for SRE triage.

Usage:
  ./scripts/dd.py search --query "service:superset status:error" --hours 24
  ./scripts/dd.py search --cluster production-aws-eu5a --service superset --component app --status error --hours 24
  ./scripts/dd.py search --cluster production-aws-us1a --query '"SSL connection"' --hours 48 --limit 1000
  ./scripts/dd.py top-errors --hours 24 --limit 500
  ./scripts/dd.py stack-traces --query '"USE DATABASE"' --cluster production-aws-eu5a --hours 24

Env vars required: DD_API_KEY, DD_APP_KEY
"""

import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError

DD_API_KEY = os.environ.get("DD_API_KEY")
DD_APP_KEY = os.environ.get("DD_APP_KEY")
DD_API_BASE = "https://api.datadoghq.com/api/v2/logs/events/search"

PROD_CLUSTERS = [
    "production-aws-us1a",
    "production-aws-us2a",
    "production-aws-eu5a",
    "production-aws-ap1a",
]


def check_creds():
    if not DD_API_KEY or not DD_APP_KEY:
        print("ERROR: DD_API_KEY and DD_APP_KEY must be set in environment.", file=sys.stderr)
        sys.exit(1)


def iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def now_and_ago(hours: float):
    now = datetime.now(timezone.utc)
    return iso(now), iso(now - timedelta(hours=hours))


def dd_search(query: str, from_ts: str, to_ts: str, limit: int = 1000) -> list:
    payload = json.dumps({
        "filter": {"query": query, "from": from_ts, "to": to_ts},
        "page": {"limit": min(limit, 1000)},
        "sort": "-timestamp",
    }).encode()

    req = Request(
        DD_API_BASE,
        data=payload,
        headers={
            "DD-API-KEY": DD_API_KEY,
            "DD-APPLICATION-KEY": DD_APP_KEY,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(req) as resp:
            data = json.load(resp)
    except HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)

    logs = data.get("data", [])

    # Page if needed and more results exist
    cursor = data.get("meta", {}).get("page", {}).get("after")
    while cursor and len(logs) < limit:
        paged_payload = json.dumps({
            "filter": {"query": query, "from": from_ts, "to": to_ts},
            "page": {"limit": min(limit - len(logs), 1000), "cursor": cursor},
            "sort": "-timestamp",
        }).encode()
        req = Request(DD_API_BASE, data=paged_payload,
                      headers={"DD-API-KEY": DD_API_KEY, "DD-APPLICATION-KEY": DD_APP_KEY,
                               "Content-Type": "application/json"}, method="POST")
        with urlopen(req) as resp:
            data = json.load(resp)
        logs.extend(data.get("data", []))
        cursor = data.get("meta", {}).get("page", {}).get("after")
        if not data.get("data"):
            break

    return logs


def build_query(args) -> str:
    parts = []
    if args.cluster:
        parts.append(f"kube_cluster_name:{args.cluster}")
    if hasattr(args, "service") and args.service:
        parts.append(f"service:{args.service}")
    if hasattr(args, "component") and args.component:
        parts.append(f"@component:{args.component}")
    if hasattr(args, "status") and args.status:
        parts.append(f"status:{args.status}")
    if hasattr(args, "query") and args.query:
        parts.append(args.query)
    return " ".join(parts) if parts else "service:superset"


def attr(log: dict, key: str):
    return log.get("attributes", {}).get("attributes", {}).get(key)


def normalize_message(msg: str) -> str:
    msg = re.sub(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", "<UUID>", msg)
    msg = re.sub(r"\b\d{5,}\b", "<ID>", msg)
    msg = re.sub(r"'[^']{30,}'", "'<...>'", msg)
    return msg.strip()


def cmd_search(args):
    to_ts, from_ts = now_and_ago(args.hours)
    query = build_query(args)
    print(f"Query: {query}")
    print(f"From:  {from_ts}  To: {to_ts}\n")

    logs = dd_search(query, from_ts, to_ts, limit=args.limit)
    print(f"Results: {len(logs)}\n")

    for log in logs:
        ts = log["attributes"].get("timestamp", "")[:19]
        status = log["attributes"].get("status", "")
        msg = log["attributes"].get("message", "")[:150]
        cluster = next((t.split(":")[1] for t in log["attributes"].get("tags", [])
                        if t.startswith("kube_cluster_name:")), "?")
        workspace = attr(log, "workspace") or ""
        print(f"[{ts}] [{cluster}] [{status}] ws={workspace}  {msg}")


def cmd_top_errors(args):
    to_ts, from_ts = now_and_ago(args.hours)
    clusters = [args.cluster] if args.cluster else PROD_CLUSTERS

    all_logs = []
    for cluster in clusters:
        q = f"service:superset @component:app status:error kube_cluster_name:{cluster}"
        if args.query:
            q += f" {args.query}"
        print(f"Querying {cluster}...", file=sys.stderr)
        all_logs.extend(dd_search(q, from_ts, to_ts, limit=args.limit))

    print(f"\nTotal logs: {len(all_logs)}\n")

    counts = Counter()
    examples = {}
    workspaces: dict = {}

    for log in all_logs:
        msg = log["attributes"].get("message", "")
        exc = attr(log, "exception_class") or ""
        key = exc if exc else normalize_message(msg)[:120]
        counts[key] += 1
        if key not in examples:
            examples[key] = msg
        ws = attr(log, "workspace")
        if ws:
            workspaces.setdefault(key, set()).add(ws)

    print(f"{'Rank':<5} {'Count':<7} {'Exception / Pattern'}")
    print("-" * 80)
    for i, (key, count) in enumerate(counts.most_common(20), 1):
        ws_count = len(workspaces.get(key, set()))
        ws_note = f"  ({ws_count} workspace{'s' if ws_count != 1 else ''})" if ws_count else ""
        print(f"{i:<5} {count:<7} {key[:70]}{ws_note}")
    print()

    if args.verbose:
        print("\nTop 5 full examples:")
        for key, _ in counts.most_common(5):
            print(f"\n--- {key[:80]} ---")
            print(examples[key])


def cmd_stack_traces(args):
    to_ts, from_ts = now_and_ago(args.hours)
    query = build_query(args)
    print(f"Query: {query}")
    print(f"From:  {from_ts}  To: {to_ts}\n")

    logs = dd_search(query, from_ts, to_ts, limit=args.limit)
    with_traces = [l for l in logs if attr(l, "exc_info")]
    print(f"Results: {len(logs)}  (with stack traces: {len(with_traces)})\n")

    seen = set()
    printed = 0
    for log in with_traces:
        exc_class = attr(log, "exception_class") or ""
        exc_info = attr(log, "exc_info") or ""
        dedup_key = exc_class + exc_info[-200:]
        if dedup_key in seen:
            continue
        seen.add(dedup_key)

        ts = log["attributes"].get("timestamp", "")[:19]
        cluster = next((t.split(":")[1] for t in log["attributes"].get("tags", [])
                        if t.startswith("kube_cluster_name:")), "?")
        ws = attr(log, "workspace") or "?"
        uid = attr(log, "user_id") or "?"

        print(f"=== [{ts}] cluster={cluster} workspace={ws} user={uid} ===")
        print(f"Message: {log['attributes'].get('message','')[:200]}")
        print(f"Exception: {exc_class}")
        print("Stack trace:")
        print(exc_info)
        print()

        printed += 1
        if printed >= args.top:
            break

    if printed == 0:
        print("No stack traces found. Try broadening the query or time window.")


def main():
    check_creds()
    parser = argparse.ArgumentParser(description="Datadog log query helper")
    sub = parser.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--cluster", help="kube_cluster_name (default: all prod clusters)")
    common.add_argument("--hours", type=float, default=24, help="How many hours back to search")
    common.add_argument("--limit", type=int, default=1000, help="Max results")
    common.add_argument("--query", help="Extra Datadog query string")

    p_search = sub.add_parser("search", parents=[common], help="Raw log search")
    p_search.add_argument("--service", default="superset")
    p_search.add_argument("--component", default="")
    p_search.add_argument("--status", default="")

    p_top = sub.add_parser("top-errors", parents=[common], help="Rank top errors by frequency")
    p_top.add_argument("--verbose", "-v", action="store_true")

    p_stack = sub.add_parser("stack-traces", parents=[common], help="Show deduplicated stack traces")
    p_stack.add_argument("--service", default="superset")
    p_stack.add_argument("--component", default="app")
    p_stack.add_argument("--status", default="error")
    p_stack.add_argument("--top", type=int, default=10, help="Max unique stack traces to show")

    args = parser.parse_args()

    if args.cmd == "search":
        cmd_search(args)
    elif args.cmd == "top-errors":
        cmd_top_errors(args)
    elif args.cmd == "stack-traces":
        cmd_stack_traces(args)


if __name__ == "__main__":
    main()
