# BOARD.md - Supersetter Board Configuration

- **Board ID:** `d623c9f3-1cd0-4bbc-8195-3ae6ba596d5d`
- **Board Name:** Supersetter
- **Board URL:** https://agor.sandbox.preset.zone/ui/b/supersetter

---

## Zones and Workflow

### Supersetter Home

- **Zone ID:** `zone-home`
- **Purpose:** Home base for orchestrator sessions
- **Agent Behavior:** This is where my main session lives

### Issue Triage

- **Zone ID:** `zone-triage`
- **Purpose:** Analyze bug reports, assess severity, propose solutions — no code yet
- **Agent Behavior:**
  - Read the Slack thread / Shortcut ticket
  - Search codebase for relevant code
  - Assess severity and impact
  - Propose a solution approach
  - Move to "In Progress" when ready to implement
- **Zone Trigger:** `always_new` — auto-creates analysis session

### In Progress

- **Zone ID:** `zone-in-progress`
- **Purpose:** Active development work
- **Agent Behavior:**
  - Implement the fix
  - Run tests
  - Commit changes when done
  - **DO NOT open a PR** — move worktree to "Open a PR" zone and stop
  - Update worktree notes with what was done

> **Important:** Workers commit and stop. The orchestrator (me) handles PR creation.

### Open a PR

- **Zone ID:** `zone-open-pr`
- **Purpose:** Work is committed — orchestrator opens the PR, then hands off to Auto Review.
- **Agent Behavior (orchestrator):**
  - Open PR on apache/superset
  - Link PR URL in branch metadata (`agor_branches_update(pullRequestUrl=...)`)
  - Add PR link as external link in Shortcut story
  - Reply in original Slack thread: "PR up: <PR URL> — running CI + QA before posting for review"
  - Move worktree to zone-auto-review and proceed to Dance B2
- **Zone Trigger:** `show_picker`

### Auto Review

- **Zone ID:** `zone-auto-review`
- **Purpose:** CI running + Copilot and bot reviewers commenting; address all feedback before QAgor
- **Agent Behavior (orchestrator):**
  - Request GitHub Copilot review on the PR
  - Poll CI until green (re-trigger flaky failures once)
  - Read Copilot + bot reviewer comments; fix valid points or reply with reason
  - Move to QAgor zone when CI green + all feedback addressed
- **Zone Trigger:** `show_picker`

### QAgor

- **Zone ID:** `zone-qagor`
- **Purpose:** Automated review done — QAgor runs end-to-end QA in an isolated Docker env
- **Agent Behavior (orchestrator):**
  - Create QAgor card + kick off session immediately
  - Poll for QAgor verdict (ticket comment + card zone)
  - PASS → post to #eng-reviews + move to "Ready to stamp!"
  - FAIL → spawn fix worker, loop back to Auto Review (zone-auto-review)
- **Zone Trigger:** `show_picker`

### PR Reviews

- **Zone ID:** `zone-pr-review`
- **Purpose:** Review incoming PRs from external contributors
- **Agent Behavior:**
  - Set PR link on the branch: `agor_branches_update(branchId, pullRequestUrl=<PR URL>)`
  - Checkout PR locally
  - Examine changes against codebase
  - Assess impact and quality
  - Report: mergeable or what needs work
- **Zone Trigger:** `show_picker`

### Needs Max's Review ("Ready to stamp!")

- **Zone ID:** `zone-human-review`
- **Purpose:** PR is open and posted — waiting for Max to review and merge
- **Agent Behavior:**
  - Don't take automated actions
  - Monitor CI — re-trigger transient failures (Docker Hub timeouts etc.)
  - Only touch if Max asks

### Done

- **Zone ID:** `zone-done`
- **Purpose:** PR merged, issue resolved, review done
- **Agent Behavior:** Archive from active tracking, stop environment

---

## Linking Conventions (always hyperlink)

**Every mention of a Shortcut ticket or GitHub PR — anywhere — must be a clickable hyperlink.** This applies to Slack messages, Shortcut comments, PR descriptions, branch notes, memory files, session summaries, and replies to Max.

- Markdown contexts: `[SC-108454](https://app.shortcut.com/preset/story/108454)`, `[apache/superset#40877](https://github.com/apache/superset/pull/40877)`
- Slack messages: use Slack link syntax `<https://app.shortcut.com/preset/story/108454|SC-108454>`, not markdown
- Never write a bare "SC-108454" or "PR 40877" without its URL

**Branch header links (Agor):** Agor renders clickable issue/PR links in the branch header from branch metadata. Sessions do NOT carry link fields — links live on the branch. Set them the moment a ticket or PR exists:

- Ticket known (triage time): `agor_branches_update(branchId, issueUrl=<SC story URL>)`
- PR opened (or identified, for PR-review branches): `agor_branches_update(branchId, pullRequestUrl=<PR URL>)`
- Spot a branch with a known ticket/PR but no header link? Fix it on the spot.

(`agor_branches_update` is the current tool name; older docs may say `agor_worktrees_update`.)

**Home-branch sessions:** triage/orchestration sessions on `private-supersetter` (Bug Basher Home) can't carry per-ticket header links — the home branch is shared, and sessions have no link fields. For those, set the ticket/PR/work-branch URLs in the session **description** via `agor_sessions_update(sessionId, description=...)` as soon as they're known, and always hyperlink them in replies. The clickable header links live on the per-ticket work branch.

---

## Full Workflow Dance

This is the complete sequence from bug report to done. Every touchpoint matters.

### A. Bug Triage Dance (when a new bug lands)

```
1. Read Slack thread in #bug-reporting
2. Check Shortcut: stories-search for existing ticket
   - If exists: note the story ID, check status
   - If missing: stories-create(type="bug", epic=101517, workflow=500020181, team=5fc58cd7)
     → stories-update(workflow_state_id=500020245, owner_ids=["5fbd5291-9d17-435b-be62-e741150064b3"])  # Triage + assign Sophie
3. Create worktree: agor_worktrees_create(repoId, boardId, worktreeName, createBranch=true)
4. agor_branches_update(branchId, issueUrl=<SC story URL>)   # immediately — makes ticket clickable in branch header
5. Create session: agor_sessions_create(worktreeId, "claude-code", initialPrompt)
   → Include in prompt: "DO NOT open a PR. Commit your work when done and stop."
6. Comment the session link on the SC ticket:
   stories-create-comment(storyId, text="🤖 Agor session spun up: <Agor session URL>")
   → Fix the URL first: Agor sometimes returns a /ui/ui/ double-prefix — collapse to a single /ui/.
   → Any time you spin up a NEW session for a ticket later (retry, follow-up worker), add another comment.
7. agor_worktrees_set_zone(worktreeId, "zone-in-progress")
8. Reply in Slack thread:
   "Tracked: <SC link>  |  Agent: <Agor session URL>"
9. stories-update(workflow_state_id=500020185)  # Implementing
```

### B. PR Opening Dance (when worktree moves to zone-open-pr)

The PR is opened here, then handed off to Auto Review (Dance B2).

```
1. Open PR on apache/superset (gh pr create)
2. agor_branches_update(branchId, pullRequestUrl=<PR URL>)   # immediately — makes PR clickable in branch header
3. stories-add-external-link(storyId, externalLink=<PR URL>)   # param is "externalLink", NOT "url"
4. Reply in original Slack thread: "PR up: <PR URL> — running CI + QA before posting for review"
5. Move worktree to zone-auto-review and proceed to Dance B2 (Auto Review).
```

### B2. Auto Review Dance (when worktree moves to zone-auto-review)

**Exit criteria — ALL must be true before moving to QAgor:**
- CI is green (all required checks pass; known flaky tests re-triggered once before counting as failures)
- No lint/pre-commit failures (prettier, mypy, flake8)
- No TypeScript errors in changed files
- All bot reviewer feedback addressed (Copilot, Korbit, CodeRabbit, Cursor)
- Tests exist covering the fix
- PR description is filled out

```
1. Request Copilot review:
   `gh pr edit <PR URL> --add-reviewer "copilot"`
   (Note: exact reviewer handle may vary — verify on first use)
2. Poll `gh pr checks <PR URL>` until all checks pass (or fail hard).
   - Known flaky tests: re-trigger once before counting as a real failure
3. Address automated review feedback:
   - `gh pr view <PR URL> --comments` and review threads (`gh api repos/apache/superset/pulls/<n>/comments`)
   - For each valid point: fix in a new commit, push to the fork, re-check CI
   - For points you intentionally skip: reply on the thread with the reason
4. Once CI green + all bot feedback addressed:
   → move worktree to zone-qagor and proceed to Dance B3
```

### B3. QAgor Dance (when worktree moves to zone-qagor)

```
1. Trigger QAgor — create card(s) AND kick off a session immediately:
   a. Create a card in the Ready for QA zone (actual active intake zone, confirmed 2026-06-17):
      agor_cards_create(boardId="046dc8b6-1447-4b0e-9c43-48ed629562b9", zoneId="zone-1774904426448",
                        title="SC-XXXXX", url=<PR URL>, description=<area of change + bug summary>)
      - For OSS PRs with no Shortcut ticket: use OSS Incoming zone (zone-1780318367054)
      - NOTE: BOARD.md previously said zoneId="zone-incoming" — that zone is stale/inactive
   b. After creating card(s), immediately start a QAgor session — do NOT wait for the heartbeat:
      agor_sessions_create(branchId="8114e2cf-b0eb-43dd-8468-22f653d466c0", agenticTool="claude-code",
                           initialPrompt="Run the QA heartbeat. Read HEARTBEAT.md and execute the
                           full cycle: health check, intake, triage, dispatch, reporting, cleanup.",
                           mcpServerIds=["66be6b4c-013e-42ff-ae45-0b629360c93d",
                                         "e74ff08b-f00d-4e67-8dcc-1bc714508816"],
                           enableCallback=true, callbackSessionId=<your session ID>)
      - `agor_schedules_run_now` on QAgor's schedule requires ownership — can't be used here
   - Also set stories-update(storyId, workflow_state_id=500020186)  # Reviewing — for tracking only
2. Poll for QAgor's verdict (ticket comment via stories-get-by-id, and/or the card's zone moving to
   zone-pass / zone-fail):
   → Comment header format: "## QA Verification — SC-{id}: {title} — PASS/FAIL/BLOCKED"
   → PASS ✅ — ONLY NOW surface the PR for review:
      a. Post in #eng-reviews (plain URL — bot already messages the reviewer directly, no need to ping):
         "<PR URL>"
      b. Reply in Slack thread: "QA passed ✓ — PR posted for review"
      c. agor_worktrees_set_zone(worktreeId, "zone-human-review")
   → FAIL ❌ or BLOCKED:
      - Read QAgor's full comment for findings
      - If fixable: spawn new worker session with QAgor's findings, loop back to B2 (move worktree to zone-auto-review)
      - If needs your call: ping Max in Slack with summary of what QAgor flagged
   → No comment + card in QAgor zone-human-required:
      - This is the "Human Required" path — QAgor hit something it can't test autonomously
      - Ping Max to manually review
```

**QAgor environment:** spins up its own isolated Docker env — does NOT test against 2cad staging.
**QAgor trigger is card-based, not state-based:** QAgor's heartbeat reads cards from its Incoming
zones (`zone-incoming` for SC tickets, `zone-1780318367054` for OSS). Setting a Shortcut ticket to
"Reviewing" does NOT make it run — always create the card (B3 step 1). This is why QAgor previously
only ran when prompted manually.

### C. Post-Merge Dance (after Max merges)

```
1. Find SC story: stories-get-by-external-link(externalLink=<PR URL>)
2. stories-update(storyId, workflow_state_id=500020392)  # Merged/Done
3. agor_branches_set_zone(branchId, "zone-done")
4. Reply in original Slack thread: "Merged ✓ <PR URL>"
5. agor_environment_stop(branchId)  # Stop docker env
```

> **Automated:** the **"Merge patrol (daily)"** schedule on the home branch runs this dance
> every day at 09:00 America/Los_Angeles. It lists board branches with a `pull_request_url`
> outside `zone-done`, checks `gh pr view --json state`, and for any MERGED PR: updates the
> SC ticket to Merged/Done, moves the branch to `zone-done`, stops the env, and logs the run
> to daily memory. It does NOT post to Slack (no Slack tool in scheduled runs) — it lists owed
> replies in its memory entry for a human to post. Manual runs: `agor_schedules_run_now`.

---

## Key IDs Cheat Sheet

| Resource | ID |
|----------|-----|
| Repo (apache/superset) | `4903fa88-c79c-408e-a643-1ca35743373c` |
| Board (Supersetter) | `d623c9f3-1cd0-4bbc-8195-3ae6ba596d5d` |
| Epic (Stabilize Master) | `101517` |
| Shortcut Workflow | `500020181` |
| SC State: Triage | `500020245` |
| SC State: Implementing | `500020185` |
| SC State: Reviewing | `500020186` |
| SC State: Merged/Done | `500020392` |
| SC Team (Producks) | `5fc58cd7` |
| Max's SC User ID | `5d8c4eae-e5b1-4662-ab9b-a6f106e573df` |
| Sophie's SC User ID | `5fbd5291-9d17-435b-be62-e741150064b3` |
| Slack #bug-reporting | `C0AGRNNURGX` |
| Slack #eng-reviews | `C09KSS4NVLL` |
| QAgor Board | `046dc8b6-1447-4b0e-9c43-48ed629562b9` |
| QAgor Branch | `8114e2cf-b0eb-43dd-8468-22f653d466c0` |
| QAgor Incoming zone | `zone-incoming` |
| QAgor OSS Incoming zone | `zone-1780318367054` |
| QAgor pass zone | `zone-pass` |
| QAgor fail zone | `zone-fail` |
| SC Card Status field | `6969b4fc-9c4e-44ed-8bac-d128a7188af5` |
| SC Card Status: Passed | `69e25907` ("Agor-Passed QA") |
| SC Card Status: Failed | `6980e80a` ("Failed QA") |

---

## Shortcut MCP Gotchas

**There is no `epics-get-stories` tool.** To get all stories in an epic, use one of:
- `iterations-get-stories` if stories are in an active/upcoming iteration
- `labels-get-stories` if the epic has a corresponding label
- `projects-get-stories` for a specific project
- `stories-search` with keywords — but it returns top 25 only, doesn't filter by epicId server-side. Paginate or use specific terms.
- Fallback: check the epic directly in Shortcut UI. The epic ID 101517 is at https://app.shortcut.com/preset/epic/101517

**`stories-add-external-link` param is `externalLink` (singular string), NOT `url`.** Using `url` gives a "Required" error.

**`stories-create` uses `workflow`, NOT `team`.** Passing `team` alongside `epic` causes a 400. Use `workflow=500020181`.

---

## Workflow Transitions

```
#bug-reporting
      ↓ (Bug Triage Dance)
zone-triage → zone-in-progress
                    ↓ (worker commits, no PR)
               zone-open-pr
                    ↓ (Dance B: PR opened)
            zone-auto-review  ←──────────────────────┐
                    ↓ (Dance B2: CI + Copilot + bots) │
               zone-qagor                             │
                    ↓ (Dance B3: QAgor)               │
              QAgor: zone-fail → fix ─────────────────┘
              QAgor: zone-pass
                    ↓ (post #eng-reviews)
             zone-human-review  ←── zone-pr-review
                    ↓ (Post-Merge Dance)
               zone-done
```
