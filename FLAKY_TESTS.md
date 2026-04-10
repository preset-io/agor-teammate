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

### DataTablesPane.test.tsx — `Should copy data table content correctly`

- **File:** `superset-frontend/src/explore/components/DataTablesPane/test/DataTablesPane.test.tsx`
- **Shard:** `sharded-jest-tests (4)`
- **Symptom:** Worker process teardown crash after test
- **Pattern:** Async teardown. PR #39246 touches clipboard — watch on clipboard-adjacent PRs
- **Verdict:** Likely flaky. Watch for second occurrence.

| GHA Job ID | PR | Date | Notes |
|------------|-----|------|-------|
| 70714654084 | #39246 (sql-popover-fix) | 2026-04-10 | First observed; clipboard PR proximity noted |

---

## Cross-PR Anecdotal Table

Quick-reference of all flaky hits across PRs. Useful for spotting patterns at a glance.

| Test file (short) | Test name | Shard | Job ID | PR | Date |
|-------------------|-----------|-------|--------|----|------|
| FiltersConfigModal.test.tsx | modifies the name of a filter | 5 | 70709522736 | #39248 | 2026-04-10 |
| DatasetList.listview.test.tsx | type filter persists after duplicating | 4 | 70709522744 | #39248 | 2026-04-10 |
| ShareMenuItems.test.tsx | Test suite failed to run | 3 | 70714654077 | #39246 | 2026-04-10 |
| DataTablesPane.test.tsx | Should copy data table content correctly | 4 | 70714654084 | #39246 | 2026-04-10 |
| FiltersConfigModal.test.tsx | modifies the name of a filter | 5 | 70705021032 | #39249 | 2026-04-10 |

---

## NOT Flaky — Real Failures (don't log here, fix in PR)

| PR | Test | Reason it's real |
|----|------|-----------------|
| #39251 | GlobalStyles.test.tsx | PR broke GlobalStyles (unused React import, component throws) |
| #39249 | PropertiesModal.test.tsx — "Certification details" | PR removed "Advanced" tab, test can't find element |
| #39253 | TableChart.test.tsx TS errors | Worker wrote bad TypeScript in tests |
| #39252 | pre-commit prettier | Worker didn't format before committing |

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

_Last updated: 2026-04-10_
