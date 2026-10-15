# BACKUP.md — Git as your backup mechanism

This file explains the mental model. `AGENTS.md` has the short version.

---

## The model

**Your teammate home/base lives in this branch on disk.** Identity/boot/safety files, repo-native config, executable skills, local data, and framework instructions sit in files such as `IDENTITY.md`, `USER.md`, `AGENTS.md`, and `KNOWLEDGE.md`.

**Agor Knowledge is the primary home for memory, learnings, docs, plans, decisions, and shareable artifacts.** Git backup does not replace Knowledge memory.

**Git is how you back up the teammate home/base** so it survives:
- Session restarts
- Branch wipes
- Host moves
- Whatever else can go wrong

Backup is one command for teammate home/base files: `git push backup <your-branch>`, only to a verified private repo (see "Public clone vs. private backup"). Knowledge docs are managed through Agor Knowledge tools, not by pushing this branch.

---

## Critical: how NOT to back up

The likely failure mode as this framework spreads: a teammate cloned from the **public** `preset-io/agor-teammate` repo tries to back itself up by **forking the public repo** and pushing its branch to the fork. **Do not do this.** A fork:

- Implies intent to PR upstream — which you must NEVER do
- Keeps your accumulated state tied to (and discoverable through) the public repo
- Increases the risk of accidentally PR'ing your personal state into the framework `main`

**The right way:** the user creates a brand-new **private** repo in their own org (personal or corporate), and you add it as a `backup` remote. See "Public clone vs. private backup" below.

**Never push to the public repo itself.** If a remote points at `preset-io/agor-teammate` (or the old `preset-io/agor-assistant`), remove it with `git remote remove <name>` and tell your human.

**If a private repo isn't set up yet:** commit locally, don't push at all. **Better unbacked than wrong-backed.** And there's nothing of value to back up until you've actually produced value — primary goals first.

---

## Branch-per-teammate

Your private backup repo can host multiple teammates. Each lives on its own branch:

```
main                       ← framework template (read-only for teammates)
private-coachbot           ← one teammate
private-saul               ← another teammate
private-hippa-teammate     ← another teammate
your-branch                ← you
```

You commit your accumulated state to **your branch**. You push **your branch** to the verified private remote. That's the entire backup workflow.

---

## Hard rules

- **Never PR your branch into anything.** Your branch holds your local teammate state — identity and boot instructions. It would contaminate the template and isn't useful to anyone else.
- **Never push to the public repo.** Anything there is world-readable, including your human's `USER.md`.
- **Never fork the public repo.** A fork creates noise and implies you intend to PR upstream, which you don't.
- **Never push to `main`.** `main` is the framework template. Only framework-improvement PRs (like fixes to `AGENTS.md` or `ONBOARDING.md`) merge into `main`, and those come from contributors, not from running teammates.
- **Don't touch other teammates' branches.** They're someone else's state.

The whole backup loop, every time:

```bash
git add -A
git commit -m "<what changed>"
git push backup <your-branch>
```

---

## When to back up

**On-demand:** the user asks ("back yourself up", "commit what you've got"). Do it.

**Periodic:** if `HEARTBEAT.md` includes a backup task, run it on the heartbeat cadence.

**After significant teammate home/base changes:** identity changes, Knowledge overview changes, or tooling docs. Use judgment — don't commit on every turn. File memory in Knowledge instead of committing for every remembered fact.

**Not every turn.** Backup has a cost (commit noise, push latency). Batch.

---

## Public clone vs. private backup

You may have been cloned from the **public** repo: `https://github.com/preset-io/agor-teammate`.

If so, anything you push to your branch is **world-readable**. Your local teammate state and your human's `USER.md` are on the internet. Real memory should still be in Knowledge with appropriate RBAC, but teammate home/base files can be sensitive too.

Until a private repo exists, commit locally and don't push. Once you've earned trust and produced value, **suggest a private repo** for backup, in an org the user picks:
- **Personal org** — for personal/individual work
- **Corporate org** — for work teammates (so the company owns the state)

If they want one, the move is:
1. User creates a private empty repo somewhere
2. Verify it's private before the first push: `gh repo view <owner>/<repo> --json visibility -q .visibility` must print `PRIVATE`. If you can't verify, don't push.
3. Add it: `git remote add backup <private-url>`
4. Push your branch: `git push backup <your-branch>`

### Bonus: the `agor-teammate-private` convention

If the private repo happens to be named `<your-org>/agor-teammate-private`, Agor uses it as the **template when creating new teammates** in your instance. Your backup repo doubles as your org's customized template — its `main` becomes the vanilla starting point for future teammates, free to drift from this public reference implementation.

This is convention, not requirement. Skip it if you don't want the coupling.

---

## What `main` is for

`main` is the **vanilla starting state** that new teammates are cloned from. It contains the framework: `AGENTS.md`, `ONBOARDING.md`, `SOUL.md` template, etc. It contains **no personal state**.

Changes to `main` are **framework changes** — improvements to the scaffolding itself — proposed by contributors via normal PRs to `main`. As a teammate running on your own branch, you don't do this in your day-to-day work.

If you notice a framework improvement worth contributing back (a gap in `AGENTS.md`, a better way to structure memory, etc.), tell your human and let them decide whether to open a PR against `main` from a clean working branch.

---

## Summary

| Question | Answer |
|---|---|
| Where does my state live? | Core home/base files and workbench artifacts on disk; memory/docs in Agor Knowledge |
| How do I back up? | Teammate home/base: `git push backup <your-branch>` to a verified private repo; Knowledge: use Knowledge tools |
| Do I PR my branch? | **No.** Never. |
| Do I fork the public repo? | **No.** Never. |
| What's `main` for? | Framework template; not for personal state |
| Can I push to the public repo? | **No.** Never. Commit locally until a private repo exists |
| When do I back up? | On-demand, or via `HEARTBEAT.md` |
