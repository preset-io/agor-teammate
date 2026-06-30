---
name: "#eng-reviews message format"
description: Correct format for posting PRs to #eng-reviews Slack channel
type: feedback
---

Just the bot tag + reviewer request + PR link. No description, no one-liner, no QAgor PASS line.

```
<@U0B0BPQV9SQ> can you find a reviewer for <https://github.com/apache/superset/pull/XXXXX>
```

**Why:** Bot ID `U0B0BPQV9SQ` triggers reviewer assignment. Do NOT include the display name (e.g. `|Agor Code Review Bot`) — the bot's display name changes and using it can break the mention. Do NOT use `|display text` on the URL — the pipe suffix renders literally instead of as a hyperlink. Post only after QAgor PASS.

**How to apply:** Channel ID `C09KSS4NVLL`.
