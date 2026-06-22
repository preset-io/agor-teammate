# Skill: connect-saas

**When to use:** The user wants this assistant connected to an external SaaS/tool/API such as GitHub, Slack, Fellow, HubSpot, Google Drive, a calendar, CRM, or issue tracker.

**Goal:** Find the best maintained connection path and apply it safely in Agor. This is a research method + Agor wrapper, not a hand-maintained SaaS catalog.

## Principles

- Lead with the value the connection unlocks.
- Prefer reusable, approved paths over one-off secrets.
- Ask/apply the user's security stance from `USER.md` when scopes, visibility, or posting are involved.
- Never ask for secrets in chat; use `agor_widgets_request_env_vars`.
- Verify the full chain: public URL → OAuth discovery/DCR → register → enable → attach to current session when needed → authenticate → tools visible → first useful action works → fallback if blocked.
- Be clear about scope words: **catalog/registry** means discoverable connection templates or candidates; **global/workspace MCP** means a reusable server registration in Agor; **session MCP** means attached to this conversation so tools can appear here. “No MCP servers attached” does not mean none exist in the catalog or workspace.

## Research order

1. Existing Agor MCP registration / company-approved connector already available to the user/workspace.
2. MCP server + OAuth / URL discovery.
3. MCP server + Dynamic Client Registration (DCR).
4. Trusted community skill.
5. PAT/API token fallback with exact minimum scopes inline.
6. Manual/export fallback if authentication or admin approval is blocked.

Registry pointers, not a catalog:

- Skills: [skills.sh](https://skills.sh), [SkillsMP](https://skillsmp.com), [github.com/anthropics/skills](https://github.com/anthropics/skills), internal `preset-io/agent-skills`, internal `preset-io/preset-agent-skills`.
- MCP: [registry.modelcontextprotocol.io](https://registry.modelcontextprotocol.io), [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers), [Smithery](https://smithery.ai), [Glama](https://glama.ai), [mcp.so](https://mcp.so), [PulseMCP](https://pulsemcp.com), [awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers).
- Meta-connectors: Zapier MCP, Composio, Pipedream.

## Agor wrapper: full connection chain

1. **Discover Agor tools at runtime.** Search `mcp-servers`, service-specific tools, widgets, and gateway tools as relevant; inspect schemas before execution.
2. **Find the public connection URL.** Prefer a documented remote MCP URL or provider OAuth URL. If there is no public URL, use the best approved connector or API-token path.
3. **Try OAuth discovery.** Register non-secret config first: `name` + public `url` + `auth:{type:"oauth"}` where supported. Let the server advertise metadata/endpoints when possible.
4. **Use DCR when offered.** If discovery indicates Dynamic Client Registration, let Agor create/register a client rather than asking the user for client id/secret.
5. **Register the MCP server in Agor.** This creates a reusable workspace/global config, not necessarily a tool in the current chat.
6. **Enable it.** Disabled registrations may remain visible but should not be treated as usable.
7. **Attach it to the current session when needed.** Do not stop at “registered.” Session attachment is what usually makes tools visible to this assistant turn/session.
8. **Authenticate.** Send the user through OAuth or request env vars via the secure widget only after explaining token type and minimum scopes.
9. **Verify.** Check registration state, enabled state, session attachment, auth state, and available tools. If tools are not visible, refresh/re-prompt or re-check attachment before concluding failure.
10. **Prove value.** Do one small read-only useful action first; require explicit user buy-in before writes/posts.
11. **Record outcome.** File memory/Knowledge if available; never store secret values.
12. **Fallback.** If OAuth/admin/auth is blocked, offer manual/export/API-key alternatives with clear tradeoffs.

## Redirect URI troubleshooting

OAuth failures such as `invalid_request`, `redirect_uri_mismatch`, or “Mismatching redirect URI” usually mean the provider does not allow Agor's exact callback URL.

Guide the user/admin to fix this **on the provider side**:

1. Locate the exact Agor OAuth callback/redirect URI shown by the Agor MCP auth flow or error page.
2. Open the provider's developer/admin settings for the app/client.
3. Add that exact URI to the allowed redirect/callback URI list. Match scheme, host, path, and trailing slash exactly; test/self-hosted Agor URLs are often different from production.
4. Save, reinstall/reauthorize if the provider requires it, then retry authentication.

Example: for Fellow, an admin may need to allowlist the exact Agor callback URL in Fellow's admin/developer settings before `https://fellow.app/mcp` OAuth can complete. If the admin path is unavailable, move to fallback rather than burning time.

## Manual/export fallback pattern

When OAuth, DCR, app review, or admin approval blocks the ideal connector, make fallback a first-class move:

1. State the blocker plainly and name the ideal path still preferred.
2. Offer a bounded fallback that can produce value today without weakening security.
3. Create or point to a small skill/procedure for repeated imports/exports if useful.
4. Disable or pause noisy broken connector attempts when appropriate, and explain whether stale session attachments may still be visible.
5. Keep the door open to return to the ideal connector later.

Worked example: **Fellow manual export**

- Ideal path: Fellow public MCP `https://fellow.app/mcp` with OAuth.
- Common blocker: redirect URI mismatch or Fellow admin settings unavailable.
- Fallback: ask the user to export/copy selected meeting notes, upload/place them in the agreed workbench or Knowledge location, then summarize/extract action items locally. If Fellow Developer API is available, request an API key via secure env var with minimum read scopes instead of raw chat paste.

## Examples

- **GitHub:** Prefer existing GitHub MCP/App/OAuth. PAT fallback should be fine-grained, selected repos only, minimum permissions for the task.
- **Fellow:** Try public MCP `https://fellow.app/mcp` with OAuth. Verify current-session attachment. Watch for redirect URI allowlisting on dev/test hosts. If blocked, use the manual/export fallback pattern.
- **Slack:** Use `skills/connect-slack.md` for Slack-specific decisions, scopes, Socket Mode, event subscriptions, channel invite/ID, and `app_mention` test. Use `skills/agor-gateway-channels.md` for inbound mention gateway setup.
