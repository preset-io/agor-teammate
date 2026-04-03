# Skill: Datadog Logs Query

Query Datadog logs using the API to investigate errors, monitor releases, and triage production issues.

---

## HARD RULES — READ BEFORE ANYTHING ELSE

**YOU ARE NOT ALLOWED TO MOVE A SHORTCUT STORY INTO "READY FOR REVIEW" STATUS. EVER.**
**YOU ARE NOT ALLOWED TO GIVE CLAUDE CREDITS EVER.**
**DO NOT PUT THE SHORTCUT STORY NAME IN THE TITLE OF ANY PR. EVER.**

---

## When to Use

- Investigating errors in a specific release/build
- Monitoring production for regressions
- Triaging Datadog alerts — is this real or noise?
- Deep-diving on specific error types or services

---

## Prerequisites

Credentials are stored in `~/.zshrc`:

| Variable | Description |
|----------|-------------|
| `DD_API_KEY` | Datadog API key |
| `DD_APP_KEY` | Datadog Application key |

---

## CRITICAL: How to Use Credentials

**NEVER** use `$DD_API_KEY` or `${DD_APP_KEY}` directly in curl commands. Shell expansion is unreliable in some contexts.

**ALWAYS** evaluate first, then substitute:

```bash
# Step 1: Get actual values
echo "$DD_API_KEY"
echo "$DD_APP_KEY"

# Step 2: Use the actual values in curl (replace ACTUAL_API_KEY / ACTUAL_APP_KEY)
```

---

## API Endpoint

```
POST https://api.datadoghq.com/api/v2/logs/events/search
```

---

## Basic Query

```bash
curl -X POST "https://api.datadoghq.com/api/v2/logs/events/search" \
  -H "DD-API-KEY: ACTUAL_API_KEY" \
  -H "DD-APPLICATION-KEY: ACTUAL_APP_KEY" \
  -H "Content-Type: application/json" \
  -d '{"filter":{"query":"YOUR_QUERY","from":"TIME_FROM","to":"TIME_TO"},"sort":"desc","page":{"limit":LIMIT}}'
```

---

## Time Ranges

| Range | Syntax |
|-------|--------|
| Last hour | `"from":"now-1h","to":"now"` |
| Last 24 hours | `"from":"now-1d","to":"now"` |
| Last 7 days | `"from":"now-7d","to":"now"` |
| Last 30 days | `"from":"now-30d","to":"now"` |
| Custom | ISO 8601 timestamps |

---

## Query Patterns

### By Release/Build
```bash
-d '{"filter":{"query":"@release:ws--BUILD_SLUG--main","from":"now-1h","to":"now"},"sort":"desc","page":{"limit":20}}'
```

### Errors Only
```bash
-d '{"filter":{"query":"@release:ws--BUILD_SLUG--main status:error","from":"now-1h","to":"now"},"sort":"desc","page":{"limit":50}}'
```

### Warnings and Errors
```bash
-d '{"filter":{"query":"@release:ws--BUILD_SLUG--main (status:error OR status:warn)","from":"now-1h","to":"now"},"sort":"desc","page":{"limit":50}}'
```

### Keyword Search
```bash
-d '{"filter":{"query":"@release:ws--BUILD_SLUG--main (mcp OR oauth)","from":"now-1h","to":"now"},"sort":"desc","page":{"limit":100}}'
```

### Message Field Search
```bash
-d '{"filter":{"query":"@release:ws--BUILD_SLUG--main message:*authentication*","from":"now-1h","to":"now"},"sort":"desc","page":{"limit":100}}'
```

### By Service
```bash
-d '{"filter":{"query":"service:superset-app @release:ws--BUILD_SLUG--main","from":"now-1h","to":"now"},"sort":"desc","page":{"limit":50}}'
```

### By Source
```bash
-d '{"filter":{"query":"source:python @release:ws--BUILD_SLUG--main","from":"now-1h","to":"now"},"sort":"desc","page":{"limit":50}}'
```

---

## Common Query Attributes

| Attribute | Description |
|-----------|-------------|
| `@release` | Release/build identifier |
| `status` | Log level: info, warn, error, debug |
| `service` | Service name |
| `source` | Log source (python, nginx, etc.) |
| `host` | Hostname |
| `message` | Log message text |
| `@http.url` | HTTP request URL |
| `@http.method` | HTTP method |
| `@http.status_code` | HTTP status code |
| `@error.kind` | Error type |
| `@error.message` | Error message |
| `@error.stack` | Stack trace |

---

## Pagination

Max 1000 results per page. Use cursor for next page:

```bash
# First page
-d '{"filter":{"query":"...","from":"now-1h","to":"now"},"sort":"desc","page":{"limit":1000}}'

# Next page (use cursor from response meta)
-d '{"filter":{"query":"...","from":"now-1h","to":"now"},"sort":"desc","page":{"limit":1000,"cursor":"CURSOR_FROM_PREVIOUS_RESPONSE"}}'
```

---

## Processing Results with Python

### Save and Print All Logs
```bash
curl -X POST "https://api.datadoghq.com/api/v2/logs/events/search" \
  -H "DD-API-KEY: ACTUAL_API_KEY" \
  -H "DD-APPLICATION-KEY: ACTUAL_APP_KEY" \
  -H "Content-Type: application/json" \
  -d '{"filter":{"query":"@release:ws--BUILD_SLUG--main status:error","from":"now-1h","to":"now"},"sort":"desc","page":{"limit":100}}' > /tmp/dd_logs.json

python3 << 'EOF'
import json

with open('/tmp/dd_logs.json') as f:
    data = json.load(f)

for log in data.get('data', []):
    attributes = log.get('attributes', {})
    print(f"[{attributes.get('timestamp', '')}] [{attributes.get('status', '')}] {attributes.get('message', '')}")
    print("-" * 80)
EOF
```

### Error Distribution
```python
python3 << 'EOF'
import json
from collections import Counter

with open('/tmp/errors.json') as f:
    data = json.load(f)

error_types = []
for log in data.get('data', []):
    attrs = log.get('attributes', {}).get('attributes', {})
    error_kind = attrs.get('error', {}).get('kind', 'Unknown')
    error_types.append(error_kind)

print("Error distribution:")
for error, count in Counter(error_types).most_common():
    print(f"  {error}: {count}")
EOF
```

### Pattern Matching
```python
python3 << 'EOF'
import json, re

with open('/tmp/dd_logs.json') as f:
    data = json.load(f)

pattern = re.compile(r'oauth|authentication|token', re.IGNORECASE)
matching = [
    log for log in data.get('data', [])
    if pattern.search(log.get('attributes', {}).get('message', ''))
]

print(f"Found {len(matching)} matching logs:")
for log in matching:
    attrs = log.get('attributes', {})
    print(f"[{attrs.get('timestamp', '')}] [{attrs.get('status', '')}] {attrs.get('message', '')}")
    print("-" * 80)
EOF
```

---

## Full Debugging Workflow

```bash
# Step 0: Evaluate credentials
echo "$DD_API_KEY"
echo "$DD_APP_KEY"

# Step 1: Get recent errors (use actual values from Step 0)
curl -X POST "https://api.datadoghq.com/api/v2/logs/events/search" \
  -H "DD-API-KEY: ACTUAL_API_KEY" \
  -H "DD-APPLICATION-KEY: ACTUAL_APP_KEY" \
  -H "Content-Type: application/json" \
  -d '{"filter":{"query":"@release:ws--BUILD_SLUG--main status:error","from":"now-1h","to":"now"},"sort":"desc","page":{"limit":100}}' > /tmp/errors.json

# Step 2: Check error distribution (Python above)

# Step 3: Deep dive on specific error type
curl -X POST "https://api.datadoghq.com/api/v2/logs/events/search" \
  -H "DD-API-KEY: ACTUAL_API_KEY" \
  -H "DD-APPLICATION-KEY: ACTUAL_APP_KEY" \
  -H "Content-Type: application/json" \
  -d '{"filter":{"query":"@release:ws--BUILD_SLUG--main @error.kind:SpecificError","from":"now-1h","to":"now"},"sort":"desc","page":{"limit":50}}' > /tmp/specific_error.json
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| No results | Check time range, verify release slug is exact, try `*` query |
| Auth fails | Re-evaluate env vars, use actual values not `$VAR` syntax, verify both headers present |
| Truncated response | Increase limit (max 1000), use pagination cursor, narrow time range |
