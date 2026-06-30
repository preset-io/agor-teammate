---
name: "#eng-reviews message format"
description: Correct format for posting PRs to #eng-reviews Slack channel
type: feedback
---

Just the bot tag + reviewer request + PR link. No description, no one-liner, no QAgor PASS line.

```
<@U0B0BPQV9SQ> can you find a reviewer for <https://github.com/apache/superset/pull/XXXXX>
```

**Why:** Bot ID `U0B0BPQV9SQ` is Minerva McGonagall (the reviewer assignment bot). The message must be sent AS Sophie (via `mcp__Slack__slack_send_message`) — NOT via the Agor gateway. The gateway sends as the McGonagall Slack app, which means the message appears to come from McGonagall herself rather than Sophie. Do NOT use `|display text` on the URL — the pipe suffix renders literally. Post only after QAgor PASS.

**How to apply:** Use `mcp__Slack__slack_send_message` with `channel_id: C09KSS4NVLL`. Fall back to the gateway only if the Slack MCP is unavailable, and note the sender limitation.
