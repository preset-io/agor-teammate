# Preset Expertise Map

**Source:** GitHub contributor data (`gh api repos/preset-io/REPO/contributors`) + CODEOWNERS files
**Last updated:** 2026-03-16
**Note:** Contribution counts are all-time. Some people may have left Preset — this reflects historical + current knowledge.

---

## Key People at a Glance

| Person | Primary Domain | Signal |
|--------|---------------|--------|
| **mistercrunch** (Max) | Superset core, Agor, data | #1 in superset-private (2,385), agor (1,228), dataeng (#2) |
| **craig-rueda** | Infra/DevOps (everything) | #1 in 10+ repos: helm, manager, service-deploy-pipeline, api-gateway, docker-images, platform-broker, devops-tools, mpc-init, ephemeral-env-pipeline |
| **dpgaspar** | Platform/Infra | #1 in argocd, superset-shell, birdsai, cronjobs; #2 in helm, manager, docker-images |
| **betodealmeida** | Python SDK/API layer | #1 in backend-sdk, superset-sup; #5 superset-private |
| **sadpandajoe** | QA/Testing/Releases | #1 in e2e-automation (412), release-maker (49) |
| **stevepisani** | Data engineering | #1 in dataeng (288) — owns the data pipeline |
| **thiagorossener** | Marketing website | #1 in preset-marketing-website (599) |
| **geido** | AI/Copilot + Frontend | #1 in ai-assist-lib; CODEOWNERS for frontend components |

---

## By Area of Expertise

### Founder / Cross-Cutting

| Person | Key Repos |
|--------|-----------|
| **mistercrunch** | superset-private (#1, 2385), agor/agor-shell (#1, 1228), dataeng (#2, 225), superset-sup (#3). CODEOWNERS: migrations, Helm, GH actions, E2E |

---

### Infrastructure / DevOps

| Person | Key Repos | Notes |
|--------|-----------|-------|
| **craig-rueda** | helm (#1, 1061), manager (#1, 642), service-deploy-pipeline (#1), api-gateway (#1), docker-images (#1), devops-tools (#1), platform-broker (#1), ephemeral-env-pipeline (#1), mpc-init (#1), argocd (#2) | Most critical infra engineer — touches everything |
| **dpgaspar** | argocd (#1, 183), superset-shell (#1, 298), helm (#2, 650), manager (#2), api-gateway (#2), docker-images (#2), birdsai (#1), cronjobs (#1) | Second most prolific — ArgoCD primary owner |
| **henryyeh** | helm (#3, 354), devops-tools (#3), docker-images (#5), release-maker (#3) | Helm specialist |
| **innovia** | helm (#4, 224), argocd (#4), docker-images (#3), api-gateway (#3) | Infra generalist |
| **garciajrx** | argocd (#3, 99), api-gateway (#4), mpc-init (#2) | ArgoCD + MPC |
| **stevenuray** | helm (#6), docker-images (#4), devops-tools (#4) | Infra/Docker |
| **mgorak** | argocd (#5), helm (#7) | ArgoCD/Helm |
| **binbashing** | helm (#8), api-gateway (#7) | Helm/Gateway |
| **maxim-preset** | helm (#5), devops-tools (#6) | Helm contributor |

---

### Core Platform — Superset Backend

| Person | Key Repos | Notes |
|--------|-----------|-------|
| **betodealmeida** | backend-sdk (#1, 398), superset-sup (#1, 397), superset-private (#5), superset-shell (#4) | Python/API expert, SDK owner |
| **villebro** | superset-private (#3, 851). CODEOWNERS: Helm, geojson, extensions | Core committer, geospatial |
| **kristw** | superset-private (#4, 834) | Core contributor |
| **john-bodley** | superset-private (#8, 577) | Core contributor |
| **Vitor-Avila** | backend-sdk (#2, 202), superset-sup (#2, 192), frontend-sdk (#2) | SDK layer |
| **eschutho** | CODEOWNERS: migrations, E2E, extensions | Core committer |

---

### Core Platform — Superset Frontend

| Person | Key Repos | Notes |
|--------|-----------|-------|
| **michael-s-molina** | superset-private (#6, 760). CODEOWNERS: Select, MetadataBar, DropdownContainer, extensions | Component owner |
| **kgabryje** | superset-private (#9, 547), superset-shell (#6). CODEOWNERS: same components + GH actions | Component/CI |
| **rusackas** | superset-private (#7, 582), preset-marketing-website (#3). CODEOWNERS: geojson, extensions | Design/UX bridge |
| **suddjian** | frontend-sdk (#1, 10), manager (#8), dataeng (#4) | Frontend SDK primary |

---

### Manager (Account/Workspace Management)

| Person | Key Repos | Notes |
|--------|-----------|-------|
| **craig-rueda** | manager (#1, 642) | Also infra — deep across the stack |
| **dpgaspar** | manager (#2, 305) | Platform/infra overlap |
| **jfrag1** | manager (#3, 268), frontend-sdk (#2) | Manager specialist |
| **nytai** | manager (#4, 145), ephemeral-env-pipeline (#2) | Manager + deployments |
| **samtfm** | manager (#5, 115) | Manager contributor |
| **riahk** | manager (#7, 93) | Manager contributor |

---

### QA / Testing / Releases

| Person | Key Repos | Notes |
|--------|-----------|-------|
| **sadpandajoe** | e2e-automation (#1, 412), release-maker (#1, 49), superset-shell (#5). CODEOWNERS: migrations, E2E | QA lead |
| **Adam-stasiak** | e2e-automation (#2, 212) | E2E automation |
| **jinghua-qa** | e2e-automation (#3, 169) | QA specialist |
| **novikovmax** | e2e-automation (#4, 134) | QA specialist |

---

### AI / Copilot

| Person | Key Repos | Notes |
|--------|-----------|-------|
| **geido** | ai-assist-lib (#1, 32). CODEOWNERS: components, E2E, GH actions | AI UI primary owner |
| **Antonio-RiveroMartnez** | birdsai (#2), ai-assist-lib (#2), preset-bot (#1), argocd (#6) | AI + automation, cross-cutting |
| **dpgaspar** | birdsai (#1, 42) | AI infra |
| **betodealmeida** | ai-assist-lib (#3) | AI backend |

---

### Agor Platform

| Person | Key Repos | Notes |
|--------|-----------|-------|
| **mistercrunch** | agor (#1, 1228), agor-shell (#1, 1228) | Creator/primary |
| **aminghadersohi** | agor (#3), agor-shell (#3), testmcpy (#2) | Agor platform dev |
| **ryw** | agor (#4), agor-shell (#4) | Agor platform dev |

---

### Data Engineering

| Person | Key Repos | Notes |
|--------|-----------|-------|
| **stevepisani** | dataeng (#1, 288) | Data engineering lead (sole primary owner) |
| **todd-dawson** | dataeng (#3, 80) | Data engineer |
| **suddjian** | dataeng (#4, 14) | Cross-cutting (also frontend) |

---

### Marketing Website

| Person | Key Repos | Notes |
|--------|-----------|-------|
| **thiagorossener** | preset-marketing-website (#1, 599) | Website lead |
| **marcomiduri** | preset-marketing-website (#2, 397) | Website developer |
| **rusackas** | preset-marketing-website (#3, 141) | Design/UX crossover |

---

## Risk Observations

1. **craig-rueda is a single point of failure for infra** — #1 contributor in 10+ repos. If he's unavailable, Helm, service-deploy-pipeline, docker-images, devops-tools, ephemeral-env-pipeline, and mpc-init have no close second.

2. **stevepisani owns dataeng solo** — 288 commits vs 80 for #2. The data pipeline depends heavily on one person.

3. **betodealmeida owns the SDK layer** — backend-sdk and superset-sup are almost entirely his work.

4. **dpgaspar is the second most critical person** — touches ArgoCD, Helm, superset-shell, manager, Docker. Strong complement to craig-rueda.

5. **Marketing website is siloed** — thiagorossener + marcomiduri have zero overlap with platform engineering.

---

## CODEOWNERS Summary

**superset-private** (most detailed):
- Migrations: @mistercrunch @michael-s-molina @betodealmeida @eschutho @sadpandajoe
- Frontend components (Select, MetadataBar, DropdownContainer): @michael-s-molina @geido @kgabryje
- Helm chart: @craig-rueda @dpgaspar @villebro @nytai @michael-s-molina @mistercrunch @rusackas @Antonio-RiveroMartnez
- E2E tests: @sadpandajoe @geido @eschutho @rusackas @betodealmeida @mistercrunch
- GH Actions: large group (11 people)

**manager**: @preset-io/platform team (migrations, models, security), @preset-io/data-team (ETL)

**terraform-live-envs**: @preset-io/infra team (all environments)
