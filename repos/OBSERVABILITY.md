# Preset Observability

**Last updated:** 2026-03-16

How Preset monitors its infrastructure and applications. This is a pointer map — dig into the referenced repos/files for details.

---

## Stack at a Glance

```
App Code (StatsD + Sentry + event_logger)
    |
    v
Datadog Agent (DaemonSet per cluster)
    |
    ├── Metrics ──> Datadog Dashboards
    ├── Logs ──> Datadog Log Pipelines ──> Monitors
    └── APM/Traces ──> Datadog APM
              |
              v
        Datadog Monitors (Terraform-managed)
              |
              ├── PagerDuty (5 escalation paths)
              └── Slack (#p0-p1, #deployments, per-team channels)

Security:  Falco (DaemonSet) ──> Datadog security monitors
Errors:    Sentry (per-service SDK init)
Queues:    celery-prometheus-exporter ──> Prometheus
```

---

## Where Things Live

### Metrics Emission (Application Layer)

| Service | File | What It Emits |
|---------|------|---------------|
| Manager | `preset/managers/app_metrics.py` | SQLAlchemy pool gauges (size, checkedin, checkedout, overflow) per DB bind |
| Superset Shell | `preset/config.py` → `STATS_LOGGER` | Query times, cache hits, dashboard loads — all via DogStatsD |
| Superset Shell | `preset/mcp/metrics.py` | MCP tool execution duration, auth events (StatsD + event_logger) |
| Superset Shell | `preset/celery.py` | Celery task metrics |
| Superset Shell | `preset/gunicorn/hooks.py` | Gunicorn worker lifecycle metrics |
| Copilot | `preset/copilot/helpers/concurrency.py` | Copilot concurrency/token metrics |
| Cronjobs | `cronjobs/` | K8s CronJob metrics via Sentry + Datadog APM |

### Monitor Definitions (IaC)

**Repo:** `terraform-modules-services/aws/datadog-monitors/`

30+ Terraform files, one per concern:

| File | Monitors |
|------|----------|
| `superset.tf` | SQLA operational errors, Celery error rates (high + flaky), websocket errors, per-release error spikes |
| `manager.tf` | Manager service health |
| `api-gateway.tf` | Gateway errors/latency |
| `postgres.tf` / `rds.tf` | DB health, connections, replication |
| `elasticache.tf` | Redis health (broker `ss` + cache `sc`) |
| `kubernetes.tf` / `nodes.tf` | Pod restarts, OOM, node health |
| `karpenter.tf` | Node provisioner |
| `security.tf` | Falco alerts |
| `pii.tf` | PII detection in logs |
| `http.tf` | HTTP error rates |
| `velero.tf` | Backup health |
| `process.tf` | Process-level monitors |

**Alert routing:** Per-environment notification channels with separate alert/warn paths. 5 PagerDuty escalation policies: `devops`, `production`, `production_staging`, `manager`, `superset`.

### Log Pipelines

**Repo:** `datadog-config`
- YAML definitions in `conf/log_pipelines/`
- Daily Jenkins backup job → pushes changes to `main` → notifies `#infra-team-automation`
- Primarily managed in Datadog UI; repo is version-controlled backup
- Apply changes: set `BACKUP_MODE=APPLY` in Jenkins job

### Agent Deployment

**Repos:** `helm` (chart), `argocd` (per-cluster values)
- Datadog Agent deployed as Helm chart to every K8s cluster (SaaS + MPC)
- Per-cluster config: `argocd/environments/<env>/<cloud>/regions/<region>/<cluster>/datadog/`
- IAM + log forwarder Lambda: `terraform-live-envs/environments/<env>/<cloud>/regions/global/datadog/`

### Error Tracking (Sentry)

| Service | Init Location |
|---------|--------------|
| Superset Shell (Python) | `preset/app.py` |
| Manager (JS frontend) | `preset/static/src/services/Sentry.ts` |
| Platform Broker (TS) | `src/sentry.ts` |
| Cronjobs | Per-job Sentry init |

### Security Monitoring

- **Falco**: DaemonSet on all clusters, deployed via `helm/charts/falco/` + ArgoCD
- **Falcon Sensor**: CrowdStrike agent, also deployed via Helm
- Falco alerts → Datadog `security.tf` monitors

### Celery Queue Monitoring

**Repo:** `celery-prometheus-exporter`
- Prometheus exporter for Celery task queues (supports Redis + RabbitMQ brokers)
- Factory pattern for extensible broker monitoring
- Covers Superset's async infrastructure: queries, reports, cache warming, thumbnails

---

## Incident Response Path

```
Datadog Monitor triggers
    → PagerDuty (on-call rotation, per-team escalation)
    → Slack #p0-p1 (P0/P1 incidents), #p0-p1comms (customer comms)
    → DR runbooks: disaster-recovery-plans repo

During deploys:
    → service-deploy-pipeline suppresses PagerDuty maintenance windows
    → Posts to Slack #deployments
```

**RTO targets** (from `disaster-recovery-plans`):
- Single workspace: 1h
- All workspaces / metadata DB: 2h
- Complete AWS region failure: 2h
- Single AZ failure: 30min

---

## What's NOT Here (Gaps / Future Research)

- Datadog dashboard inventory (managed in UI, no IaC)
- SLO/SLI definitions (if any exist)
- OpenTelemetry adoption status — appears in deps for newer services (agor, cronjobs, manager) but unclear how widely instrumented
- Kubecost (in Helm charts) — cost observability, not yet documented
- Uptime/synthetic monitoring (Datadog Synthetics? External?)
