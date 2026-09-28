# Skill: Sentry Error Burndown (daily)

Find one code-fixable production error in Sentry, root-cause it with evidence, ship a fix PR through the standard review pipeline. Modeled on the 2026-07-22 MANAGER-PYTHON-2ZF fix (PR preset-io/manager#3872).

## Before starting

1. Read `memory/` daily logs for the last ~7 days and `MEMORY.md` — collect Sentry issue IDs already fixed, in-flight, or intentionally skipped. Never pick one of those.
2. Check open PRs you authored on the target repos (`gh pr list --author @me`) — an unmerged fix means that issue is still in flight.
3. **Sentry access is via `./scripts/sentry.py` (direct REST API), not the Sentry MCP.** The MCP's OAuth flow has been blocked since 2026-08-10 by a client/server issuer-parameter mismatch (RFC 9207 / MCP SEP-2468) this non-interactive environment can't resolve — see `project_sentry_mcp_auth_blocked`. `SENTRY_API_TOKEN` (Internal Integration token, org `preset-inc`) is set in env; if a fresh run finds it missing, that's a real blocker again — don't fall back to the MCP tools, flag it the same way the prior outage was flagged.

## Picking an issue

1. Sentry org is `preset-inc` (region https://us.sentry.io). List unresolved issues sorted by frequency: `./scripts/sentry.py search --query "is:unresolved" --sort freq --limit 20` (requires `SENTRY_API_TOKEN` in env — direct REST API, not the Sentry MCP; see note below).
2. **Skip infra noise** — not code-fixable in an app repo: websocket disconnects/502s, SIGKILL/TimeLimitExceeded celery kills, SSL cert mismatches, psycopg2/Redis connection drops, customer-database errors (e.g. Snowflake "no current database" — user config). If something looks like a real infra problem (e.g. a staging cert mismatch flooding events), note it in the daily log for Elizabeth instead of fixing.
3. **Prefer**: high event volume or high users-impacted, in repos we own (preset-io/manager, apache/superset via preset deployment, superset-shell...). A "noise" issue (log spam) is a valid pick — killing 100k+ events/month of noise has real SRE value.
4. Pick exactly ONE issue per run. Log the pick + rationale before starting the fix.

## Root-causing (evidence, not guesses)

- Pull full issue details AND breadcrumbs: `./scripts/sentry.py issue <SHORT-ID>` (add `--frames N` to widen the trailing stacktrace/breadcrumb window, `--raw` for the full event JSON) — breadcrumbs often pinpoint the exact trigger (e.g. the Redis MGET immediately before an error identified the missing Split flag).
- Read the actual dependency source when a library is involved: `python3 -m pip download <pkg>==<pinned> --no-deps` and diff against latest before assuming "upgrade fixes it" — verify the code path actually changed.
- Reproduce the mechanism standalone when possible (small python snippet) before writing the fix.
- **Prove the production call path BEFORE writing the fix** (memory `feedback-prove-production-call-path`). Reviewers keep catching "right mechanism, wrong target." The code you patch must be what prod actually executes for the reported symptom — **if it's a base-class method with subclass overrides, the live path is the override, not the base** (#44172: guarded `ExploreMixin.get_timestamp_expression` but prod dispatches through `TableColumn`/`SqlMetric` overrides → dead-code guard + tests that asserted a false guarantee). For a deprecation/warning-driven pick, confirm the warning actually *originates* from the code you're changing, not an upstream layer (#43723: renamed `groupby` in example YAMLs, but the warning came from the frontend query-builder — wrong layer, and it broke ~13 charts). Grep for the real caller and trace the symptom to the exact line you're editing. A green test proves your code does what you intended — not that you changed the right code.

## Implementing

1. Create an Agor branch on the right repo (`agor_branches_create`, board `9a49d11a-...` SRE board). Descriptive kebab name.
2. Fresh branch dirs: your shell may predate the unix group, so direct file edits can hit `EACCES`. `sg`/`newgrp`/`su` workarounds get (correctly) denied by the permission classifier as privilege-escalation-shaped even when `/etc/group` already lists you as a member — don't fight it. Instead, spawn an Agor session on the new branch (`agor_sessions_create`, `enableCallback: true`) and hand it the implementation with full root-cause context; that session's process is provisioned fresh with the correct group from the start (see 2026-07-26 run).
3. Follow the repo's CLAUDE.md. For manager tests see memory `reference_manager_test_recipe`: `__is_unit_test__=1 PARALLEL_TESTS_ENABLED=True TABLESPACE=pg_default <borrowed-venv>/bin/python -m pytest ...` (borrow a sibling worktree's .venv; mgr-test-pg postgres on 5430).
4. Fix + test must both land. Run the relevant test file and ruff (check AND format) before committing.
5. Keep the fix surgical. If the correct fix requires infra changes (Datadog monitors, Terraform, Split console), DO NOT do them — IaC-only rule; note as follow-up for the owning team.

## Shipping

Mirror the "Daily deprecation fix" pipeline — the card + zone placement is what lets the companion schedules (11am requested-changes triage on `zone-in-review`, 3pm PR status check on `zone-pr-ready`) manage the PR lifecycle after this run ends.

1. Shortcut story first — use `scripts/shortcut.py` (direct REST API via `SHORTCUT_API_TOKEN`) for `create`/`update`/state moves: `./scripts/shortcut.py create --type bug --state 500020185 --team automations --name "<title>" --description "<root cause + fix + follow-ups>"`. Engineering Kanban = workflow `500020181` — that's the workflow ID, NOT a valid `--state` value (passing it 422s); `--state` needs a state ID *within* that workflow: Implementing=`500020185`, Reviewing=`500020186`, Merged/Done=`500020392` (run `./scripts/shortcut.py workflows` to re-list if these drift). **Always pass `--team automations`** (a create without it lands orphaned in Triage with no team — the sc-117856 gap from 2026-08-19). **Update 2026-09-11:** the `mcp__shortcut-bug-sorting__*` MCP tools (e.g. `stories-add-external-link`) worked fine, no OAuth prompt, when called directly from this workspace — the "needs interactive OAuth" note above may be stale/scoped to a different flow than assumed. Still use `scripts/shortcut.py` for create/update (it's the tested path and doesn't depend on re-verifying this), but the MCP tools are a live option for anything the script doesn't cover (e.g. attaching a PR/issue URL as an external link on the story, for link-based lookups — the script has no `--external-link` flag).
2. Commit as Elizabeth Thompson <elizabeth@preset.io>, conventional-commit style with `(SC-<story>)` in the subject and `Fixes <SENTRY-ISSUE-ID>` in the body (auto-resolves Sentry on merge). Include the Claude co-author line. **Commit-identity gotcha (confirmed 09-24, 09-27; fixed 09-28)**: this sandbox's default git identity silently overrides the commit author unless forced — stating "commit as elizabeth@preset.io" as prose instruction to the implementation session isn't reliable enough (drifted to eschutho@gmail.com twice). Bake the literal commands into the implementation-session prompt instead: `git config user.name "Elizabeth Thompson"` then `git config user.email "elizabeth@preset.io"`, with an instruction to verify via `git config user.email` before committing. This held on the first try once done this way (preset-io/manager#3997).
3. Push to origin, `gh pr create`. PR body MUST include: root cause, fix rationale, **a Tradeoffs section disclosing any failure-mode semantics change** (raise→warn, suppress, degrade — never leave these undisclosed), follow-ups, testing evidence. **On `apache/superset` (public OSS repo) only: never include the Sentry link/ID or the Shortcut link in the PR body** — see memory `superset-pr-no-preset-refs`; keep that internal tracking in the SRE board card and daily log instead. On the private repos (preset-io/manager, preset-io/superset-shell) the Sentry link + volume and Shortcut link are fine and expected in the PR body.
4. Spawn self-review session on the fix branch (claude-code; codex if OpenAI auth is fixed — it was broken 2026-07-22) with the template from memory `reference_self_review_prompt`. **Give it the raw symptom (Sentry error/breadcrumb), NOT your root-cause writeup or which method you changed** — a review seeded with your framing just re-confirms your target (memory `feedback-prove-production-call-path`). Explicitly task it to independently find the production call path and say whether the patched code is on it. Address blocking findings; failure-mode/unratified findings get disclosed to Elizabeth, never self-ratified.
5. **Card on the SRE board** (`agor_cards_create`):
   - `boardId`: `9a49d11a-6605-4581-b58e-f45fe6bfbadb`
   - `zoneId`: `zone-pr-ready` (the "In Review" zone)
   - `title`: the PR title
   - `url`: the PR URL
   - `description`: one-line summary + Sentry issue ID + Shortcut story URL
   - `data`: `{"agor_branch_id": "<the fix branch's branch_id>"}` — the 3pm PR status check uses this to archive the branch after merge (archive-on-merge cleanup; don't archive it yourself)
6. **Move the Shortcut story to Reviewing**: `./scripts/shortcut.py update <story> --state 500020186`.
7. **Send to Minerva for review** — create a session on the Minerva/EngCodeReviewBot branch (`019df42c-8d6d-76d2-92bd-a49c169db7f1`, board "Minerva") via `agor_sessions_create` (`agenticTool: claude-code`, `enableCallback: true`, `includeLastMessage: true`), asking it to:
   1. Review the PR (include URL, the Sentry issue + volume, and a one-line description of the fix)
   2. Find a reviewer from its roster for the affected repo
   3. Assign them on the GitHub PR
   4. Notify them per their personal preference (GitHub mention vs. a session on their Agor agent's branch)
   Also relay any follow-up notes for Elizabeth (e.g. infra follow-ups discovered during root-causing).
   NEVER comment on the PR directly; own-PR body edits are fine.
8. Update the Agor branch metadata with PR + story URLs (`agor_branches_update`).

After this run, do NOT babysit the PR: the 3pm "Daily PR status check" merges approved cards from `zone-pr-ready` (→ `zone-merged`, story → 500020392) and routes CHANGES_REQUESTED to `zone-in-review`; the 11am "Daily requested-changes triage" addresses feedback there and moves cards back. That's their job, not this run's.

## Wrap-up

- Append to `memory/YYYY-MM-DD.md`: issue picked, root cause, PR/story links, session IDs, learnings, and candidate issues spotted for the next run.
- Commit the workspace memory changes (this repo, `log:` prefix) if that's the current convention in `git log`.
- Final message: lead with what was fixed and the PR link; list anything needing Elizabeth's judgment (tradeoffs, infra follow-ups, blocked items).

## Guardrails

- **Ship the PR — don't hold.** This pipeline carries the fix all the way to an opened PR (Elizabeth, 2026-08-13). Never tell the implementation session "get to a clean tree, I'll handle commit/PR" and hand a finished-but-unshipped fix back to her. The ONLY legitimate reason to stop short of a PR is the unresolved commit-identity classifier block (memory `project_commit_identity_classifier_blocked`) — and if that's the blocker, flag it and the pending identity decision explicitly, don't silently sit on the fix.
- One issue per run; no scope creep into "while I'm here" fixes.
- If no suitable code-fixable issue exists, or the only candidates are already in flight: say so, log the triage notes, and stop — do not force a marginal fix.
- If tests can't be made to pass or the root cause stays unverified, stop and write up findings instead of shipping a speculative fix.
- Never resolve/ignore Sentry issues manually — `Fixes <ID>` in the merged commit is the only resolution path.
