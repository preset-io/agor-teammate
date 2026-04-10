# FLAKY_TESTS.md — Superset CI Flakiness Log

Tracking observed flaky test failures across our PRs. Job IDs recorded so we can identify double-offenders (same test failing on multiple unrelated PRs).

**How to use:** When CI fails, check if the test is already listed here. If so, it's a known flake — re-trigger and add a new `| job_id | PR |` row to its Occurrences table. Two+ hits = double-offender worth skipping/fixing.

---

## Observed Failures

### FiltersConfigModal.test.tsx — `modifies the name of a filter`

- **File:** `superset-frontend/src/dashboard/components/nativeFilters/FiltersConfigModal/FiltersConfigModal.test.tsx`
- **Shard:** `sharded-jest-tests (5)`
- **Symptom:** `ReferenceError: You are trying to access a property or method of the Jest environment after it has been torn down.` + `A worker process has failed to exit gracefully and has been force exited.`
- **Pattern:** Async teardown leak — open handles (timers, subscriptions) outliving the runner
- **Verdict:** Flaky. Needs `--detectOpenHandles` investigation.

| GHA Job ID | PR | Date | Notes |
|------------|-----|------|-------|
| 70709522736 | #39248 (sql-expr-editor-fix) | 2026-04-10 | First observed |

---

### DatasetList.listview.test.tsx — `type filter persists after duplicating a dataset`

- **File:** `superset-frontend/src/pages/DatasetList/DatasetList.listview.test.tsx`
- **Shard:** `sharded-jest-tests (4)`
- **Symptom:** 429s runtime then worker teardown failure
- **Pattern:** Async teardown — something hanging (mock, timer, unresolved promise)
- **Verdict:** Flaky. 429s is a red flag.

| GHA Job ID | PR | Date | Notes |
|------------|-----|------|-------|
| 70709522744 | #39248 (sql-expr-editor-fix) | 2026-04-10 | First observed |

---

### ShareMenuItems.test.tsx — `Test suite failed to run`

- **File:** `superset-frontend/src/dashboard/components/menu/ShareMenuItems/ShareMenuItems.test.tsx`
- **Shard:** `sharded-jest-tests (3)`
- **Symptom:** "Test suite failed to run" + worker process teardown crash
- **Pattern:** Same async teardown leak family
- **Verdict:** Flaky.

| GHA Job ID | PR | Date | Notes |
|------------|-----|------|-------|
| 70714654077 | #39246 (sql-popover-fix) | 2026-04-10 | First observed |

---

### DataTablesPane.test.tsx — `Should copy data table content correctly`

- **File:** `superset-frontend/src/explore/components/DataTablesPane/test/DataTablesPane.test.tsx`
- **Shard:** `sharded-jest-tests (4)`
- **Symptom:** Worker process teardown crash after test
- **Pattern:** Async teardown. PR #39246 touches clipboard — worth watching on clipboard-adjacent PRs
- **Verdict:** Likely flaky, but monitor.

| GHA Job ID | PR | Date | Notes |
|------------|-----|------|-------|
| 70714654084 | #39246 (sql-popover-fix) | 2026-04-10 | First observed; clipboard PR proximity noted |

---

## Double-Offenders (seen 2+ times)

_None yet. Once a test appears in 2+ PRs above, move it here._

---

## Patterns

| Pattern | Tests affected | Shards |
|---------|----------------|--------|
| Async teardown / "worker process force exited" | FiltersConfigModal, DatasetList.listview, ShareMenuItems, DataTablesPane | 3, 4, 5 |

Shards 3–5 seem to be where the flaky teardown cluster lands. Likely due to test ordering / shared global state in those shards.

---

## Next Steps

- [ ] Verify these fail on master with no changes (confirm truly flaky, not our code)
- [ ] Run `--detectOpenHandles` locally on the worst offenders
- [ ] Once a test is a confirmed double-offender, open an issue on apache/superset
- [ ] Consider `jest.retryTimes(1)` as a short-term mitigation for confirmed flakes

---

_Last updated: 2026-04-10_
