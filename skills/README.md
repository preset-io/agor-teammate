# Skills

Reusable procedures the assistant can reference.

Agor Knowledge is the preferred home for lightweight, evolving, long-lived, or shareable skill instructions/procedures. The filesystem is often the right home for skills that include executable code, scripts, assets, fixtures, or folders that need to run locally.

---

## Two homes

**Agor Knowledge (`skills/` path in your namespace)** — good for skill instructions that should be searchable, linked to related docs, shared with users/assistants, or updated over time.

**This directory (`skills/`) or another repo-native path** — good for skills with executable code, scripts, assets, fixtures, package manifests, or anything that needs a filesystem/runtime. Also useful for boot-critical procedures that must work before Knowledge tools are available.

Rule of thumb: instructions and references can live in Knowledge; executable skill bundles live in the filesystem, with Knowledge pointers/docs when useful.

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

See `task-management.md` for a local worked example. Use `connect-saas.md` when connecting external SaaS/MCP tools; it is intentionally a research-and-wrapper method, not a catalog. Use `connect-slack.md` for Slack-specific app/token/gateway prerequisites before requesting secrets. Use `agor-gateway-channels.md` for inbound Slack/GitHub/Teams-style gateway channels.

---

## Community skills

A large community ecosystem of SKILL.md files exists. Main discovery points:

| Platform | Notes |
|---|---|
| [skills.sh](https://skills.sh) | Curated skills, `npx skills add <owner/repo>` install. Best signal-to-noise. |
| [SkillsMP](https://skillsmp.com) | Larger catalog, auto-crawls GitHub. More volume, less curation. |
| [github.com/anthropics/skills](https://github.com/anthropics/skills) | Anthropic's official reference skills. Good starting points. |

### Before installing

1. **Read the SKILL.md** — it's markdown, easy to audit
2. **Check install count and publisher** — prefer well-adopted skills from known orgs
3. **Review what it executes** — skills can run shell commands
4. **Decide home:** if it is for this assistant's long-term use, consider recording a Knowledge skill/reference doc rather than only adding local files

Community hubs have had malicious submissions. Standard supply-chain hygiene applies.

---

## Related

- `AGENTS.md` — points here from the Files glossary
- `KNOWLEDGE.md` — explains why Knowledge is the default home for reusable procedures
- `TOOLS.md` — env-specific shortcuts
