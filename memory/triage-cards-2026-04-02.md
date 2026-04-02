# Stale Issue Triage Cards — 2026-04-02

Board: RepoBot3000 (`a97875fe-34de-4f37-9e43-85c03de86d20`)
Repo: apache/superset
Run: 10 oldest open issues by `updated_at` ascending

> NOTE: Agor MCP was not connected in this session. Cards are documented here
> for manual creation or re-run once MCP is available. Zone IDs must be
> resolved via `agor_boards_get` on the next connected session.

---

## Card 1 — Zone: Propose: Comment (nudge)

**Title:** `#33756: Row limit shouldn't carry over when chart type is switched`

```
## Issue
#33756: Row limit shouldn't carry over when chart type is switched
https://github.com/apache/superset/issues/33756
Created: Jun 12, 2025 | Last updated: Jun 12, 2025
Labels: viz:charts:line, viz:charts:pie

## Assessment
When users switch chart types, configuration like row limits carries over from
the previous type — e.g., a pie chart's 100-row limit persists on a line chart
that should default to 10,000. Maxime Beauchemin +1'd the idea and proposed a
framework where destination chart types define which params carry over, reset,
or transform; Michael Molina stressed clear toast notifications when controls
change. No implementation started; design is roughly sketched but the issue has
been idle since its creation day (~10 months).

## Proposed action
Propose: Comment (nudge) — "This had some good design discussion on day one
(thanks @mistercrunch and @michael-s-molina). Is there anyone interested in
picking this up? The toast-notification approach for surfacing control changes
seems like the right UX direction."

## Links
- Related issues: none identified
- Linked PRs: none
```

---

## Card 2 — Zone: Propose: Comment (nudge)

**Title:** `#28248: Add Missing Stacktrace information on errors, SQL lab query execution`

```
## Issue
#28248: Add Missing Stacktrace information on errors, SQL lab query execution
https://github.com/apache/superset/issues/28248
Created: Apr 28, 2024 | Last updated: Jun 13, 2025
Labels: none

## Assessment
This enhancement requests surfacing full stacktraces in SQL Lab query error
messages to aid debugging. PR #28268 was opened and then closed after CI
failures; Evan Rusackas (the PR author) was still trying to revive it as of
Jun 13 2025 ("stay tuned, folks!") but there has been no activity since. The
underlying ask is still valid — better error context is a common developer pain
point — but the in-progress PR appears to have stalled.

## Proposed action
Propose: Comment (nudge) — "Hey @rusackas — any update on PR #28268? It looks
like it stalled after CI issues last June. Is it still being pursued, or would
this be a good candidate for someone else to pick up?"

## Links
- Related issues: #28200
- Linked PRs: #28268 (closed, was being revived)
```

---

## Card 3 — Zone: Propose: Comment (nudge)

**Title:** `#32771: No saved queries shown if there is a saved query with jinja {{ dataset(id) }}`

> ⚠️ **cares:preset label present**

```
## Issue
#32771: No saved queries shown if there is a saved query with jinja {{ dataset(id) }}
https://github.com/apache/superset/issues/32771
Created: Mar 20, 2025 | Last updated: Jun 13, 2025
Labels: cares:preset, global:jinja, sqllab:saved_queries

## Assessment
⚠️ This issue carries the `cares:preset` label. When a dataset referenced in a
Jinja-templated saved query (e.g. `{{ dataset(id) }}`) is deleted, the saved
queries list throws "Dataset ID not found" and blocks access to ALL saved
queries — a catch-22 where the offending query can't be deleted. Evan confirmed
the list should still render and asked for error logs; reporter provided
screenshots but found no relevant app logs. No PR exists. The bug is clear and
likely still present: the `SavedQueryList` component should handle missing
dataset IDs gracefully rather than hard-failing the entire list.

## Proposed action
Propose: Comment (nudge) — "Still relevant and tagged cares:preset. The fix
would be in SavedQueryList to catch 'Dataset ID not found' errors per-row
rather than aborting the whole list render. @vickr397 are you still hitting
this? Anyone interested in a fix?"

## Links
- Related issues: none
- Linked PRs: none
```

---

## Card 4 — Zone: Propose: Comment (nudge)

**Title:** `#29485: Incorrect Michigan State in Country Map`

```
## Issue
#29485: Incorrect Michigan State in Country Map
https://github.com/apache/superset/issues/29485
Created: Jul 4, 2024 | Last updated: Jun 16, 2025
Labels: viz:charts:map

## Assessment
The Country Map chart draws Michigan's polygon including the Great Lakes as
state territory rather than land-only boundaries. Rusackas confirmed ECharts
doesn't supply GeoJSON natively and recommended using NaturalEarth data via a
Jupyter Notebook; a draft fix PR #29503 ("fix: update Michigan polygon") was
opened July 5, 2024 and remains open but unmerged. Rusackas has nudged the PR
twice (March and June 2025) asking for the notebook to be updated, but no
progress. An open PR exists — do not close.

## Proposed action
Propose: Comment (nudge) — "PR #29503 has been open since July 2024 and seems
close — the approach (NaturalEarth GeoJSON via Jupyter Notebook) is agreed
upon. Is there a reviewer available to help get this over the line?"

## Links
- Related issues: none
- Linked PRs: #29503 (open draft — fix: update Michigan polygon)
```

---

## Card 5 — Zone: Propose: Comment (nudge)

**Title:** `#33788: The build of generated Visualization plugin does not work out of the box`

```
## Issue
#33788: The build of generated Visualization plugin does not work out of the box
https://github.com/apache/superset/issues/33788
Created: Jun 17, 2025 | Last updated: Jun 17, 2025
Labels: none

## Assessment
Using the official plugin generator produces a template with four out-of-the-box
problems: unused import causing compile errors, missing jest-environment-jsdom,
slow test execution (~60s), and console warnings about uninitialized i18n
configuration. Dosu bot provided workarounds on the same day (remove the unused
`sections` import, install jest-environment-jsdom, add a Jest setupFilesAfterEnv
with translation init). The reporter went quiet after the bot replied. The
underlying template bugs are still likely present and affect any new plugin
developer's first experience.

## Proposed action
Propose: Comment (nudge) — "The plugin generator template likely still has these
four issues (unused import, missing jest-environment-jsdom, slow tests, i18n
warnings). These are bad DX for new contributors. Is there a quick PR opportunity
here to fix the template? Dosu's suggestions from June 2025 have the solutions."

## Links
- Related issues: none
- Linked PRs: none
```

---

## Card 6 — Zone: Propose: Comment (nudge)

**Title:** `#33757: Tooltip ignores metric format in line charts – Regression in 4.X`

```
## Issue
#33757: Tooltip ignores metric format in line charts – Regression in 4.X
https://github.com/apache/superset/issues/33757
Created: Jun 12, 2025 | Last updated: Jan 8, 2026 (cross-reference to #36978)
Labels: #bug:regression, viz:charts:line

## Assessment
Line chart tooltips display values in dollar format ($,.2f) even when metrics
are configured as percentages — a regression from v4.0. Michael Molina asked
to confirm on 5.0.0 RC3; reporter confirmed neither currency format field is
populated. A second contributor (Kasper Mol) reported the same behavior on bar
charts with Time Comparison. The issue was cross-referenced with #36978 in
January 2026, suggesting it may be tracked elsewhere or partially addressed,
but the original issue remains open and the regression is confirmed.

## Proposed action
Propose: Comment (nudge) — "Is this still present in 6.x? The cross-reference
to #36978 in January suggests there may be overlap — are these the same root
cause? If so, closing this in favour of the newer issue might be appropriate."

## Links
- Related issues: #36978
- Linked PRs: none
```

---

## Card 7 — Zone: Propose: Comment (nudge)

**Title:** `#33609: After user logged out, getting Internal Server Error in browser`

```
## Issue
#33609: After user logged out, getting Internal Server Error in browser
https://github.com/apache/superset/issues/33609
Created: May 28, 2025 | Last updated: Jun 24, 2025
Labels: authentication:sso, global:error

## Assessment
After logging out of Superset 4.1.1 with Azure AD (`AUTH_ROLE_PUBLIC =
'NoAccess'`), users hit an Internal Server Error that persists until cookies
are cleared manually. Rusackas questioned whether this is a core bug or a
custom security manager issue and suggested moving the conversation to Help
discussions; a contributor asked for server logs. The reporter's last update
described running Superset in an iframe with cross-origin restrictions making
cookie clearing hard. No confirmed bug, no PR, and the maintainer's framing
suggests this may not be a core issue.

## Proposed action
Propose: Comment (nudge) — "@nagarajmmu this may be better suited for GitHub
Discussions (Help & General) rather than an issue tracker, since it appears to
be configuration-specific (Azure AD + AUTH_ROLE_PUBLIC + iframe). Would you be
able to move this there and include your superset_config.py (redacted)? That
would help pinpoint whether it's a Superset bug or a setup issue."

## Links
- Related issues: none
- Linked PRs: #38092 (open draft — Keycloak PKCE logout example, different provider)
```

---

## Card 8 — Zone: Propose: PR

**Title:** `#33855: Error in applying db migration to azure mysql instance`

```
## Issue
#33855: Error in applying db migration to azure mysql instance
https://github.com/apache/superset/issues/33855
Created: Jun 22, 2025 | Last updated: Jun 23, 2025
Labels: data:connect:mysql, install:docker

## Assessment
When running Superset 5.0.0rc3 migrations against Azure MySQL with the
`mysql+mysqlconnector` dialect, a migration script passes a Python Enum object
directly to a SQLAlchemy filter — which mysql-connector-python cannot convert,
causing a TypeError. The fix is clear and confirmed: change `ReportState.WORKING`
to `ReportState.WORKING.value` in the migration script (or use the mysqlclient
driver). The reporter verified this fix works. No PR exists; this is a small,
well-scoped change that would benefit all Azure MySQL users.

## Proposed action
Propose: PR — Fix migration script to use `.value` on Enum references in filter
clauses rather than passing Enum objects directly (affects at least one migration
referencing `ReportState.WORKING`). The change is 1-2 lines, low risk, and
confirmed by the reporter.

## Links
- Related issues: none
- Linked PRs: none (reporter fixed locally, no PR submitted)
```

---

## Card 9 — Zone: Propose: Comment (nudge)

**Title:** `#33861: HostAliases not added to init job on`

```
## Issue
#33861: HostAliases not added to init job on
https://github.com/apache/superset/issues/33861
Created: Jun 23, 2025 | Last updated: Jun 29, 2025
Labels: deploy:helm

## Assessment
The Helm chart applies `hostAliases` to regular deployment pods but omits them
from the initialization job pod, breaking networking scenarios that depend on
custom host entries (e.g., Google Cloud SQL Proxy). The issue author proactively
opened PR #33968 ("fix(helm): add host alias to init job") within days; it was
assigned to villebro but has not been merged. The fix and PR both look
straightforward. An open PR exists — do not close.

## Proposed action
Propose: Comment (nudge) — "PR #33968 has been open since June 2025 with an
assignee (@villebro) but no merge. Could someone take a review pass? This is a
clear Helm gap affecting Cloud SQL Proxy and similar networking setups."

## Links
- Related issues: none
- Linked PRs: #33968 (open — fix(helm): add host alias to init job)
```

---

## Card 10 — Zone: Propose: Comment (help)

**Title:** `#33884: /api/v1/dashboard endpoint returns a different response than the open api specification`

```
## Issue
#33884: /api/v1/dashboard endpoint returns a different response than the open api specification
https://github.com/apache/superset/issues/33884
Created: Jun 24, 2025 | Last updated: Oct 13, 2025 (cross-reference)
Labels: api

## Assessment
The `/api/v1/dashboard` endpoint returns `results.owners` as an array of user
objects, but the published OpenAPI documentation describes it as a single object.
Vitor-Avila confirmed the mismatch is visible in official docs; Dosu suggests the
bug is in the OpenAPI spec generation tooling rather than the API itself (the
backend correctly returns an array). This is a documentation/spec accuracy issue
that affects SDK/client generators. No PR exists.

## Proposed action
Propose: Comment (help) — "This looks like a spec generation issue, not an API
bug — the backend correctly returns an array. The fix would be in the OpenAPI
annotation for the dashboard schema's `owners` field (likely in
`superset/views/api/schemas.py` or equivalent). Happy to point at the exact
file if a contributor wants to open a doc/spec fix PR."

## Links
- Related issues: none
- Linked PRs: none
```

---

## Summary

| # | Issue | Zone |
|---|-------|------|
| #33756 | Row limit carries over on chart switch | Propose: Comment (nudge) |
| #28248 | Missing stacktrace in SQL lab | Propose: Comment (nudge) |
| #32771 | Saved queries broken w/ deleted Jinja dataset (**cares:preset**) | Propose: Comment (nudge) |
| #29485 | Michigan map includes Great Lakes | Propose: Comment (nudge) |
| #33788 | Viz plugin build broken out of box | Propose: Comment (nudge) |
| #33757 | Tooltip ignores metric format (regression) | Propose: Comment (nudge) |
| #33609 | Internal Server Error on logout (Azure AD) | Propose: Comment (nudge) |
| #33855 | DB migration fails on Azure MySQL (Enum bug) | Propose: PR |
| #33861 | hostAliases missing from Helm init job | Propose: Comment (nudge) |
| #33884 | Dashboard API response ≠ OpenAPI spec | Propose: Comment (help) |

Skipped: #33810 (validation:required label — out of scope per triage rules)
