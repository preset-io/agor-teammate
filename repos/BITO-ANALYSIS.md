# Bito AI Architect — Analysis & Agor Recreation Plan

## What Bito AI Architect Actually Is

At its core, Bito is a **codebase indexing service** that builds a knowledge graph of your repos and exposes it to AI agents via MCP. It's not magic — it's:

1. **Indexer:** Clones your repos, uses LLMs (Claude Haiku + Grok) to analyze code structure, dependencies, call graphs, and patterns. Costs ~$0.20-0.40/MB. Takes 3-10 min per repo.
2. **Knowledge Graph:** Stores the indexed understanding in MySQL — services, endpoints, dependencies, design patterns, API relationships.
3. **MCP Server:** Exposes the knowledge graph to Claude Code, Cursor, etc. via Model Context Protocol.
4. **Skills/Commands:** Pre-built workflows that use the knowledge graph context.

## Bito's Feature Set (from their Claude plugin)

| Feature | What It Does |
|---------|-------------|
| **Codebase Explorer** | Cross-repo code search, dependency exploration |
| **Feature Plan** | Implementation planning informed by actual architecture |
| **PRD Generator** | Product Requirements Documents with system context |
| **TRD Generator** | Technical Requirements Documents based on existing patterns |
| **Production Triage** | Incident diagnosis with blast radius analysis |
| **Code Review** | Context-aware PR reviews (GitHub/GitLab/Bitbucket) |
| **Spec-Driven Dev** | Generate detailed LLDs (Low-Level Designs) |

## Bito's Architecture (Self-Hosted)

```
[GitHub/GitLab Repos]
        |
        v
[CIS Provider] ──LLM──> [Knowledge Graph in MySQL]
[CIS Manager]            (services, APIs, deps,
[CIS Config]              patterns, call graphs)
[CIS Tracker]
        |
        v
[MCP Server] ──exposed──> [Claude Code / Cursor / etc.]
        |
        v
[Skills: explore, plan, triage, review, ...]
```

Runs as Docker Compose (5 containers + MySQL) or Kubernetes.
Needs 6-8 cores, 8-12 GB RAM for self-hosted.

## What We Already Have (vs. What Bito Provides)

| Bito Capability | Current Preset Architect Status | Gap |
|----------------|-------------------------------|-----|
| Repo catalog | **DONE** — 171 repos cataloged in CATALOG.md | None |
| Architecture map | **DONE** — ARCHITECTURE.md, INFRA.md | Need per-repo deep dives |
| Cross-repo search | **PARTIAL** — `gh` CLI search works across repos | No indexed graph, slower |
| Dependency mapping | **PARTIAL** — documented at high level | Need code-level deps (imports, packages) |
| Code exploration | **PARTIAL** — can read any file via `gh api` | No pre-indexed knowledge |
| Feature planning | **NOT BUILT** — could do ad-hoc | Need skill/workflow |
| TRD generation | **NOT BUILT** | Need skill/workflow |
| Production triage | **NOT BUILT** | Need skill/workflow |
| Code review | **EXISTS** — Supersetter board has review zones | Not architecture-aware |
| Knowledge persistence | **PARTIAL** — file-based memory | No structured graph DB |

## Recreation Strategy: What's Needed

### Tier 1: Already Working (Free)

We already do what Bito's codebase explorer does, just differently:
- **`gh search code`** — search across all preset-io repos
- **`gh api repos/preset-io/<repo>/contents/<path>`** — read any file
- **File-based memory** — CATALOG.md, ARCHITECTURE.md, INFRA.md, per-repo docs

The difference: Bito pre-indexes; we search on-demand. For an org with ~30 active repos, on-demand via `gh` is fast enough.

### Tier 2: Build Per-Repo Context Files (Medium Effort)

For each key repo, create `repos/preset-io-<repo>.md` with:
- README/CLAUDE.md summaries (already doing this for infra)
- Key file paths and what they do
- Dependencies (from requirements.txt, package.json, go.mod)
- API endpoints exposed
- How it connects to other repos

**This is the highest-value next step.** It gives future sessions instant context without re-reading READMEs every time.

### Tier 3: Build Skills (Medium Effort)

Create skill files in `skills/` that replicate Bito's workflows:

#### `skills/feature-plan/SKILL.md`
- Input: feature description + target repo(s)
- Steps: search relevant code, identify impacted files, propose implementation plan
- Output: structured implementation plan with file paths and changes

#### `skills/trd/SKILL.md`
- Input: product requirement
- Steps: analyze existing patterns, identify relevant services/APIs, generate technical design
- Output: TRD with architecture diagrams, API contracts, data models

#### `skills/production-triage/SKILL.md`
- Input: error/incident description
- Steps: search for related code, trace call paths, identify blast radius
- Output: diagnosis with root cause hypothesis and affected services

#### `skills/code-review/SKILL.md`
- Input: PR URL
- Steps: read changes, check against architecture patterns, assess cross-repo impact
- Output: architecture-aware review comments

### Tier 4: Structured Knowledge Graph (High Effort, Questionable Value)

This is what Bito's core IP is — a MySQL-backed graph of code entities. We could:
- Build a JSON/SQLite graph of services → endpoints → dependencies
- Auto-generate from parsing actual code
- Keep it in `memory/knowledge-graph/`

**My take:** For Preset's scale (~30 active repos), this is overkill. The file-based approach in Tier 2 + `gh` search gives 90% of the value at 10% of the complexity. A knowledge graph makes sense at 500+ repos.

## Recommended Path

1. **Now:** Finish per-repo context files for the ~15 most important repos (superset-shell, manager, api-gateway, argocd, helm, terraform-live-envs, etc.)
2. **Next:** Build the feature-plan and trd skills
3. **Later:** Add production-triage skill (needs more operational context)
4. **Maybe never:** Build a structured graph DB (files + search is sufficient)

The key insight: **Bito sells infrastructure for a problem we can solve with files + `gh` + Agor sessions.** Their knowledge graph is needed because generic tools (Cursor, Claude Code) don't have persistent memory. We do — that's what this repo is.
