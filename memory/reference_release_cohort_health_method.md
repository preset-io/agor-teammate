# Release cohort health method (Superset 6.1 vs 6.0 weekly)

_Created 2026-09-28 (prompt referenced this file for 7 runs before it existed)._

## CRITICAL: don't use `release:<release_name>` for app-error counts
Sentry's data scrubber replaces the `release` tag with `REDACTED: Message may have contained an email address`
on ~95% of `superset-python` production events, because `superset@6.1.0.8.<sha>-<sha>` matches an email regex.
(2026-09-28: 119k of 126.5k prod superset-python errors/7d had a REDACTED release.) The events that keep
their release are mostly websocket-client noise (VVE/A9F/VVF/VVG). Release-scoped counts from 08-31..09-21
therefore measured ~only websocket noise, and 6.1.0.8's release-scoped events were all `environment:staging`.
Long-term fix (not ours to make read-only): scrubber safe-field for `release`, or a release format without `@`.

## Method that works: attribute by pod prefix
1. Birds sweep (subagent): list_preset_deployments(production) → get_deployment each. Use get_deployment's
   `workspace_count` and `app_versions.release_name`; list_preset_deployments returns 0 ws / null versions.
   Keep `slug` too: every pod is named `ws--<slug>--main-...` (k8s_namespace `ws--<slug>--main`).
2. Sentry Discover events, dataset=errors, project=-1, statsPeriod=7d, `environment:production
   server_name:[ws--<slug1>--*,ws--<slug2>--*,...]` (list+wildcard syntax works; verified sum == per-slug sum).
3. Group by `issue` (not `title`: 502 handshake titles fragment per timestamp). For each code-shaped
   top issue on 6.1, count it on the 6.0 slug list too. 6.1-only / disproportionate → localize by
   server_name + transaction + url host (workspace) before calling it a regression (7NR lesson).
4. Normalize per workspace, but websocket noise is per-pod, not per-tenant, so compute both and
   caveat.
5. Helpers: /tmp/sq.sh-style curl wrapper (fields..., sort=-count()).

## Posting
`SLACK_BOT_TOKEN_XOXB` has been absent every run since 09-14. Post via `agor_gateway_emit_message`,
gatewayChannelId `019edd38-92af-73a4-9691-a3a8c55ce4f4`, target `channel:C017U4N8RJP`. Worked 2026-09-28.
