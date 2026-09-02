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
- **`groupby`-deprecation noise in apache/superset now has three separate open PRs chasing it (#43468 08-24, #43520 08-25, #43723 08-31), all opened *after* the actual root-cause fix (#41204, merged 2026-06-18) should have already stopped new occurrences at the source.** Before picking a Datadog-driven "deprecation warning" or "groupby" fix in this repo again: (1) `gh pr list --search "query_object OR groupby deprecated"` first — this exact symptom has been re-discovered independently multiple times because the standard `gh pr list --author @me` pre-flight only catches same-author collisions, not same-symptom ones; (2) treat the underlying Datadog volume as possibly stale — it may reflect a `superset-private` build that hasn't merged #41204 yet, not a live apache/superset gap, and that's unverifiable from this checkout alone (superset-private isn't a registered/accessible repo here). 2026-09-02's self-review caught this before a 4th duplicate PR was opened.

---

## Preset Architecture Patterns

_(Will build this as I learn the codebase)_

---

## Common Errors & Fixes

_(Will track patterns from Datadog monitoring)_

---

_This file grows with me._
