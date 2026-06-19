# Stale Issues Triage — apache/superset — 2026-04-07

**Board:** RepoBot3000(`a97875fe-34de-4f37-9e43-85c03de86d20`)
**Note:** Agor MCP was not available in this session. Cards are staged here for manual creation or next session.
**Skipped:** #33810 (`validation:required` label — out of scope per triage rules)

---

## Card 1 — #33756

**Title:** `#33756: Row limit shouldn't carry over when chart type is switched`
**Zone:** Stale Issues / Propose: PR

```
## Issue
#33756: Row limit shouldn't carry over when chart type is switched
https://github.com/apache/superset/issues/33756
Created: 2025-06-12 | Last updated: 2025-06-12
Labels: viz:charts:line, viz:charts:pie

## Assessment
When switching chart types, the previous chart's row limit persists (e.g., pie chart's 100-row limit carries over to a line chart defaulting to 10,000), causing silent data truncation. Three maintainers engaged (Rusackas, Beauchemin, Molina) and reached alignment: each destination chart type should define what happens to control values on transition, with toast notifications to inform users of changes. No open PR exists despite strong maintainer consensus.

## Proposed action
Propose: PR — Implement chart-type-defined transition logic for row limits (and other per-type-defaulted controls). When a user switches chart types, if the incoming chart type has a different default for a control, reset to that default and surface a toast notification. Starting point: explore chart type plugin control definitions and the chart type switch handler in explore/controls.

## Links
- Related issues: none identified
- Linked PRs: none
```

---

## Card 2 — #28248

**Title:** `#28248: Add Missing Stacktrace information on errors, SQL lab query execution`
**Zone:** Stale Issues / Propose: Comment (nudge)

```
## Issue
#28248: Add Missing Stacktrace information on errors, SQL lab query execution
https://github.com/apache/superset/issues/28248
Created: 2024-04-28 | Last updated: 2025-06-13
Labels: none

## Assessment
Enhancement request to surface more stacktrace detail in SQL lab query execution errors. Rusackas acknowledged the issue in April 2024 and was actively trying to get a linked PR (#28268) to pass CI as recently as June 2025 ("Fiddling with the PR again... stay tuned"). However, PR #28268 was ultimately closed without merging in February 2026. The issue is now orphaned — no active PR, but a maintainer invested 2 years of on-and-off effort on it.

## Proposed action
Propose: Comment (nudge) — "PR #28268 was closed in Feb 2026. Is there still interest in this enhancement? Happy to see a fresh PR if someone wants to pick this up — the debugging improvement is still worthwhile."

## Links
- Related issues: #28200 (related discussion)
- Linked PRs: #28268 (closed Feb 2026, without merging)
```

---

## Card 3 — #32771

**Title:** `#32771: No saved queries shown if saved query has jinja dataset(id) after dataset deletion`
**Zone:** Stale Issues / Propose: PR

```
## Issue
#32771: No saved queries shown if saved query has jinja dataset(id) after dataset deletion
https://github.com/apache/superset/issues/32771
Created: 2025-03-20 | Last updated: 2025-06-13
Labels: sqllab:saved_queries, global:jinja, cares:preset

## Assessment
⚠️ cares:preset — flag for Evan's attention.
When any saved query contains `{{ dataset(id) }}` Jinja templating and the referenced dataset is deleted, the entire saved query list becomes inaccessible (errors on both welcome page and list view). Users cannot even delete the broken query to restore access. Rusackas confirmed: "they should be listed, even if the queries WILL fail." Root cause is in the SavedQueryList component's error handling — a DatasetNotFoundError in one query crashes the whole list render. No PR exists.

## Proposed action
Propose: PR — Fix SavedQueryList to handle per-query Jinja resolution errors gracefully: catch `DatasetNotFoundError` per row rather than letting it bubble up to crash the list. The broken query should render with an error indicator and remain deletable. This is a targeted frontend fix in the SavedQueryList component.

## Links
- Related issues: none
- Linked PRs: none
```

---

## Card 4 — #29485

**Title:** `#29485: Incorrect Michigan State in Country Map`
**Zone:** Stale Issues / Propose: Comment (nudge)

```
## Issue
#29485: Incorrect Michigan State in Country Map
https://github.com/apache/superset/issues/29485
Created: 2024-07-04 | Last updated: 2025-06-16
Labels: viz:charts:map

## Assessment
Michigan's polygon in the Country Map viz includes portions of the Great Lakes, making it visually incorrect. The issue is in the NaturalEarth GeoJSON source used by the Country Map plugin. Rusackas engaged and confirmed the constraint (license-compatible data source, ECharts provides renderer not data). A draft PR #29503 ("fix: update Michigan polygon") was opened by the original reporter. As of March 2025, Rusackas was asking for updates to the Jupyter notebook used to generate map data. The draft PR may be stalled.

## Proposed action
Propose: Comment (nudge) — "Draft PR #29503 was opened to fix Michigan's polygon. Is that still moving forward? Also pinging on rusackas's March 2025 request for a Jupyter notebook update — if that's blocking, let us know what's needed."

## Links
- Related issues: none
- Linked PRs: Draft PR #29503 "fix: update Michigan polygon" (open, draft)
```

---

## Card 5 — #33788

**Title:** `#33788: Build of generated Visualization plugin does not work out of the box`
**Zone:** Stale Issues / Propose: PR

```
## Issue
#33788: Build of generated Visualization plugin does not work out of the box
https://github.com/apache/superset/issues/33788
Created: 2025-06-17 | Last updated: 2025-06-17
Labels: none

## Assessment
The official `create-superset-plugin` generator produces a template with at least four immediate issues: (1) unused `sections` import in controlPanel.ts causes compilation failure; (2) missing `jest-environment-jsdom` dependency causes test failures; (3) tests run extremely slowly; (4) console warnings about calling `configure()` before other methods due to missing i18n setup. Only a bot responded with workarounds, but the underlying generator template has not been fixed. No PR exists.

## Proposed action
Propose: PR — Fix the generator template directly: remove the unused `sections` import in controlPanel.ts, add `jest-environment-jsdom` to template devDependencies with correct `testEnvironment` config in jest.config.js, and add a `jest.setup.js` that calls `configure({ languagePack: {} })` before tests. These are template-only changes in `superset-frontend/packages/generator-superset`.

## Links
- Related issues: none
- Linked PRs: none
```

---

## Card 6 — #33757

**Title:** `#33757: Tooltip ignores metric format in line charts – Regression in 4.X`
**Zone:** Stale Issues / Propose: Comment (needs-info)

```
## Issue
#33757: Tooltip ignores metric format in line charts – Regression in 4.X
https://github.com/apache/superset/issues/33757
Created: 2025-06-12 | Last updated: 2025-06-19
Labels: #bug:regression, viz:charts:line

## Assessment
Regression in Superset 4.x where line chart tooltips always display values in dollar format ($,.2f) regardless of the metric's configured format (e.g., percentage .2%). Reporter confirmed currency format fields are empty. The "Show Values" overlay correctly respects format; only tooltips are broken. A second user confirmed the same issue with Time Comparison charts. Michael-s-molina asked in June 2025 whether the reporter could reproduce on 5.0.0 RC3 — no response was received. No PR exists.

## Proposed action
Propose: Comment (needs-info) — "Can you confirm if this is still reproducible on the latest Superset release (5.0.0 or newer)? @michael-s-molina asked about RC3 back in June — any update? If it reproduces on latest, a fix targeting the ECharts timeseries tooltip formatter would be welcome."

## Links
- Related issues: none
- Linked PRs: none
```

---

## Card 7 — #33609

**Title:** `#33609: After user logged out, getting Internal Server Error in browser`
**Zone:** Stale Issues / Propose: Comment (needs-info)

```
## Issue
#33609: After user logged out, getting Internal Server Error in browser
https://github.com/apache/superset/issues/33609
Created: 2025-05-28 | Last updated: 2025-06-24
Labels: global:error, authentication:sso

## Assessment
User reports Internal Server Error on logout with Superset 4.1.1, Azure AD auth, and `AUTH_ROLE_PUBLIC = 'NoAccess'`. The user cannot clear cookies when Superset is embedded in an iframe due to cross-origin restrictions. No server-side logs have been provided. Rusackas asked whether this is a core Superset bug or a custom security manager issue — the question was not clearly answered. A contributor asked for server logs; none have been provided. A loosely related PR #38092 (docs: Keycloak PKCE logout) landed in Feb 2026.

## Proposed action
Propose: Comment (needs-info) — "To triage this properly, we need: (1) any server logs around the time of logout, even at DEBUG level; (2) confirmation of whether a custom security manager is in use; and (3) whether the issue reproduces with a standard browser session (not iframe). Without server logs this is hard to diagnose as a core bug."

## Links
- Related issues: none
- Linked PRs: PR #38092 (merged Feb 2026 — docs auth, loosely related)
```

---

## Card 8 — #33855

**Title:** `#33855: Error in applying db migration to azure mysql instance`
**Zone:** Stale Issues / Propose: PR

```
## Issue
#33855: Error in applying db migration to azure mysql instance
https://github.com/apache/superset/issues/33855
Created: 2025-06-22 | Last updated: 2025-06-24
Labels: install:docker, data:connect:mysql

## Assessment
Migration `2022-05-03_19-39_cbe71abde154_fix_report_schedule_and_log.py` fails on Azure MySQL with `mysql-connector-python` because it passes `ReportState.WORKING` (a Python Enum) directly to a MySQL query filter, but the driver cannot convert Enum objects to MySQL string types. The fix is to use `ReportState.WORKING.value` instead. A user confirmed the workaround but noted multiple migration files may have the same pattern. No PR exists.

## Proposed action
Propose: PR — In the affected migration script, replace direct Enum usages with `.value` (e.g., `ReportState.WORKING` → `ReportState.WORKING.value`) when used in DB query filters. Audit other migration files for the same pattern across enum types. The fix is isolated to migration scripts and does not affect runtime code.

## Links
- Related issues: none
- Linked PRs: none
```

---

## Card 9 — #33861

**Title:** `#33861: HostAliases not added to init job on Kubernetes`
**Zone:** Stale Issues / Propose: Comment (nudge)

```
## Issue
#33861: HostAliases not added to init job on Kubernetes
https://github.com/apache/superset/issues/33861
Created: 2025-06-23 | Last updated: 2025-06-24
Labels: deploy:helm

## Assessment
The `hostAliases` Helm value is applied to deployment pods but not to the Superset init job pod, breaking use cases like custom networking and Google Cloud SQL proxy. The reporter filed the issue and immediately opened a fix PR. PR #33968 ("fix(helm): add host alias to init job") is open and addresses the issue exactly. The PR has been assigned to villebro but has no comments and likely just needs a review.

## Proposed action
Propose: Comment (nudge) — "PR #33968 is open and looks like it addresses this directly. Pinging @villebro (assignee) for a review when you get a chance."

## Links
- Related issues: none
- Linked PRs: PR #33968 "fix(helm): add host alias to init job" (OPEN, assigned to villebro)
```

---

## Card 10 — #33884

**Title:** `#33884: /api/v1/dashboard endpoint returns different response than OpenAPI spec`
**Zone:** Stale Issues / Propose: PR

```
## Issue
#33884: /api/v1/dashboard endpoint returns different response than OpenAPI spec
https://github.com/apache/superset/issues/33884
Created: 2025-06-24 | Last updated: 2025-06-26
Labels: api

## Assessment
The `/api/v1/dashboard` endpoint returns `owners` as an array of user objects, but the OpenAPI spec documents it as a single object. Vitor-Avila confirmed the discrepancy is real ("the issue is indeed visible in https://superset.apache.org/docs/api/ ... I'm just not sure where that info comes from"). The dosubot suggested this is a spec documentation issue (array is correct behavior). No PR exists to fix the spec.

## Proposed action
Propose: PR — Correct the OpenAPI specification for `/api/v1/dashboard` to document `owners` as an array of user objects (not a single object). Likely a fix to the Marshmallow schema or the `@spec` decorator on the dashboard API endpoint. Coordinate with Vitor-Avila to confirm the correct source of the spec definition before submitting.

## Links
- Related issues: none
- Linked PRs: none
```

---

## Summary

| Issue | Title (short) | Zone |
|-------|--------------|------|
| #33756 | Row limit carries over on chart switch | Propose: PR |
| #28248 | Missing stacktrace in SQL lab errors | Propose: Comment (nudge) |
| #32771 | Saved queries broken after dataset deletion ⚠️ cares:preset | Propose: PR |
| #29485 | Michigan polygon incorrect in Country Map | Propose: Comment (nudge) |
| #33788 | Generated viz plugin template broken | Propose: PR |
| #33757 | Tooltip ignores metric format (regression) | Propose: Comment (needs-info) |
| #33609 | Internal Server Error after logout (Azure AD) | Propose: Comment (needs-info) |
| #33855 | DB migration fails on Azure MySQL (enum bug) | Propose: PR |
| #33861 | HostAliases missing from Helm init job | Propose: Comment (nudge) |
| #33884 | Dashboard API response != OpenAPI spec | Propose: PR |
