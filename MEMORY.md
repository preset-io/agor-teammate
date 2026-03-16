# MEMORY.md - Long-Term Memory

---

## Key Architecture Facts

### The Shell Pattern
Preset wraps OSS projects with "shell" repos that add auth, feature flags, analytics, and config:
- `superset-shell` wraps `superset-private` (which forks `apache/superset`)
- `agor-shell` wraps `agor`
- This is THE core architectural pattern at Preset

### Core Request Path
`User -> api-gateway -> manager -> superset-shell -> superset-private`

### Infrastructure Stack
Terraform modules (resources -> services -> live-envs) + ArgoCD + Helm + Docker

### Repo Scale
171 total repos, ~30 actively maintained, ~95 dormant/legacy

---

## Important Context

- Max is CEO of Preset and creator of Apache Superset
- Wants BITO.ai-like capability: an agent that deeply understands repo interconnections
- Board: "Preset Architect" (ID: 8e1c3e06)
- I have `gh` CLI access to the full preset-io org

## Repos Not Yet in Agor (Key Ones)
superset-private, manager, api-gateway, agor-shell, terraform-live-envs,
argocd, helm, backend-sdk, frontend-sdk, birdsai, ai-assist-lib, testmcpy

---

## Ongoing Projects

### Architecture Mapping (Active)
- Created CATALOG.md and ARCHITECTURE.md
- Next: deep-dive into key repos (superset-shell, manager, api-gateway)
- Next: map actual code-level dependencies (requirements.txt, package.json)
