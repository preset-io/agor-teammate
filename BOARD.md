# BOARD.md — Your Agor board

Document your board's structure, zones, and workflow expectations so you (and other agents) know how to organize work spatially.

---

## Board info

- **Board ID:** `[from IDENTITY.md]`
- **Board Name:** `[your board name]`
- **Board URL:** `https://agor.live/board/[board_id]`

---

## Zones

Zones represent workflow states. The zone a worktree is in **is** its status.

Zone info is included in every worktree response as `zone_id` and `zone_label` (no position calculations needed). Trust `zone_label` as the source of truth.

Document each zone below:

```markdown
### [Zone Name]

- **Zone ID:** zone-xxxxx
- **Workflow state:** planning / in-progress / review / done
- **What you do here:** [actions when worktrees land here]
- **When to move out:** [criteria for transition]
- **Trigger (if any):** always_new / show_picker + agent + prompt template
```

---

## Example zones (delete or adapt)

### Design
Planning before implementation. Don't code yet. Move to "In Progress" when design is approved.

### In Progress
Active development. Run tests frequently. Move to "Open a PR" when complete.

### Open a PR
If PR creation has prior user buy-in (zone trigger or explicit ask), create the PR, link `pull_request_url` on the worktree via `agor_worktrees_update`, ensure CI passes, then move to review. Otherwise flag for approval.

### Review
Wait for human or AI review. Don't take automated actions.

### Done
Note the final outcome in memory if useful. Archive the worktree in Agor when appropriate. Stop surfacing in heartbeat reports.

### Trash
Abandoned work. Archive in Agor when appropriate. Stop surfacing in heartbeat reports.

**Typical flow:** Design → In Progress → Open a PR → Review → Done (or Trash)

---

## Working with zones via MCP

- `agor_worktrees_list` — every worktree includes `zone_id`, `zone_label`, `board_id`
- `agor_worktrees_set_zone` — move a worktree
- `agor_boards_get` — full board with all zone definitions

For heartbeat patterns based on `zone_label`, see `HEARTBEAT.md`.

---

## Notes

- Update this file when board structure changes.
- Zone IDs are stable; positions/sizes may drift.
- Adapt the zones to your workflow, not the other way around.
