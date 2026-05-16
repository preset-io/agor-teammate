# agor-assistant

**Framework for AI assistants that live inside [Agor](https://agor.live).**

This repo is a template. Clone it, give it to an AI agent, and you get an assistant with file-based identity, memory, and continuity — orchestrating work through the Agor multiplayer canvas.

Inspired by [OpenClaw](https://openclaw.ai/), adapted for Agor's worktree/session/board primitives.

---

## How it works

The framework is just markdown files in a git worktree:

- **Identity** — `IDENTITY.md`, `SOUL.md`, `USER.md`
- **Memory** — `MEMORY.md`, `memory/YYYY-MM-DD.md`, `memory/learnings/`
- **Operating manual** — `AGENTS.md` (always loaded — keep tight), with deeper docs in `BACKUP.md`, `BOARD.md`, `HEARTBEAT.md`, `TOOLS.md`
- **Reusable procedures** — `skills/` ([SKILL.md format](https://agentskills.io))

An assistant wakes up fresh each session, reads these files to reconstitute itself, and orchestrates work through the [Agor MCP](https://agor.live).

---

## Branch model

```
main                       ← this template (framework only)
private-coachbot           ← one running assistant
private-saul               ← another
your-assistant-branch      ← yours
```

Each assistant lives on its own branch. **State is on disk; git is the backup.** See `BACKUP.md`.

- Assistants **never** PR their branch anywhere.
- Assistants **never** fork the public repo.
- Framework improvements come as PRs against `main` from contributors.

---

## Getting started

1. Clone or import this repo into your Agor setup.
2. Create a branch for your assistant: `git checkout -b <your-assistant-name>`.
3. Start an Agor session in the worktree.
4. The assistant follows `BOOTSTRAP.md` on first run — establish identity, connect resources, prove value.
5. After value is established, the assistant suggests a backup setup (private repo, if needed).

---

## Files at a glance

| File | Purpose |
|---|---|
| `AGENTS.md` (= `CLAUDE.md`) | Always-loaded operating manual |
| `BACKUP.md` | Git-as-backup model |
| `BOOTSTRAP.md` | First-run ritual (deleted after) |
| `SOUL.md` | Values and communication style |
| `IDENTITY.md` | Name, vibe, board config |
| `USER.md` | Profile of the human |
| `MEMORY.md` | Long-term curated memory |
| `BOARD.md` | Agor board zones + workflow |
| `HEARTBEAT.md` | Optional periodic tasks |
| `TOOLS.md` | Env-specific shortcuts (incl. roster of your repos) |
| `skills/` | Reusable procedures |

---

## Resources

- **Agor:** [agor.live](https://agor.live)
- **OpenClaw (inspiration):** [openclaw.ai](https://openclaw.ai)
- **Skills ecosystem:** [agentskills.io](https://agentskills.io), [skills.sh](https://skills.sh)
