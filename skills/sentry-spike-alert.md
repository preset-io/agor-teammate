# Skill: Sentry New-Error Spike Alert (daily)

Detect **new or escalating high-volume** Sentry errors and DM Elizabeth when something novel is driving volume. This is a *monitoring/notification* job — it never fixes anything and never resolves/ignores issues. It exists so a sudden spike (e.g. the error dashboard "doubling") gets surfaced the same day instead of waiting for the weekly health-dashboard refresh.

Complements, does not replace:
- **Daily Sentry error burndown** (8am) — picks ONE code-fixable issue to fix. Runs *after* this alert (7am) so a fresh spike is on the radar before it picks.
- **Weekly SRE health dashboard refresh** (Fri) — trend snapshot, not real-time.

## Quiet by default

Only ping when there is something genuinely **new** to report. A run that finds nothing above threshold (or only already-alerted issues) writes a one-line memory note and sends **no** Slack message. No alert fatigue.

## State file — `memory/sentry-spike-alerts.json`

De-dup ledger so the same issue isn't paged day after day. Shape:

```json
{
  "acknowledged_baseline": ["SUPERSET-PYTHON-12EZ"],
  "alerted": {
    "SUPERSET-PYTHON-158W": { "first_alerted": "2026-08-07", "peak_events_24h": 523, "note": "fsspec ImportError" }
  }
}
```

- `acknowledged_baseline` — chronic high-volume issues Elizabeth already knows about; never alert on these unless volume grows ≥3× the last recorded peak.
- `alerted` — issues already paged. Re-alert only if 24h volume grew **≥2×** since `peak_events_24h` (a real re-escalation), and update the peak.

## Procedure

1. **Read state** — load `memory/sentry-spike-alerts.json` (create from the template above if missing). Also skim the last ~3 days of `memory/` daily logs and open burndown PRs (`gh pr list --author @me`) — an issue already in flight is not "news."

2. **Pull candidates** (org `preset-inc`, region `https://us.sentry.io`). Three lenses, union the results:
   - **New**: `search_issues` with `is:unresolved firstSeen:-3d`, sort `freq`, limit 25.
   - **Escalating**: `search_issues` with `is:unresolved is:escalating`, sort `freq`, limit 25.
   - **Org-wide volume delta** (directly catches "the dashboard doubled"): `search_events` dataset `errors`, `is:unresolved`, `count()`, for `period:24h` vs the prior 24h (query the 48h and 24h windows and subtract). If today's 24h total is **≥1.5×** yesterday's, that's a reportable spike even when spread across many issues — identify the top issues driving the delta.

3. **Threshold — flag an issue if ANY of:**
   - New (firstSeen ≤ 72h) **and** ≥ 100 events, **or**
   - `is:escalating` **and** ≥ 500 events in the trailing 24h, **or**
   - it's a top contributor to a ≥1.5× org-wide 24h volume jump.

4. **De-dup** — drop anything in `acknowledged_baseline` (unless ≥3× its peak) or already in `alerted` (unless ≥2× its recorded peak). Drop issues already being fixed by an open burndown PR.

5. **Classify, don't filter** — for each surviving issue, tag it **code-shaped** vs **infra-noise** using the skip-list in `skills/sentry-error-burndown.md` (websocket/502, SIGKILL/TimeLimitExceeded, SSL cert mismatches, psycopg2/Redis drops, customer-DB config errors, thumbnail/screenshot timeouts). A doubling can be infra-driven, so report both — just label them. Note the affected workspace(s) when the volume is concentrated in one (often a customer self-inflicted config/template issue, not our bug).

6. **If nothing survives** → append a one-line note to today's `memory/YYYY-MM-DD.md` ("Sentry spike check: nothing new above threshold") and STOP. No Slack.

7. **If something survives → DM Elizabeth on Slack.** Look up her IM channel by email, then post (Agor Slack gateway is broken for this bot — use curl with `SLACK_BOT_TOKEN_XOXB`):
   ```bash
   UID=$(curl -s "https://slack.com/api/users.lookupByEmail?email=elizabeth@preset.io" \
     -H "Authorization: Bearer $SLACK_BOT_TOKEN_XOXB" | python3 -c 'import sys,json;print(json.load(sys.stdin)["user"]["id"])')
   # build payload.json via python json.dump; channel = $UID (Slack opens the IM automatically)
   curl -s -X POST "https://slack.com/api/chat.postMessage" \
     -H "Authorization: Bearer $SLACK_BOT_TOKEN_XOXB" \
     -H "Content-Type: application/json; charset=utf-8" \
     --data-binary @payload.json
   ```
   Verify the response has `"ok":true`. Message format (Slack mrkdwn):
   ```
   :rotating_light: *New Sentry volume* — <N> issue(s) worth a look

   :fire: *<ISSUE-ID>* — <title> [code-shaped | infra-noise]
   • <events> events / <users> users, first seen <when>, culprit `<culprit>`
   • workspace <id> (if concentrated) · <link>

   (repeat per issue; if triggered by an org-wide jump, lead with:
   ":chart_with_upwards_trend: Org 24h errors <today> vs <yesterday> (<multiplier>×)")
   ```

8. **Update state** — add each newly-alerted issue to `alerted` with today's date + its 24h peak; bump peaks for re-escalations. Write `memory/sentry-spike-alerts.json` and commit it (`log:` prefix, mirroring the workspace convention).

9. **Log** — append to today's `memory/YYYY-MM-DD.md`: what was flagged, what was suppressed as already-known, and the Slack `ts` if a message was sent.

## Guardrails

- Never resolve/ignore/assign Sentry issues — read-only.
- Never open a PR or fix code from this run — that's the burndown's job. If a flagged issue is clearly code-fixable, just say so in the DM so Elizabeth (or the next burndown) can pick it up.
- Don't page on issues already in `acknowledged_baseline` / `alerted` unless they cross the re-escalation multipliers. When in doubt, stay quiet — this is a low-noise alert.
