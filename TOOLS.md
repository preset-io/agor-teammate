# TOOLS.md — Your env-specific cheatsheet

This is your personal shortcuts file. Keep what's useful, drop what isn't. Knowledge is the source of truth for long-lived notes/skills; this file is only for local environment shortcuts.

---

## Main board

```markdown
- Board ID:   [from IDENTITY.md]
- Board Name: [your board]
- URL:        https://agor.live/board/[board_id]
```

---

## Knowledge

```markdown
- Primary namespace: [from IDENTITY.md]
- URI root:          agor://kb/[namespace]/
```

Useful discovery pattern:

```text
agor_search_tools(domain: "knowledge")
agor_get_tool_details(<tool>)
agor_execute_tool(<tool>, <args>)
```

Prefer Knowledge docs for reusable prompts, plans, notes, and skills. Keep only short local pointers here.

---

## Repos

Quick reference for repos you work in often. (Agor itself is the source of truth — use `agor_repos_list` for fresh IDs.)

| Repo slug | Local path | Notes |
|-----------|------------|-------|
| org/repo1 | /path/to   | Primary |
| org/repo2 | /path/to   | Side    |

For each repo's conventions, **read the repo's own `AGENTS.md` / `CLAUDE.md` / `README`** — don't duplicate them here. For accumulated wisdom about a specific repo (gotchas, user preferences), file it in Knowledge under `refs/`, `skills/`, or `memory/` as appropriate.

---

## Branch naming conventions

```
feature-<description>     # feature-user-auth
fix-<issue>-<description> # fix-123-login-error
exp-<topic>               # exp-react-query
tmp-<purpose>             # tmp-test-integration
```

---

## Reusable prompts

Prefer saving reusable prompts in Knowledge (for search, links, and sharing). Keep only tiny local snippets here when needed during boot or before Knowledge access is available.

---

## Local environment

```markdown
- Agor branches root: ~/.agor/branches/
- Agor database:       ~/.agor/agor.db
- Agor config:         ~/.agor/config.yaml
- Editor / tools:      [your setup]
```

---

## Skills shortcuts

Quick links to your most-used Knowledge skills and any bootstrap-critical local skills (in `skills/`).

---

For Agor MCP tool discovery, use `agor_search_tools` — don't inline tool signatures here. They'd just go stale.
