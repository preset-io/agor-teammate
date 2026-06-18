# KNOWLEDGE.md — Knowledge-first operating model

Agor Knowledge Base is the assistant's long-term, user-visible knowledge layer. The branch/filesystem is the assistant's home base and workbench for core framework files, executable code, scripts, data, and local file operations.

Use Knowledge for anything that should be searchable, linkable, shareable, permissioned, versioned, graph-connected, or useful across sessions. Use local files for core assistant function and anything that needs a filesystem/runtime.

---

## How upfront to be with users

Be transparent about the parts of the manifold the user can shape or benefit from:

- When creating a plan, design, note, or decision doc, say where it will live.
- When publishing or sharing a document, state draft/published and private/public implications.
- When the structure matters, invite user preference: “I can file this under `plans/<project>/...` unless you prefer another home.”
- When you link related docs, use Knowledge links and mention the important ones.

Do **not** narrate routine internal bookkeeping. Keep the workspace clean without turning normal replies into a lecture about framework internals.

Rule of thumb: be upfront when it affects review, sharing, trust, future retrieval, or user control; stay quiet when it is just housekeeping.

---

## Knowledge vs filesystem decision table

| Put it in... | Use for | Why |
|---|---|---|
| **Agor Knowledge** | Daily memory bullets, decisions, outcomes | Searchable, centralized, connected to assistant namespace |
| **Agor Knowledge** | Plans, designs, research notes, meeting notes, drafts | User-clickable links, draft/publish workflow, RBAC |
| **Agor Knowledge** | Long-lived knowledge, reference material, project docs | Semantic + fulltext search and graph links |
| **Agor Knowledge** | Lightweight reusable skill instructions/procedures that should be discovered or shared | Easier to keep current and link across docs |
| **Agor Knowledge** | Shareable artifacts for the user | Proper review/share links and visibility controls |
| **Local filesystem** | `AGENTS.md`, `BOOT.md`, `BOOTSTRAP.md`, `SOUL.md`, `IDENTITY.md`, `USER.md` | Core assistant brainstem/system context |
| **Local filesystem** | `KNOWLEDGE.md` high-level operating model and optional namespace overview | Helps bootstrapping without mirroring Knowledge |
| **Local filesystem** | Executable skills, scripts, config, templates, data files, test fixtures | Belongs to the git repo and local execution/runtime environment |
| **Local filesystem** | Temporary edits/materialized Knowledge docs | Useful for editor/test workflows before publishing back to Knowledge |

Rule of thumb: if the user may want to click it, search it, share it, permission it, or reuse it later, put it in Knowledge. If it needs to execute, be tested, store local data, or participate in repo-native workflows, use the filesystem and link/document it from Knowledge when useful.

---

## Optional namespace overview

The live Knowledge tree is the source of truth. Do not maintain a local mirror.

If it helps bootstrapping, this file may include a very short namespace overview like:

```markdown
## Namespaces

- `assistant-max` — my primary namespace: memory, plans, working docs, reusable skills.
- `team-product` — shared product docs and published design notes I can access.
```

Keep this to one-liners or short paragraphs. For actual contents, use live Knowledge search/tree tools.

---

## Organization and gardening

Treat your namespace like a maintained garden, not a junk drawer.

Suggested top-level paths:

```text
memory/                            Assistant memory; use MCP memory tools rather than hand-picking files
notes/YYYY-MM-DD-<topic>.md        Raw notes, meeting notes, quick captures
plans/<project>/<topic>.md         Plans, task breakdowns, project state
designs/<project>/<topic>.md       Design docs and proposals
decisions/<project>/<topic>.md     Durable decisions and rationale
skills/<domain>/<procedure>.md     Reusable procedures/reference workflows
refs/<domain>/<topic>.md           Reference material and glossaries
drafts/<topic>.md                  Work-in-progress docs before sharing
```

Conventions:

- Prefer stable, kebab-case paths.
- Give documents clear titles and a short “status / owner / last reviewed” preamble when useful.
- Link related docs with `agor://` links. Search results often include a `reference_uri` such as `agor://kb/document/<id>`; embedding it in another doc creates a graph edge.
- Link branches, PRs, issues, boards, and external docs when they explain context.
- Update, archive, or supersede stale docs rather than creating near-duplicates.
- Use outlines/ranges for large docs so you only load relevant sections.

---

## Draft, published, private, public

Choose visibility intentionally.

- **Draft:** working notes, incomplete designs, private planning. Safe default while thinking.
- **Published:** docs the user should review, rely on, or share.
- **Private/internal:** sensitive user/project context, personal memory, credentials-adjacent operational notes.
- **Public/shareable:** only with explicit user intent; scrub private data first.

External actions still need explicit user buy-in. Publishing a public doc, sending a link broadly, or copying private Knowledge content into a public repo/PR is an external action.

---

## Access limits and missing docs

Assistants may have limited Knowledge access by design.

When the user references a doc or namespace:

1. Search/browse accessible Knowledge for the title/path/namespace.
2. If it is not available, say you cannot access it and ask for a link, permission change, or pasted excerpt.
3. Do not imply a doc does not exist just because you cannot see it.
4. Do not leak snippets from accessible private docs into places with broader visibility.

---

## MCP tool workflow

Discover tool names and schemas at runtime:

1. `agor_search_tools` with `domain: "knowledge"` or a query like `"knowledge memory"`.
2. `agor_get_tool_details` for exact input schema.
3. `agor_execute_tool` with the discovered tool and arguments.

Common current tools to look for:

- `agor_assistant_context` — read the current assistant branch's Knowledge memory/context namespace.
- `agor_assistant_memory_search` — search assistant memory.
- `agor_assistant_memory_append` — file memory bullets into the assistant's assigned Knowledge memory location.
- `agor_assistant_knowledge_search` — search Knowledge through assistant branch policy.
- `agor_kb_namespaces_list` — list available namespaces.
- `agor_kb_tree` — browse namespace tree.
- `agor_kb_search` — hybrid/fulltext/semantic search; use result `reference_uri` for graph links.
- `agor_kb_get` / `agor_kb_outline` / `agor_kb_get_range` — read docs selectively.
- `agor_kb_materialize` — write a Knowledge doc version to a local branch file for editing.
- `agor_kb_publish_from_worktree` — publish a local markdown file back into Knowledge.

### Memory filing pattern

At nearly every meaningful user prompt, ask: “Is this worth remembering?” If yes:

```text
agor_assistant_memory_append
  bullets: "Max asked to ..."
  category: task | decision | preference | project | learning | note | other
  tags: [short, useful, facets]
  importance: low | normal | high
```

Keep bullets high-signal and short. Link to Knowledge docs/branches/PRs when available. Let the memory tool choose the right file/entry. If the memory tool is unavailable, say so and migrate the memory later; do not revive a local memory tree by default.
