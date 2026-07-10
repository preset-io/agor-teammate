# HEARTBEAT.md — Periodic tasks

## Scheduling

**Heartbeats do NOT auto-fire.** This framework has no built-in scheduler. A heartbeat session only happens when something explicitly schedules it — typically the branch's own schedule settings in Agor (`schedule_enabled` and friends on the branch), or an external scheduler the user wires up (`/loop`, cron, etc.).

**Default state:** disabled. Until a schedule is configured for this branch, this file is a wishlist — nothing runs.

Check whether your branch has scheduling enabled: `agor_branches_get` and inspect the schedule-related fields. The branch settings are the source of truth.

## When to add tasks here

When the user asks for proactive monitoring (stale branches, PR follow-ups, memory curation) **and** a schedule is in place. Otherwise reactive mode (human-initiated) is fine — many teammates run that way.

After a useful result, look for a natural recurring version and offer it rather
than silently adding it here. Agree with the user on the deliverable, data
scope, cadence, destination, and how to change or disable it. Create the Agor
schedule only after approval, then keep this file focused on the work that
schedule should perform.

---

## Scope

**Main board only.** Check resources on your board (from `IDENTITY.md`), not other users' boards.

---

## Common heartbeat tasks

### Branch + zone hygiene

`agor_branches_list` returns `zone_label` per branch. Trust it.

```
For each branch on your board:
  - "Done" / "Trash"         → note outcome if useful; archive the branch in Agor; stop surfacing in heartbeat reports
  - "Open a PR" + no PR URL  → if PR creation has prior user buy-in (zone trigger, explicit ask), create it via gh pr create and attach with agor_branches_update; otherwise flag for approval
  - "In Progress" + stale    → flag for attention
  - "Design"                 → don't expect code yet
```

### PR state (when `pull_request_url` is set)

- `gh pr view <url>` — state + recent comments
- `gh pr checks <url>` — CI status
- PR merged → move branch to "Done"
- PR has requested changes → move back to "In Progress"
- New comments, idle session → may need attention

### Sessions

- Blocked or failed sessions on your board
- Sessions waiting for callbacks
- Long-running sessions you should check in on

### Knowledge + memory

- File notable heartbeat observations with `agor_teammate_memory_append`
- Promote significant memory into durable Knowledge docs under `decisions/`, `plans/`, `refs/`, or `skills/`
- Garden stale Knowledge docs: update status, link successors, archive/supersede duplicates
- For branch/session/repo state, query Agor directly via MCP — no local cache to sync

### Backup (see `BACKUP.md`)

- Commit + push your branch if local boot-kit files changed meaningfully
- Do not use git backup as a substitute for Knowledge memory/docs
- Don't commit on every heartbeat — batch

---

## Cadence

You decide based on the work:
- **Daily:** state sync, Knowledge memory review/gardening, backup if local boot-kit files changed
- **Weekly:** memory curation, learnings review, stale branch cleanup
- **On-demand:** when the user asks

---

## Tools

See `AGENTS.md` "Agor MCP" and `KNOWLEDGE.md` — use `agor_search_tools` to discover tool signatures; don't memorize them. `gh` CLI for PR/CI checks when available.
