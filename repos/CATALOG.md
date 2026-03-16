# Preset Repository Catalog

**Organization:** preset-io (GitHub)
**Total repos:** 171 (125 active, 39 forks, 7 archived)
**Last synced:** 2026-03-16

---

## Core Platform

These repos form the heart of Preset's managed Superset offering.

### Superset Core
| Repo | Language | Description | Activity |
|------|----------|-------------|----------|
| `superset-private` | TypeScript | Preset's private fork of Superset | Very Active |
| `superset-shell` | Python | Superset wrapper for config/extensibility | Very Active |
| `manager` | Python | Account and workspace management for Superset instances | Very Active |
| `api-gateway` | HTML | Gateway/router for multi-tenant Superset workspaces | Active |
| `backend-sdk` | Python | Backend SDK | Active |
| `frontend-sdk` | TypeScript | Frontend SDK | Moderate |
| `api-clients` | Python | API clients SDK | Moderate |
| `platform-broker` | TypeScript | "One broker to rule them all" | Low |

### How They Connect
```
[apache/superset] (upstream OSS)
       |
       v (private fork)
[superset-private] --- Preset's fork with private features
       |
       v (wraps)
[superset-shell] --- Configuration, auth, feature flags, Preset-specific behavior
       |
       v (deployed via)
[manager] --- Workspace provisioning, account management, billing
       |
       v (routed through)
[api-gateway] --- Multi-tenant routing, auth verification
       |
       v (orchestrated by)
[platform-broker] --- Service orchestration
```

---

## PCS (Private Cloud Service)

For customers running Superset in their own cloud.

| Repo | Language | Description | Activity |
|------|----------|-------------|----------|
| `preset-pcs` | Go Template | PCS release tags hub | Active |
| `pcs-superset-fips` | Shell | FIPS-compliant Superset | Low |
| `pcs-superset-shell` | N/A | PCS shell wrapper | Low |
| `pcs-ivanti` | Shell | PCS Ivanti integration | Low |
| `mpc-init` | Shell | Terraform/CloudFormation for MPC init | Active |

---

## Infrastructure & DevOps

| Repo | Language | Description | Activity |
|------|----------|-------------|----------|
| `terraform-live-envs` | HCL | Live Terraform environments | Very Active |
| `terraform-modules-services` | HCL | Service-level Terraform modules | Very Active |
| `terraform-modules-resources` | HCL | Resource-level Terraform modules | Moderate |
| `argocd` | Python | ArgoCD configuration | Very Active |
| `helm` | Mustache | Helm charts for Preset | Active |
| `docker-images` | Dockerfile | Docker images | Active |
| `infra` | HCL | Legacy infrastructure | Low |
| `service-deploy-pipeline` | Python | Deploy pipeline ("a pile of potatoes") | Low |
| `ephemeral-env-pipeline` | Groovy | Ephemeral environment lifecycle | Moderate |
| `devops-tools` | Python | Various DevOps utilities | Active |
| `cronjobs` | Python | K8s generic cronjobs | Moderate |
| `release-maker` | Python | Automates building release SHAs | Active |

### Infrastructure Flow
```
[terraform-modules-resources] --- Low-level AWS/GCP resources
       |
       v (composed into)
[terraform-modules-services] --- Service definitions (RDS, EKS, etc.)
       |
       v (instantiated by)
[terraform-live-envs] --- Per-environment configurations
       |
       v (deployed via)
[argocd] --- GitOps delivery
       |
       v (packages)
[helm] --- Helm charts
       |
       v (images from)
[docker-images] --- Container images
```

---

## Agor (AI Orchestration Platform)

| Repo | Language | Description | Activity |
|------|----------|-------------|----------|
| `agor` | TypeScript | Main Agor platform | Very Active |
| `agor-shell` | TypeScript | Agor wrapper for config/extensibility | Very Active |
| `agor-assistant` | N/A | Agent operating framework (OpenClaw-inspired) | Active |
| `slack-mcp` | TypeScript | Slack MCP integration | Moderate |

---

## AI & ML

| Repo | Language | Description | Activity |
|------|----------|-------------|----------|
| `birdsai` | Python | BirdsAI | Active |
| `ai-assist-lib` | Python | AI assist library | Moderate |
| `testmcpy` | Python | MCP testing framework for Superset | Very Active |
| `promptimize` | Python | Prompt engineering eval toolkit | Active |
| `ai18n` | Python | AI-powered .po translation | Active |
| `ai-coding-instructions` | N/A | Global AI coding instructions for repos | Low |
| `claude-commands` | Shell | Custom slash commands for Claude | Low |
| `awesome-data-mcp` | N/A | Curated list of data MCP services | Low |

---

## Data Engineering

| Repo | Language | Description | Activity |
|------|----------|-------------|----------|
| `dataeng` | Jupyter Notebook | Everything data engineering | Active |
| `allstars` | Python | Smart semantic layer | Low |
| `elasticsearch-dbapi` | Python | ES DBAPI + SQLAlchemy dialect | Moderate |
| `preset-pinot-db-engine-spec` | Python | Enriched Pinot DB engine spec | Low |

---

## Marketing & Content

| Repo | Language | Description | Activity |
|------|----------|-------------|----------|
| `preset-marketing-website` | JavaScript | Marketing website | Very Active |
| `superset-showtime` | Python | Demo/showcase | Moderate |
| `dashboard-optimization` | Python | Blog post: dashboard optimization | Active |
| `embedded-example` | Python | Sample Flask embedding app | Moderate |
| `public-examples` | N/A | Superset public examples | Low |
| `dashboard-templates` | N/A | Dashboard templates | Low |

---

## Testing & QA

| Repo | Language | Description | Activity |
|------|----------|-------------|----------|
| `e2e-automation` | TypeScript | End-to-end automation tests | Active |
| `superset-and-shell-combo-tester` | Groovy | Tests incoming Superset changes with shell | Low |

---

## Internal Tools

| Repo | Language | Description | Activity |
|------|----------|-------------|----------|
| `superset-sup` | Python | Modern CLI for Superset/Preset | Very Active |
| `preset-bot` | Python | Slack bot for Preset | Moderate |
| `preset-operations` | Python | Operations tooling | Low |
| `customer-engagement-userscripts` | JavaScript | CE team userscripts | Moderate |
| `celery-prometheus-exporter` | Python | Celery metrics exporter | Low |

---

## Database Connectors (Forks)

Preset maintains forks of several database connectors:
- `PyHive` - Hive/Presto connector
- `snowflake-connector-python` - Snowflake connector
- `snowflake-sqlalchemy` - Snowflake SQLAlchemy dialect
- `preset-sqlalchemy-redshift` / `sqlalchemy-redshift-no-spectrum` - Redshift dialects
- `gsheets-db-api` - Google Sheets connector
- `sqlalchemy-utils` - SQLAlchemy utilities

---

## Legacy / Low Activity (pre-2023)

These repos haven't seen significant updates recently:
`fab_multitenant`, `fab_addon_multitenancy`, `cli-tools`, `cron-tasks`, `preset-static`,
`website-assets`, `website-widgets`, `semantic-ui-theming`, `jwt-validator`, `pyhive-http`,
`shoutoutbot`, `community-tracker`, `dev-laptop-automation`, `chart-hello-world`,
`auth0`, `rate-limit-alerter`, `examples`, `release-validator`, `pysuperset`,
`jenkins-deploy`, `egaf`, `superset-community-content`, `superset-community-stats-action`,
`dbt_github_archive_bigquery`, `jenkins-lib`, `superset-jenkins`, `db-driver-monitor`,
`shell-apache-master-sync`, `db-backups`, `jira-webhooks`, `embedded-poc`, `slackbot`,
`embedded-demo`, `embedded-beta-docs`, `ci-test`, `jenkins-test`, `k8s-training`,
`eks-image-builder`, `terratest`, `terraform-provider-preset-manager`, `qa-infra`,
`vpc-peering`, `datadog-config`, `jenkins-rds-snapshot-manager`, `jenkins-repo-test`,
`burrito-bot`, `dependabot-shortcut-automation`, `interview-questions`, `pr-puller`,
`prompt_eng`, `ai-assist-datasets`, `white-label-blog-post-examples`,
`headless-bi-blog-post-examples`, `dbt-integration-blog-post`, `partner-connect`,
`pingpong-patrol`, `ce_test_db`, `repo-drift-alerts`, `aws-hybrid`, `testrail-data`,
`dbt-coalesce-2022`, `community-data`, `disaster-recovery-plans`, `preset-codespaces`,
`cord-shell`, `cord-preview`, `superset-plugin-chart-liquid`, `superset-viz-plugin-template`,
`github-actions`
