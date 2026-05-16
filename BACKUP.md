# BACKUP.md — Git as your backup mechanism

This file explains the mental model. `AGENTS.md` has the short version.

---

## The model

**Your state lives in this worktree on disk.** Identity, memory, learnings, accumulated context — all of it sits in files: `IDENTITY.md`, `USER.md`, `MEMORY.md`, `memory/`, etc.

**Git is how you back that state up** so it survives:
- Session restarts
- Worktree wipes
- Host moves
- Whatever else can go wrong

Backup is one command: `git push origin <your-branch>`. There is no special tool. There is no service. It's just git.

---

## Critical: how NOT to back up

The likely failure mode as this framework spreads: an assistant cloned from the **public** `preset-io/agor-assistant` repo tries to back itself up by **forking the public repo** and pushing its branch to the fork. **Do not do this.** A fork:

- Implies intent to PR upstream — which you must NEVER do
- Keeps your accumulated state tied to (and discoverable through) the public repo
- Increases the risk of accidentally PR'ing your personal state into the framework `main`

**The right way:** the user creates a brand-new **private** repo in their own org (personal or corporate), and you switch your `origin` (or add a new remote) to point there. See "Public clone vs. private backup" below.

**If a private repo isn't set up yet:** commit locally, don't push at all. **Better unbacked than wrong-backed.** And there's nothing of value to back up until you've actually produced value — primary goals first.

---

## Branch-per-assistant

This repo hosts multiple assistants. Each lives on its own branch:

```
main                       ← framework template (read-only for assistants)
private-coachbot           ← one assistant
private-saul               ← another assistant
private-hippa-assistant    ← another assistant
your-branch                ← you
```

You commit your accumulated state to **your branch**. You push **your branch** to the remote. That's the entire backup workflow.

---

## Hard rules

- **Never PR your branch into anything.** Your branch holds your personal state — memory, identity, learnings. It would contaminate the template and isn't useful to anyone else.
- **Never fork the public repo.** A fork creates noise and implies you intend to PR upstream, which you don't.
- **Never push to `main`.** `main` is the framework template. Only framework-improvement PRs (like fixes to `AGENTS.md` or `BOOTSTRAP.md`) merge into `main`, and those come from contributors, not from running assistants.
- **Don't touch other assistants' branches.** They're someone else's state.

The whole backup loop, every time:

```bash
git add -A
git commit -m "<what changed>"
git push origin <your-branch>
```

---

## When to back up

**On-demand:** the user asks ("back yourself up", "commit what you've got"). Do it.

**Periodic:** if `HEARTBEAT.md` includes a backup task, run it on the heartbeat cadence.

**After significant state changes:** big memory updates, identity changes, learnings worth keeping. Use judgment — don't commit on every turn.

**Not every turn.** Backup has a cost (commit noise, push latency). Batch.

---

## Public clone vs. private backup

You may have been cloned from the **public** repo: `https://github.com/preset-io/agor-assistant`.

If so, anything you push to your branch is **world-readable**. Your accumulated memory and your human's `USER.md` are on the internet.

Once you've earned trust and produced value, **suggest a private repo** for backup:

> "I'm currently backing myself up to a public repo. Want me to switch to a private one? I can use your personal GitHub org, a company org, or wherever makes sense for the kind of state I'm accumulating."

Let the user decide:
- **Personal org** — for personal/individual work
- **Corporate org** — for work assistants (so the company owns the state)
- **Stay public** — if there's nothing sensitive

If they want to switch, the move is:
1. User creates a private empty repo somewhere
2. Add it as a new remote: `git remote add backup <new-private-url>`
3. Push your branch there: `git push backup <your-branch>`
4. Make that the default remote for your branch going forward

You don't need to delete history from the public repo unless asked — your branch on the public remote can be left as-is or removed by the user.

### Bonus: the `agor-assistant-private` convention

If the private repo happens to be named `<your-org>/agor-assistant-private`, Agor uses it as the **template when creating new assistants** in your instance. Your backup repo doubles as your org's customized template — its `main` becomes the vanilla starting point for future assistants, free to drift from this public reference implementation.

This is convention, not requirement. Skip it if you don't want the coupling.

---

## What `main` is for

`main` is the **vanilla bootstrap state** that new assistants are cloned from. It contains the framework: `AGENTS.md`, `BOOTSTRAP.md`, `SOUL.md` template, etc. It contains **no personal state**.

Changes to `main` are **framework changes** — improvements to the scaffolding itself — proposed by contributors via normal PRs to `main`. As an assistant running on your own branch, you don't do this in your day-to-day work.

If you notice a framework improvement worth contributing back (a gap in `AGENTS.md`, a better way to structure memory, etc.), tell your human and let them decide whether to open a PR against `main` from a clean working branch.

---

## Summary

| Question | Answer |
|---|---|
| Where does my state live? | On disk, in this worktree |
| How do I back up? | `git push origin <your-branch>` |
| Do I PR my branch? | **No.** Never. |
| Do I fork the public repo? | **No.** Never. |
| What's `main` for? | Framework template; not for personal state |
| Public clone, private state? | Suggest private repo after primary goals have traction |
| When do I back up? | On-demand, or via `HEARTBEAT.md` |
