# Skill: agor-gateway-channels

**When to use:** The user wants the assistant reachable from Slack, GitHub, Teams, or another gateway channel.

**Goal:** Help open an approved inbound channel so users can tag/prompt the assistant where work already happens.

## Model

Gateway channels are incoming-first: they create Agor sessions from external messages/mentions. Do not assume they can proactively post scheduled outbound digests; use an outbound-capable SaaS connector for that.

## Slack conversation semantics

Document and configure Slack gateway channels around this intended model:

- A top-level `@assistant` mention in an allowlisted channel starts a new Agor session on the target branch.
- The assistant replies in the Slack thread for that mention.
- The Slack thread is the session scope: `channel_id + thread_ts` maps to the Agor session, and follow-up thread replies continue that session.
- New top-level mentions create new sessions.
- Random channel messages should be ignored unless the gateway is explicitly configured otherwise.
- Thread replies without another mention may be allowed only inside an existing mapped thread/session.

If current product behavior does not thread replies or map sessions this way, note it as a gateway product issue and keep the skill documentation focused on the intended setup model.

## Tools

Discover schemas at runtime with `agor_search_tools` / `agor_get_tool_details` in the `gateway` domain. Current core tools:

- `agor_gateway_channels_list` — find existing channels and IDs; secrets are redacted.
- `agor_gateway_channels_create` — create a channel definition; current active connectors include Slack, GitHub, and Teams.
- `agor_gateway_channels_update` — update/disable/rotate config; omit redacted secrets or pass `••••••••` to preserve them.

These tools are admin-only. If permission is denied, give the user/admin the exact setup proposal instead of pretending it is done.

## Steps

1. Read `USER.md` for security stance and posting policy.
2. Clarify: service, target branch, run-as Agor user if needed, allowed workspace/repo/channel scope, and whether replies may post or should draft/preview.
3. List existing channels first; reuse/update approved company channels before creating new ones.
4. Create/update with least privilege: require mentions where possible, restrict allowed channel IDs/repos, attach only needed MCP servers to gateway-created sessions.
5. Never ask for pasted secrets. Prefer env/template references where supported; if a secret must be supplied, use the secure env-var widget path or hand off to an admin UI path.
6. Verify with a minimal test mention/message, then return the channel/config link or ID and record the preference without secrets.
