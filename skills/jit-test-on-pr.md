# Skill: Just-in-Time Test on a PR (apache/superset pilot)

Given one `apache/superset` PR diff, an independent agent infers what the change was *supposed* to do, generates a targeted test that would **fail if that change introduced a regression**, runs it against both the pre- and post-change code to prove it discriminates, and reports the result as a signal on the PR — **without ever committing or pushing the test**. Modeled on Meta's Just-in-Time Testing (JiTTest, 2026): tests are created on demand for a single change and discarded, not maintained.

**Why this exists on top of the fix author's own regression test:** the fix author writes a test knowing their intended fix, so it inherits their blindspots. A JiTTest is written by an agent that saw *only the diff* — an adversarial second opinion whose whole job is "what regression could this exact change have introduced that the author didn't think to guard?" It is a **verification gate, not a deliverable**: nothing it produces lands in the PR.

**Pilot scope:** `apache/superset` only, ephemeral only, one PR per invocation. Invoked on-demand (pass a PR#) or as a verification step inside an existing run (Sentry burndown, superset-error-cleanup, deprecation-fix) after the PR is opened but before/alongside Minerva review. Not yet wired to a cron schedule — see "Wiring" at the end.

## Before starting

1. Read the target PR: `gh pr view <N> --repo apache/superset` and `gh pr diff <N> --repo apache/superset`. Note the head repo/branch (`headRepositoryOwner` — usually the `eschutho` fork; see memory `project_superset_push_origin_works`).
2. This runs in an **isolated Agor branch, never the shared clone** — we must not touch a live fix branch's tree, and the shared clone has its own documented breakage. Create a fresh Agor branch off the PR head (it materializes as `storage_mode: clone` — a self-standing clone with its own `.git`/venv, *not* the shared clone's env) so the generated test lives only there and is thrown away.
3. Do NOT read the fix author's PR description reasoning or their own test before inferring intent — infer from the diff alone first, then you may read theirs to avoid writing a byte-identical duplicate. The independence is the value.

## Setup (isolated, ephemeral worktree)

1. Create an Agor branch on the `superset` repo (`repoId` `4903fa88-c79c-408e-a643-1ca35743373c`), board `9a49d11a-6605-4581-b58e-f45fe6bfbadb` (SRE), sourced from the PR head branch. Kebab name, e.g. `jit-test-pr-<N>`. This branch is scratch — it gets archived at the end, nothing merges from it.
2. Fresh branch dirs hit `EACCES` on direct writes from a shell that predates the branch's unix group. Don't fight it with `sg`/`newgrp` (correctly denied as privilege-escalation-shaped) — spawn a session scoped to the branch (`agor_sessions_create` with that `branchId`, `enableCallback: true`) to do the file work; sessions created after the branch exists get correct group membership from process start. This is the same workaround the burndown/error-cleanup skills use.
3. In that session: `git fetch --unshallow` if the clone is shallow (memory `project_superset_shared_repo_shallow_clone`) so you can diff/checkout against the merge base.
4. **Build the test env (verified recipe, 2026-09-02 spike, ~15s on a warm uv cache):**
   ```bash
   uv venv --python 3.11 .venv && source .venv/bin/activate
   # The two native builds (mysqlclient, python-ldap) need MySQL/LDAP C headers that
   # aren't installed and can't be (sandbox has no_new_privileges → no apt-get). A DB-free
   # unit test needs neither, so drop them:
   grep -vE '^(mysqlclient|python-ldap)==' requirements/development.txt > /tmp/dev_filtered.txt
   uv pip install -r /tmp/dev_filtered.txt          # resolves clean (~278 pkgs), editable superset + superset-core build fine
   ```
   The prior "pytest is broken" note (`project_superset_shared_repo_pytest_env_broken`) was about the *shared* clone and blamed a uv lock conflict — the spike proved a **fresh clone resolves cleanly**; the only obstacle is those two native headers, which we sidestep by exclusion. **Scope caveat: this gets you `tests/unit_tests/` (DB-free) only.** Integration tests needing a real MySQL/Postgres won't run here — but our exception-handling regression tests live in `tests/unit_tests/` (e.g. `jinja_context_test.py`), which is the target. Per-test cost after setup: ~1–2s pytest + a one-time ~15s cold superset import.

## Inferring intent (diff only)

- Classify the change: **bug fix** (behavior should change for the buggy input), **refactor / no-behavior-change** (behavior must stay identical), or **new behavior** (a path that didn't exist before).
- Identify the changed code path(s) and the smallest input that reaches them. For exception-handling fixes (the superset-error-cleanup pipeline's bread and butter), that's the input that makes the wrapped call throw.
- **Pin down what *observably* changed — type, HTTP status, message, or a side effect — before writing an assertion.** This is where the gate earns its keep. A change can *look* like a behavior fix but be cosmetic. Worked example, the #42366 dry-run (2026-08-27): the diff added an `except UndefinedError` branch *before* the existing `except (TemplateError, ...)`. But `UndefinedError` is already a subclass of `TemplateError` (verify: `python3 -c "import jinja2.exceptions as e; print(e.UndefinedError.__mro__)"`), so **base already caught it** and already raised `QueryObjectValidationError` (HTTP 400). The *only* observable difference base→head was the message string ("Error while rendering virtual dataset query: …" → "Virtual dataset template error: …"). Same type, same status. If you'd blindly asserted `pytest.raises(QueryObjectValidationError)`, the test would pass on **both** base and head and discriminate nothing. When the "raw" exception being newly caught is already a subclass of something an existing handler catches, the change is almost always message-quality, not a functional fix — say so.
- Watch the `DebugUndefined` trap: Superset's Jinja env degrades some undefined-access patterns to a placeholder string instead of raising, so the "obvious" repro may not actually throw (memory-worthy gotcha from PR #42401). Confirm your trigger input actually exercises the path on real code before trusting the test.

## Generating + running the JiTTest

Write the test into the repo's test tree in the *style of the neighboring test file* (fixtures, factories, client helpers) — but it is **uncommitted and temporary**. Then prove it discriminates:

1. **On PR HEAD** (the change applied) → run the generated test. Expected: **PASS**. If it fails here, either the change is actually buggy or your test is wrong — do NOT report a regression yet; investigate which, and only report a real finding once you've ruled out a bad test.
2. **On base** (revert just the changed *non-test* implementation files to the merge base, keep your test): `git checkout <merge-base> -- <changed source files>`, then re-run.
   - **Bug fix:** expected **FAIL** on base — this proves the test catches the exact regression the fix addresses. A test that passes on both base and head for a bug-fix PR is not exercising the fix; discard it and try a sharper input.
   - **Refactor / no-behavior-change:** expected **PASS** on both — the test asserts an invariant that must survive the refactor. Here the value is confirming the change is genuinely behavior-preserving.
3. Restore head (`git checkout <head> -- <changed source files>` or reset), **delete the test file**, confirm `git status` is clean. Nothing from this worktree is ever committed or pushed.

Run only the single generated test (not the suite) for speed. Use `uvx ruff@0.9.7` if you lint the test (the shared hook pins a stale ruff, memory `project_superset_shared_repo_stale_ruff_hook`) — though for an ephemeral test, lint is optional.

## Reporting

The output is a **signal, never a PR comment** (never comment on GitHub PRs without approval — memory `feedback_no_pr_comments_without_approval`). Report as:

- A note back to the invoking run / to Elizabeth: `PASS` (change verified, test discriminates as expected) or `FAIL` (independent JiTTest caught a regression the author's test missed — include the failing test, the input, and expected-vs-actual).
- **Report cosmetic-vs-functional, and whether the author's own test actually discriminates.** If the only observable change is a message string (see the #42366 worked example above), say "message-quality change, no type/status regression to protect — low risk" rather than dressing it up as a caught bug. And check the author's test the same way: does it fail on base, or would it pass on base too? A non-discriminating author test (e.g. asserts the exception type but the type didn't change) is itself a finding worth surfacing — it's the gate's highest-value catch.
- If a real regression is found, that's a blocking finding: route it to the fix author via Minerva (session on the Minerva/EngCodeReviewBot branch `019df42c-8d6d-76d2-92bd-a49c169db7f1`), the same way review findings are routed — do not self-ratify or comment directly.
- If the card exists on the SRE board, you may add the JiT result to the card `description`/`data`. Do not gate auto-merge on it during the pilot — it's advisory until we trust it.

## Wrap-up

- Archive the scratch `jit-test-pr-<N>` branch (it has no commits worth keeping).
- Append to `memory/YYYY-MM-DD.md`: PR#, intent classification, whether the JiTTest passed/failed, whether it discriminated (failed on base for bug fixes), and — importantly for tuning the pilot — whether it found anything the author's own test didn't. That signal is how we decide if this graduates to a schedule.
- Commit workspace memory changes (`log:` prefix, matching `git log` convention).

## Guardrails

- **Ephemeral, always.** The generated test is a gate, not an artifact. Never `git add`/commit/push it, never open a PR from the scratch branch. If a JiTTest turns out to be genuinely worth keeping, that's a *separate* decision to raise with Elizabeth — do not smuggle it into the fix PR.
- **Never report a regression you haven't disambiguated.** A HEAD failure can mean (a) the change is buggy, (b) the test is wrong, or (c) the env/flake is broken. Rule out (b) and (c) before claiming (a). A false "your fix is broken" is worse than staying quiet.
- **Independence is the whole point.** Infer intent from the diff before reading the author's rationale/test. If you just re-derive their test, you've added no coverage.
- **Never comment on the GitHub PR** — route findings through Minerva/Elizabeth (memory `feedback_no_pr_comments_without_approval`).
- One PR per invocation; don't batch-sweep during the pilot.
- If the isolated env can't run the test at all (not just a test failure — an environment failure), stop and report the env blocker; do not fall back to the broken shared-clone pytest, and do not report the change as unverified-therefore-bad.

## Wiring (scheduled, DISABLED pending sign-off)

A dedicated **disabled** schedule exists: **"JiT test gate (advisory)"** — `01a0698f-6d8c-7665-ba72-599df73e494f` on the private-sre branch, `0 13 * * *` America/Los_Angeles (1pm PT, a couple hours before the 3pm merge sweep), Opus 4.8/high. Deliberately a *separate* schedule rather than folded into the merge-critical 3pm "Daily PR status check" (`019ea9d1`), so it's independently toggleable and can never affect merge. Each run: pulls `zone-pr-ready` apache/superset cards, skips any already gated (`data.jit_gate`), caps at 3/run, spawns an ephemeral gate session per card, records the verdict on the card, and DMs Elizabeth only on a real FAIL / meaningful author-test gap. It is **advisory and non-blocking** — never comments on PRs, never moves cards, never gates merge. Enable only after Elizabeth reviews the pilot's false-positive rate (`agor_schedules_patch … enabled:true`).

## Related skills

- `skills/superset-error-cleanup.md` — the primary source of superset PRs this gate runs against; already contains the base-vs-head discrimination motion for the fix author's own test.
- `skills/sentry-error-burndown.md` — another PR source; same pipeline shape.
- `skills/request-minerva-review.md` (Minerva routing) — how JiT findings reach the fix author.
