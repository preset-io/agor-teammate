---
name: "#eng-reviews message format"
description: Correct format for posting PRs to #eng-reviews Slack channel
type: feedback
---

Just the bot tag + reviewer request + PR link. No description, no one-liner, no QAgor PASS line.

```
<@U0B0BPQV9SQ|Agor Code Review Bot> can you find a reviewer for <https://github.com/apache/superset/pull/XXXXX|apache/superset#XXXXX>
```

**Why:** Bot ID `U0B0BPQV9SQ` triggers reviewer assignment. The description is noise — just ask for a reviewer. Use the bot ID, NOT plain text "@Agor Code Review Bot". Post only after QAgor PASS.

**How to apply:** Channel ID `C09KSS4NVLL`.
