# Superset 6.1 launch health — running findings

_Created 2026-09-28. Method: [[reference_release_cohort_health_method]]. Per-week detail is in daily logs
(08-31, 09-04, 09-14, 09-21, 09-28)._

## Trend (6.1.x prod workspaces)
08-31 22 → 09-04 22 → 09-14 3 (parked) → 09-21 414 (6.1.0.8 to all 4 main clusters, 09-16) → 09-28 364 (flat) → 10-05 403 (6.1.0.9, 10 deploys/400 ws; all deploys rebuilt ~09-29/30).
The 6.0 line consolidated 6.0.0.33 → .34 → .35 → .36 (2,623 ws on 09-28). 6.1.0.9 was staging-only on 09-28.

## Open 6.1-only issues
- SUPERSET-PYTHON-16B2/176D/176E (found 10-05): `NoSuchModuleError: Can't load plugin: sqlalchemy.dialects:databricks.connector`,
  2 ws (189409e4.us2a, a92e022d.us1a), 77 ev/7d, 0 on 6.0 ever. Likely the legacy `databricks+connector` dialect is missing from
  the 6.1 image (unverified). Migration risk for 6.0 tenants using databricks+connector URIs. Flagged in the 10-05 post.
- SUPERSET-PYTHON-175B: `TypeError: timeout must be an int or datetime.timedelta, got 'str'` in
  DatabaseRestApi.schemas → get_all_schema_names → cache.set(timeout=<str>) → cachelib _to_seconds.
  First seen 09-17. On 09-28: 45 ev/7d, 4 workspaces (6a1e68cd.us2a, 9a6eb30d.eu5a, 264afcad.us2a,
  73cc29dd.us1a), 0 on 6.0.0.36. The DB extra has a string schema_cache_timeout. Why 6.1 is stricter
  (cachelib bump? preset cache_helper?) is unverified. No ticket. Contained, not blocking.

## Posted example (2026-09-28, verdict WATCH)
See /tmp/slack_launch_health_msg.txt copy in memory/2026-09-28.md. Style: verdict line, 6.1 build+counts,
6.0 baseline, 7d per-cohort compare with per-ws, 6.1-only issue with short-id/status/containment, method note.

## 10-05 post: verdict WATCH, permalink p1791216716086739. 6.0 line now on 6.0.0.37 (26/2,819).

## Stop condition
If no 6.0.x prod deploys remain → post 'rollout complete' + DM Elizabeth to disable the weekly schedule.
