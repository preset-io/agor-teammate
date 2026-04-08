# SKILL: Bug Bash

## When to Use
When a bug is reported on Slack (#bug-reporting), found in Shortcut, or mentioned by Max.

## The Flow

### 1. Find the Bug
```
- Search Slack: slack_search_public_and_private(query, in:#bug-reporting)
- Read thread: slack_read_thread(channel_id, message_ts, response_format="detailed")
  → Gets text, file metadata (name, ID, type, size), and replies
- File search: slack_search_public_and_private(content_types="files", type:images)
  → Gets image metadata/permalinks (can't view actual images)
```

### 2. Check Shortcut
```
- Search: stories-search(name="keyword", isDone=false)
- If exists: get story details, check if assigned
- If missing: create story
  → name, type="bug", epic=101517, workflow=500020181
  → Include Slack thread link in description
```

### 3. Assign & Update
```
- Assign to Max: stories-update(storyPublicId, owner_ids=["5d8c4eae-..."])
- Move to Implementing: workflow_state_id=500020185
- Add external links (PR URLs) as they come
```

### 4. Create Worktree + Session
```
- Worktree: agor_worktrees_create(repoId, worktreeName, createBranch=true, boardId)
- Update metadata: agor_worktrees_update(worktreeId, notes, issueUrl)
- Session: agor_sessions_create(worktreeId, agenticTool="claude-code", initialPrompt)
- Place in zone: agor_worktrees_set_zone(worktreeId, "zone-in-progress")
```

### 5. Thread on Slack
```
- Reply on original message with BOTH links:
  "Tracked in Shortcut: https://app.shortcut.com/preset/story/XXXXX
   Agent working on it: https://agor.sandbox.preset.zone/ui/b/supersetter/SESSION_ID"
```

### 6. Follow Up
```
- Check session status: agor_sessions_get(sessionId)
- When done: move worktree to zone-open-pr
- Update Shortcut with PR link: stories-add-external-link
- Thread PR link on Slack too
```

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
| Max's Shortcut User ID | `5d8c4eae-e5b1-4662-ab9b-a6f106e573df` |
| Slack #bug-reporting | `C0AGRNNURGX` |

## Notes

- Slack MCP returns text only — no image content. Use `read_thread` for file metadata.
- Always include Agor session link in Slack thread (not just Shortcut).
- Check if Shortcut story already exists before creating duplicates.
- Check if PR #39173 or other recent PRs already addressed the issue.
