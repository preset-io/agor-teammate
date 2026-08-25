#!/usr/bin/env python3
"""
Shortcut REST API helper for the daily error-cleanup / burndown pipelines.

Replaces the Shortcut MCP tools (stories-create, stories-update, stories-get-by-id,
stories-create-comment, stories-add-relation, workflows-list, teams-list), which
require an interactive OAuth flow the non-interactive Agor session can't complete.
Auth here is a static API token instead of OAuth -- same pattern as scripts/sentry.py
and scripts/dd.py.

Usage:
  ./scripts/shortcut.py story 117856
  ./scripts/shortcut.py create --name "fix(x): ..." --description "..." \
      --type chore --state 500020181 --team automations
  ./scripts/shortcut.py update 117856 --state 500020186
  ./scripts/shortcut.py update 117856 --team automations
  ./scripts/shortcut.py update 117856 --state 500020193 --archive
  ./scripts/shortcut.py comment 117856 --text "Closing as dup of sc-118184."
  ./scripts/shortcut.py relate 117856 118184 --verb duplicates
  ./scripts/shortcut.py search --query "state:Triage owner:eschutho"
  ./scripts/shortcut.py workflows          # list workflows + state IDs
  ./scripts/shortcut.py teams              # list teams (a.k.a. groups) + IDs

Notes:
  - "team" in the REST API is a "group" (group_id); --team accepts a group name
    substring (e.g. "automations") or a raw UUID, resolved via GET /groups.
  - Engineering Kanban workflow = 500020181. Common states:
      Triage 500020245 | Implementing 500020185 | Reviewing 500020186
      Merged/Done 500020392 | Deployed to Stable 500020512 | Won't Do 500020193
  - --state on `create` takes a *workflow_state_id*; the story lands in that state's
    workflow. Omit it to use the org default workflow's default state.

Env vars required: SHORTCUT_API_TOKEN
"""

import argparse
import json
import os
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError

SHORTCUT_API_TOKEN = os.environ.get("SHORTCUT_API_TOKEN")
SHORTCUT_API_BASE = "https://api.app.shortcut.com/api/v3"


def check_creds():
    if not SHORTCUT_API_TOKEN:
        print("ERROR: SHORTCUT_API_TOKEN must be set in environment.", file=sys.stderr)
        sys.exit(1)


def sc_request(method: str, path: str, body: dict | None = None) -> dict | list | None:
    url = f"{SHORTCUT_API_BASE}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = Request(
        url,
        data=data,
        method=method,
        headers={
            "Shortcut-Token": SHORTCUT_API_TOKEN,
            "Content-Type": "application/json",
        },
    )
    try:
        with urlopen(req) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else None
    except HTTPError as e:
        detail = e.read().decode()
        print(f"HTTP {e.code}: {detail}", file=sys.stderr)
        sys.exit(1)


def resolve_group_id(team: str) -> str:
    """Accept a raw UUID or a case-insensitive name substring; return group UUID."""
    if "-" in team and len(team) >= 32:
        return team  # looks like a UUID already
    groups = sc_request("GET", "/groups")
    matches = [g for g in groups if team.lower() in g["name"].lower()]
    if not matches:
        names = ", ".join(g["name"] for g in groups)
        print(f"ERROR: no team/group matching {team!r}. Available: {names}", file=sys.stderr)
        sys.exit(1)
    if len(matches) > 1:
        names = ", ".join(g["name"] for g in matches)
        print(f"ERROR: {team!r} is ambiguous: {names}", file=sys.stderr)
        sys.exit(1)
    return matches[0]["id"]


def print_story(s: dict):
    print(f"sc-{s['id']}  {s['name']}")
    print(f"  type={s.get('story_type')}  workflow={s.get('workflow_id')}  "
          f"state={s.get('workflow_state_id')}  team={s.get('group_id')}  "
          f"archived={s.get('archived')}")
    print(f"  url: {s.get('app_url')}")


def cmd_story(args):
    s = sc_request("GET", f"/stories/{args.story_id}")
    print_story(s)
    if args.raw:
        print(json.dumps(s, indent=2))
    else:
        print(f"\n  description:\n{s.get('description','')}")


def cmd_create(args):
    body = {"name": args.name, "story_type": args.type}
    if args.description:
        body["description"] = args.description
    if args.state:
        body["workflow_state_id"] = args.state
    if args.team:
        body["group_id"] = resolve_group_id(args.team)
    if args.epic:
        body["epic_id"] = args.epic
    s = sc_request("POST", "/stories", body)
    print("Created:")
    print_story(s)


def cmd_update(args):
    body = {}
    if args.state is not None:
        body["workflow_state_id"] = args.state
    if args.team is not None:
        body["group_id"] = resolve_group_id(args.team)
    if args.name is not None:
        body["name"] = args.name
    if args.description is not None:
        body["description"] = args.description
    if args.archive:
        body["archived"] = True
    if args.unarchive:
        body["archived"] = False
    if not body:
        print("ERROR: nothing to update (pass --state/--team/--name/--archive/...).",
              file=sys.stderr)
        sys.exit(1)
    s = sc_request("PUT", f"/stories/{args.story_id}", body)
    print("Updated:")
    print_story(s)


def cmd_comment(args):
    c = sc_request("POST", f"/stories/{args.story_id}/comments", {"text": args.text})
    print(f"Comment added to sc-{args.story_id}: {c.get('app_url','(ok)')}")


def cmd_relate(args):
    # subject <verb> object, e.g. 117856 duplicates 118184
    sc_request("POST", "/story-links", {
        "subject_id": args.subject_id,
        "verb": args.verb,
        "object_id": args.object_id,
    })
    print(f"Linked: sc-{args.subject_id} {args.verb} sc-{args.object_id}")


def cmd_search(args):
    res = sc_request("GET", f"/search/stories?query={args.query.replace(' ', '%20')}&page_size={args.limit}")
    stories = res.get("data", []) if isinstance(res, dict) else res
    print(f"Query: {args.query}   results: {len(stories)}\n")
    for s in stories:
        print(f"sc-{s['id']:<7} [{s.get('story_type','?'):<7}] state={s.get('workflow_state_id')} "
              f"team={s.get('group_id')}  {s.get('name','')[:80]}")


def cmd_workflows(args):
    for w in sc_request("GET", "/workflows"):
        print(f"workflow {w['id']}  {w['name']}")
        for st in w.get("states", []):
            print(f"    {st['id']}  [{st['type']:<9}] {st['name']}")


def cmd_teams(args):
    for g in sc_request("GET", "/groups"):
        if g.get("archived"):
            continue
        print(f"{g['id']}  {g['name']}  (mention: {g.get('mention_name','')})")


def main():
    check_creds()
    parser = argparse.ArgumentParser(description="Shortcut REST API helper")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("story", help="Get a story by public ID")
    p.add_argument("story_id", type=int)
    p.add_argument("--raw", action="store_true", help="Dump full JSON")

    p = sub.add_parser("create", help="Create a story")
    p.add_argument("--name", required=True)
    p.add_argument("--description", default=None)
    p.add_argument("--type", default="chore", choices=["feature", "bug", "chore"])
    p.add_argument("--state", type=int, default=None, help="workflow_state_id")
    p.add_argument("--team", default=None, help="group name substring or UUID")
    p.add_argument("--epic", type=int, default=None)

    p = sub.add_parser("update", help="Update a story")
    p.add_argument("story_id", type=int)
    p.add_argument("--state", type=int, default=None, help="workflow_state_id")
    p.add_argument("--team", default=None, help="group name substring or UUID")
    p.add_argument("--name", default=None)
    p.add_argument("--description", default=None)
    p.add_argument("--archive", action="store_true")
    p.add_argument("--unarchive", action="store_true")

    p = sub.add_parser("comment", help="Add a comment to a story")
    p.add_argument("story_id", type=int)
    p.add_argument("--text", required=True)

    p = sub.add_parser("relate", help="Link two stories (subject <verb> object)")
    p.add_argument("subject_id", type=int)
    p.add_argument("object_id", type=int)
    p.add_argument("--verb", default="relates to",
                   choices=["blocks", "duplicates", "relates to"])

    p = sub.add_parser("search", help="Search stories")
    p.add_argument("--query", required=True, help='e.g. "state:Triage owner:eschutho"')
    p.add_argument("--limit", type=int, default=25)

    sub.add_parser("workflows", help="List workflows and their state IDs")
    sub.add_parser("teams", help="List teams/groups and their IDs")

    args = parser.parse_args()
    {
        "story": cmd_story,
        "create": cmd_create,
        "update": cmd_update,
        "comment": cmd_comment,
        "relate": cmd_relate,
        "search": cmd_search,
        "workflows": cmd_workflows,
        "teams": cmd_teams,
    }[args.cmd](args)


if __name__ == "__main__":
    main()
