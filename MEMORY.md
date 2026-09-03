# MEMORY.md - Long-Term Memory

_Curated memories. The distilled essence, not raw logs._

---

## Bootstrap

**Created:** 2026-03-20

I'm Soraya 🧑‍💻, super senior SRE for Preset. Elizabeth is my human (PST timezone, elizabeth@preset.io). I work on the SRE board in Agor.

**My job:** Monitor Datadog for errors, triage signal vs. noise, create Shortcut tickets for real issues, fix in Github.

**Repos I work with:**
- preset-io/superset-shell (configured)
- preset-io/manager (need to set up)
- preset-io/superset-private (need to set up)
- preset-io/terraform-live-envs (need to set up)
- preset-io/terraform-modules (need to set up)
- preset-io/helm (need to set up)

**My vibe:** Sharp, direct, don't waste words. I've seen the fires. I know what matters.

---

## Key Decisions

_(Will grow over time)_

---

## Lessons Learned

- **A dotted-attribute grep doesn't rule out a field being read.** When checking whether a frontend `buildQuery.ts` reads a form-data field before renaming/removing it, `grep "formData.groupby"` or `grep "\.groupby\b"` misses object-destructuring (`const { groupby } = formData`), which is a completely different literal pattern. Grep for the bare field name too, or better, read the function. Cost real risk on 2026-08-31: a first-pass fix would have silently dropped the grouping dimension from 10 production example charts (Timeseries/Treemap plugins) had self-review not caught the destructuring pattern.
- **`gh pr view --json state` before trusting a memory log's "merged precedent" label.** An earlier day's log called PR #43468 a "merged precedent" when it was actually still open (`DIRTY`/`CONFLICTING`, never merged) — that PR itself contains a live bug (renamed `groupby`→`columns` in a `box_plot` chart YAML, which the box_plot buildQuery treats as a separate, still-active field). Don't inherit a prior day's characterization of a PR's status without re-verifying it live.
- **`groupby`-deprecation noise in apache/superset now has three separate open PRs chasing it (#43468 08-24, #43520 08-25, #43723 08-31), all opened *after* the actual root-cause fix (#41204, merged 2026-06-18) should have already stopped new occurrences at the source.** Before picking a Datadog-driven "deprecation warning" or "groupby" fix in this repo again: (1) `gh pr list --search "query_object OR groupby deprecated"` first — this exact symptom has been re-discovered independently multiple times because the standard `gh pr list --author @me` pre-flight only catches same-author collisions, not same-symptom ones; (2) treat the underlying Datadog volume as possibly stale — it may reflect a `superset-private` build that hasn't merged #41204 yet, not a live apache/superset gap, and that's unverifiable from this checkout alone (superset-private isn't a registered/accessible repo here). 2026-09-02's self-review caught this before a 4th duplicate PR was opened. **Update 2026-09-03:** #43520 is itself the right generic fix for the *whole* `DEPRECATED_FIELDS` family in `query_object.py` (log-level downgrade, not per-field fixture renaming) — it covers `timeseries_limit`/`granularity_sqla` too, not just `groupby`. Any future warning from that same mechanism is very likely already covered by #43520; check it before touching `query_object.py` or any example fixture again.
- **A prod deprecation-warning hit doesn't mean apache/superset has a live bug — confirm the warning's source line still exists at `origin/master` before writing any code.** 2026-09-03's daily "find a deprecation warning, fix it" run: the top two Datadog `deprecat*` hits (`appbuilder.app is deprecated`, `Superset.explore_json ... deprecated`) both traced to code that's **already fully removed/fixed on `origin/master`** (`appbuilder.app`'s only two call sites were fixed by `c0e78f39d7`/`689fc34ac2`; `explore_json` was deleted entirely by `2ecce20e48`/#41714 — `grep -rn "def explore_json"` returns nothing). The prod noise is stale-build noise: either `superset-private` (inaccessible here) running behind `apache/superset:master`, or a deployed image that hasn't picked up a recent merge. Check `git log --grep=<symptom>` and confirm the offending line/function still exists at HEAD *before* spending time on a fix — a warning with zero live call sites in the repo isn't a task, it's a version-skew signal worth flagging to Elizabeth, not a PR. No PR/card/Shortcut story opened that day — forcing one to fill the checklist would have been noise.

---

## Preset Architecture Patterns

_(Will build this as I learn the codebase)_

---

## Common Errors & Fixes

_(Will track patterns from Datadog monitoring)_

---

_This file grows with me._
