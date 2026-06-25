# Skill: Sync 2cad → 2Caddy (prod → staging)

**When to use:** Whenever you need to refresh staging (2Caddy) with the latest assets from the prod 2cad workspace — before evals, rate limit testing, or any work that needs prod-parity data without touching production.

---

## Prerequisites

- [ ] `SUP_PRESET_API_TOKEN` / `SUP_PRESET_API_SECRET` set (prod Preset credentials)
- [ ] `STG_PRESET_API_TOKEN` / `STG_PRESET_API_SECRET` set (staging credentials)
- [ ] `prison`, `yarl`, `jinja2`, `pyyaml`, `requests` available (`pip install preset-cli` covers these)

Verify:
```bash
env | grep -E "SUP_PRESET|STG_PRESET" | sed 's/=.*/=<set>/'
```

---

## Steps

### Full sync (pull from prod + push to staging)

```bash
cd /var/lib/agor/home/agorpg/.agor/worktrees/mistercrunch/agor-openclaw/private-preset-architect/2cad-to-2caddy
python3 sync.py
```

### Pull only (refresh local assets from 2cad, don't push yet)

```bash
python3 sync.py --pull-only
```

### Push only (re-push existing local assets to 2Caddy — useful when assets already pulled)

```bash
python3 sync.py --push-only
```

### Custom assets directory

```bash
python3 sync.py --assets-dir /tmp/staging-assets
```

---

## What the script does

1. **Pull** — authenticates with prod Preset Manager (`api.app.preset.io`), finds 2cad's workspace URL, exports all databases / datasets / charts / dashboards via the Superset export API
2. **Transform** — strips `configuration_method` from database YAMLs (staging Superset doesn't support this field)
3. **Push** — authenticates with staging Preset Manager (`api.app-stg.preset.io`), imports all assets to 2Caddy with dependency ordering (databases → datasets → charts → dashboards), skipping failures instead of aborting

---

## Expected output

```
✅  databases     15 ok    0 failed
✅  datasets     193 ok    0 failed
⚠️   charts       933 ok    5 failed
✅  dashboards    50 ok    0 failed

Total: 1191 imported, 5 failed
```

Exit code `0` = full success, `1` = at least one failure (safe for CI/cron).

---

## Known permanent failures (5 charts — not fixable without prod changes)

These 5 charts will always fail because they can't resolve cross-environment:

| Chart | Reason |
|-------|--------|
| 🏖️ Chatbot Cost — Month to Date | Uses `handlebars` viz plugin not installed on staging |
| Database Connection / attempts | Null datasource — broken on prod too |
| New Leads (id 400) | Hardcoded prod datasource ID 36, no UUID |
| New Leads (id 451) | Hardcoded prod datasource ID 53, no UUID |
| Registrant by Lead Status | Hardcoded prod datasource ID 36, no UUID |

---

## After the sync

1. **Update database credentials** — the 15 database YAMLs contain masked passwords (`XXXXXXXXXX`). Someone needs to set real staging credentials for each connection in the 2Caddy workspace UI.

2. **Verify** — spot-check a dashboard or two in 2Caddy to confirm assets landed correctly.

---

## Error handling

**`Unable to fetch JWT` / auth timeout**
- Check that env vars are set and credentials haven't expired
- Staging manager (`api.app-stg.preset.io`) can be slow; retry

**`HTTP 500` on specific assets**
- Usually a schema mismatch between prod and staging Superset versions
- The script logs the exact error per asset — search logs for `FAILED:`
- `continue_on_error` means the rest of the sync completes regardless

**`Workspace N not found`**
- Workspace IDs are hardcoded in `sync.py` (`PROD_WORKSPACE_ID = 187`, `STAGING_WORKSPACE_ID = 181032`)
- If 2Caddy is recreated, update `STAGING_WORKSPACE_ID` in the script

**Import hangs**
- 60s timeout per request is baked in — script will move on after timeout and mark asset as failed

---

## Files

| File | Purpose |
|------|---------|
| `2cad-to-2caddy/sync.py` | The sync script — self-contained, no patched packages needed |
| `2cad-to-2caddy/assets/` | Local copy of exported assets (re-pulled each full sync) |
| `2cad-to-2caddy/sync_config.yml` | Reference config used during initial manual sync (not used by script) |

---

## Related

- Initial manual sync notes: session `c1fc9825` (2026-06-05)
- Slack announcement: #engineering (2026-06-05)

---

**Last Updated:** 2026-06-05
**Created By:** Preset Architect
