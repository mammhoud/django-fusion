# FileGator — shared media file manager

Self-hosted file manager served at **`https://media.structa.cloud/filegator/`**
behind the `shared-media` nginx (see `../nginx/default.conf`). Uses the
official `filegator/filegator:latest` image. Docs: https://docs.filegator.io/

## Deployment

The repository bind-mount target `projects/assets/media/filegator/` ships
in git (via `.gitkeep`) so Docker does **not** auto-create it as
`root:root`. On a **fresh clone**, ensure it is owned by the container's
`www-data` (uid 33) before first start, or FileGator cannot write uploads:

```bash
mkdir -p projects/assets/media/filegator
chown -R 33:33 projects/assets/media/filegator   # www-data
cd applications/proxy
docker compose -f docker-compose.nginx.yml up -d filegator shared-media
```

Routing chain: Traefik → `shared-media` nginx (`location /filegator/`) →
`filegator` container (port 8080). The SPA serves relative asset paths and
builds its API base from `window.location.pathname`, so no asset rewriting
is needed under the subpath.

## Files

| Path | Purpose |
|---|---|
| `docker-compose.nginx.yml` | `filegator` service (8080, volumes, healthcheck) |
| `nginx/default.conf` | `/filegator/` proxy + `/filegator` → `/filegator/` redirect |
| `configuration.php` | Hardened config: randomized `csrf_key`, `cookie_secure=true`, 100 MB uploads, UTC |
| `users.json` | Admin credentials — **version-controlled** so a fresh volume cannot regenerate the baked `admin/admin123` default |

## Credentials

- **Username:** `admin`
- **Password:** `u6OC3hHE5Zaa2NXP`

The bcrypt hash lives in `users.json`, which is bind-mounted read-write into
`/var/www/filegator/private/users.json`. UI user-management edits write back
to the repo file. The default guest account is disabled (no permissions).

> **Rotating the password:** generate a new hash with
> `docker run --rm --entrypoint php filegator/filegator:latest -r "echo password_hash('<pw>', PASSWORD_BCRYPT);"`
> and replace the `password` value in `users.json`, then
> `docker compose -f docker-compose.nginx.yml restart filegator`.

## Volumes & shared media

- **Repository** — bind-mounted to the **shared media tree** at
  `projects/assets/media/filegator` (`/var/www/filegator/repository` in the
  container, owned by www-data uid 33). `shared-media` mounts the same host
  directory at `/var/www/media/filegator:ro`, so anything uploaded through
  FileGator is immediately public at
  **`https://media.structa.cloud/media/filegator/<path>`** — no extra
  configuration needed.
- `filegator-private` — logs + sessions (`/var/www/filegator/private`)

Both persist independently of the containers; only `users.json` and
`configuration.php` are bind-mounted from this directory.

## Scripting uploads (API contract)

The API is reached through the same nginx route: `POST /filegator/?r=<route>`.
Two gotchas worth knowing:

1. **Route names must be slash-prefixed** (`?r=/login`, `?r=/upload`). The SPA
   joins routes with a leading `/` against its `...?r=` base, and the backend
   matches FastRoute paths exactly — `?r=login` returns a JSON 404.
2. **Uploads use the resumable.js contract.** A single-chunk upload must send
   `resumableChunkNumber=1`, `resumableTotalChunks=1`, `resumableTotalSize`,
   `resumableChunkSize`, `resumableCurrentChunkSize`, `resumableFilename`,
   `resumableRelativePath` (destination dir, `/` for root), `resumableIdentifier`,
   plus the `file` part — or the server never assembles the final file and
   errors on a missing tmp stream.

Minimal working flow (session cookie jar required):

```bash
BASE=https://media.structa.cloud/filegator/?r=
JAR=/tmp/fg.jar
# 1. Bootstrap session (captures cookie + X-CSRF-Token header)
curl -sk -c "$JAR" -D - -o /dev/null https://media.structa.cloud/filegator/ \
  | grep -i '^x-csrf-token:' | tr -d '\r' | awk '{print $2}' > /tmp/fg.csrf
TOKEN=$(cat /tmp/fg.csrf)
# 2. Login (slash-prefixed route) — password from Credentials section above
curl -sk -b "$JAR" -c "$JAR" -H "X-CSRF-Token: $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"<admin-password>"}' \
  "${BASE}/login"
# 3. Upload (resumable contract) -> body: {"data":"Stored"}
curl -sk -b "$JAR" -H "X-CSRF-Token: $TOKEN" \
  -F resumableChunkNumber=1 -F resumableTotalChunks=1 \
  -F resumableTotalSize=$(stat -c%s /tmp/foo.png) -F resumableChunkSize=1048576 \
  -F resumableCurrentChunkSize=$(stat -c%s /tmp/foo.png) \
  -F resumableFilename=foo.png -F resumableRelativePath=/ \
  -F resumableIdentifier=foo-$(date +%s) \
  -F 'file=@/tmp/foo.png' "${BASE}/upload"
# Uploaded file is instantly public:
#   https://media.structa.cloud/media/filegator/foo.png
```
