# SKILL: Bug Bash

## When to Use
When a bug is reported on Slack (#bug-reporting), found in Shortcut, or mentioned by Max.

> **Full workflow with all zone transitions and Slack/Shortcut/GitHub touchpoints is in BOARD.md.**
> Read it. This skill is a quick reference.

---

## The Flow

### 1. Find the Bug
```
- Read thread: slack_read_thread(channel_id, message_ts)
  → Gets text, file metadata. Can't view image content — ask reporter to describe in thread.
- Check for existing SC ticket: stories-search(name="keyword", isDone=false)
```

### 2. Triage in Shortcut
```
- If missing, create:
  stories-create(name, type="bug", epic=101517, workflow=500020181, team="5fc58cd7")
  stories-update(storyId, workflow_state_id=500020245)  # Triage
- Note the SC story URL: https://app.shortcut.com/preset/story/<ID>
```

### 3. Spin Up Worktree + Session
```
- agor_worktrees_create(repoId="4903fa88-...", boardId="d623c9f3-...", worktreeName, createBranch=true)
- agor_worktrees_update(worktreeId, notes, issueUrl=<SC story URL>)
- agor_sessions_create(worktreeId, "claude-code", initialPrompt)
  ↳ ALWAYS include in prompt: "DO NOT open a PR. Commit your work and stop."
- agor_worktrees_set_zone(worktreeId, "zone-in-progress")
- stories-update(storyId, workflow_state_id=500020185)  # Implementing
```

### 4. Reply in Slack Thread
```
"Tracked: <SC story URL>  |  Agent: <Agor session URL>"
```

### 5. When Worker is Done (worktree moves to zone-open-pr)
See **PR Opening Dance** in BOARD.md:
```
- gh pr create (orchestrator opens PR, not worker)
- Post in #eng-reviews with one-liner
- Link PR in Shortcut + Slack thread
- agor_worktrees_set_zone(worktreeId, "zone-human-review")
```

### 6. After Max Merges
See **Post-Merge Dance** in BOARD.md:
```
- stories-get-by-external-link(url=<PR URL>) → find SC story
- stories-update(workflow_state_id=500020392)  # Merged/Done
- agor_worktrees_set_zone(worktreeId, "zone-done")
- Reply in Slack thread: "Merged ✓"
- agor_environment_stop(worktreeId)
```

---

## Key IDs (Cheat Sheet)

| Resource | ID |
|----------|-----|
| Repo (apache/superset) | `4903fa88-c79c-408e-a643-1ca35743373c` |
| Board (Supersetter) | `d623c9f3-1cd0-4bbc-8195-3ae6ba596d5d` |
| Epic (Stabilize Master) | `101517` |
| Workflow (Engineering Kanban) | `500020181` |
| State: Triage | `500020245` |
| State: Implementing | `500020185` |
| State: Merged/Done | `500020392` |
| SC Team (Producks) | `5fc58cd7` |
| Max's SC User ID | `5d8c4eae-e5b1-4662-ab9b-a6f106e573df` |
| Slack #bug-reporting | `C0AGRNNURGX` |
| Slack #eng-reviews | `C09KSS4NVLL` |

## Notes

- Slack MCP: text only, no image content. Ask reporter to describe in thread.
- Always include Agor session URL in Slack reply (not just SC link).
- Workers commit but DO NOT open PRs — orchestrator handles that.
- Tiny/easy PRs: mark with ✨ in #eng-reviews post.
- #eng-reviews: unfurling unreliable — always add a one-liner alongside the URL.
