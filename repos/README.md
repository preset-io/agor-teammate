# Repo Context Files

Per-repository context and workflow documentation.

## Purpose

Each file in this directory contains:
- Repository-specific workflows (build, test, commit, PR process)
- Tech stack and tooling
- Common patterns and conventions
- Things to know when working in this codebase

## Usage

When working in a repo, read its context file first. Update it as you learn new patterns.

## File Naming

Use the repo slug: `org-name-repo-name.md`

Examples:
- `preset-io-agor.md` → preset-io/agor
- `apache-superset.md` → apache/superset

## Template

```markdown
# [Repo Name]

**Slug:** org/repo
**Repo ID:** [from Agor]
**Tech Stack:** [languages, frameworks, tools]

## Workflow

### Before Starting Work
- [ ] Step 1
- [ ] Step 2

### Before Committing
- [ ] Run checks/tests
- [ ] Format code
- [ ] etc.

### Opening PRs
- [ ] Run final checks
- [ ] Create PR with template
- [ ] Attach PR to worktree via Agor MCP

## Common Patterns

### Pattern Name
Description and code examples

## Things to Know

- Important context
- Gotchas
- Conventions
```
