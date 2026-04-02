---
name: Superset triage automation
description: Daily automated triage of stale issues on apache/superset, organized on RepoBot3000 board
type: project
---

Stale issue triage system is live.

**Why:** Evan wants to systematically work through the apache/superset issue backlog, starting with the oldest untouched issues. All actions require his approval before posting.

**Setup:**
- Trigger ID: `trig_01KQyhBijDPpDWqWnPVUrbpF`
- Trigger URL: https://claude.ai/code/scheduled/trig_01KQyhBijDPpDWqWnPVUrbpF
- Board: RepoBot3000 (`a97875fe-34de-4f37-9e43-85c03de86d20`)
- Board URL: https://agor.sandbox.preset.zone/ui/b/repobot3000
- Schedule: Daily at 09:00 UTC
- Rules file: `backlogs/superset-stale-issues.md` in agor-assistant-private

**How to apply:** When Evan mentions Superset triage, issue backlogs, or RepoBot3000, this is the active system.

**Known issue:** `agor_boards_get`, `agor_boards_update`, and `agor_cards_create` all fail with "Board not found: undefined" regardless of boardId format. Board zones need to be set up manually in the UI. Remote agent may have the same problem — needs Agor team to investigate.
