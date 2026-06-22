# Skill: connect-slack

**When to use:** The user wants Slack connected to an assistant, either as a Slack MCP/tool connector or as an Agor gateway channel where people can mention the assistant.

**Goal:** Guide Slack setup without opening a token widget too early. First choose ownership and app path; only request secrets after the user/admin understands prerequisites, scopes, and test criteria.

## Start with the decision

Before asking for tokens, present these options and ask which applies:

1. **Reuse an existing Slack app** — best when the company already has an approved Agor/assistant bot. Needs a Slack app admin who can confirm scopes, Socket Mode, event subscriptions, and install/reinstall.
2. **Create a new Slack app** — best for a pilot or isolated workspace/channel. Needs permission to create/install Slack apps and to generate bot/app tokens.
3. **Invite a workspace admin** — best when the user lacks Slack admin/app permissions. Give the admin the exact checklist below; do not ask the user to paste secrets.

Clarify who owns the connector:

- **Private/user-owned:** tokens live in the user's env vars; other users may need their own setup.
- **Shared/admin-owned:** a workspace/admin service identity owns the Slack app/tokens and gateway config; better for teams.
- **Gateway config is not the same as secrets:** channel ID, target branch, mention policy, and session mapping may be shared; token values must stay out of chat/logs/docs.

## Prerequisites checklist

- Slack workspace where the app can be installed.
- App admin or workspace admin available if the user cannot manage apps.
- Target Agor branch/session behavior selected: which assistant/branch receives Slack mentions.
- Target channel chosen; for private channels, the bot must be invited and private-channel scopes are required.
- Posting policy from `USER.md`: read/draft only vs allowed to post replies in Slack.

## Slack app requirements

For Slack gateway/Socket Mode setup, verify or configure:

1. **Socket Mode enabled.**
2. **App-level token** with `connections:write` (`xapp-...`).
3. **Bot token** (`xoxb-...`) after installing/reinstalling the app.
4. **Bot OAuth scopes** minimum typical set:
   - Public channels: `app_mentions:read`, `channels:read`, `channels:history`, `chat:write`, `users:read`.
   - Private channels: also include `groups:read` and `groups:history` (or the specific `groups:*` scopes the gateway requires).
   - Add broader scopes only when justified by the requested workflow.
5. **Event subscriptions:** subscribe the bot to `app_mention`.
6. **Install/reinstall** the app after scope/event changes.
7. **Invite the bot** to the target channel, especially private channels.
8. **Find the channel ID** (for example `C...`), not just the display name.

## Secret handling

Only after the checklist is understood and the user/admin agrees to proceed:

- Request env vars with `agor_widgets_request_env_vars`; never ask for raw tokens in chat.
- Typical names: `SLACK_BOT_TOKEN` for `xoxb-...`, `SLACK_APP_TOKEN` for `xapp-...`.
- Include required scopes in the widget reason or surrounding explanation.
- Stop after opening the widget; resume by verifying presence without printing values.

## Agor gateway configuration

Use `skills/agor-gateway-channels.md` for the Agor-side gateway steps. For Slack, the intended model is:

- Top-level `@assistant` mention in an allowed channel starts a new Agor session.
- Replies from the assistant should go in the Slack thread.
- The Slack thread is the conversation/session scope; follow-up thread replies continue the same Agor session.
- Random channel messages are ignored unless the gateway policy explicitly allows them.

## Verification

Run a minimal test before declaring success:

1. Confirm gateway/channel is enabled and restricted to the intended channel ID.
2. In Slack, post a top-level `@assistant` mention with a harmless prompt.
3. Confirm Agor creates/routes a session on the target branch.
4. Confirm the assistant reply appears in-thread and future thread replies stay in the same session.
5. If the reply is not threaded, note it as a gateway product issue; do not try to fix product behavior in this skill.

## If blocked

- No Slack admin/app permission → ask the user to invite an admin and provide the checklist.
- Bot cannot see a channel → invite the bot; for private channels confirm `groups:*` scopes and reinstall.
- Tokens unavailable → pause Slack setup; offer a non-Slack first-value path (e.g. GitHub/Knowledge digest) while waiting.
- OAuth/MCP path unavailable → use gateway setup if the ask is inbound mentions; use an outbound Slack connector only if proactive posting is required.
