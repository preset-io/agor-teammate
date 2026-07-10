# agor-teammate

**Framework for AI teammates that live inside [Agor](https://agor.live).**

This repo is a template. Clone it, give it to an AI agent, and you get an AI teammate with a filesystem home base plus a Knowledge Base-first working model — orchestrating work through the Agor multiplayer canvas.

Inspired by [OpenClaw](https://openclaw.ai/), adapted for Agor's branch/session/board primitives and Agor Knowledge Base.

---

## How it works

The framework has two layers:

1. **Branch/filesystem home base in git** — core framework files, identity, operating manual, executable skills, scripts, local data, and code/file workbench.
2. **Agor Knowledge Base** — long-term, user-visible memory/docs: notes, plans, designs, decisions, drafts, reference material, and shareable artifacts. It is searchable, versioned, permissioned, linkable, and graph-aware.

On each fresh session, a teammate reads its core local files, then searches/reads its assigned Knowledge namespace for current context. The teammate files useful memory back into Knowledge via Agor MCP, especially with the teammate memory append tool.

---

## Local files at a glance

| File | Purpose |
|---|---|
| `AGENTS.md` (= `CLAUDE.md`) | Always-loaded operating manual; points to Knowledge-first model |
| `KNOWLEDGE.md` | Knowledge-first model, conventions, and optional namespace overview |
| `BACKUP.md` | Git backup model for teammate home/base files |
| `BOOTSTRAP.md` | First-run ritual (deleted after) |
| `BOOT.md` | Startup checklist |
| `SOUL.md` | Values and communication style |
| `IDENTITY.md` | Name, vibe, board config, primary Knowledge namespace |
| `USER.md` | Minimal profile of the human |
| `BOARD.md` | Agor board zones + workflow |
| `HEARTBEAT.md` | Optional periodic tasks |
| `TOOLS.md` | Env-specific shortcuts (incl. roster of repos) |
| `skills/` | Local bootstrap/emergency procedures, including `connect-saas` and `agor-gateway-channels`; prefer Knowledge for evolving/shareable skills |

---

## Onboarding defaults

- Ask and record the user’s security/sharing stance early: private vs trusted-team shared, and draft/read-only vs post/write after explicit approval.
- First boot should greet the real user by name when known, lead with user value instead of internal files, avoid unexplained Agor jargon, and return clickable links for created artifacts.
- For SaaS connections, use `skills/connect-saas.md`; for inbound gateway channels, use `skills/agor-gateway-channels.md`.

## Knowledge-first defaults

Use Agor Knowledge for:

- Daily memory and decisions
- Plans, design docs, notes, meeting notes, and research
- Drafts and shareable user-facing docs
- Long-lived reference material and reusable skills/procedures
- Internal graph links between concepts/docs via `agor://`

Use the local filesystem for:

- Core framework/identity/safety files
- `KNOWLEDGE.md` high-level model and optional namespace overview
- Repo-native scripts/config/templates, executable skills, data files, and test fixtures
- Temporary materialized Knowledge docs while editing locally

See `KNOWLEDGE.md` for the detailed decision table and conventions.

---

## Branch model

```
main                       ← this template (framework only)
private-coachbot           ← one running teammate's home/base
private-saul               ← another
kb-first-teammate          ← yours
```

Each teammate lives on its own branch. Git backs up the **teammate home/base files**; Agor Knowledge stores long-term memory and docs. See `BACKUP.md`.

- Running teammates **never** PR their personal branch anywhere.
- Running teammates **never** fork the public repo for private state.
- Framework improvements come as PRs against `main` from contributors/clean branches.

---

## Getting started

1. Clone or import this repo into your Agor setup.
2. Create a branch for your teammate: `git checkout -b <your-teammate-name>`.
3. Assign or identify the teammate's primary Agor Knowledge namespace.
4. Start an Agor session in the branch.
5. The teammate follows `BOOTSTRAP.md` on first run — establish identity, connect Knowledge/board/repos, prove value.
6. After value is established, the teammate suggests a backup setup for the teammate home/base files (private repo, if needed).

---

## Resources

- **Agor:** [agor.live](https://agor.live)
- **OpenClaw (inspiration):** [openclaw.ai](https://openclaw.ai)
- **Connector skill:** [`skills/connect-saas.md`](skills/connect-saas.md)
- **Gateway channel skill:** [`skills/agor-gateway-channels.md`](skills/agor-gateway-channels.md)
