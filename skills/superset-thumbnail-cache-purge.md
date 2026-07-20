# Runbook: Inspect & Clear the Superset Thumbnail/Screenshot S3 Cache

**Last verified:** 2026-07-20, against `superset-shell`, `superset-private`, `infra`,
`terraform-live-envs`, and a live purge investigation on `production-aws-us2a`
(workspace `19afbfef`, deployment `ws--f02c1626--main`).

## When to use

A workspace reports blank, stale, or broken dashboard screenshots/thumbnails
(e.g. `/api/v1/dashboard/<pk>/screenshot/<digest>/` returns a blank image or 404)
and you need to inspect or delete the cached entries in S3.

**Redis is NOT part of this path.** In production, thumbnails use the S3 backend
(`preset.cache.s3.S3CacheFlaskAdapter`, from the `s3werkzeugcache` package)
whenever `THUMBNAILS` or `ENABLE_DASHBOARD_SCREENSHOT_ENDPOINTS` is enabled.
The Redis thumbnail config only exists in local dev.

## Architecture facts (verified in code)

| Fact | Value |
|------|-------|
| Bucket | `{environment}-{region}-superset-thumbnails-1` (e.g. `production-us-east-1-superset-thumbnails-1`), defined in `terraform-live-envs/modules/aws/app_stack/superset_buckets.tf` |
| S3 object key | `thumbs_cache_v3__{workspace_hash}_{sha256(SECRET_KEY)[:6]}/{cache_key}` |
| Prefix version | `thumbs_cache_v3_` from `superset-shell/helm/superset/values.yaml` (`cacheConfig.THUMBS_KEY_PREFIX`); the double underscore comes from the f-string in `DynamicConfigs.thumbs_key_prefix` |
| Payload format | Pickled dict `{"image": base64-PNG-or-None, "status": str, "timestamp": iso8601}` (`ScreenshotCachePayload.to_dict()` in `superset/utils/screenshots.py`) |
| Statuses | `pending` / `computing` (no image yet, ~hundreds of bytes pickled), `updated` (has image), error states |
| Lifecycle | Objects auto-expire after **15 days**; versioning is **suspended** (deletes are permanent) |
| IAM | Bucket policy grants get/put/delete/**list** to the **cluster-wide** Superset IRSA role — any Superset pod on the cluster can operate on any workspace's keys |
| Multi-tenancy | Namespaces `ws--{deployment_hash}--{name}` are per-**deployment**; one deployment hosts **multiple workspaces**. `WORKSPACE_NAME` is NOT a pod env var — it resolves per-request. Never assume namespace hash == workspace hash. |

### Digest semantics (important)

- `/api/v1/dashboard/<pk>/screenshot/<digest>/` — the URL digest **is** the cache
  key verbatim. S3 object = `{prefix}{digest}`. It comes from the JSON response of
  `POST /api/v1/dashboard/<pk>/cache_dashboard_screenshot/` (field `cache_key`).
- `/api/v1/dashboard/<pk>/thumbnail/<digest>/` — the URL digest is the dashboard
  *model* digest, which gets re-hashed with window/thumb size into the cache key.
  It will **never** appear in an S3 key; you must compute the cache key via
  `DashboardScreenshot(...).get_cache_key()`.
- The screenshot cache key also includes the **permalink key**, so re-POSTing
  `cache_dashboard_screenshot` with fresh state mints a *new* cache key. To find
  the poisoned entry, use the digest from the **original failing request**
  (reporter's URL, browser devtools, or Datadog access logs for the workspace).

## Prerequisites

- `oktaLogin <environment>` (saml2aws + Okta; each AWS account needs its own login).
  Credentials land in a **named profile** — `export AWS_PROFILE=production` or the
  bare `aws` CLI will say "Unable to locate credentials".
- `OktaReadOnlyAccess` is enough for ALL inspection (list + get). **Deletes are
  denied from the laptop** — they go through a pod (cluster IRSA role).
- `kubectl` access to the cluster for the delete step.

## Steps

### 1. Login and sanity-check

```bash
oktaLogin production
export AWS_PROFILE=production
aws sts get-caller-identity   # expect the target account + your Okta role
```

### 2. Discover the workspace's prefix (delimiter listing)

Never list the whole bucket — it holds every workspace in the environment. A
delimiter listing returns one `CommonPrefix` per workspace:

```bash
aws s3api list-objects-v2 \
  --bucket production-us-east-1-superset-thumbnails-1 \
  --prefix "thumbs_cache_v3_" \
  --delimiter "/" \
  --query 'CommonPrefixes[].Prefix' --output text | tr '\t' '\n' | grep <WORKSPACE_HASH>
```

Expected result: `thumbs_cache_v3__<workspace_hash>_<6hex>/`. If absent, the
workspace has written no thumbnails in the last 15 days (lifecycle expiry) — the
failing screenshots are NOT coming from stale S3 entries.

### 3. List the workspace's cache entries (read-only)

```bash
aws s3api list-objects-v2 \
  --bucket production-us-east-1-superset-thumbnails-1 \
  --prefix "thumbs_cache_v3__<workspace_hash>_<6hex>/" \
  --query 'Contents[].[Size,LastModified,Key]' --output text
```

Reading sizes:
- **A few hundred bytes** → stuck `pending`/`computing` payload (no image).
- **Tens of KB** → could be a blank/white capture (blank PNGs compress small) —
  but small ≠ blank; verify visually in step 4.
- **~1–2 MB** → full-size capture with real content.
- **Zero-byte objects essentially never occur** — do not scan for them; the
  payload is a pickled dict, never a raw/empty file.

### 4. Download and visually inspect (read-only, definitive)

A workspace rarely has more than a few dozen entries — pull them all and render
every payload to a PNG:

```bash
mkdir -p /tmp/thumbs && cd /tmp/thumbs
aws s3 cp "s3://production-us-east-1-superset-thumbnails-1/thumbs_cache_v3__<workspace_hash>_<6hex>/" . --recursive

python3 - <<'PY'
import pickle, base64, glob
for f in sorted(glob.glob("*")):
    if f.endswith(".png"):
        continue
    try:
        p = pickle.load(open(f, "rb"))
    except Exception as e:
        print(f[:12], "unpickle failed:", e)   # old-format payload → run inside superset venv/pod
        continue
    img = p.get("image") if isinstance(p, dict) else None
    size = 0
    if img:
        raw = base64.b64decode(img)
        open(f[:12] + ".png", "wb").write(raw)
        size = len(raw)
    print(f[:12], "| status:", p.get("status"), "| captured:", p.get("timestamp"), "| png bytes:", size)
PY
open .   # blanks are obvious at a glance; filename = first 12 chars of the digest
```

This identifies the poisoned digests even if you don't have the failing URL.

### 5. Targeted delete (via any Superset pod on the cluster)

Address the object by **explicit full key** — no app config resolution, nothing
to get wrong about which tenant it hits. Note `exec -i` is REQUIRED for heredocs
(without `-i`, python receives empty stdin and silently does nothing):

```bash
kubectl --context <cluster> -n <any-superset-namespace> \
  exec -i <superset-pod> -c app -- python - <<'PY'
import boto3
key = "thumbs_cache_v3__<workspace_hash>_<6hex>/<DIGEST>"
boto3.client("s3").delete_object(
    Bucket="production-us-east-1-superset-thumbnails-1", Key=key)
print("deleted", key)
PY
```

### 6. Force a re-capture and interpret

Deleting does **not** trigger regeneration — GET just returns 404 until a new
capture is requested:

```
POST /api/v1/dashboard/<pk>/cache_dashboard_screenshot/?q=(force:!t)
```

(`force:!t` also works *without* deleting — a zero-delete way to test the
capture path first.)

- Fresh capture is valid → the cached entry was stale/poisoned. Done.
- Fresh capture is blank again → the **live capture path** (webdriver/Playwright
  in the Celery worker) is producing blanks; no amount of cache purging fixes
  it. Investigate the worker instead.

### 7. Bulk purge (only if many entries are poisoned)

List first (step 3), review, then delete under the exact workspace prefix. The
prefix ends in `/` and embeds workspace hash + secret-key hash, so it cannot
touch other tenants. Needs write creds → run in the pod, or an admin role:

```bash
# dry-run from laptop first if you have write creds:
aws s3 rm "s3://production-us-east-1-superset-thumbnails-1/thumbs_cache_v3__<workspace_hash>_<6hex>/" --recursive --dryrun
```

Or from the pod, boto3 paginate `Prefix=<exact prefix>` + `delete_objects` in
batches. Deletes are permanent (versioning suspended). Worst case afterwards is
a burst of re-captures as thumbnails repopulate. The lazy alternative: entries
self-expire in ≤15 days.

## Error handling / gotchas

| Symptom | Cause / fix |
|---------|-------------|
| `Unable to locate credentials` after oktaLogin | Creds are in a named profile — `export AWS_PROFILE=<env>` (`aws configure list-profiles` to see them) |
| Laptop delete → AccessDenied | `OktaReadOnlyAccess` is read-only by design; delete via pod IRSA role |
| kubectl heredoc runs but prints nothing | Missing `-i` on `kubectl exec` — stdin never reached python |
| `printenv WORKSPACE_NAME` exits 1 / empty | Expected: multi-tenant deployment; workspace resolves per-request, not via env. Use the S3 prefix from step 2 as ground truth |
| `create_app()` + `app_context()` scripts fail to resolve prefix | Same reason — never rely on app-context config resolution on shell deployments; use explicit keys |
| Unpickle fails with `ModuleNotFoundError: superset` | Old-format payload (pickled class instance, pre-dict). Run the inspect script inside a superset-shell venv or in the pod |
| Digest not found under prefix | Either the entry expired (15-day lifecycle), or the digest is from a `/thumbnail/` URL (model digest, gets re-hashed — compute the real cache key), or a freshly-minted permalink changed the key |

## Related

- `repos/ARCHITECTURE.md` — shell pattern, deployment models
- Code: `superset-shell/preset/config.py` (`DynamicConfigs.thumbs_key_prefix`),
  `superset-shell/preset/cache/s3.py`, `superset-private/superset/utils/screenshots.py`,
  `superset-private/superset/dashboards/api.py` (screenshot endpoints),
  `terraform-live-envs/modules/aws/app_stack/superset_buckets.tf` (bucket + IAM)
