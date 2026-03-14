# BOARD.md - Supersetter Board Configuration

- **Board ID:** `d623c9f3-1cd0-4bbc-8195-3ae6ba596d5d`
- **Board Name:** Supersetter
- **Board URL:** https://agor.sandbox.preset.zone/ui/b/supersetter

---

## Zones and Workflow

### Supersetter Home

- **Zone ID:** zone-home
- **Purpose:** Home base for orchestrator sessions
- **Workflow State:** home
- **Agent Behavior:** This is where my main session lives

### Issue Triage

- **Zone ID:** zone-triage
- **Purpose:** Analyze GitHub issues, assess severity, propose solutions
- **Workflow State:** triage
- **Agent Behavior:**
  - Read and understand the issue
  - Search the codebase for relevant code
  - Assess severity and impact
  - Propose solution approach (no code yet)
  - Move to "In Progress" when ready to implement
- **Zone Trigger:** always_new — auto-creates analysis session

### In Progress

- **Zone ID:** zone-in-progress
- **Purpose:** Active development work
- **Workflow State:** in-progress
- **Agent Behavior:**
  - Implement the solution
  - Run tests frequently
  - Update worktree notes with progress
  - Move to "Open a PR" when done

### Open a PR

- **Zone ID:** zone-open-pr
- **Purpose:** Finalize work and create pull request
- **Workflow State:** ready-for-pr
- **Agent Behavior:**
  - Run tests, commit changes
  - Open PR on apache/superset
  - Link PR URL to worktree metadata
  - Move to "Needs Max's Review" or "PR Reviews"
- **Zone Trigger:** show_picker

### PR Reviews

- **Zone ID:** zone-pr-review
- **Purpose:** Review incoming PRs from contributors
- **Workflow State:** reviewing
- **Agent Behavior:**
  - Checkout PR locally
  - Examine changes against codebase
  - Assess impact and quality
  - Report whether mergeable or what needs work
- **Zone Trigger:** show_picker

### Needs Max's Review

- **Zone ID:** zone-human-review
- **Purpose:** Work ready for Max to look at
- **Workflow State:** human-review
- **Agent Behavior:**
  - Don't take automated actions
  - Only touch if Max asks

### Done

- **Zone ID:** zone-done
- **Purpose:** Completed work (PR merged, issue resolved, review done)
- **Workflow State:** done
- **Agent Behavior:**
  - Mark completed in memory
  - Archive from active tracking

---

## Workflow Transitions

```
Issue Triage -> In Progress -> Open a PR -> Needs Max's Review -> Done
                                   |
PR Reviews -> Needs Max's Review -> Done
```
