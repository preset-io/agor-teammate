# MEMORY.md - Long-Term Memory

## Identity

I'm the **Preset Architect** — systems cartographer for preset-io's 170+ repos.
Board: "Preset Architect" (ID: `8e1c3e06`). Human: Max (CEO, Superset creator).

## Architecture Docs Index

All deep knowledge lives in `repos/`:
- **CATALOG.md** — 171 repos categorized (125 active, 39 forks, 7 archived)
- **ARCHITECTURE.md** — system architecture, dependency graph, deployment models
- **INFRA.md** — all 23 infra repos, Terraform 3-tier, GitOps, PCS/MPC
- **DIAGRAMS.md** — 9 mermaid diagrams for reference
- **SEARCH-STRATEGY.md** — `gh search code` patterns, repo scoping guide
- **BITO-ANALYSIS.md** — Bito AI Architect reverse-engineering + recreation plan

## Key Patterns Discovered

1. **Shell Pattern** — THE core pattern. OSS → private fork → shell wrapper
2. **Terraform 3-tier** — modules-resources (deprecated) → modules-services → live-envs
3. **Three deployment models** — SaaS (Preset-managed), MPC (Preset manages in customer cloud), PCS (customer self-manages)
4. **SOPS + KMS everywhere** — secrets in Terraform, Helm, ArgoCD
5. **Atlantis** — TF CI/CD auto-applies on merge
6. **Jenkins (legacy) → CircleCI/GH Actions (modern)** — migration in progress
7. **K8s namespaces** — `ws--<identifier>--main` for Superset workspaces

## Search Approach

`gh search code` + architectural knowledge > vector search at this scale.
I know which repos to look in for each question type. See `repos/SEARCH-STRATEGY.md`.

## Lessons Learned

- MPC ≠ PCS: MPC = Preset manages in customer's cloud. PCS = customer self-manages.
- GitHub linguist calls Helm charts "Mustache" — it's actually Go templates
- The `infra` repo is deprecated but architecturally important (shows the original blueprint)
- Copilot system prompt lives in `superset-shell/preset/copilot/commands/generate_completion.py:1204`

## Next Steps

- Deep-dive per-repo context files for core platform (superset-shell, manager, api-gateway)
- Build skills: feature-plan, TRD, production-triage
- Map code-level dependencies (requirements.txt, package.json)
