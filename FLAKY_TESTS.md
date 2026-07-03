# FLAKY_TESTS.md — Superset CI Flakiness Log

Tracking observed flaky test failures across PRs to identify patterns and build a case for skipping or fixing the worst offenders.

**How to use:**
- When CI fails, check this file first before re-triggering
- If the test is listed here → re-trigger CI, add a row to its Occurrences table with job ID + PR
- If a test appears on 2+ unrelated PRs → it's a **double-offender** → prioritize for fix/skip
- If CI fails for a real reason (test asserts on changed UI, TS error in new code) → do NOT log here

---

## ⚠️ Double-Offenders (seen on 2+ unrelated PRs)

### FiltersConfigModal.test.tsx — `modifies the name of a filter`

- **File:** `superset-frontend/src/dashboard/components/nativeFilters/FiltersConfigModal/FiltersConfigModal.test.tsx`
- **Shard:** `sharded-jest-tests (5)`
- **Symptom:** `ReferenceError: You are trying to access a property or method of the Jest environment after it has been torn down.` + `A worker process has failed to exit gracefully and has been force exited.`
- **Pattern:** Async teardown leak — Redux store / subscriptions / timers leaking across tests. 761s runtime on second occurrence.
- **Verdict:** ✅ Confirmed flaky. **High priority to fix or skip.**

| GHA Job ID | PR | Date | Notes |
|------------|-----|------|-------|
| 70709522736 | #39248 (sql-expr-editor-fix) | 2026-04-10 | First observed, shard 5 |
| 70705021032 | #39249 (sc-101015 chart properties modal) | 2026-04-10 | Second hit, unrelated PR, 761s runtime — confirmed double-offender |

---

## Single Occurrences (monitor for recurrence)

### DatasetList.listview.test.tsx — `type filter persists after duplicating a dataset`

- **File:** `superset-frontend/src/pages/DatasetList/DatasetList.listview.test.tsx`
- **Shard:** `sharded-jest-tests (4)`
- **Symptom:** 429s runtime then worker teardown failure
- **Pattern:** Async teardown — hanging mock, timer, or unresolved promise
- **Verdict:** Likely flaky. Watch for second occurrence.

| GHA Job ID | PR | Date | Notes |
|------------|-----|------|-------|
| 70709522744 | #39248 (sql-expr-editor-fix) | 2026-04-10 | First observed |

---

### FileHandler/index.test.tsx — LaunchQueue mock teardown ⚠️ DOUBLE-OFFENDER

- **File:** `superset-frontend/src/pages/FileHandler/index.test.tsx`
- **Shard:** `sharded-jest-tests (6)`
- **Symptom:** Individual tests time out at 20s (`setupLaunchQueue` mock never resolves), then worker teardown crash cascades to remaining tests in file.
- **Pattern:** LaunchQueue mock not torn down between tests — entire file is affected (Parquet, Excel, and unsupported file type tests all hit).
- **Verdict:** ✅ Confirmed flaky. **Fix in progress** — worktree `fix-filehandler-flaky-tests`, session `f35cd838`.

| GHA Job ID | PR | Date | Notes |
|------------|-----|------|-------|
| 71151070116 | #39332 (sc-102502 download orderby fix) | 2026-04-14 | First observed — "handles Parquet file correctly" timed out |
| 71282515731 | #39345 (sc-91230 conditional formatting fix) | 2026-04-21 | Second hit, unrelated PR — "handles Excel (.xls) file correctly" timed out — confirmed double-offender |

---

### ShareMenuItems.test.tsx — `Test suite failed to run`

- **File:** `superset-frontend/src/dashboard/components/menu/ShareMenuItems/ShareMenuItems.test.tsx`
- **Shard:** `sharded-jest-tests (3)`
- **Symptom:** "Test suite failed to run" + worker process teardown crash
- **Pattern:** Same async teardown family
- **Verdict:** Likely flaky. Watch for second occurrence.

| GHA Job ID | PR | Date | Notes |
|------------|-----|------|-------|
| 70714654077 | #39246 (sql-popover-fix) | 2026-04-10 | First observed |

---

### ~~DataTablesPane.test.tsx~~ — MOVED TO REAL FAILURES (see below)

---

### SavedQueryList.test.tsx — `"+ Query" button pushes a router-relative path (subdirectory deployment)`

- **File:** `superset-frontend/src/pages/SavedQueryList/SavedQueryList.test.tsx`
- **Shard:** `sharded-jest-tests (5)`
- **Symptom:** Test assertion failure on router push path — unrelated to PR changes
- **Verdict:** ✅ Confirmed flaky — seen on #41557 (2026-06-30) and #41314 (2026-07-03). **Double-offender.**

| GHA Job ID | PR | Date | Notes |
|------------|-----|------|-------|
| 84221764450 | #41557 (fix-db-docs-links-sc111787) | 2026-06-30 | First observed |
| 84911151687 | #41314 (fix-sc-111554-save-chart-overwrite) | 2026-07-03 | Second hit — confirmed double-offender |

---

### TablePreview.test.tsx — `refreshes table metadata when triggered` + `shows CREATE VIEW statement`

- **File:** `superset-frontend/src/SqlLab/components/TablePreview/TablePreview.test.tsx`
- **Shard:** `sharded-jest-tests (7)`
- **Symptom:** `TestingLibraryElementError: Unable to find an accessible element with the role "button" and name "sync"` / `"eye"`
- **Verdict:** ❌ NOT flaky — **deterministic master regression.** Commit `8aa0faf8061` *"fix(a11y): use tooltip string as aria-label on ActionButton, not test-id"* changed the ActionButton accessible name from the icon name to the tooltip string, but `TablePreview.test.tsx:154,173` still queries `getByRole('button', { name: 'sync' / 'eye' })`. Fails on master on every PR. Fix = update the test to query by the tooltip label (or add `name`/`aria-label` back). Re-triggering CI does NOT help.
- **Fixed in:** #41314 — updated queries to `'Refresh table schema'` / `'Show CREATE VIEW statement'`

| GHA Job ID | PR | Date | Notes |
|------------|-----|------|-------|
| 84221764465 | #41557 (fix-db-docs-links-sc111787) | 2026-06-30 | First observed |
| 84334928007 | #41557 (fix-db-docs-links-sc111787) | 2026-06-30 | 2nd run, same failure → confirmed deterministic, root-caused to a11y commit `8aa0faf8061` |
| 84911152159 | #41314 (fix-sc-111554-save-chart-overwrite) | 2026-07-03 | Fixed by updating queries to tooltip strings — committed to this PR |

---

## Cross-PR Anecdotal Table

Quick-reference of all flaky hits across PRs. Useful for spotting patterns at a glance.

| Test file (short) | Test name | Shard | Job ID | PR | Date |
|-------------------|-----------|-------|--------|----|------|
| FiltersConfigModal.test.tsx | modifies the name of a filter | 5 | 70709522736 | #39248 | 2026-04-10 |
| DatasetList.listview.test.tsx | type filter persists after duplicating | 4 | 70709522744 | #39248 | 2026-04-10 |
| ShareMenuItems.test.tsx | Test suite failed to run | 3 | 70714654077 | #39246 | 2026-04-10 |
| ~~DataTablesPane.test.tsx~~ | ~~Should copy data table content correctly~~ | 4 | 70714654084 | #39246 | 2026-04-10 | **REAL REGRESSION** (PR broke test) |
| FiltersConfigModal.test.tsx | modifies the name of a filter | 5 | 70705021032 | #39249 | 2026-04-10 |
| FileHandler/index.test.tsx | handles Parquet file correctly + cascade | 6 | 71151070116 | #39332 | 2026-04-14 |
| Cypress dashboard-header-container | `[data-test=dashboard-header-container]` not found | E2E shards 0,2,3,4 | 78357237457/449/417/500 | #40506 | 2026-05-28 |
| Playwright global setup | Authentication timeout (5s) at login | E2E (chromium) | 78357237506 | #40506 | 2026-05-28 |
| SavedQueryList.test.tsx | "+ Query" button pushes router-relative path | 5 | 84221764450 | #41557 | 2026-06-30 |
| TablePreview.test.tsx | refreshes table metadata + shows CREATE VIEW statement | 7 | 84221764465 | #41557 | 2026-06-30 |
| SavedQueryList.test.tsx | "+ Query" button pushes router-relative path | 5 | 84911151687 | #41314 | 2026-07-03 | **double-offender** |
| TablePreview.test.tsx | refreshes table metadata + shows CREATE VIEW statement | 7 | 84911152159 | #41314 | 2026-07-03 | fixed in #41314 |

---

## NOT Flaky — Real Failures (don't log here, fix in PR)

| PR | Test | Reason it's real |
|----|------|-----------------|
| #39251 | GlobalStyles.test.tsx | PR broke GlobalStyles (unused React import, component throws) |
| #39249 | PropertiesModal.test.tsx — "Certification details" | PR removed "Advanced" tab, test can't find element |
| #39253 | TableChart.test.tsx TS errors | Worker wrote bad TypeScript in tests |
| #39252 | pre-commit prettier | Worker didn't format before committing |
| #39246 | DataTablesPane.test.tsx — "Should copy data table content correctly" | `TypeError: Cannot redefine property: default` at `jest.spyOn(copyUtils, 'default')` — PR changed `src/utils/copy.ts` from own impl to `export { default }` re-export, which creates non-configurable live binding that spyOn can't override. Fix: use `import X from ...; export default X` instead. |

---

## Patterns

| Pattern | Tests | Shards hit |
|---------|-------|------------|
| Async teardown / "worker process force exited" | FiltersConfigModal ⚠️, DatasetList, ShareMenuItems, DataTablesPane | 3, 4, 5 |
| Timing-dependent (long runtime before crash) | FiltersConfigModal (761s!), DatasetList (429s) | 4, 5 |

**Shard 4 and 5 are hot spots** — most flaky teardown crashes land there. Likely due to test ordering in those shards causing shared state contamination.

---

## Next Steps

- [ ] **FiltersConfigModal** (double-offender): run `--detectOpenHandles` locally, open apache/superset issue
- [ ] Verify DatasetList, ShareMenuItems, DataTablesPane fail on master with no changes
- [ ] Consider `afterEach` cleanup audit in the dashboard/nativeFilters test suite
- [ ] If a third test hits shard 4/5, audit that shard's test ordering

---

_Last updated: 2026-06-30_
