# 2026-09-03 — Birds/Datadog `get_logs` query traps (cost real wrong answers today)

Three independent traps, all of which silently produce **confidently wrong numbers**. Hit during the
v6.0.0.33 blank-PDF investigation for Amin. Check this file before any Datadog-driven triage.

## 1. `total_count` is capped by `limit` — it is NOT a true match count

`get_logs(..., limit=5)` returns `total_count: 5` even when 85 logs match. I nearly reported a
10x "post-release ramp" off a `limit=5` baseline vs a `limit=200` post-release query.

**Rule:** always `limit=1000` when counting. If it comes back **exactly** 1000, you are capped —
narrow the window and re-query. Never quote a count taken at a low limit.

## 2. Unparenthesized `OR` in `query=` silently destroys cluster/namespace/service scoping

The `query` string is **appended** to the auto-built filters with no grouping. So:

```
query='A OR B'  +  cluster=us1a, service=superset
  ->  kube_cluster_name:us1a service:superset A OR B
  ->  parsed as (us1a AND superset AND A) OR (B)
```

`B` matches **every cluster and every service**. Proof it bites: a namespace-scoped query returned
logs from other namespaces *and* from the unrelated `birdsai` service (my own subagent's tool calls).
A subagent independently got *identical* SIGKILL counts (267) for us1a and us2a on 09-02 where the
true scoped values are 102 and 23.

**Rule:** always wrap multi-term queries yourself: `query='(A OR B)'`.

## 3. The signal that matters is `status:info`, not `status:error`

`report_execution_terminal` — the structured, one-line-per-execution report telemetry
(`capture_kind / state / terminal_reason / elapsed_seconds / attempt / report_schedule_id /
dashboard_id / expected_holders`) — is logged at **info**. Filtering `status=error` loses it entirely.

This is the only trustworthy customer-facing report outcome signal. See
[[report-telemetry-vs-targetclosederror]].

## Bonus: workspace attribution IS possible (a subagent wrongly concluded it wasn't)

`get_logs` returns no namespace field, and filtering by the *workspace* slug returns 0 — because the
namespace is keyed on the **deployment** slug, not the workspace slug. The chain is:

```
search_teams(name) -> get_team_workspaces(team) -> get_workspace_by_name(ws)
  -> .deployment.k8s_namespace   # ws--<DEPLOYMENT slug>--main
  -> get_logs(namespace=that)
```

Also: `list_preset_deployments()` returns `app_versions: null` and `workspace_count: 0` for every
row — both fields are only populated by `get_deployment(deployment_id)`. Do not conclude "no data".
