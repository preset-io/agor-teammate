# Skill: Superset Error Cleanup (daily)

Find one place in `apache/superset` where a raw system/library exception is raised or allowed to propagate instead of a proper Superset exception, fix it, ship a PR through the standard review pipeline. Modeled on PR apache/superset#42366 (jinja `UndefinedError` → `QueryObjectValidationError` in `models/helpers.py`) and the 2026-07-24 follow-up, PR apache/superset#42401 (same bug class, 4 sites in `connectors/sqla/models.py`).

**Goal:** the application should eventually only ever raise Superset errors (subclasses in `superset/exceptions.py` or a domain `errors.py`), each correctly mapped to a 4xx (user-fixable: bad input, malformed template, invalid syntax) or 500 (genuine system/infra failure) status — never a raw, unhandled system exception surfacing as an opaque 500.

## Before starting

1. Read `memory/` daily logs for the last ~7 days and `MEMORY.md` — collect examples already fixed, in-flight (open PRs you authored), or intentionally skipped. Never re-pick one of those. Check `gh pr list --repo apache/superset --author @me --state all --search "in:title exception OR error"` too.
2. This is a distinct pipeline from the Sentry burndown and deprecation-fix schedules — don't cross-pollinate picks, but do check their recent logs so you don't duplicate a fix that happened to touch the same file for a different reason.

## Finding a candidate

There's no single query for this — it's pattern-matching across the codebase. Good places to look, roughly in priority order:

1. **Sibling-site drift**: grep for exception class names already used correctly elsewhere in the same file/module (e.g. `except (TemplateError, SupersetSyntaxErrorException)`) and check whether *other* call sites in the same file only catch the narrower type. This is the highest-confidence pattern — it means the correct fix already exists in the codebase as precedent, so the diff is minimal and consistent by construction. This is exactly how both #42366 and #42401 were found.
2. **Command layer** (`superset/commands/**`): look for `except <NarrowLibraryException>` where the try body can raise a broader sibling exception from the same library (e.g. `yaml.parser.ParserError` narrower than `yaml.YAMLError`; `jinja2.exceptions.UndefinedError`/`TemplateSyntaxError` narrower than `TemplateError`). `superset/commands/importers/v1/utils.py` and `superset/commands/report/*.py` are known to have unexamined candidates as of 2026-07-24 — verify current state, don't assume they're still broken.
3. **Unguarded library calls reachable from API/view/command layers**: `json.loads`, `yaml.safe_load`, `croniter(...)`, `requests.*`, raw SQLAlchemy calls — anywhere one of these runs directly inside a command/API method with no try/except at all, and a plausible user-input path can make it throw.
4. **Template/SQL rendering call sites generally** — `superset/jinja_context.py`, `superset/sql_parse.py`, `superset/sql_validators/`, `superset/common/query_object.py` — anywhere Jinja or SQL-parsing is invoked outside a try block that's present a few lines away for a sibling call.

Grep starting points:
```bash
grep -rn "except Superset.*Exception" superset/ | grep -v test   # find correct patterns to check siblings against
grep -rn "except.*Error.*:$" superset/connectors superset/commands superset/common
grep -rln "process_template\|process_string" superset/ --include=*.py | grep -v test
```

Pick exactly ONE example per run. It must be a real, reachable code path — not a defensive catch for something that can't actually happen. Log the pick + rationale (file:line, trigger condition, chosen exception class) before starting the fix.

## Root-causing / choosing the right exception

- Confirm the exception hierarchy first: read `superset/exceptions.py` in full. Prefer reusing an existing subclass whose `status` already matches the failure mode (400/422 for user-fixable, 404 for not-found, 500 only for genuine system failure) over inventing a new one. `QueryObjectValidationError`, `SupersetTemplateException`, `SupersetParseError`, and the `CommandInvalidError`/`ObjectNotFoundError` family in `superset/commands/exceptions.py` cover most cases.
- Only create a new exception class if nothing in `superset/exceptions.py` or the relevant domain's `errors.py` fits — and if so, follow the existing plain-`SupersetException`-subclass-with-a-`status`-attr pattern (simplest, most common shape in the file).
- Verify empirically that the "raw" exception you're catching is actually reachable and actually a subclass of what you think it is — don't guess at exception hierarchies. E.g. `python3 -c "import jinja2.exceptions as e; print(e.UndefinedError.__mro__)"` was how #42401 confirmed `UndefinedError` is a `TemplateError`. The obvious repro (e.g. `filter_values('col')[0]` on an empty list) may not actually raise in this codebase — Superset's Jinja env uses `DebugUndefined`, which degrades some undefined-access patterns to a placeholder string instead of raising. Verify your repro actually throws the raw exception on pre-fix code (e.g. via `git stash`) before writing the regression test around it.

## Implementing

1. Create an Agor branch on the `superset` repo (`repoId` `4903fa88-c79c-408e-a643-1ca35743373c`), board `9a49d11a-6605-4581-b58e-f45fe6bfbadb` (SRE). Descriptive kebab name, e.g. `fix-<pattern>-<module>`.
2. Fresh branch dirs: your shell may predate the branch's unix group and hit `EACCES` on direct writes. Don't fight this with `sg`/`newgrp` — instead spawn a session scoped to the branch (`agor_sessions_create` with that `branchId`) to do the actual file edits; sessions created after the branch exists get correct group membership from process start. This is the standard workaround, not a permission bypass.
3. Keep the fix surgical: widen/correct exception handling only. Don't refactor surrounding code, don't touch unrelated exception sites in the same file even if they look similar-but-different — one bug class, fixed everywhere it appears *identically* in one file is fine (as in #42401's 4 sites); fixing a *different* bug class in the same PR is not.
4. Add a regression test that fails on pre-fix code and passes after (verify both, don't assume). Match the existing test file's house style/fixtures.
5. Run `ruff check`, `ruff format --check`, and `mypy` on changed files; run the specific test file(s) touched and confirm green.
6. Commit as Elizabeth Thompson <eschutho@gmail.com> (or the repo's convention — check recent commits), new commit, never amend.

## Shipping

Mirrors the Sentry burndown / deprecation-fix pipeline — the card + zone placement is what lets the companion schedules manage the PR lifecycle after this run ends: the 11am "Daily requested-changes triage" works `zone-in-review`, and the 3pm "Daily PR status check" (schedule `019ea9d1`, enabled) sweeps `zone-pr-ready` and **auto-merges any APPROVED PR** (`gh pr merge --squash`), then moves the card to `zone-merged`, the Shortcut story to Merged/Done (500020392), and archives the fix branch. So once carded correctly in `zone-pr-ready` and approved, merge is automatic — don't merge by hand. (Historical note: this auto-merge schedule did not exist as of 2026-07-24; it does now.)

1. Shortcut story first — use `scripts/shortcut.py` (direct REST API via `SHORTCUT_API_TOKEN`; don't depend on the Shortcut MCP, which needs an interactive OAuth flow the session can't complete): `./scripts/shortcut.py create --type chore --state 500020181 --team automations --name "<title>" --description "<bug pattern, root cause, fix, PR link>"`. Engineering Kanban = workflow 500020181; **always pass `--team automations`** (a create without it lands orphaned in Triage with no team — the sc-117856 gap from 2026-08-19).
2. Push to the `eschutho` fork (`git remote add fork https://github.com/eschutho/superset.git` if not already configured; `git push fork HEAD:<branch-name>`). Never force-push on first push.
3. Open PR via `gh pr create --repo apache/superset --base master --head eschutho:<branch-name>`, following `.github/PULL_REQUEST_TEMPLATE.md` (SUMMARY/PROBLEM/FIX/TESTING INSTRUCTIONS/ADDITIONAL INFORMATION). Link the originating pattern PR (#42366 or the most recent cleanup PR) for context. Include a **Tradeoffs** note if the fix changes any failure-mode semantics (it shouldn't, for this pipeline — these are additive catches, not behavior changes — but call it out explicitly if it ever does).
4. Move the Shortcut story to Reviewing: `./scripts/shortcut.py update <story> --state 500020186` (only once the PR exists to point it at).
5. Spawn a self-review session on the fix branch (claude-code) using the template from memory `reference_self_review_prompt`. Address blocking findings; disclose anything ambiguous to Elizabeth rather than self-ratifying.
6. **Card on the SRE board** (`agor_cards_create`):
   - `boardId`: `9a49d11a-6605-4581-b58e-f45fe6bfbadb`
   - `zoneId`: `zone-pr-ready`
   - `title`: the PR title
   - `url`: the PR URL
   - `description`: one-line summary + Shortcut story URL
   - `data`: `{"agor_branch_id": "<the fix branch's branch_id>"}`
7. **Send to Minerva for review** — `agor_sessions_create` on the Minerva/EngCodeReviewBot branch (`019df42c-8d6d-76d2-92bd-a49c169db7f1`, board "Minerva"), `agenticTool: claude-code`, `enableCallback: true`, `includeLastMessage: true`. Ask it to review the PR, find + assign a reviewer for `apache/superset`, and notify them per their preference. NEVER comment on the PR directly yourself.
8. Update the Agor branch metadata with PR + Shortcut story URLs (`agor_branches_update`).

After this run, do NOT babysit the PR — that's the 11am requested-changes triage's job for anything landing in `zone-in-review`.

## Wrap-up

- Append to `memory/YYYY-MM-DD.md`: pattern found, file:line, root cause, PR/story links, session IDs, and any other candidate sites spotted in the same sweep (for next run — note them explicitly so tomorrow's run doesn't duplicate the search from scratch).
- Commit the workspace memory changes (`log:` prefix, matching `git log` convention).
- Final message: lead with what was fixed and the PR link; list anything needing Elizabeth's judgment.

## Guardrails

- **Ship the PR — don't hold.** This pipeline carries the fix all the way to an opened PR (Elizabeth, 2026-08-13). Never tell the implementation session "get to a clean tree, I'll handle commit/PR" and hand a finished-but-unshipped fix back to her. The ONLY legitimate reason to stop short of a PR is the unresolved commit-identity classifier block (memory `project_commit_identity_classifier_blocked`) — and if that's the blocker, flag it and the pending identity decision explicitly, don't silently sit on the fix.
- One example per run; no scope creep into "while I'm here" fixes elsewhere in the file.
- If no clean, high-confidence candidate exists, say so, log candidates considered and why they were rejected, and stop — do not force a marginal or speculative fix.
- Never invent a new exception class when an existing one fits — check `superset/exceptions.py` and the relevant domain's `errors.py` first.
- Never assume an exception hierarchy — verify with a quick Python MRO check or by reading the library source.
- Never claim a regression test is valid without confirming it fails on pre-fix code.
