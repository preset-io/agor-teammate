# Skill: Release Health Check (GitHub Tag → Datadog Logs + Sentry New Issues)

**When to use:** Given a superset-shell release tag (e.g. `v6.1.0.0`), resolve the commit SHA and pull deployment health from **two** sources:
1. **Datadog logs** — aggregate status counts and dominant error/warn messages for the deployed SHA (Steps 4–5).
2. **Sentry new issues** — error groups that *first appeared in this release* (Step 5b). Sentry stamps every issue with the release it debuted in, so a release with new `firstRelease:` groups is introducing new failure modes that Datadog's status-count aggregate can bury. This is the "what broke that wasn't broken before" lens.

Can also run in **comparison mode** to diff the current release against the previously checked one.

---

## ⚠️ Compare Within the Same Release Line

**Always diff a release against the previous release on the _same_ branch line.** The version format is `v<major>.<minor>.<patch>.<build>` (e.g. `v6.0.0.33`), where `<major>.<minor>.<patch>` identifies the **release line** and `<build>` is the incrementing build number on that line.

- ✅ `v6.0.0.33` vs `v6.0.0.32` — same line (`6.0.0.x`), a real apples-to-apples diff.
- ❌ `v6.0.0.33` vs `v6.1.0.6` — **different lines** (`6.0.0.x` vs `6.1.0.x`). These come from different branches with different code, deploy windows, and cluster targets — the diff is meaningless and will produce false "new issue" / "resolved issue" noise.

**Before running comparison mode:**
1. Extract the release line prefix (`major.minor.patch`) of the current tag.
2. Confirm `last_checked.tag` shares that same prefix. If it does **not**, do **not** diff against it — instead find the previous build on the current line (highest `<build>` below the current one with the same prefix) via `gh api .../releases`, and compare against that. If no prior build exists on this line, report it as a **baseline / first check** for the line rather than forcing a cross-line diff.
3. Note the release line explicitly in the Slack summary so the comparison basis is auditable.

---

## Prerequisites

- [ ] GitHub CLI (`gh`) authenticated with access to `preset-io`
- [ ] At least one Datadog auth method available (checked in priority order):
  1. `DD_API_KEY` + `DD_APP_KEY` — traditional API key auth (preferred)
  2. `DATADOG_BEARER_TOKEN` — Personal Access Token fallback
- [ ] `SENTRY_API_TOKEN` set — used by `./scripts/sentry.py` for the Sentry new-issue lens (Step 5b). **Use the script, not the Sentry MCP** — the MCP's OAuth is blocked in this non-interactive env (see `project_sentry_mcp_auth_blocked`). If the token is missing, run Datadog-only, note the gap in the summary, and don't fall back to the MCP.

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
    ],
    "sentry": {
      "project": "superset-python",
      "matched_releases": [
        { "version": "superset@6.0.0.33.014b4fa9-1f499d88", "new_groups": 0 },
        { "version": "superset@hotfix-43784-6.0.0.33.55c27acf-c5eb4281", "new_groups": 3 }
      ],
      "new_issue_ids": ["SUPERSET-PYTHON-1695", "SUPERSET-PYTHON-1696", "SUPERSET-PYTHON-1697"]
    }
  }
}
```

`sentry.new_issue_ids` is the de-dup ledger: an issue already listed here from a prior build on the same line is not "new" again — only report shortIds not present in the previous run's list.

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

### 5b. Sentry: new issue groups that first appeared in this release

Sentry tags each error group with the **release it debuted in**, so this step answers "what new failure modes did this build introduce?" — a signal Datadog's raw status counts can't isolate. Access is via `./scripts/sentry.py` (the app project is `superset-python`), **not** the Sentry MCP (OAuth blocked, see prerequisites).

**Release-name mapping (validated 2026-09-03).** A superset-shell tag maps to Sentry releases whose `version` embeds both the app version string and the **same commit SHA** Datadog uses:
- Datadog `version:014b4fa9…` ⇄ Sentry release `superset@6.0.0.33.**014b4fa9**-1f499d88`.
- One shell tag can map to **several** Sentry releases: the main build plus hotfix builds (`superset@hotfix-43784-6.0.0.33.…`). Check all of them — a clean main build can still ship a hotfix that introduces new groups.

**Step 5b.1 — find the Sentry release(s) for this tag.** Query by the bare version (strip the `v`), then confirm the SHA fragment matches `COMMIT_SHA[:8]`:

```bash
VERSION="${TAG#v}"          # e.g. v6.0.0.33 -> 6.0.0.33
SHA8="${COMMIT_SHA:0:8}"    # e.g. 014b4fa9

curl -s "https://us.sentry.io/api/0/organizations/preset-inc/releases/?query=${VERSION}&per_page=25" \
  -H "Authorization: Bearer $SENTRY_API_TOKEN" \
  | jq -r '.[] | "\(.version)\tnewGroups=\(.newGroups)\tcreated=\(.dateCreated[:10])"'
# Keep the release(s) whose version contains $VERSION. The one containing $SHA8 is the exact
# main build; hotfix-* releases on the same version are also in scope. newGroups>0 => investigate.
```

**Step 5b.2 — enumerate the new issues per matched release** with `firstRelease:` (this is the precise "new in this release" lens):

```bash
for REL in "superset@6.0.0.33.014b4fa9-1f499d88" "superset@hotfix-43784-6.0.0.33.55c27acf-c5eb4281"; do
  echo "=== firstRelease:$REL ==="
  ./scripts/sentry.py search --query "is:unresolved firstRelease:\"$REL\"" --sort new --limit 25
done
```

**Step 5b.3 — time-window fallback** (robust when release-name mapping is fuzzy, e.g. continuous `superset@master.<sha>` deploys that don't embed the version). Catches new groups org-wide since the release date; cross-reference against the matched releases above:

```bash
# N = whole days since RELEASE_DATE (round up). Answers "new issues since this release shipped".
./scripts/sentry.py search --query "is:unresolved firstSeen:-2d" --sort new --limit 25
```

**Classify, don't just count.** For each new issue, tag it **code-shaped** vs **infra-noise** using the skip-list in `skills/sentry-error-burndown.md` (websocket/502, SIGKILL/TimeLimitExceeded, SSL/psycopg2/Redis drops, customer-DB config errors, thumbnail/screenshot timeouts, MCP customer-SQL errors). Note volume (`events`/`users`) and environment (a `firstSeen` issue with 1 event, 0 users, on `app-stg` is a staging blip, not a prod regression). Pull a stack trace for anything code-shaped and non-trivial: `./scripts/sentry.py issue <SHORT-ID>`.

**De-dup** against the previous run's `sentry.new_issue_ids` — a group carried over from an earlier build on the same line is not news.

### 6. Compare against previous run

**First, verify the comparison baseline is on the same release line** (see "⚠️ Compare Within the Same Release Line" above). Confirm `last_checked.tag` shares the current tag's `major.minor.patch` prefix. If it doesn't, pick the previous build on the current line as the baseline (or declare a baseline check if none exists) — never diff across lines.

Then diff the current results against the chosen baseline's `status_summary` and `known_noise`:

- **New error messages** not in `known_noise` → flag these prominently
- **Status count changes** (e.g. errors went from 0 → 12) → flag
- **New clusters** appearing → note (rollout expanding)
- **Sentry new issues** (Step 5b) not in the previous run's `sentry.new_issue_ids` → flag code-shaped ones; note infra-noise ones briefly. A matched release with `newGroups > 0` is the headline even if Datadog status counts look flat.
- **Known noise** (see table below) → mention briefly, don't alarm

### 7. Update state file

Write the new run's results back to `memory/release-health-state.json` and commit:

```bash
# Update last_checked with new tag, sha, release_date, checked_at, status_summary, known_noise,
# and the sentry block (matched_releases + new_issue_ids from Step 5b).
# No credentials stored — only metadata
git add memory/release-health-state.json && git commit -m "chore: update release health state for $TAG"
```

### 8. Send results to Slack via Soraya (SRE assistant)

**Use `agor_gateway_emit_message`** — confirmed working 2026-09-17. Soraya's gateway channel (`019edd38-92af-73a4-9691-a3a8c55ce4f4`) is bound to the `private-sre` branch, has outbound enabled, and its default target is already `#engineering-monitor-logs-production`, so a plain emit delivers the message natively with no token handling required.

The older "Do NOT use `agor_gateway_emit_message` — lacks `chat:write` scope" / "spawn a session and curl with `$SLACK_BOT_TOKEN_XOXB`" instruction is **stale** — same class of staleness as the Sentry spike and JiT gate schedule prompts (see `project_sentry_spike_schedule_stale_prompt` / `project_jit_gate_schedule_stale_dm_instruction` memory notes). Don't spawn a subsession for this step; call the gateway tool directly.

Format the message as:

```
*superset-shell Release Health Check* — <date>
- Release: <tag> (`<sha[:8]>`) — <verdict: ✅ CLEAN | ⚠️ NEEDS ATTENTION | ℹ️ NO CHANGE>
- Release line: <major.minor.patch>.x
- Previous: <last_tag>  (⚠️ note if baseline is a different line, or "baseline — first check on this line")
- Status: info:<n> warn:<n> error:<n> critical:<n>
- Clusters: <list>
- New DD issues: <bulleted list, or "none">
- Sentry new groups: <matched release(s) + count, e.g. "hotfix build +3: LLM/OpenRouter Copilot errors (staging, 1 ev each)"; or "none">
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
| Sentry release `newGroups > 0` / new `firstRelease:` issues | New failure mode introduced by this build — classify code-shaped vs infra-noise, weight by events/users and prod-vs-staging |
| Sentry new issue: 1 event, 0 users, `app-stg` culprit | Staging blip — note, don't alarm |

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
| **How she posts** | `agor_gateway_emit_message` directly (confirmed working 2026-09-17; no subsession/token needed) |
| **Target channel** | `#engineering-monitor-logs-production` (gateway's default target) |

---

## Notes

- The `version` tag in Datadog tracks the **superset-shell** commit SHA, not superset-private.
- **Sentry release ⇄ Datadog version:** the same commit SHA fragment appears in both — Datadog `version:014b4fa9…` ⇄ Sentry `superset@6.0.0.33.014b4fa9-…`. That's the join key when mapping a shell tag to Sentry releases (Step 5b). One shell tag can fan out to multiple Sentry releases (main + hotfix builds).
- Sentry `newGroups` on the release object and `firstRelease:<version>` on the issue search are the two forms of the same "new in this release" signal — `newGroups` is the count, `firstRelease:` enumerates them.
- Logs for a version disappear from `now-Xh` queries once pods are replaced — use absolute `from`/`to` dates tied to the release window.
- Auth priority: `DD_API_KEY` + `DD_APP_KEY` (standard headers) → `DATADOG_BEARER_TOKEN` PAT (`Authorization: Bearer`). Both are in `AGOR_USER_ENV_KEYS` and inherited by scheduled sessions.
- Never store credentials in files — always read from env vars.

---

**Last Updated:** 2026-09-17 (Step 8: `agor_gateway_emit_message` works directly for Soraya's channel — dropped the stale curl/token subsession workaround)
**Created By:** Preset Architect
