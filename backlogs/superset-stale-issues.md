# Backlog: Superset Stale Issues

**Repo:** apache/superset
**Board:** RepoBot3000 (`a97875fe-34de-4f37-9e43-85c03de86d20`)
**Board URL:** https://agor.sandbox.preset.zone/ui/b/repobot3000
**Trigger ID:** `trig_01KQyhBijDPpDWqWnPVUrbpF`
**Schedule:** Daily at 9:00 UTC
**Batch size:** 10 oldest open issues (by `updated_at` ascending)

---

## Purpose

Work through the long tail of open issues that haven't been touched in a while.
The goal is to either close noise, surface still-valid bugs, or nudge things forward.
Evan reviews every proposed action before it goes live.

---

## What the scheduled agent does each run

1. Fetch the 10 oldest open issues from `apache/superset` (by `updated_at` ascending)
2. Skip any issue already tracked on the board (check card titles for issue numbers)
3. For each new issue, do a deep read: body, all comments, linked PRs, related issues
4. Assess relevance and propose an action (see below)
5. Create a card on the board in the appropriate zone
6. Do NOT post any comment or close any issue — Evan approves all actions first

---

## Assessment criteria

### Still relevant?

Ask:
- Does this describe a bug or missing feature that likely still exists in current Superset?
- Has it been fixed by a merged PR (search for keywords in merged PRs)?
- Is there an open PR addressing it? Link it.
- Is the reported version ancient enough that the behavior may have changed?
- Did the reporter go quiet / never responded to requests for info?

### Proposed actions (pick the best fit)

| Zone on board | When to use |
|---|---|
| **Propose: Close (stale)** | Reporter never responded to requests, issue is >1yr old with no traction, or clearly fixed |
| **Propose: Close (duplicate)** | Another open issue covers the same thing — link it |
| **Propose: Comment (nudge)** | Still relevant, just needs a nudge — ask if still reproducible on latest version, or offer a workaround |
| **Propose: Comment (help)** | You can provide useful context, link to related code, or point to a workaround |
| **Propose: Comment (needs-info)** | Issue is incomplete — need repro steps, version, logs, etc. |
| **Propose: PR** | Bug is small/clear, no open PR exists, good candidate for a fix — describe the fix |
| **Keep: Valid + Active** | Issue is actively being worked on or has recent meaningful traction — leave it alone |

---

## Card format

Each card should contain:

```
## Issue
#[number]: [title]
[url]
Created: [date] | Last updated: [date]
Labels: [labels]

## Assessment
[2-4 sentences: what the issue is about, current status, why you're recommending this action]

## Proposed action
[Zone name] — [specific proposed comment text OR close reason OR PR description]

## Links
- Related issues: [if any]
- Linked PRs: [if any — open or merged]
```

---

## Rules

- Never post a comment or close an issue without Evan's approval
- If `cares:preset` label is present, flag it prominently in the assessment
- If there's an open PR linked, do NOT propose closing — propose commenting to nudge the PR instead
- If the issue is a feature request (not a bug), note that and be more conservative about closing
- If unsure, land in **Propose: Comment (nudge)** rather than close

---

## Out of scope for this backlog

- Issues created in the last 60 days
- Issues with `validation:required` label (need a committer to validate first)
- Pull requests (separate backlog)
- Dependabot PRs (separate backlog)
