#!/usr/bin/env python3
"""
Sentry REST API helper for the daily spike-check / burndown pipelines.

Replaces the Sentry MCP tools (search_issues, get_sentry_resource, search_events),
which have been blocked since 2026-08-10 by a client/server OAuth issuer-parameter
mismatch (RFC 9207 / MCP SEP-2468) that the non-interactive session can't resolve.
Auth here is a static Internal Integration token instead of OAuth.

Usage:
  ./scripts/sentry.py search --query "is:unresolved" --sort freq --limit 20
  ./scripts/sentry.py search --query "is:unresolved firstSeen:-3d" --sort freq --limit 25
  ./scripts/sentry.py search --query "is:unresolved is:escalating" --sort freq --limit 25
  ./scripts/sentry.py volume-delta --window 24h
  ./scripts/sentry.py issue SUPERSET-PYTHON-12EZ

Env vars required: SENTRY_API_TOKEN
"""

import argparse
import json
import os
import sys
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError

SENTRY_API_TOKEN = os.environ.get("SENTRY_API_TOKEN")
SENTRY_ORG = "preset-inc"
SENTRY_API_BASE = "https://us.sentry.io/api/0"


def check_creds():
    if not SENTRY_API_TOKEN:
        print("ERROR: SENTRY_API_TOKEN must be set in environment.", file=sys.stderr)
        sys.exit(1)


def sentry_get(path: str, params: dict | None = None) -> dict | list:
    url = f"{SENTRY_API_BASE}{path}"
    if params:
        qs = "&".join(f"{k}={quote(str(v))}" for k, v in params.items() if v is not None)
        url = f"{url}?{qs}"

    req = Request(url, headers={"Authorization": f"Bearer {SENTRY_API_TOKEN}"})
    try:
        with urlopen(req) as resp:
            return json.load(resp)
    except HTTPError as e:
        body = e.read().decode()
        print(f"HTTP {e.code}: {body}", file=sys.stderr)
        sys.exit(1)


def cmd_search(args):
    issues = sentry_get(
        f"/organizations/{SENTRY_ORG}/issues/",
        {"query": args.query, "sort": args.sort, "limit": args.limit,
         "statsPeriod": args.stats_period},
    )
    print(f"Query: {args.query}  sort={args.sort}  statsPeriod={args.stats_period}")
    print(f"Results: {len(issues)}\n")
    for i in issues:
        print(f"{i.get('shortId','?'):<24} {i.get('count','?'):>8} events  "
              f"{i.get('userCount','?'):>5} users  "
              f"firstSeen={i.get('firstSeen','')[:10]}  lastSeen={i.get('lastSeen','')[:10]}")
        print(f"    {i.get('title','')[:100]}")
        print(f"    culprit: {i.get('culprit','')[:100]}")
        print()


def cmd_volume_delta(args):
    # "Prior window" = the [2x, 1x] window minus the [1x, 0] window, since Sentry's
    # events endpoint only gives a single count() for a statsPeriod ending now.
    window = args.window
    double = f"{int(window.rstrip('hd')) * 2}{window[-1]}"

    recent = sentry_get(
        f"/organizations/{SENTRY_ORG}/events/",
        {"field": "count()", "query": args.query, "statsPeriod": window, "dataset": "errors"},
    )
    both = sentry_get(
        f"/organizations/{SENTRY_ORG}/events/",
        {"field": "count()", "query": args.query, "statsPeriod": double, "dataset": "errors"},
    )

    recent_count = recent.get("data", [{}])[0].get("count()", 0)
    both_count = both.get("data", [{}])[0].get("count()", 0)
    prior_count = both_count - recent_count

    print(f"Window: {window} vs prior {window}  (query={args.query!r})")
    print(f"  current {window}: {recent_count}")
    print(f"  prior   {window}: {prior_count}")
    if prior_count > 0:
        print(f"  ratio: {recent_count / prior_count:.2f}x")
    else:
        print("  ratio: n/a (prior window is 0 — can't compute a multiplier)")
    if recent_count == 0 and prior_count == 0:
        print("  NOTE: both windows returned 0 — known short-window aggregation quirk "
              "(see project_sentry_mcp_auth_blocked / prior daily logs), not necessarily "
              "a real all-clear. Cross-check with the issue-level search lenses.")


def cmd_issue(args):
    detail = sentry_get(f"/organizations/{SENTRY_ORG}/issues/{args.issue_id}/")
    print(f"{detail.get('shortId')} — {detail.get('title')}")
    print(f"  count={detail.get('count')}  userCount={detail.get('userCount')}  "
          f"status={detail.get('status')}  firstSeen={detail.get('firstSeen')}  "
          f"lastSeen={detail.get('lastSeen')}")
    print(f"  culprit: {detail.get('culprit')}")
    print(f"  permalink: {detail.get('permalink')}")

    event = sentry_get(f"/organizations/{SENTRY_ORG}/issues/{args.issue_id}/events/latest/")
    print("\nLatest event entries:")
    for entry in event.get("entries", []):
        etype = entry.get("type")
        if etype == "exception":
            for val in entry.get("data", {}).get("values", []):
                print(f"  [exception] {val.get('type')}: {val.get('value')}")
                frames = val.get("stacktrace", {}).get("frames", [])
                for f in frames[-args.frames:]:
                    print(f"    {f.get('filename')}:{f.get('lineNo')} in {f.get('function')}")
        elif etype == "breadcrumbs":
            crumbs = entry.get("data", {}).get("values", [])
            print(f"  [breadcrumbs] ({len(crumbs)} total, showing last {args.frames})")
            for c in crumbs[-args.frames:]:
                print(f"    {c.get('timestamp','')} {c.get('category','')}: "
                      f"{c.get('message', c.get('data',''))}")
        elif etype == "message":
            print(f"  [message] {entry.get('data', {}).get('formatted')}")

    if args.raw:
        print("\n--- raw event JSON ---")
        print(json.dumps(event, indent=2))


def main():
    check_creds()
    parser = argparse.ArgumentParser(description="Sentry REST API helper")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_search = sub.add_parser("search", help="Search issues (search_issues MCP equivalent)")
    p_search.add_argument("--query", required=True, help='e.g. "is:unresolved firstSeen:-3d"')
    p_search.add_argument("--sort", default="freq", choices=["freq", "date", "new", "user"])
    p_search.add_argument("--limit", type=int, default=25)
    p_search.add_argument("--stats-period", default="14d")

    p_vol = sub.add_parser("volume-delta", help="Org-wide event count, window vs prior window")
    p_vol.add_argument("--window", default="24h", help="e.g. 24h, 48h")
    p_vol.add_argument("--query", default="is:unresolved")

    p_issue = sub.add_parser("issue", help="Issue detail + latest event (breadcrumbs/stacktrace)")
    p_issue.add_argument("issue_id", help="e.g. SUPERSET-PYTHON-12EZ")
    p_issue.add_argument("--frames", type=int, default=15, help="Trailing frames/breadcrumbs to show")
    p_issue.add_argument("--raw", action="store_true", help="Dump raw event JSON")

    args = parser.parse_args()

    if args.cmd == "search":
        cmd_search(args)
    elif args.cmd == "volume-delta":
        cmd_volume_delta(args)
    elif args.cmd == "issue":
        cmd_issue(args)


if __name__ == "__main__":
    main()
