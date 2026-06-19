# Superset Stale Issues Triage — 2026-04-05

Board: a97875fe-34de-4f37-9e43-85c03de86d20
NOTE: Agor MCP not available this run. Cards are staged here for manual creation or next run.

Issues batch: 10 oldest open by updated_at (excluding validation:required, PRs)
Fetched from: https://api.github.com/repos/apache/superset/issues?state=open&sort=updated&direction=asc&per_page=20

---

## Card 1 — #33756

**Title:** `#33756: Row limit shouldn't carry over when chart type is switched`
**Zone:** Propose: Comment (nudge)

```
## Issue
#33756: Row limit shouldn't carry over when chart type is switched
https://github.com/apache/superset/issues/33756
Created: 2025-06-12 | Last updated: 2025-06-12
Labels: viz:charts:line, viz:charts:pie

## Assessment
When switching chart types (e.g., line → pie), the row limit from the previous chart type persists rather than resetting to the new chart type's default. This is a UX issue that could lead to misleading visualizations. The issue was filed in June 2025 but has had no comments or activity — unclear if anyone has confirmed or triaged it. No linked PR found.

## Proposed action
Propose: Comment (nudge) — "Hi! Just checking in — is this still reproducible on the latest version of Superset? If so, any additional context about the charts involved would help move this forward."

## Links
- Related issues: None found
- Linked PRs: None found
```

---

## Card 2 — #28248

**Title:** `#28248: Add Missing Stacktrace information on errors, SQL lab query execution`
**Zone:** Propose: Comment (nudge)

```
## Issue
#28248: Add Missing Stacktrace information on errors, SQL lab query execution
https://github.com/apache/superset/issues/28248
Created: 2024-04-28 | Last updated: 2025-06-13
Labels: (none)

## Assessment
Enhancement request to surface stacktrace/debug information for SQL Lab query execution errors. This is still a valid developer experience improvement. Notably, @rusackas has been actively working on a linked PR since April 2024, most recently commenting in June 2025 that they were "fiddling with the PR again to try to get it to pass." However, there has been no update since June 2025 — 10 months of silence. The PR may be stalled on CI failures.

## Proposed action
Propose: Comment (nudge) — "@rusackas — any update on the linked PR? Would love to see this land. If CI is the blocker, happy to help get it across the finish line."

## Links
- Related issues: None found
- Linked PRs: Open PR in progress (worked on by @rusackas, stalled since ~June 2025)
```

---

## Card 3 — #32771

**Title:** `#32771: No saved queries shown if dataset used in Jinja {{ dataset(id) }} is deleted`
**Zone:** Propose: PR

```
## Issue
#32771: No saved queries shown if dataset used in Jinja {{ dataset(id) }} is deleted
https://github.com/apache/superset/issues/32771
Created: 2025-03-20 | Last updated: 2025-06-13
Labels: sqllab:saved_queries, global:jinja, cares:preset

## Assessment
⚠️ **cares:preset** — This issue is flagged as relevant to Preset customers.
When a saved query contains Jinja `{{ dataset(id) }}` and the referenced dataset is deleted, ALL saved queries become inaccessible with a "Dataset ID not found" error — not just the affected query. This is a data integrity / graceful degradation bug: one broken saved query blocks the entire saved queries view. The fix should be to catch and skip (or flag) queries with invalid dataset references rather than failing the entire list fetch. No linked PR found after 13 months.

## Proposed action
Propose: PR — Fix the saved queries list endpoint to handle `DatasetNotFoundError` gracefully: catch the error per-query, skip/flag the problematic query, and return the rest. This is isolated to the saved queries list view logic.

## Links
- Related issues: None found
- Linked PRs: None found
```

---

## Card 4 — #29485

**Title:** `#29485: Incorrect Michigan State in Country Map`
**Zone:** Propose: PR

```
## Issue
#29485: Incorrect Michigan State in Country Map
https://github.com/apache/superset/issues/29485
Created: 2024-07-04 | Last updated: 2025-06-16
Labels: viz:charts:map

## Assessment
The Country Map plugin's GeoJSON data for the United States includes the Great Lakes as part of Michigan's state boundary, visually misrepresenting the state. This is a data quality bug in the bundled geographic assets, not application logic. With 6 comments over 21 months it has attracted community interest but no PR. The fix is a one-time update to the Michigan polygon in the US states GeoJSON file to use the correct land-only boundaries (e.g., from Natural Earth or Census Bureau data).

## Proposed action
Propose: PR — Update the Michigan state geometry in the bundled US Country Map GeoJSON to exclude the Great Lakes. Source correct boundary data from US Census Bureau TIGER or Natural Earth datasets.

## Links
- Related issues: None found
- Linked PRs: None found
```

---

## Card 5 — #33788

**Title:** `#33788: Generated Visualization plugin build does not work out of the box`
**Zone:** Propose: Comment (nudge)

```
## Issue
#33788: Generated Visualization plugin build does not work out of the box
https://github.com/apache/superset/issues/33788
Created: 2025-06-17 | Last updated: 2025-06-17
Labels: (none)

## Assessment
The visualization plugin generator (used to scaffold new custom chart plugins) produces code that fails to build due to unused imports, missing test dependencies, and misconfigured build settings. Filed June 2025 with no comments or follow-up activity since. This affects the custom plugin developer experience. No linked PR found.

## Proposed action
Propose: Comment (nudge) — "Is this still reproducible with the current version of the plugin generator? If so, a PR to fix the generated template would be very welcome — could you provide the specific errors you encountered?"

## Links
- Related issues: None found
- Linked PRs: None found
```

---

## Card 6 — #33757

**Title:** `#33757: Tooltip ignores metric format in line charts (Regression in 4.X)`
**Zone:** Propose: Comment (nudge)

```
## Issue
#33757: Tooltip ignores metric format in line charts (Regression in 4.X)
https://github.com/apache/superset/issues/33757
Created: 2025-06-12 | Last updated: 2025-06-19
Labels: #bug:regression, viz:charts:line

## Assessment
Line chart tooltips always display values in dollar format ($,.2f) regardless of the metric's configured format (e.g., percentage .2%). The "Show Values" on-chart labels correctly respect the configured format, so this is isolated to the tooltip rendering path. Labeled as a regression from ~4.0. Had 7 comments through June 2025 suggesting active community interest, but no update in ~10 months. No linked PR found.

## Proposed action
Propose: Comment (nudge) — "Is this still reproducible in the latest Superset? If confirmed, this regression has a narrow scope (tooltip format lookup in line chart) and would make a good PR candidate. Can anyone share the last version where it worked correctly?"

## Links
- Related issues: None found
- Linked PRs: None found
```

---

## Card 7 — #33609

**Title:** `#33609: After user logged out, getting Internal Server Error in browser`
**Zone:** Propose: Comment (needs-info)

```
## Issue
#33609: After user logged out, getting Internal Server Error in browser
https://github.com/apache/superset/issues/33609
Created: 2025-05-28 | Last updated: 2025-06-24
Labels: global:error, authentication:sso

## Assessment
After logout on Superset 4.1.1 with Azure AD SSO and AUTH_ROLE_PUBLIC='NoAccess', users see an Internal Server Error page in the browser. The issue also occurs after long inactivity. No server-side errors appear in logs, suggesting this may be a client-side redirect/cookie issue rather than a backend crash. 4 comments in June 2025, then silence for ~10 months. The current Superset version is well past 4.1.1.

## Proposed action
Propose: Comment (needs-info) — "Is this still reproducible on the latest Superset version? Also helpful: server logs (even if empty), browser console errors, and the exact AUTH configuration (AUTH_TYPE, AUTH_ROLE_PUBLIC value). If the server logs show nothing, this may be a browser-side session/cookie redirect issue."

## Links
- Related issues: None found
- Linked PRs: None found
```

---

## Card 8 — #33855

**Title:** `#33855: Error in applying db migration to azure mysql instance`
**Zone:** Propose: PR

```
## Issue
#33855: Error in applying db migration to azure mysql instance
https://github.com/apache/superset/issues/33855
Created: 2025-06-22 | Last updated: 2025-06-24
Labels: install:docker, data:connect:mysql

## Assessment
The migration `cbe71abde154_fix_report_schedule_and_log` fails on Azure MySQL when using the `mysql-connector-python` driver. The error is: "Python 'reportstate' cannot be converted to a MySQL type" — the migration is passing a `ReportState.WORKING` Python enum object directly instead of its string value. This is a clear, narrow bug in the migration script: it should use `ReportState.WORKING.value` (the string) rather than the enum instance when building the SQL query. 4 comments in June 2025, no PR opened.

## Proposed action
Propose: PR — In migration `cbe71abde154_fix_report_schedule_and_log`, replace `ReportState.WORKING` with `ReportState.WORKING.value` (or equivalent string `"working"`) in any raw SQL / SQLAlchemy column expressions. The fix is a one-line change in the migration file.

## Links
- Related issues: None found
- Linked PRs: None found
```

---

## Card 9 — #33861

**Title:** `#33861: HostAliases not added to init job on Helm chart`
**Zone:** Propose: PR

```
## Issue
#33861: HostAliases not added to init job on Helm chart
https://github.com/apache/superset/issues/33861
Created: 2025-06-23 | Last updated: 2025-06-24
Labels: deploy:helm

## Assessment
The Superset Helm chart supports `hostAliases` in the main deployment but does not propagate them to the init job (database migration / init container). This means environments using custom DNS overrides via hostAliases (common in air-gapped or private-network setups) cannot complete the init phase. This is a small gap in the Helm template — the fix is to add the `hostAliases` block to the init job pod spec template, mirroring how it's done elsewhere in the chart.

## Proposed action
Propose: PR — Add `{{- with .Values.hostAliases }}hostAliases: {{ toYaml . | nindent 8 }}{{- end }}` to the init job pod spec in the Helm chart, matching the pattern used in the main deployment template.

## Links
- Related issues: None found
- Linked PRs: None found
```

---

## Card 10 — #33884

**Title:** `#33884: "/api/v1/dashboard" endpoint returns different response than OpenAPI spec`
**Zone:** Propose: Comment (nudge)

```
## Issue
#33884: "/api/v1/dashboard" endpoint returns different response than OpenAPI spec
https://github.com/apache/superset/issues/33884
Created: 2025-06-24 | Last updated: 2025-06-26
Labels: api

## Assessment
The `/api/v1/dashboard` endpoint returns an array for the `owners` field, while the OpenAPI specification describes it as an object. This mismatch breaks generated API clients. 3 comments in late June 2025, then no activity for ~10 months. The root cause could be either an incorrect spec definition or an incorrect API response — needs a committer to clarify intent. No linked PR found.

## Proposed action
Propose: Comment (nudge) — "Is this still present in the latest version? Also: should the spec be updated to match the implementation (array of user objects) or should the implementation be changed to match the spec? Knowing the intent would unblock a PR."

## Links
- Related issues: None found
- Linked PRs: None found
```

---

## Zone Summary

| # | Issue | Proposed Zone |
|---|-------|--------------|
| 1 | #33756 Row limit carries over | Propose: Comment (nudge) |
| 2 | #28248 SQL Lab stacktrace | Propose: Comment (nudge) — PR stalled |
| 3 | #32771 Saved queries broken (cares:preset) | Propose: PR |
| 4 | #29485 Michigan map incorrect | Propose: PR |
| 5 | #33788 Plugin build broken | Propose: Comment (nudge) |
| 6 | #33757 Tooltip format regression | Propose: Comment (nudge) |
| 7 | #33609 Internal error after logout | Propose: Comment (needs-info) |
| 8 | #33855 MySQL migration enum error | Propose: PR |
| 9 | #33861 Helm hostAliases in init job | Propose: PR |
| 10 | #33884 Dashboard API spec mismatch | Propose: Comment (nudge) |
