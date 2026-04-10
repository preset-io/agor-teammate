# FLAKY_TESTS.md — Superset CI Flakiness Log

Tracking observed flaky test failures across our PRs to identify patterns and build a case for skipping or fixing the worst offenders.

---

## Observed Failures

### FiltersConfigModal.test.tsx — `modifies the name of a filter`

- **File:** `superset-frontend/src/dashboard/components/nativeFilters/FiltersConfigModal/FiltersConfigModal.test.tsx`
- **Shard:** `sharded-jest-tests (5)`
- **Symptom:** `ReferenceError: You are trying to access a property or method of the Jest environment after it has been torn down.` + `A worker process has failed to exit gracefully and has been force exited.`
- **Pattern:** Async teardown leak — test has open handles (timers, subscriptions) that outlive the test runner
- **First seen:** 2026-04-10 on PR #39248 (sql-expr-editor-fix) — unrelated to that PR's changes
- **Verdict:** Flaky. Likely leaking async state (Redux store, subscriptions). Needs `--detectOpenHandles` investigation.

---

### DatasetList.listview.test.tsx — `type filter persists after duplicating a dataset`

- **File:** `superset-frontend/src/pages/DatasetList/DatasetList.listview.test.tsx`
- **Shard:** `sharded-jest-tests (4)`
- **Symptom:** Test runs for 429s then hits worker teardown failure. Same "worker process has failed to exit gracefully" pattern.
- **Pattern:** Async teardown leak — very long test runtime (429s) suggests a mock or timer that never resolves
- **First seen:** 2026-04-10 on PR #39248 (sql-expr-editor-fix) — unrelated to that PR's changes
- **Verdict:** Flaky. The 429s runtime is a red flag — something is hanging.

---

## Patterns

| Pattern | Tests affected |
|---------|----------------|
| Async teardown / "worker process force exited" | FiltersConfigModal, DatasetList.listview |
| Jest shard | Shard 4 and 5 seem to be where these land |

---

## Next Steps

- [ ] Investigate `--detectOpenHandles` on both tests locally
- [ ] Check if these fail on master with no changes (confirm truly flaky)
- [ ] Consider adding `jest.setTimeout` guards or explicit cleanup
- [ ] If confirmed flaky, open issue on apache/superset to track

---

_Last updated: 2026-04-10_
