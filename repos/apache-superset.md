# apache/superset - Repository Context

**Repo:** https://github.com/apache/superset
**Default Branch:** master
**Agor Repo ID:** 4903fa88-c79c-408e-a643-1ca35743373c

## Overview

Apache Superset is a modern data exploration and visualization platform. 60k+ stars, large contributor community.

## Tech Stack

- **Backend:** Python (Flask, SQLAlchemy, Pandas)
- **Frontend:** TypeScript, React, Ant Design
- **Database:** Supports many via SQLAlchemy (Postgres, MySQL, etc.)
- **Build:** Node.js (webpack), Python (setuptools/pip)
- **Tests:** pytest (backend), Jest (frontend)

## Key Directories

*(To be filled in as I explore the codebase)*

- `superset/` — Python backend
- `superset-frontend/` — React/TypeScript frontend
- `tests/` — Backend tests
- `superset-frontend/src/` — Frontend source

## Workflow

- PRs go to `master`
- CI runs on GitHub Actions
- Tests: `pytest` for backend, `npm run test` for frontend

## Opening PRs on apache/superset

**All PRs must go to apache/superset — never to superset-private or any other fork.**

Two tokens are in the environment — use the right one for each step:

| Operation | Token | Why |
|-----------|-------|-----|
| `git push` to fork | `GITHUB_TOKEN` (default) | fine-grained PAT, push access to preset-io org |
| `gh pr create` on apache/superset | `GITHUB_TOKEN_WRITE` | classic PAT with `public_repo` scope |

```bash
# 1. Push branch to preset-io/superset (not yousoph/superset — it 403s)
git remote add preset-io-public https://github.com/preset-io/superset.git  # if not already set
git push preset-io-public <branch-name>

# 2. Create PR on apache/superset
GH_TOKEN=$GITHUB_TOKEN_WRITE gh pr create \
  --repo apache/superset \
  --head "preset-io:<branch-name>" \
  --base master \
  --title "..." \
  --body "..."
```

**Do not use `yousoph/superset`** — push fails (403) as of 2026-06-11.
**Do not use `GITHUB_TOKEN` for `gh pr create`** — fine-grained PAT lacks `createPullRequest` permission on apache org.

## Patterns & Conventions

*(To be filled in as I learn)*

## Things to Know

*(To be filled in as I learn)*
