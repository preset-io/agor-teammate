# SKILL: Slack Interaction

## When to Use
Any time you post to Slack — bug-thread replies in #bug-reporting, #eng-reviews
posts, status updates, or proactive DMs/threads. Read this **before** sending.

> Borrowed from Hodor's Slack guidelines + the `slack-gateway-reply-restraint`
> learning (per Max, 2026-06-18). The complaint that prompted it: agents being
> chatty and piping up on every message. Don't be that bot.

---

## Core Rule: Act Like a Normal Slack User, Not a Bot

- **Be brief.** No walls of text. No wall of consecutive messages. Match the
  channel's casual register. One tight message beats five.
- **In group threads you're just one actor** — every message you post is visible
  to everyone. A non-answer reply is real noise, not a private no-op.
- **Stay silent unless directly addressed** (@-mention or reply) *and* you have
  something genuinely useful to add. When unsure whether you're being addressed,
  default to silence.
- **Lead with the result**, then link to the session/artifact/PR for the "how."
- **Long/complex content goes elsewhere.** File it in the best place (Shortcut,
  GitHub issue/PR, a doc, Knowledge) and **link** to it in a short message.

---

## Outbound vs. Reply

| Situation | Tool |
|-----------|------|
| Reply in an existing thread you were prompted from | reply in that thread, briefly |
| Proactive / self-initiated (new thread, DM, from a schedule/heartbeat) | Agor gateway: `agor_gateway_outbound_targets_list` → `agor_gateway_emit_message` (posts as *you*, supports `<@user>` tags + new threads) |
| Deliberately posting *as the user* / reading their private channels | Slack MCP (borrows user creds — different security profile, rarely needed) |

Don't use Slack MCP for self-initiated posts — it posts as-the-user, which is
wrong for messages you originate (in a schedule it posts as the schedule owner
with a "Sent from Agor" footer).

---

## Gateway-Bound Sessions: Keep the Thread Quiet

When a Slack thread is mapped to a session on this branch (via the "Bug Basher"
gateway channel), **the gateway mirrors every assistant turn of that bound
session into the thread** — reasoning, status narration, "let me look at…", all
of it. This is automatic; it is *not* something the "be brief" rule above can
suppress, because those aren't deliberate sends. A DnD thread once collected ~90
of my narration turns this way (Max, 2026-07-08: "you're prompting from Agor and
it dumps in the thread… should be a child branch/session, disconnect the
callbacks").

**The mirror follows the *bound session*, not where the prompt came from.**
Whatever session is tied to the thread, its turns go to the thread — whether the
prompt arrived from Slack or from the Agor UI.

Rules:

- **Do the work in an unbound child, not the bound session.** When a thread
  routes to me, the thread-facing (orchestrator) session should stay terse. Spin
  up a child branch/session (the normal orchestrator→worker pattern) for the
  actual investigation/fix. Child sessions aren't bound to the thread, so their
  chatter never reaches Slack.
- **The thread gets milestones only:** a short "on it," PR opened, QAgor pass,
  merged, deployed, and any question/blocker for the human. Everything else
  happens in the child.
- **Don't wire worker callbacks to re-post into Slack.** Let completions land in
  the Agor session UI; then I summarize with *one* short thread message. A
  callback that dumps the worker's full result into the thread re-floods it.
- **Follow-ups obey the same rule.** A thread reply routes back to the same bound
  session — answer briefly in-thread, and if it needs real work, delegate to a
  child again. Don't start doing the work inline in the bound session.
- There is currently **no per-channel "final message only" gateway toggle** — the
  only knobs are target branch / agent / blunt enable-off. Keeping the thread
  quiet is a *working-style* discipline, not a setting. (A platform-level
  final-message-only option would need to come from the Agor side.)

---

## Before Sending — Quick Checklist

- [ ] Am I actually being addressed, or just observing? If observing → stay quiet.
- [ ] Can this be one message instead of several? Collapse it.
- [ ] Is the long part better as a link? Move it out, link to it.
- [ ] Leading with the result, not the process?
- [ ] `@here`/`@channel`/`@everyone` only if explicitly warranted — these are high-impact.

## Notes

- For bug-bash thread etiquette specifics (what to post when), see `bug-bash.md`
  and `BOARD.md`.
- #eng-reviews posts have their own format rules — see the
  `feedback_eng_reviews_format` memory (use the bot ID, post only after QAgor PASS).
