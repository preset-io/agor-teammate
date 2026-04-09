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
- **Purpose:** Work is committed and ready — waiting for orchestrator to open PR
- **Agent Behavior (orchestrator):**
  - Open PR on apache/superset
  - Link PR URL in worktree metadata (`agor_worktrees_update`)
  - Post in #eng-reviews (with a one-liner — unfurling is unreliable, add context)
  - Add PR link as external link in Shortcut story
  - Reply in original Slack thread with PR link
  - Move worktree to "Needs Max's Review"
- **Zone Trigger:** `show_picker`

### PR Reviews

- **Zone ID:** `zone-pr-review`
- **Purpose:** Review incoming PRs from external contributors
- **Agent Behavior:**
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

## Full Workflow Dance

This is the complete sequence from bug report to done. Every touchpoint matters.

### A. Bug Triage Dance (when a new bug lands)

```
1. Read Slack thread in #bug-reporting
2. Check Shortcut: stories-search for existing ticket
   - If exists: note the story ID, check status
   - If missing: stories-create(type="bug", epic=101517, workflow=500020181, team=5fc58cd7)
     → stories-update(workflow_state_id=500020245)  # Triage state
3. Create worktree: agor_worktrees_create(repoId, boardId, worktreeName, createBranch=true)
4. agor_worktrees_update(worktreeId, issueUrl=<SC story URL>)
5. Create session: agor_sessions_create(worktreeId, "claude-code", initialPrompt)
   → Include in prompt: "DO NOT open a PR. Commit your work when done and stop."
6. agor_worktrees_set_zone(worktreeId, "zone-in-progress")
7. Reply in Slack thread:
   "Tracked: <SC link>  |  Agent: <Agor session URL>"
8. stories-update(workflow_state_id=500020185)  # Implementing
```

### B. PR Opening Dance (when worktree moves to zone-open-pr)

```
1. Open PR on apache/superset (gh pr create)
2. agor_worktrees_update(worktreeId, pullRequestUrl=<PR URL>)
3. stories-add-external-link(storyId, externalLink=<PR URL>)   # param is "externalLink", NOT "url"
4. Post in #eng-reviews:
   "<PR URL>
   One-liner description. Mark easy/tiny ones with ✨"
5. Reply in original Slack thread: "PR up: <PR URL>"
6. agor_worktrees_set_zone(worktreeId, "zone-human-review")
```

### C. Post-Merge Dance (after Max merges)

```
1. Find SC story: stories-get-by-external-link(url=<PR URL>)
2. stories-update(storyId, workflow_state_id=500020392)  # Merged/Done
3. agor_worktrees_set_zone(worktreeId, "zone-done")
4. Reply in original Slack thread: "Merged ✓ <PR URL>"
5. agor_environment_stop(worktreeId)  # Stop docker env
```

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
| SC State: Merged/Done | `500020392` |
| SC Team (Producks) | `5fc58cd7` |
| Max's SC User ID | `5d8c4eae-e5b1-4662-ab9b-a6f106e573df` |
| Slack #bug-reporting | `C0AGRNNURGX` |
| Slack #eng-reviews | `C09KSS4NVLL` |

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
                    ↓ (PR Opening Dance)
             zone-human-review  ←── zone-pr-review
                    ↓ (Post-Merge Dance)
               zone-done
```
