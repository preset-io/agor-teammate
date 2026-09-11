---
name: gateway-proactive-dm-via-email
description: Elizabeth's directive — send proactive Slack DMs via the Agor gateway (email as target), NOT a Slack bot token; SLACK_BOT_TOKEN_XOXB is not needed for alerts
metadata:
  type: feedback
---

**Elizabeth, 2026-09-11:** "you shouldn't need a Slack bot token. You should be using the gateway." Directive, not a preference — stop treating a missing `SLACK_BOT_TOKEN_XOXB` as a blocker and use the gateway for all proactive Slack sends.

**Why:** the spike-alert skill had stale instructions to curl the Slack Web API with `SLACK_BOT_TOKEN_XOXB` ("Agor Slack gateway is broken for this bot"), which was wrong and left outage alerts undelivered 09-08→09-11 whenever the token was missing from the session env.

**How to apply:** `skills/sentry-spike-alert.md` step 7 now uses `agor_gateway_emit_message`. Any future proactive DM/notify to Elizabeth (or others) goes through the gateway; never gate it on a bot token.

To send a proactive Slack **DM to Elizabeth**, use `agor_gateway_emit_message` with her **email** as the target — this is the reliable path:

```
agor_gateway_emit_message(
  gatewayChannelId="019edd38-92af-73a4-9691-a3a8c55ce4f4",   # the "Soraya" gateway channel
  target="elizabeth@preset.io",
  message="...", purpose="...")
```

Confirmed working 2026-09-11: resolved to a real DM channel (`D0BBR2PPFQ9`), message delivered (permalink returned). `target` also accepts channel IDs, `channel_name:`, `#name`, and `user_email:`/`email:` prefixed emails.

**Why this matters:** earlier runs (09-04, and the 22:00 board sweep note) concluded "the gateway can't open a fresh DM to Elizabeth" after a `provider_request_failed` — but those attempts targeted her by user ID/name. **Targeting by email works.** Don't repeat the "gateway can't DM her, fall back to #eng-reviews" conclusion.

**Corollary — `SLACK_BOT_TOKEN_XOXB` is NOT a hard blocker for alerts.** The Sentry spike-alert skill's queued DMs sat undelivered for days (09-08 → 09-11) because that skill uses a direct bot-token Slack send and the token was missing from the session env. The gateway `emit_message` path sidesteps the token entirely (it uses the gateway channel's own credentials). Prefer the gateway-email path for proactive DMs; only the token-based direct-send path needs `SLACK_BOT_TOKEN_XOXB`.

Elizabeth has stated she does not read the daily-log flags — push anything she needs to know as a gateway DM, not just a log entry. Related: [[project_sentry_mcp_auth_blocked]], the Sentry ingestion quota-exhaustion outage tracked in `memory/sentry-spike-alerts.json`.
