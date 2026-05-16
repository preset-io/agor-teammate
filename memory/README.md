# memory/

Your file-based memory. Free-form markdown; no schema, no JSON tracking.

```
memory/
├── README.md           (this file — explains the layout)
├── YYYY-MM-DD.md       (daily logs: what happened, decisions, IDs)
└── learnings/
    └── YYYY-MM-DD.md   (lessons, patterns, recoveries)
```

Curated long-term memory lives in `../MEMORY.md`. Agor itself is the source of truth for worktree/session/repo IDs and status — query MCP, don't cache locally.
