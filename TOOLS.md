# TOOLS.md — Your env-specific cheatsheet

This is your personal shortcuts file. Keep what's useful, drop what isn't. Skills are generic; this file is yours.

---

## Main board

```markdown
- Board ID:   [from IDENTITY.md]
- Board Name: [your board]
- URL:        https://agor.live/board/[board_id]
```

---

## Repos

Quick reference for repos you work in often. (Agor itself is the source of truth — use `agor_repos_list` for fresh IDs.)

| Repo slug | Local path | Notes |
|-----------|------------|-------|
| org/repo1 | /path/to   | Primary |
| org/repo2 | /path/to   | Side    |

For each repo's conventions, **read the repo's own `AGENTS.md` / `CLAUDE.md` / `README`** — don't duplicate them here. For accumulated wisdom about a specific repo (gotchas, user preferences), log it in `memory/learnings/`.

---

## Worktree naming conventions

```
feature-<description>     # feature-user-auth
fix-<issue>-<description> # fix-123-login-error
exp-<topic>               # exp-react-query
tmp-<purpose>             # tmp-test-integration
```

---

## Reusable prompts

Save prompts you spawn often (code review, test run, doc update, etc.) here as templates.

---

## Local environment

```markdown
- Agor worktrees root: ~/.agor/worktrees/
- Agor database:       ~/.agor/agor.db
- Agor config:         ~/.agor/config.yaml
- Editor / tools:      [your setup]
```

---

## Skills shortcuts

Quick links to your most-used local skills (in `skills/`).

---

For Agor MCP tool discovery, use `agor_search_tools` — don't inline tool signatures here. They'd just go stale.
