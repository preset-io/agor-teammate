# Skill: connect-saas

**When to use:** The user wants this assistant connected to an external SaaS/tool/API such as GitHub, Slack, Fellow, HubSpot, Google Drive, a calendar, CRM, or issue tracker.

**Goal:** Find the best maintained connection path and apply it safely in Agor. This is a research method + Agor wrapper, not a hand-maintained SaaS catalog.

## Principles

- Lead with the value the connection unlocks.
- Prefer reusable, approved paths over one-off secrets.
- Ask/apply the user's security stance from `USER.md` when scopes, visibility, or posting are involved.
- Never ask for secrets in chat; use `agor_widgets_request_env_vars`.
- Verify: registered → enabled → attached to current session when needed → authenticated → tools visible → first useful action works.

## Research order

1. Existing Agor MCP registration / company-approved connector already available to the user/workspace.
2. MCP server + OAuth / URL discovery.
3. MCP server + Dynamic Client Registration (DCR).
4. Trusted community skill.
5. PAT/API token fallback with exact minimum scopes inline.

Registry pointers, not a catalog:

- Skills: [skills.sh](https://skills.sh), [SkillsMP](https://skillsmp.com), [github.com/anthropics/skills](https://github.com/anthropics/skills), internal `preset-io/agent-skills`, internal `preset-io/preset-agent-skills`.
- MCP: [registry.modelcontextprotocol.io](https://registry.modelcontextprotocol.io), [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers), [Smithery](https://smithery.ai), [Glama](https://glama.ai), [mcp.so](https://mcp.so), [PulseMCP](https://pulsemcp.com), [awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers).
- Meta-connectors: Zapier MCP, Composio, Pipedream.

## Agor wrapper

1. Discover exact Agor tool schemas at runtime (`mcp-servers`, service-specific tools, widgets).
2. Find or create the non-secret config. For remote OAuth, start simple: `name` + public `url` + `auth:{type:"oauth"}`; add client/endpoints only if discovery/DCR fails.
3. If session-scoped, attach it to the **current session**; don't stop at “registered.”
4. Check auth status. If a token is unavoidable, explain token type + minimum scopes, call `agor_widgets_request_env_vars`, then stop.
5. Verify tools are visible after refresh/re-prompt if needed.
6. Do the first useful action, usually read/summarize/draft before write/post.
7. Record outcome in memory/Knowledge if available; never record secrets.

## Examples

- **GitHub:** Prefer existing GitHub MCP/App/OAuth. PAT fallback should be fine-grained, selected repos only, minimum permissions for the task.
- **Fellow:** Try public MCP `https://fellow.app/mcp` with OAuth. Verify current-session attachment. Watch for redirect URI allowlisting on dev/test hosts.
- **Slack:** Prefer an existing company Slack app/MCP if available. Proactive posts require an outbound-capable Slack connector and explicit posting policy.
