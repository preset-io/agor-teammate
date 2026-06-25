# Skill: Release Health Check (GitHub Tag → Datadog Logs)

**When to use:** Given a superset-shell release tag (e.g. `v6.1.0.0`), resolve the commit SHA and pull deployment health from Datadog logs. Can also run in **comparison mode** to diff the current release against the previously checked one.

---

## Prerequisites

- [ ] GitHub CLI (`gh`) authenticated with access to `preset-io`
- [ ] At least one Datadog auth method available (checked in priority order):
  1. `DD_API_KEY` + `DD_APP_KEY` — traditional API key auth (preferred)
  2. `DATADOG_BEARER_TOKEN` — Personal Access Token fallback

---

## State File

State is persisted at `memory/release-health-state.json` between runs:

```json
{
  "last_checked": {
    "tag": "v6.1.0.1",
    "sha": "db341f72caeead6ba7c9e151abaf6af6b38d678d",
    "release_date": "2026-06-23T18:13:45Z",
    "checked_at": "2026-06-25T23:15:00Z",
    "status_summary": {
      "info": 0,
      "warn": 95,
      "error": 0,
      "critical": 0
    },
    "known_noise": [
      "AuthlibDeprecationWarning: authlib.jose module is deprecated",
      "NO_WORKSPACES_AVAILABLE: No workspaces available for task=reports.scheduler",
      "Shutting down: Master",
      "Worker exiting",
      "Not authorized Missing JWT in cookies or headers"
    ]
  }
}
```

---

## Steps

### 1. Load previous state and set up Datadog auth

```bash
cat memory/release-health-state.json
# Note: last_checked.tag, last_checked.sha

# Resolve Datadog auth — prefer DD_API_KEY+DD_APP_KEY, fall back to PAT
if [ -n "$DD_API_KEY" ] && [ -n "$DD_APP_KEY" ]; then
  DD_AUTH_HEADERS=(-H "DD-API-KEY: $DD_API_KEY" -H "DD-APPLICATION-KEY: $DD_APP_KEY")
  echo "Using DD_API_KEY + DD_APP_KEY"
elif [ -n "$DATADOG_BEARER_TOKEN" ]; then
  DD_AUTH_HEADERS=(-H "Authorization: Bearer $DATADOG_BEARER_TOKEN")
  echo "Using DATADOG_BEARER_TOKEN (PAT fallback)"
else
  echo "ERROR: No Datadog credentials found. Set DD_API_KEY+DD_APP_KEY or DATADOG_BEARER_TOKEN."
  exit 1
fi
```

### 2. Find the latest release tag

```bash
gh api "repos/preset-io/superset-shell/releases?per_page=10" \
  --jq '[.[] | {tag: .tag_name, created: .created_at}] | .[0:5]'
```

Pick the most recent tag. If it matches `last_checked.tag` — **no new release**, skip to step 7 with a "no change" message.

### 3. Resolve the new tag to a commit SHA

```bash
TAG="v6.2.0.0"   # substitute latest tag

TAG_OBJ_SHA=$(gh api "repos/preset-io/superset-shell/git/ref/tags/$TAG" --jq '.object.sha, .object.type')
# If type == "tag" (annotated), dereference:
COMMIT_SHA=$(gh api "repos/preset-io/superset-shell/git/tags/$TAG_OBJ_SHA" --jq '.object.sha')
# If type == "commit" (lightweight), TAG_OBJ_SHA IS the commit SHA

gh api repos/preset-io/superset-shell/commits/$COMMIT_SHA \
  --jq '{date: .commit.committer.date, message: .commit.message[:120]}'
```

### 4. Query Datadog logs for the new SHA

```bash
RELEASE_DATE="2026-06-22T00:00:00Z"   # from step 2 created_at, rounded back ~1 day

curl -s -X POST "https://api.datadoghq.com/api/v2/logs/events/search" \
  "${DD_AUTH_HEADERS[@]}" \
  -H "Content-Type: application/json" \
  -d "{
    \"filter\": {
      \"query\": \"version:$COMMIT_SHA\",
      \"from\": \"$RELEASE_DATE\",
      \"to\": \"now\"
    },
    \"sort\": \"-timestamp\",
    \"page\": { \"limit\": 100 }
  }" | jq '{
    total: (.data | length),
    by_status: [.data[].attributes.status] | group_by(.) | map({status: .[0], count: length}),
    environments: [.data[].attributes.tags[] | select(test("^environment:"))] | unique,
    clusters: [.data[].attributes.tags[] | select(test("^cluster_name:"))] | unique,
    first_log: (.data | last).attributes.timestamp,
    last_log: (.data | first).attributes.timestamp
  }'
```

### 5. Pull errors and warnings for the new SHA

```bash
curl -s -X POST "https://api.datadoghq.com/api/v2/logs/events/search" \
  "${DD_AUTH_HEADERS[@]}" \
  -H "Content-Type: application/json" \
  -d "{
    \"filter\": {
      \"query\": \"version:$COMMIT_SHA (status:error OR status:critical OR status:warn)\",
      \"from\": \"$RELEASE_DATE\",
      \"to\": \"now\"
    },
    \"sort\": \"-timestamp\",
    \"page\": { \"limit\": 50 }
  }" | jq '[.data[] | {
    time: .attributes.timestamp,
    status: .attributes.status,
    cluster: (.attributes.tags[] | select(test("^cluster_name:")) | ltrimstr("cluster_name:")),
    message: .attributes.message[:400]
  }] | group_by(.message) | map({message: .[0].message, count: length, status: .[0].status}) | sort_by(-.count)'
```

### 6. Compare against previous run

Diff the current results against `last_checked.status_summary` and `last_checked.known_noise`:

- **New error messages** not in `known_noise` → flag these prominently
- **Status count changes** (e.g. errors went from 0 → 12) → flag
- **New clusters** appearing → note (rollout expanding)
- **Known noise** (see table below) → mention briefly, don't alarm

### 7. Update state file

Write the new run's results back to `memory/release-health-state.json` and commit:

```bash
# Update last_checked with new tag, sha, release_date, checked_at, status_summary, known_noise
# No credentials stored — only metadata
git add memory/release-health-state.json && git commit -m "chore: update release health state for $TAG"
```

### 8. Send results to Slack via Soraya (SRE assistant)

**Do NOT use `agor_gateway_emit_message`** — Soraya's gateway lacks `chat:write` scope.

Instead, create a new session in Soraya's branch and have her post using `$SLACK_BOT_TOKEN_XOXB`:

```
Use agor_sessions_create with:
  branchId: "c0894821-afb7-46a1-9944-f31b1eabd635"  (private-sre)
  agenticTool: "claude-code"
  initialPrompt: "Post this message to #engineering-monitor-logs-production using curl and $SLACK_BOT_TOKEN_XOXB: <message>"
```

**No MCP servers needed** — Soraya has native Slack access via `$SLACK_BOT_TOKEN_XOXB`.

Format the message as:

```
*superset-shell Release Health Check* — <date>
- Release: <tag> (`<sha[:8]>`) — <verdict: ✅ CLEAN | ⚠️ NEEDS ATTENTION | ℹ️ NO CHANGE>
- Previous: <last_tag>
- Status: info:<n> warn:<n> error:<n> critical:<n>
- Clusters: <list>
- New issues: <bulleted list, or "none">
- Known noise suppressed: <count> patterns
```

---

## Known Noise (suppress from alerts)

| Pattern | Reason |
|---------|--------|
| `AuthlibDeprecationWarning: authlib.jose module is deprecated` | Python warning mis-classified as error by log pipeline. Track but don't alarm until authlib 2.0 ships. |
| `NO_WORKSPACES_AVAILABLE: No workspaces available for task=reports.scheduler` | Celery scheduler startup no-op. Benign. |
| `Shutting down: Master` / `Worker exiting` | Normal pod replacement during rolling deploy. |
| `Not authorized Missing JWT in cookies or headers` | Health-check probe hitting auth-protected endpoint. |

---

## Interpreting Results

| Signal | Meaning |
|--------|---------|
| Only `info` / `warn`, no new messages | Clean deployment |
| New `error` messages not in known noise | Investigate immediately |
| Status counts spiked vs. previous | Check if it's a specific cluster or widespread |
| Pods shut down (`Shutting down: Master`) | Version was replaced — check if successor version looks healthy |
| `NO_WORKSPACES_AVAILABLE` | Benign unless count is dramatically higher than previous run |

---

## Key Datadog Tag Conventions (Preset)

| Tag | Value |
|-----|-------|
| `version:` | Git commit SHA of the deployed image |
| `image_tag:` | Same SHA (redundant but present) |
| `service:` | `superset` (not `superset-shell`) for app pods |
| `cluster_name:` | e.g. `production-aws-us1a`, `preset-azure-mpc` |
| `environment:` | `production`, `staging` |

---

## Slack Delivery — Soraya (SRE Assistant)

| Detail | Value |
|--------|-------|
| **Branch** | `private-sre` |
| **Branch ID** | `c0894821-afb7-46a1-9944-f31b1eabd635` |
| **Gateway channel** | Soraya (`019edd38-92af-73a4-9691-a3a8c55ce4f4`) |
| **How she posts** | `curl` + `$SLACK_BOT_TOKEN_XOXB` (native Slack access) |
| **Target channel** | `#engineering-monitor-logs-production` |
| **Why not gateway emit?** | Soraya's bot token missing `chat:write` scope for proactive outbound |

---

## Notes

- The `version` tag in Datadog tracks the **superset-shell** commit SHA, not superset-private.
- Logs for a version disappear from `now-Xh` queries once pods are replaced — use absolute `from`/`to` dates tied to the release window.
- Auth priority: `DD_API_KEY` + `DD_APP_KEY` (standard headers) → `DATADOG_BEARER_TOKEN` PAT (`Authorization: Bearer`). Both are in `AGOR_USER_ENV_KEYS` and inherited by scheduled sessions.
- Never store credentials in files — always read from env vars.

---

**Last Updated:** 2026-06-25
**Created By:** Preset Architect
