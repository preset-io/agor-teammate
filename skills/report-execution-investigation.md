# Skill: Report/Alert Execution Investigation (Datadog)

**When to use:** Elizabeth (or an alert) flags a specific scheduled report/alert execution — e.g. "check on this report run for workspace X" or a Datadog monitor fires for a slow/failed report. Goal is to answer 3 questions about that one execution:

1. Did it render everything (all chart/tile slots filled)?
2. How long did it take?
3. Did it succeed?

---

## Prerequisites

- Datadog Log Explorer access (UI) or `DD_API_KEY` + `DD_APP_KEY` (API) — see [[skills/datadog/SKILL.md]] for auth/query basics.
- The workspace short-id(s) (e.g. `26f1fa3e`) — if given a workspace name instead, resolve via `mcp__Birds__get_workspace_by_name` first.

---

## Steps

### 1. Find the execution and get its `execution_id`

Search logs scoped to the workspace(s), in the time window around when the alert/report was expected to run, for the start-of-execution log line:

```
@workspace:(<workspace_id_1> OR <workspace_id_2> ...) "report_execution_start"
```

or search more loosely for `"Report execution"` if you don't yet know the exact event name. Each matching log line contains an `execution_id=<uuid>` (or `execution_id: <uuid>` in the human-readable summary line).

### 2. Pull every log for that execution_id

Re-query scoped by workspace + the exact execution id, quoted so it isn't tokenized:

```
@workspace:(<workspace_id_1> OR <workspace_id_2> ...) "execution_id=<uuid>"
```

Sort ascending by time (or read the table bottom-up) to reconstruct the timeline. Expect roughly this sequence of event types (from `superset`'s report/alert executor), all sharing the same `execution_id`:

| Event | Key fields | What it tells you |
|---|---|---|
| `report_execution_start` | `total_budget_seconds`, `expected_holders`, `report_schedule_id`, `dashboard_id` | Run kicked off; the time budget (timeout) and how many chart "holders" (slots) it expects to fill |
| `Large dashboard detected` (only for big dashboards) | `expected_charts`, `mounted_chart_containers`, `effective_chart_count`, `height_px` | Chart count sanity check before capture |
| `report_readiness_tile` (repeats as tiles come in) | `expected_holders`, `mounted_holders`, `ready_holders` | Polling progress — watch these three numbers converge |
| `report_readiness_ready` | `expected_holders`, `mounted_holders`, `ready_holders` | Terminal readiness check — **all three should be equal** |
| `report_capture_complete` | `elapsed_seconds` | Screenshot/PDF capture finished; this is the render time |
| `report_delivery_start` / `report_delivery_complete` | `recipient_type` | Delivery to email/Slack/etc. started and finished |
| `Report sent to email` / similar | `notification_type`, `notification_source` | Confirms outbound delivery per recipient |
| `report_execution_terminal` | `state=Success\|Failure`, `report_schedule_id` | **Final verdict for the run** |
| Human-readable summary: `"Report execution ... completed in <N>s"` | — | Fastest way to answer "how much time did it take" — total wall-clock for the whole execution |

### 3. Answer the three questions

- **Rendered everything?** Compare `expected_holders` vs `mounted_holders` vs `ready_holders` on the `report_readiness_ready` line (and `expected_charts` vs `mounted_chart_containers`/`effective_chart_count` on the "Large dashboard detected" line, if present). All equal = every chart/tile slot filled. If `ready_holders < expected_holders` at the terminal readiness check, some charts likely rendered blank/timed out.
  - **Caveat — single-chart (Explore) captures:** this holders check only means something for *dashboard* captures (`dashboard_id` set, `chart_id=None`). For a single-chart capture (`chart_id=<id>`, `dashboard_id=None`, `expected_holders=1`), `mounted_holders`/`ready_holders` frequently stay `0` on `report_readiness_ready` even for a fully successful run — don't treat that as a rendering failure. For chart-level executions, trust `report_execution_terminal.state` instead of the holders numbers.
- **How much time?** Use the `"completed in <N>s"` summary line, or compute `report_execution_terminal.timestamp - report_execution_start.timestamp`. Compare against `total_budget_seconds` from the start event to see how much margin there was.
- **Succeeded?** `report_execution_terminal` → `state=Success` (or `Error`). Also confirm a delivery-complete + "sent to X" log exists per recipient — a `Success` state with no delivery log is worth flagging separately. Common real `state=Error` causes seen in practice:
  - `terminal_reason=ReportScheduleScreenshotFailedError` (often preceded by a `report_capture_terminal` line with `terminal_reason=TimeoutError`) — dashboard screenshot capture timed out/failed, typically on large multi-chart dashboards.
  - `terminal_reason=Failed generating csv HTTP Error <code>: <reason>` — the underlying chart query/export failed upstream.
  - `terminal_reason=Notification sent with error` — delivery-side failure (can appear alongside a generation-failure terminal line for the same `execution_id`; two `report_execution_terminal` lines for one execution is a sign of a failure during delivery, not a data artifact).

### 4. Report back concisely

State the three answers directly, e.g.:
> Execution `03f93709-...` for workspace `26f1fa3e` (report_schedule_id=3, dashboard_id=21): rendered all 10/10 charts, took 33.11s (well under the 900s budget), delivered successfully via email. State=Success.

---

## Notes

- Datadog free-text terms need to be quoted (`"execution_id=<uuid>"`) so the UUID isn't split on hyphens by the tokenizer.
- **Quote full tokens, not partial words.** `report_execution_start` is one underscore-joined token to the log tokenizer — searching the quoted partial phrase `"report_execution"` (without `_start`) matches nothing, even though it looks like a substring. Always search the complete token: `"report_execution_start"`, `"report_execution_terminal"`, `"capture_kind=report"`, `"execution_id"`, etc.
- If you only have a workspace *name*, not the short-id, resolve it first — `@workspace:` filters are keyed on the short-id (e.g. `26f1fa3e`), not the display name.
- Multiple workspace ids can be OR'd in one `@workspace:(...)` clause if you're unsure which one owns the schedule.
- This pattern generalizes to alerts too — alert executions emit the same `report_execution_*`/`report_readiness_*`/`report_delivery_*`/`report_execution_terminal` event family with `capture_kind=alert` instead of `capture_kind=report`. Alert schedules typically fire far more often (evaluated on a tight cadence) and mostly terminate `state=Not triggered` (condition not met, expected/normal) or `state=On Grace` (condition met but inside a grace period, also normal) — don't confuse this high-frequency alert-evaluation noise with report executions. Filter by `"capture_kind=report"` to isolate actual report runs from alert-condition checks when scoping a digest.
- A workspace with **zero** `execution_id`/`report_execution_start` logs isn't necessarily broken — check how long that's been true (7d lookback) before treating it as a finding. If a workspace was only recently switched onto this event-logging format, an early "no data" period is expected, not a signal.

## Multi-workspace daily digest mode

When running this as a recurring check across a *watchlist* of workspaces (vs. investigating one specific execution):

1. For each workspace, query `@workspace:<id> "capture_kind=report"` over the digest window (e.g. `now-24h`) to pull every report-execution log line, then group by `execution_id` (regex `execution_id=([0-9a-f-]{36})`) and extract the terminal state per execution — same fields as above.
   - **Gotcha (observed 2026-08-15):** `capture_kind=report` does not cleanly isolate report deliveries from alert-condition-check noise — Alert-type schedules that route through the same capture pipeline still tag their terminal line `capture_kind=report`, with `state=Not triggered` or `state=On Grace` (the same "normal, not a report run" states the top-level note above associates with `capture_kind=alert`). On two watchlist workspaces these outnumbered real report runs 10:1+. Filter to `state in (Success, Error)` to count only actual report executions for the digest; don't trust the `capture_kind` tag alone.
2. Keep the digest **lightweight for workspaces with nothing to report** — a zero-execution workspace gets one line, not a paragraph. Reserve detail (schedule id, error reason, timing) for workspaces that actually had an error or an anomaly.
3. Don't flag "no activity" as inherently suspicious once you've confirmed it's an expected/quiet workspace (see note above on recently-onboarded logging) — a one-line "no activity" mention is enough; only escalate the tone if a workspace that's normally active suddenly goes silent.

**Related skills:** [[skills/datadog/SKILL.md]] (general Datadog query/auth patterns)
