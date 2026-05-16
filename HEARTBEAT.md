# HEARTBEAT.md — Periodic tasks

Leave this file empty (or comments only) to skip heartbeat checks. Many assistants work better in reactive mode (human-initiated).

Add tasks below when you want proactive monitoring.

---

## Scope

**Main board only.** Check resources on your board (from `IDENTITY.md`), not other users' boards.

---

## Common heartbeat tasks

### Worktree + zone hygiene

`agor_worktrees_list` returns `zone_label` per worktree. Trust it.

```
For each worktree on your board:
  - "Done" / "Trash"         → archive in memory, stop tracking
  - "Open a PR" + no PR URL  → create PR (gh pr create), attach with agor_worktrees_update
  - "In Progress" + stale    → flag for attention
  - "Design"                 → don't expect code yet
```

### PR state (when `pull_request_url` is set)

- `gh pr view <url>` — state + recent comments
- `gh pr checks <url>` — CI status
- PR merged → move worktree to "Done"
- PR has requested changes → move back to "In Progress"
- New comments, idle session → may need attention

### Sessions

- Blocked or failed sessions on your board
- Sessions waiting for callbacks
- Long-running sessions you should check in on

### Memory

- Promote significant items from daily logs into `MEMORY.md`
- New learnings → `memory/learnings/`
- For worktree/session/repo state, query Agor directly via MCP — no local cache to sync

### Backup (see `BACKUP.md`)

- Commit + push your branch if state has changed meaningfully
- Don't commit on every heartbeat — batch

---

## Cadence

You decide based on the work:
- **Daily:** state sync, daily log review, backup if state changed
- **Weekly:** memory curation, learnings review, stale worktree cleanup
- **On-demand:** when the user asks

---

## Tools

See `AGENTS.md` "Agor MCP" section — use `agor_search_tools` to discover tool signatures; don't memorize them. `gh` CLI for PR/CI checks when available.
