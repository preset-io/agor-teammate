# Skills

Reusable procedures the assistant can reference. Documented in the open [SKILL.md format](https://agentskills.io) — supported by 30+ agent platforms (Claude Code, Codex, Cursor, Copilot, Gemini CLI, etc.).

---

## Two flavors

**This directory (`skills/`)** — markdown-only procedures. Read by the assistant, executed by following the steps. Simple to write, easy to audit, version-controlled like everything else here.

**`.claude/` directory** — executable tools (MCP servers, custom tooling). Use when you need real code, not instructions. More setup.

Start in markdown; graduate to `.claude/` if a skill needs automation.

---

## Skill file format

```markdown
# Skill: <name>

**When to use:** <trigger condition>

**Prerequisites:**
- [ ] <required state / context>

**Steps:**
1. <step>
2. <step>

**Error handling:**
- <common failure> → <fix>
```

See `task-management.md` for a worked example.

---

## Community skills

A large community ecosystem of SKILL.md files exists. Main discovery points:

| Platform | Notes |
|---|---|
| [skills.sh](https://skills.sh) | Curated, ~83K skills, `npx skills add <owner/repo>` install. Best signal-to-noise. |
| [SkillsMP](https://skillsmp.com) | Largest catalog (~351K), auto-crawls GitHub. More volume, less curation. |
| [github.com/anthropics/skills](https://github.com/anthropics/skills) | Anthropic's official reference skills. Good starting points. |

### Before installing

1. **Read the SKILL.md** — it's markdown, easy to audit
2. **Check install count and publisher** — prefer well-adopted skills from known orgs
3. **Review what it executes** — skills can run shell commands

Community hubs have had malicious submissions. Standard supply-chain hygiene applies.

### Use community vs. custom

- **Community** for common patterns (linting, testing, deployment, code review)
- **Custom** for domain-specific work (Agor flows, org-specific processes)

When you spot a repeating pattern, check the ecosystem first.

---

## Related

- `AGENTS.md` — points here from the Files glossary
- `TOOLS.md` — your env-specific shortcuts
- `memory/learnings/` — where patterns surface before they become skills
