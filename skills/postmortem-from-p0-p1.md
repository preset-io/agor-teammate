# Skill: Post-Mortem from #p0-p1-comms

**When to use:** Elizabeth (or teammates) asks for a post-mortem/incident writeup for something reported in `#p0-p1-comms` (`C01SK5P63UJ`), usually alongside `#releases-preset-cloud` (`C017U4N8RJP`) for the release/rollback side of the story. Goal: gather decision-grade evidence for the Amazon-style COE defined by [[postmortem-authoring]]. **One production incident per COE is absolute:** separate production events remain separate documents even when they share a release, subsystem, page, or root cause.

> This skill gathers and verifies facts. [[postmortem-authoring]] controls incident identity, preservation, causal analysis, action quality, required structure, and the publication gate. If an existing writeup combines events, inventory every substantive fact first, split it into separate COEs, cross-reference them, and complete a preservation audit before publishing.

---

## Prerequisites

- `SLACK_BOT_TOKEN_XOXB` for reading channel history (see [[feedback_slack_posting]]).
- `gh` CLI access to the relevant repos (`superset-shell`, `manager`, `terraform-modules-services`, `terraform-live-envs`, etc.)
- `DD_API_KEY` + `DD_APP_KEY` for Datadog (never the MCP — see [[feedback_datadog_use_direct_api]]).
- Bot must be a **member** of both channels to read history — `conversations.join` reliably fails with `missing_scope` (no `channels:join`). If `conversations.history` returns `not_in_channel`, ask the requester to `/invite @soraya` (or whatever the bot's handle is) rather than trying to self-join.

---

## Steps

### 1. Pull the incident report

```bash
curl -s "https://slack.com/api/conversations.history?channel=C01SK5P63UJ&oldest=<ts>&limit=200" \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN_XOXB"
```

Get the original report message. It usually names the symptom verbatim (error string, endpoint, HTTP code) and tags who agreed on a mitigation (rollback, feature-flag, etc.). Resolve tagged user IDs to names via `users.info` — don't leave `U0XXXXXXX` placeholders in the doc.

### 2. Pull the release/rollback side

Same call against `C017U4N8RJP`. Search (`oldest` set a few days back — releases/rollouts often span multiple days before someone notices) for:
- The **release announcement** message (links the release PR — this PR's body has the full changelog with links to every constituent PR)
- **Rollout approval requests** ("ready to upgrade vX.Y.Z to region — can I get an approval?") — these establish when/where the bad version actually reached production, which is often *not* the same day it merged
- The **rollback announcement**

If the incident report links a "more details in this thread" pointer to a *third* channel (e.g. a project-specific channel like `#proj-mcp`), ask to be invited there too — that thread often has the actual root-cause diagnosis already done live by someone else. Don't skip it just because it wasn't one of the two channels named.

### 3. Find the actual root cause — don't trust changelog text alone

1. Get the release PR body (`gh pr view <release-pr> --repo <repo> --json body`) — Preset's weekly-release tooling generates a full "Changes since last release" list with links to every constituent PR.
2. Skim for PRs touching the affected subsystem by keyword (e.g. `mcp`, `auth`, `oauth` for an MCP incident). A PR titled `fix(...): stop ... 500ing ...` or `fix(...): make ... best-effort` from a *previous* date is a strong signal you're looking at a **regression of an already-fixed bug** — check whether that fix commit is actually present at the bad tag.
3. **Confirm via source diff, not changelog presence/absence.** Changelogs list "since last release" and won't mention a fix that shipped even earlier — that's normal, not evidence either way. Clone the repo and diff the actual file across tags:
   ```bash
   git clone --filter=blob:none --no-checkout <repo-url> /tmp/<repo>-check
   cd /tmp/<repo>-check
   git show <bad-tag>:<path/to/file> | grep -n '<distinguishing line from the fix commit>'
   git show <good-tag>:<path/to/file> | grep -n '<same>'
   ```
   This is the difference between "the changelog seems to suggest X" and "I directly confirmed the buggy code was present at this exact tag."
4. Check if there's already an Agor KB incident doc for the earlier occurrence (`agor_kb_get` with `namespace: "incidents"` and a guessed path, or `agor_kb_search`) — if the same bug happened before, that doc usually has the full traceback and code walkthrough already done. Link to it rather than re-deriving.

### 4. Quantify blast radius in Datadog

Pull counts at **every layer the request passes through**, not just the app. A request-path incident (auth, gateway, etc.) usually shows up at both:
- The app/pod layer (`service:<app>`, search the actual error string/exception class)
- The ingress/gateway layer (`service:api-gateway`, `source:apigw-sync` for Kong — a **separate log pipeline** from the app's own `source:nginx`/app logs; don't assume one covers the other)

Group by `cluster_name`/`environment` and get exact counts via `/api/v2/logs/analytics/aggregate`, not just samples. Find the **last** occurrence after the reported rollback/fix to confirm it's actually resolved before writing that section.

### 5. Check whether any monitor should have caught it — and why it didn't

```bash
curl -s "https://api.datadoghq.com/api/v1/monitor" -H "DD-API-KEY: $DD_API_KEY" -H "DD-APPLICATION-KEY: $DD_APP_KEY" \
  | jq '[.[] | select(.tags[]? | test("<relevant-tag>"; "i"))]'
```

For each candidate monitor, check `overall_state_modified` and pull `/api/v1/events?tags=monitor_id:<id>` over the incident window — if there are no events, it never fired, full stop. Then figure out **why**, since "no monitor exists" and "a monitor exists but didn't fire" are different findings with different fixes:
- **No monitor at all** on the failing layer → straightforward gap, propose one (check [[project_iac_only_no_manual_infra_changes]] — Datadog monitors are Terraform + PR only, never live API/console).
- **A monitor exists on the right data but didn't fire** → check if it's a volume/count threshold that a low-traffic-but-100%-failing workspace wouldn't cross, or a ratio metric whose denominator collapses when the failure happens *before* the thing being measured is ever attempted (e.g. a "tool failure rate" metric can't see an auth-layer crash that happens before any tool call). Both are real, distinct monitoring-design gaps worth calling out explicitly — don't just say "it should have fired."

### 6. Write the doc

Publish to Agor Knowledge under the `incidents` namespace, following the existing convention (see prior docs there for title/path style):

```
agor_kb_put({
  namespace: "incidents",
  path: "YYYY-MM-DD-<short-slug>.md",
  kind: "decision",
  visibility: "public",
  status: "published",
  editPolicy: "public",
  content: "<full markdown>"
})
```

Structure that's worked well:
1. **Header** — status, severity, author, and a `**Related:**` line linking any prior incident doc via `agor://kb/document/<id>` if this is a recurrence.
2. **TL;DR** — 5-8 bullets, the whole story compressible to a 30-second read.
3. **Timeline** — a UTC table. Anchor every row to something verifiable (a commit SHA, a Slack message timestamp, a Datadog event timestamp) — not vague relative time.
4. **Root cause** — the confirmed mechanism (code snippet if it clarifies), plus the source-diff evidence from step 3. If there's an open question you couldn't resolve from outside the org (e.g. *why* a fix didn't make it into a release), say so explicitly and name who should chase it — don't paper over the gap with speculation stated as fact.
5. **Impact** — the Datadog table from step 4.
6. **Detection gap** — the findings from step 5, with what you already did about it (e.g. a PR you opened) linked directly.
7. **Recommendations** — ordered by leverage. The highest-leverage fix in a "regression of an already-fixed bug" case is almost always the release-process gap, not another layer of monitoring — say that explicitly rather than burying it under a list of equally-weighted bullets.

### 7. Report back in Slack

Lead with the headline finding (usually "this is a recurrence" or "this is new"), give the one-sentence root cause, the impact numbers, and the doc URL. Don't repeat the full timeline in the chat message — that's what the doc is for.

---

## Notes

- If asked to look at a channel the bot isn't in, don't guess at content or skip it silently — say plainly you're not a member and ask for an invite. Same for any channel a "more details in this thread" link points to.
- Slack timestamps are Unix epoch floats (`ts`); convert with `datetime.fromtimestamp(ts, tz=timezone.utc)`, don't eyeball them.
- Resolve every `U0XXXXXXX` user ID to a real name via `users.info` before it goes in a doc — IDs are meaningless to a reader later.
- This skill composes with [[reference_report_execution_investigation]] and [[project_datadog_review_workflow]] for the Datadog-query side, and with [[feedback_iac_only_no_manual_infra_changes]] if the recommendation involves a new/changed monitor.

**Related skills:** [[release-health-check]] (adjacent recurring Datadog-vs-release-tag workflow), [[report-execution-investigation]] (Datadog execution-id tracing pattern)
