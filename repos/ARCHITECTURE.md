# Preset Architecture Overview

## The Big Picture

Preset is a **managed Apache Superset platform** offering both SaaS (multi-tenant) and PCS (private cloud) deployments. The architecture spans ~30 actively maintained repositories across several domains.

---

## System Architecture

```
                                    +-----------------------+
                                    |   preset-marketing-   |
                                    |      website          |
                                    |   (Marketing/Sales)   |
                                    +-----------+-----------+
                                                |
                                                v
+------------------+    +-------------------+  +-----------------------+
|  superset-sup    |    |   api-clients     |  |      manager          |
|  (CLI tool)      |--->|   (Python SDK)    |->|  (Account mgmt,      |
+------------------+    +-------------------+  |   workspace CRUD,     |
                                               |   billing, auth)      |
                                               +-----------+-----------+
                                                           |
                                                           v
                                               +-----------+-----------+
                                               |    api-gateway        |
                                               |  (Multi-tenant        |
                                               |   routing, auth)      |
                                               +-----------+-----------+
                                                           |
                                                           v
+------------------+    +-----------+-----------+-----------+-----------+
| apache/superset  |    |                                               |
| (upstream OSS)   |--->|              superset-private                 |
+------------------+    |          (Preset's private fork:              |
                        |    SSO, embedding, enterprise features)       |
                        +---------------------+-------------------------+
                                              |
                                              v
                        +---------------------+-------------------------+
                        |              superset-shell                    |
                        |    (Wraps Superset with Preset config:        |
                        |     auth, feature flags, integrations,        |
                        |     analytics events, custom behavior)        |
                        +---------------------+-------------------------+
                                              |
                    +------------+------------+------------+
                    |            |            |            |
                    v            v            v            v
              +---------+  +---------+  +---------+  +---------+
              |backend- |  |frontend-|  |ai-assist|  |birdsai  |
              |sdk      |  |sdk      |  |-lib     |  |         |
              +---------+  +---------+  +---------+  +---------+
```

---

## Deployment Pipeline

```
Code Change
    |
    v
[superset-and-shell-combo-tester] --- Validates superset + shell compatibility
    |
    v
[release-maker] --- Builds release SHA
    |
    v
[docker-images] --- Builds container images
    |
    v
[helm] --- Packages Helm charts
    |
    v
[argocd] --- GitOps delivery to clusters
    |
    v
[terraform-live-envs] --- Environment-specific config
    |
    +--> SaaS (multi-tenant K8s clusters)
    |
    +--> PCS (customer-managed via preset-pcs + mpc-init)
```

---

## Key Architectural Patterns

### 1. Shell Pattern (Wrapping)
Preset uses a "shell" pattern where core OSS projects are wrapped:
- **superset-shell** wraps **apache/superset** (via superset-private)
- **agor-shell** wraps **agor**

The shell adds: auth, feature flags, analytics, customer-specific config, and integrations. This keeps the core clean and the private stuff separate.

### 2. Terraform Module Hierarchy
```
terraform-modules-resources  (atomic: VPC, subnet, S3 bucket)
         |
         v
terraform-modules-services   (composed: "a Superset cluster needs X, Y, Z")
         |
         v
terraform-live-envs          (instantiated: "prod-us-east-1 uses service X with these params")
```

### 3. SDK Layers
```
backend-sdk   --- Python utilities for Preset backend services
frontend-sdk  --- TypeScript utilities for Preset frontend
api-clients   --- Public-facing Python SDK for Preset API
superset-sup  --- CLI built on api-clients
```

### 4. PCS vs SaaS
- **SaaS:** Multi-tenant, Preset-managed K8s clusters, deployed via ArgoCD
- **PCS:** Customer-managed infra, initialized via `mpc-init`, releases via `preset-pcs`, optional FIPS (`pcs-superset-fips`)

---

## Data Flow

```
[Superset instances] --analytics events--> [superset-shell]
         |
         v
[dataeng] (dbt + Airflow + BigQuery)
         |
         v
[Superset dashboards] (eating our own cooking)
```

See the DatAgor board for the full data pipeline diagram (Segment, Fivetran, BigQuery, dbt, Hightouch).

---

## AI/Agent Layer (Emerging)

```
[agor] --- Core orchestration platform
   |
   +-- [agor-shell] --- Preset-specific config
   |
   +-- [agor-assistant] --- Agent framework (OpenClaw-inspired)
   |
   +-- [slack-mcp] --- Slack integration via MCP
   |
   +-- [testmcpy] --- MCP testing framework
   |
   +-- [ai-assist-lib] --- AI features in Superset
   |
   +-- [birdsai] --- BirdsAI (AI for data)
   |
   +-- [promptimize] --- Prompt eval toolkit
   |
   +-- [ai18n] --- AI translation
```

---

## Inter-Repo Dependencies (Key Relationships)

| From | To | Relationship |
|------|----|-------------|
| `superset-shell` | `superset-private` | Wraps (Python dependency) |
| `superset-private` | `apache/superset` | Fork of (tracks upstream) |
| `manager` | `superset-shell` | Provisions and manages instances |
| `api-gateway` | `manager` | Routes requests, verifies auth |
| `api-clients` | `manager` | SDK for manager API |
| `superset-sup` | `api-clients` | CLI built on SDK |
| `agor-shell` | `agor` | Wraps (same shell pattern) |
| `helm` | `docker-images` | References container images |
| `argocd` | `helm` | Deploys Helm charts |
| `terraform-live-envs` | `terraform-modules-services` | Uses modules |
| `terraform-modules-services` | `terraform-modules-resources` | Uses modules |
| `release-maker` | `superset-private` + `superset-shell` | Builds release SHAs |
| `e2e-automation` | entire platform | Tests against deployed instances |
| `dataeng` | BigQuery + Superset | Data pipeline |

---

## Teams (Inferred from repo patterns)

- **Platform/Core:** superset-shell, superset-private, manager, api-gateway
- **Infrastructure/DevOps:** terraform-*, argocd, helm, docker-images, devops-tools
- **PCS:** preset-pcs, pcs-*, mpc-init
- **Data:** dataeng, allstars
- **AI/Agents:** agor, agor-shell, birdsai, ai-assist-lib, testmcpy
- **Marketing:** preset-marketing-website
- **Developer Experience:** superset-sup, api-clients, backend-sdk, frontend-sdk
- **QA:** e2e-automation
