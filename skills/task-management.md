# Skill: Task management in Agor

**When to use:** the user asks for work that needs its own worktree and session.

**Purpose:** spin up an isolated worktree + session cleanly, capture the *why*, and close the loop when done.

---

## Prerequisites

- [ ] Main board ID in `IDENTITY.md`
- [ ] Repo registered in Agor

---

## Steps

### 1. Create a worktree

```
agor_worktrees_create
  repoId:        <repo>
  worktreeName:  <kebab-case-descriptive-name>
  createBranch:  true
  sourceBranch:  main
  pullLatest:    true
  boardId:       <main-board>   # required
```

Naming: kebab-case, descriptive but concise — e.g. `superset-fix-chart-bug`, `agor-add-zone-trigger`.

### 2. Spawn a session in it

```
agor_sessions_create
  worktreeId:     <from step 1>
  agenticTool:    claude-code
  initialPrompt:  <full brief: context, goals, success criteria>
```

A good brief includes:
- Relevant background
- Specific objectives
- What "done" looks like

### 3. Log the *why*

Agor tracks IDs, status, parent/child, timestamps, zone, PR URL. Query MCP when you need them — don't duplicate.

Agor doesn't track **why**. Put that in today's daily log:

```markdown
### Task: <name>

- Worktree: <name> (<worktree_id>)
- Session:  <session_id>
- Goal:     <why this exists, what success looks like>
- Outcome:  <expected: PR / investigation / etc.>
```

### 4. Monitor

- Callbacks (if `enableCallback: true`) fire when the child session ends
- Otherwise check via `agor_sessions_get` / `agor_worktrees_get`
- Or watch the board — zone changes signal progress

### 5. Close the loop

When the task ends:

- Attach any issue or PR the session produced (`agor_worktrees_update` with `issueUrl` / `pullRequestUrl`)
- Move the worktree to the right zone (`agor_worktrees_set_zone`)
- When work is truly done, archive the worktree in Agor
- Note the outcome in today's daily log
- If you learned something reusable → `memory/learnings/`
- Curate any standout signal into `MEMORY.md`

---

## Error handling

- **Worktree create fails:** verify repoId, boardId, branch name uniqueness
- **Session spawn fails:** verify worktreeId, prompt is well-formed
- **Lost track of a worktree:** `agor_worktrees_list` — Agor knows

---

## Framework improvements

If you spot something worth fixing in the framework itself, see `BACKUP.md`: assistants don't PR their own branches. Surface the idea to your human and let them open a clean PR against `main`.
