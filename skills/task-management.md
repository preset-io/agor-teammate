# Skill: Task management in Agor

**When to use:** the user asks for work that needs its own branch and session.

**Purpose:** spin up an isolated Agor branch + session cleanly, capture the *why* in Knowledge, and close the loop when done.

---

## Prerequisites

- [ ] Main board ID in `IDENTITY.md`
- [ ] Repo registered in Agor
- [ ] Relevant Knowledge context searched/read

---

## Steps

### 1. Search and collect context

Search Knowledge for prior plans, decisions, docs, and memory related to the task. Include only relevant links/snippets in the child session brief. Do not copy private Knowledge content into public places.

### 2. Create an Agor branch

Use current Agor MCP tool discovery for the exact schema. Current shape:

```text
agor_branches_create
  repoId:        <repo>
  branchName:  <kebab-case-descriptive-name>
  createBranch:  true
  sourceBranch:  main
  pullLatest:    true
  boardId:       <main-board>   # required
```

Naming: kebab-case, descriptive but concise — e.g. `superset-fix-chart-bug`, `agor-add-zone-trigger`.

### 3. Spawn a session in it

```text
agor_sessions_create
  branchId:     <from step 1>
  agenticTool:    codex | claude-code | appropriate agent
  initialPrompt:  <full brief: context, goals, success criteria, Knowledge links>
```

A good brief includes:
- Relevant background and `agor://` Knowledge links
- Specific objectives
- What "done" looks like
- Visibility/privacy constraints

### 4. File the *why* in Knowledge

Agor tracks IDs, status, parent/child, timestamps, zone, PR URL. Query MCP when you need them — don't duplicate.

Agor doesn't track **why**. File a memory bullet with `agor_teammate_memory_append`, for example:

```text
Firing up branch <name> for <goal>; success is <done criteria>.
```

For larger task plans, create/update a Knowledge doc under `plans/<project>/...` and link it from memory.

### 5. Monitor

- Callbacks (if enabled) fire when the child session ends
- Otherwise check via session/branch MCP tools
- Or watch the board — zone changes signal progress

### 6. Close the loop

When the task ends:

- Attach any issue or PR the session produced to the branch
- Move the branch to the right zone
- When work is truly done, archive the branch in Agor
- File a Knowledge memory bullet with the outcome
- If you learned something reusable → Knowledge skill/reference doc
- If a local pointer would help future sessions start → update `KNOWLEDGE.md` lightly

---

## Error handling

- **Branch create fails:** verify repoId, boardId, branch name uniqueness
- **Session spawn fails:** verify branchId, prompt is well-formed
- **Knowledge memory append fails:** note the configuration/access gap and migrate the memory once the tool is available
- **Lost track of a branch:** query Agor — Agor knows

---

## Framework improvements

If you spot something worth fixing in the framework itself, see `BACKUP.md`: running teammates don't PR their personal branches. Surface the idea to your human and let them open a clean PR against `main`, unless you are explicitly working on a framework-improvement branch.
