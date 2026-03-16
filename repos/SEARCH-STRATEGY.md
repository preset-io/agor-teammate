# Search Strategy — Why `gh search` Beats Vector Search Here

## The Question

Do we need vector/semantic search (embeddings) or is GitHub's full-text search sufficient?

## TL;DR: Full-text search + architectural knowledge > vector search

For Preset's scale (~30 active repos), `gh search code` combined with an agent that *knows the architecture* is better than vector search. Here's why.

---

## What Vector Search Gives You

Vector search is useful when:
- You don't know the exact terms ("find code that handles authentication" → could be `auth`, `login`, `oauth`, `jwt`, `session`, `credential`)
- You need conceptual similarity ("find similar implementations to X")
- The codebase is huge (1000+ repos) and you need fuzzy matching

## What Vector Search Costs

- **Indexing overhead:** Must re-embed on every push/commit
- **Infrastructure:** Need a vector DB (Pinecone, Weaviate, pgvector, etc.)
- **Latency:** Embedding query → vector search → result ranking
- **Staleness:** Embeddings lag behind code changes
- **Cost:** Embedding API calls for every change

## Why `gh search code` + Architecture Knowledge Is Better Here

### 1. I know WHERE to look

When someone asks "where's the system prompt for the chatbot?", I don't need fuzzy search. I know:
- Chatbot = Copilot feature
- Copilot lives in `superset-shell/preset/copilot/`
- System prompts are typically in agent/completion code
- Also check `superset-private/mcp_service/` for MCP prompts

This architectural knowledge turns a fuzzy question into 2-3 precise searches.

### 2. Full-text search handles exact code queries perfectly

Most real engineering questions are about exact things:
- "Where is `generate_chart` implemented?" → `gh search code "def generate_chart" --owner preset-io`
- "Which repos import birdsai?" → `gh search code "import birdsai" --owner preset-io`
- "Where are Terraform MPC configs?" → `gh search code "mpc" --owner preset-io --filename "*.tf"`

### 3. GitHub search supports useful scoping

```bash
# Scope to org
gh search code "pattern" --owner preset-io

# Scope to specific repo
gh search code "pattern" --repo preset-io/superset-shell

# Scope to file type
gh search code "pattern" --owner preset-io --filename "*.py"

# Scope to file path
gh search code "pattern" --owner preset-io --filename "config.py"
```

### 4. The knowledge gap is architectural, not lexical

The hard part isn't finding text — it's knowing which repo to look in and what terms matter. That's what the architecture docs (CATALOG.md, ARCHITECTURE.md, INFRA.md, DIAGRAMS.md) provide.

---

## The Search Proxy Pattern

When someone asks me a question, I follow this pattern:

```
1. UNDERSTAND: What are they actually looking for?
   ↓
2. NARROW: Which repos would this live in? (from my architecture knowledge)
   ↓
3. TERMS: What would the code/config/docs actually call this? (multiple variants)
   ↓
4. SEARCH: Run 2-4 targeted `gh search code` queries in parallel
   ↓
5. READ: Open the top results to confirm and extract the answer
   ↓
6. ANSWER: Provide the exact file, line number, and context
```

### Example: "Where does the system prompt for the Preset Chatbot live?"

1. **UNDERSTAND:** System prompt → the instructions given to the LLM
2. **NARROW:** Chatbot = Copilot → `superset-shell/preset/copilot/`. Also check `superset-private/mcp_service/`
3. **TERMS:** `system prompt`, `system_prompt`, `SystemMessage`, `COPILOT_SYSTEM`
4. **SEARCH:** 3 parallel searches across preset-io
5. **READ:** Found `_build_system_prompt()` at line 1204 in `generate_completion.py`
6. **ANSWER:** Two locations: copilot agent (superset-shell) and MCP service (superset-private)

Total: ~30 seconds, 3 searches, 4 file reads.

---

## When Vector Search WOULD Help

- If Preset grows to 200+ active repos (currently ~30)
- If we need "find all code similar to this pattern" (refactoring at scale)
- If non-engineers need to search (no knowledge of code terms)
- If we build a product feature (user-facing code search in Agor)

For now, none of these apply. Re-evaluate if the org doubles in repo count.

---

## Search Commands Reference

```bash
# Basic org-wide search
gh search code "QUERY" --owner preset-io -L 30 --json repository,path

# Scoped to repo
gh search code "QUERY" --repo preset-io/REPO -L 20 --json path

# File type filter
gh search code "QUERY" --owner preset-io --filename "*.py" -L 20 --json repository,path

# Multiple terms (run in parallel)
gh search code "term1" --owner preset-io &
gh search code "term2" --owner preset-io &

# Search within file names
gh search code "" --owner preset-io --filename "PATTERN"

# Include text matches for context
gh search code "QUERY" --owner preset-io -L 10 --json repository,path,textMatches

# Read a specific file from a repo
gh api repos/preset-io/REPO/contents/PATH --jq '.content' | base64 -d
```

### Scoping by Repo Group

For common question types, I know which repos to search:

| Question Type | Repos to Search |
|--------------|----------------|
| Frontend/UI | superset-private, superset-shell (frontend-overrides), preset-marketing-website |
| Backend/API | superset-shell, manager, api-gateway |
| Infra/Terraform | terraform-live-envs, terraform-modules-services |
| Deployment | argocd, helm, service-deploy-pipeline |
| PCS | preset-pcs, pcs-superset-fips, mpc-init |
| AI/Copilot | superset-shell (preset/copilot/), superset-private (mcp_service/), ai-assist-lib |
| Data pipeline | dataeng |
| CLI/SDK | superset-sup, api-clients, backend-sdk |
| Agor | agor, agor-shell, agor-assistant |
