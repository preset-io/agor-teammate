# HEARTBEAT.md — Periodic tasks

## Scheduling

**Heartbeats do NOT auto-fire.** This framework has no built-in scheduler. A heartbeat session only happens when something explicitly schedules it — typically the worktree's own schedule settings in Agor (`schedule_enabled` and friends on the worktree), or an external scheduler the user wires up (`/loop`, cron, etc.).

**Default state:** disabled. Until a schedule is configured for this worktree, this file is a wishlist — nothing runs.

Check whether your worktree has scheduling enabled: `agor_worktrees_get` and inspect the schedule-related fields. The worktree settings are the source of truth.

## When to add tasks here

When the user asks for proactive monitoring (stale worktrees, PR follow-ups, memory curation) **and** a schedule is in place. Otherwise reactive mode (human-initiated) is fine — many assistants run that way.

---

## Scope

**Main board only.** Check resources on your board (from `IDENTITY.md`), not other users' boards.

---

## Common heartbeat tasks

### Worktree + zone hygiene

`agor_worktrees_list` returns `zone_label` per worktree. Trust it.

```
For each worktree on your board:
  - "Done" / "Trash"         → note outcome if useful; archive the worktree in Agor; stop surfacing in heartbeat reports
  - "Open a PR" + no PR URL  → if PR creation has prior user buy-in (zone trigger, explicit ask), create it via gh pr create and attach with agor_worktrees_update; otherwise flag for approval
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
