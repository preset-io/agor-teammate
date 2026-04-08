# MEMORY.md - Supersetter's Long-Term Memory

---

## Key Facts

- **I am:** Supersetter, Max's AI companion for Apache Superset maintenance
- **Max is:** Creator of Superset (mistercrunch), works at Preset
- **Primary repo:** apache/superset (master branch)
- **Board:** Supersetter (d623c9f3-1cd0-4bbc-8195-3ae6ba596d5d)

## Important Context

- Bootstrapped 2026-03-14
- Board zones: Issue Triage, In Progress, Open a PR, PR Reviews, Needs Max's Review, Done
- Repo context file: `repos/apache-superset.md` (needs to be built out as I learn the codebase)

## Lessons Learned

- **Triage flow:** When spinning up a worktree+session for a specific bug, add that **worker session's** Agor URL as an external link on the Shortcut story (not the orchestrator session). Use `stories-add-external-link` with the worker session URL after `agor_sessions_create` returns.
- **Worktree permissions:** When spinning up a worktree for a reported bug, grant the requester prompt permissions on the worktree. The Agor MCP doesn't expose this yet (`others_can` field not settable via `agor_worktrees_update`) — flag to Agor team, handle via UI for now.
- **Operating branch:** `private-supersetter` is the live operating branch. Push workspace changes there directly (`git push origin HEAD:private-supersetter`). Do NOT open PRs to main — that's unnecessary overhead.

## Ongoing Projects

*(none yet — ready for first task)*
