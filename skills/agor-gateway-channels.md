# Skill: agor-gateway-channels

**When to use:** The user asks for a messaging channel, or ongoing work creates a concrete need for the teammate to be reachable where the user already works.

**Goal:** Help open an approved inbound channel so users can tag/prompt the teammate where work already happens.

## Model

Gateway channels are incoming-first: they create Agor sessions from external messages/mentions. Do not assume they can proactively post scheduled outbound digests; use an outbound-capable SaaS connector for that.

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
5. Never ask for pasted secrets. For interactive setup, create the channel
   disabled and without secrets, then use `agor_widgets_request_gateway_token`.
   If the widget or permission is unavailable, ask an admin to complete setup
   under **Settings → Gateway Channels**.
6. Verify with a minimal test mention/message, then return the channel/config
   link or ID, explain where the user can review or disable it, and record the
   preference without secrets.
