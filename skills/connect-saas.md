# Skill: connect-saas

**When to use:** The user asks to connect an external service, or a concrete task would materially benefit from direct access to one.

**Goal:** Find the best maintained connection path and apply it safely in Agor. This is a research method + Agor wrapper, not a hand-maintained SaaS catalog.

## Principles

- Lead with the value the connection unlocks.
- Recommend one high-leverage source based on the user's goal; do not present a catalog.
- Prefer reusable, approved paths over one-off secrets.
- Offer to configure the connection, while making clear where the user can
  review, change, or disable the same configuration in Agor.
- Ask/apply the user's security stance from `USER.md` when scopes, visibility, or posting are involved.
- Never ask for secrets in chat. Prefer OAuth; otherwise discover and use the
  secure credential widget appropriate to the connection.
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
4. Check authentication status. If a credential is unavoidable, explain its
   type and minimum scope, invoke the appropriate secure flow, then stop while
   the user completes it.
5. Verify tools are visible after refresh/re-prompt if needed.
6. Do the first useful action from live context, usually read/summarize/draft before write/post; authentication alone is not an outcome.
7. If the result has recurring value, offer a specific cadence through Agor's scheduler and agree on scope, output, destination, and how to stop it.
8. Return the connection or settings link when available and explain how the
   user can review, narrow, or disable it.
9. Record outcome in memory/Knowledge if available; never record secrets.

## GitHub remote MCP

GitHub is an exception to the generic remote-OAuth path: its remote MCP server
does not support Dynamic Client Registration. Use an existing working GitHub
MCP, GitHub App, or pre-registered OAuth client when one is already available.
Otherwise use a fine-grained personal access token through the secure env-var
widget. Do not send the user through **Start OAuth Flow** without a configured
GitHub OAuth client ID, and never ask them to paste a token into chat.

1. Establish the GitHub owner, repositories, and actions needed for the user's
   outcome. Reuse an existing working GitHub connection or saved
   `GITHUB_MCP_PAT` when available.
2. Choose the smallest matching connection:
   - For reading, reviewing, or summarizing, use
     `https://api.githubcopilot.com/mcp/readonly` and request read access to
     contents, issues, and pull requests.
   - When the authorized outcome requires GitHub mutations, use
     `https://api.githubcopilot.com/mcp/` and request write access only for the
     required areas. Do not request Actions, Workflows, organization, or
     security permissions unless the task specifically needs them.
3. Build one pre-filled fine-grained-token link using
   `https://github.com/settings/personal-access-tokens/new`. Pre-fill:
   - `name=Agor GitHub MCP`;
   - a short purpose in `description`;
   - `target_name` when the repository owner is known;
   - a finite `expires_in` (normally 90 days, or less when policy requires);
   - the exact permission parameters, such as
     `contents=read&issues=read&pull_requests=read`.

   GitHub cannot pre-select individual repositories through this URL. Tell the
   user to choose **Only select repositories** and select the repositories they
   want available. Keep the explanation and link in the same message as the
   secure widget so the user can generate, copy, and submit the token in one
   pass.
4. Invoke `agor_widgets_request_env_vars` and then end the turn. Use:

   ```json
   {
     "names": ["GITHUB_MCP_PAT"],
     "reason": "Connect the GitHub repositories you selected.",
     "variable_metadata": {
       "GITHUB_MCP_PAT": {
         "description": "Fine-grained GitHub token for the repositories you selected.",
         "placeholder": "github_pat_…",
         "format_hint": "Create it with the GitHub link above.",
         "input_type": "password"
       }
     },
     "auto_resume": true
   }
   ```

   The user chooses global or session scope in the widget. Do not override that
   choice or repeat the request immediately if they dismiss it.
5. After the widget resumes the session, find or create the GitHub MCP server
   with bearer authentication. Keep the credential as a template, never a raw
   value:

   ```json
   {
     "name": "github",
     "displayName": "GitHub",
     "transport": "http",
     "url": "https://api.githubcopilot.com/mcp/",
     "auth": {
       "type": "bearer",
       "token": "{{ user.env.GITHUB_MCP_PAT }}"
     },
     "scope": "global",
     "enabled": true
   }
   ```

   Substitute the read-only URL chosen in step 2 when appropriate. If a GitHub
   server already exists with broken OAuth, update it to bearer authentication
   instead of creating a duplicate. For a session-scoped server, attach it to
   the current session.
6. Verify the server is enabled and effective, then perform one harmless live
   GitHub read against an authorized repository. If the organization requires
   approval or SSO, explain that specific blocker instead of restarting OAuth.
   After verification, continue directly to the useful GitHub outcome that
   motivated the connection.

## Examples

- **GitHub:** Follow the provider-specific remote MCP procedure above; do not attempt DCR.
- **Fellow:** Try public MCP `https://fellow.app/mcp` with OAuth. Verify current-session attachment. Watch for redirect URI allowlisting on dev/test hosts.
- **Slack:** Prefer an existing company Slack app/MCP if available. Proactive posts require an outbound-capable Slack connector and explicit posting policy.
