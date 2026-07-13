# Let's Encrypt (DNS-01) Deployment Runbook

**Scope:** `applications/proxy/traefik/*` and `applications/proxy/docker-compose.traefik.yml` (the local
proxy stack). Production deployment is currently Coolify-managed — see
[Coolify deployment](#coolify-deployment) below.

**Provider:** Cloudflare (DNS-01 challenge)
**Client:** Traefik v3 native `certificatesResolvers` (no external
`dehydrated` / `lego` / `acme.sh` container required)
**Staging strategy:** 3-stage rollout with `applications/proxy/traefik/dynamic/certs.yml`
(self-signed) kept as fallback until the last stage.

---

## Why DNS-01?

- The proxy container is reachable from Cloudflare, but HTTP-01 requires
  port 80 to be reachable from Let's Encrypt directly. DNS-01 works even
  if the box is behind a firewall or WAF that blocks :80 from arbitrary
  internet hosts.
- DNS-01 also covers wildcard certs if we ever need them.

---

## Prerequisites

1. **Cloudflare account** managing the zones for:
   - `ctc-research.com`
   - `structa.cloud`
   - `vresume.structa.cloud`
2. **API token** with `Zone / DNS / Edit` scope, restricted to the three
   zones above. Create at:
   <https://dash.cloudflare.com/profile/api-tokens>
3. **A valid contact email** for the Let's Encrypt account (used for
   expiry notifications). `admin@structa.cloud` is the default.
4. **Docker / docker compose** on the deploy host.

---

## File layout (after this migration)

```
applications/proxy/
├── .env.example                  # template — copy to .env
├── .env                          # gitignored; CF_DNS_API_TOKEN lives here
├── .gitignore                    # excludes .env and acme/acme.json
├── acme/
│   ├── .gitkeep                  # ensures dir is tracked
│   └── acme.json                 # gitignored; mode 0600; LE store
├── certs/                        # legacy self-signed — kept for rollback
├── scripts/
│   └── manage-certs.sh           # bootstrap-acme, status, check-expiry, ...
├── traefik/
│   ├── dynamic.yml               # static config — has certificatesResolvers
│   └── dynamic/
│       ├── vresume.yml           # Stage 1: tls block added
│       ├── ctc-research.yml      # Stage 2
│       ├── structa-cloud.yml     # Stage 2
│       ├── media-servers.yml     # Stage 2
│       ├── dashboard.yml         # Stage 2
│       ├── catchall.yml          # no certResolver (uses Traefik default)
│       ├── middlewares.yml
│       └── certs.yml             # Stage 3: deleted
└── docker-compose.traefik.yml    # local compose — mounts ./acme + env vars
```

---

## Stage 1 (this commit) — verify on `vresume.structa.cloud`

**Goal:** Prove DNS-01 works end-to-end against the **Let's Encrypt
staging** server using a single low-risk site (`vresume.structa.cloud`).
The self-signed certs in `applications/proxy/certs.yml` remain loaded, so if anything
fails we still serve traffic — just with the old self-signed cert.

### 1.1 Local setup

```bash
cd <repo-root>

# 1. Configure credentials
cp applications/proxy/.env.example applications/proxy/.env
$EDITOR applications/proxy/.env           # set CF_DNS_API_TOKEN

# 2. Bootstrap ACME storage (creates ./acme/acme.json, mode 0600)
./applications/proxy/scripts/manage-certs.sh bootstrap-acme

# 3. Confirm files
ls -la applications/proxy/acme/           # acme.json, mode 0600
```

### 1.2 Start the proxy (local compose)

```bash
docker compose -f applications/proxy/docker-compose.traefik.yml up -d
docker logs -f default-proxy | grep -i acme
```

Expected log line on the first https request to `vresume.structa.cloud`:

```
... level=info msg="legolog: [INFO] [vresume.structa.cloud] acme: Obtaining bundled SAN certificate"
... level=info msg="legolog: [INFO] [vresume.structa.cloud] Server responded with a certificate"
```

### 1.3 Verify the staging cert is served

```bash
# Should report a Let's Encrypt staging issuer (Fake LE Intermediate X1 / X2)
echo | openssl s_client -connect vresume.structa.cloud:443 -servername vresume.structa.cloud 2>/dev/null \
  | openssl x509 -noout -issuer -subject -dates
```

Also visit `https://vresume.structa.cloud` in a browser. The browser will
show **"untrusted"** because staging certs aren't trusted by client
trust stores — that's expected and confirms you're hitting a *new* LE
cert rather than the old self-signed one.

### 1.4 Inspect Traefik's store

```bash
./applications/proxy/scripts/manage-certs.sh status
./applications/proxy/scripts/manage-certs.sh check-expiry
```

### 1.5 Rollback (if Stage 1 fails)

```bash
# Drop the tls block from vresume.yml
git checkout -- applications/proxy/traefik/dynamic/vresume.yml
docker compose -f applications/proxy/docker-compose.traefik.yml restart default-proxy
```

The site reverts to the self-signed cert from `certs.yml` — no outage.

---

## Stage 2 — flip to production, enable remaining sites

**Pre-condition:** Stage 1 LE cert verified on `vresume.structa.cloud`.

### 2.1 Switch the static config to the production CA

In `applications/proxy/traefik/dynamic.yml`, **remove** the staging line:

```diff
       email: ${LETSENCRYPT_EMAIL:-admin@structa.cloud}
       storage: /etc/traefik/acme/acme.json
-      # STAGING — remove this line (or set to https://acme-v02.api.letsencrypt.org/directory)
-      # once the vresume test cert is verified.
-      caServer: https://acme-staging-v02.api.letsencrypt.org/directory
       dnsChallenge:
```

If you'd rather keep the line for future staging tests, set it to the
production URL:

```yaml
caServer: https://acme-v02.api.letsencrypt.org/directory
```

Restart: `docker compose -f applications/proxy/docker-compose.traefik.yml restart default-proxy`.

### 2.2 Add `tls: { certResolver: letsencrypt }` to remaining https routers

Files to edit (each `*-https` router — NOT the `*-http` redirect ones):

- `applications/proxy/traefik/dynamic/ctc-research.yml`
  - `ctc-site-https`
  - `ctc-site-media-https`
- `applications/proxy/traefik/dynamic/structa-cloud.yml`
  - `structa-site-https`
  - `structa-media-https`
- `applications/proxy/traefik/dynamic/media-servers.yml`
  - `shared-media-https`
  - `ctc-media-https`
  - `lms-media-https`
  - `vresume-media-https`
- `applications/proxy/traefik/dynamic/dashboard.yml`
  - `traefik-dashboard` (already on `web-secure`; just add the `tls` block)

`catchall.yml`'s routers are intentionally left without `certResolver` —
LE can't issue a cert for a regex host, and Traefik's default cert
gracefully handles unmatched hosts.

### 2.3 Verify

For each of the 9 https routers above (2 ctc-research, 2 structa-cloud,
4 media, 1 dashboard), hit the URL and confirm the issuer is
`Let's Encrypt` (or `R3` / `R10` / `R11`):

```bash
for h in ctc-research.com www.ctc-research.com arch.ctc-research.com \
         structa.cloud www.structa.cloud core.structa.cloud \
         media.structa.cloud media.ctc-research.com \
         media.lms-demo.com media.vresume.structa.cloud \
         traefik.structa.cloud; do
  iss=$(echo | openssl s_client -connect "$h:443" -servername "$h" 2>/dev/null \
        | openssl x509 -noout -issuer 2>/dev/null | sed 's/^issuer=//')
  echo "$h -> $iss"
done
```

All should report a `Let's Encrypt` issuer.

### 2.4 Rollback

`git checkout` the edited files and restart — the self-signed
`certs.yml` is still in place and will pick up the SAN.

---

## Stage 3 — delete the static certs block

**Pre-condition:** All sites on Stage 2 are serving LE certs for at
least 24h and have at least one successful auto-renew (visible in
`./manage-certs.sh check-expiry`).

```bash
git rm applications/proxy/traefik/dynamic/certs.yml
# Optional: keep the on-disk .crt/.key files for emergency rollback
#   - they are no longer referenced by Traefik
git commit -m "chore(proxy): drop static self-signed certs (LE migration complete)"
docker compose -f applications/proxy/docker-compose.traefik.yml restart default-proxy
```

After Stage 3, the only cert path is `applications/proxy/acme/acme.json`.

---

## Local compose

Already wired in `applications/proxy/docker-compose.traefik.yml`:

- `./acme:/etc/traefik/acme:rw` volume mount
- `CF_DNS_API_TOKEN`, `CF_API_EMAIL`, `CF_API_KEY`, `LETSENCRYPT_EMAIL`
  env vars sourced from `applications/proxy/.env` (or `${VAR:-}` defaults)

---

## Coolify deployment

The production proxy is currently `default-proxy` managed by Coolify
(see `core/docker-compose.yml` comment "Traefik → managed by
Coolify"). To keep Coolify in sync with the local compose:

1. In the Coolify UI for `default-proxy`:
   - **Add volume mount**: `./acme → /etc/traefik/acme` (read-write)
   - **Add environment variables**:
     - `CF_DNS_API_TOKEN` (Secret, scope restricted to the resource)
     - `LETSENCRYPT_EMAIL` (Plain)
   - **Sync** the `applications/proxy/traefik/dynamic.yml` and `applications/proxy/traefik/dynamic/*.yml`
     files to whatever directory Coolify mounts at `/etc/traefik/`.
     (Coolify typically reads from a configured git source — make sure
     this repo (or a deploy mirror) is the source.)
2. SSH to the Coolify host and bootstrap the on-disk acme.json:
   ```bash
   cd /data/coolify/proxy          # or wherever Coolify mounts configs
   ./scripts/manage-certs.sh bootstrap-acme
   docker restart default-proxy
   ```
3. Follow Stages 1 → 2 → 3 from above.

---

## Troubleshooting

### `acme: error: 400 :: urn:ietf:params:acme:error:dns :: DNS problem: NXDOMAIN`

Cloudflare couldn't find the `_acme-challenge` TXT record. Usually
means the API token doesn't have DNS edit scope for the zone, or the
zone isn't on Cloudflare.

### `acme: error: 403 :: ...`

API token is missing or wrong scope. Regenerate at
<https://dash.cloudflare.com/profile/api-tokens> with
`Zone / DNS / Edit` restricted to the relevant zone(s).

### Staging vs production — which am I on?

```bash
# staging issuer contains "Fake" or "STAGING"
echo | openssl s_client -connect <host>:443 -servername <host> 2>/dev/null \
  | openssl x509 -noout -issuer
# Production issuer is "Let's Encrypt" with R3 / R10 / R11
```

### Rate limits

Let's Encrypt has aggressive rate limits (5 duplicate certs per week
per domain). Always test on the **staging** server (which has much
higher limits) before flipping to production.

### `LETSENCRYPT_EMAIL` must be set

The `email` field in `certificatesResolvers` is required for ACME
account registration. The static config uses
`${LETSENCRYPT_EMAIL:-admin@structa.cloud}`; the docker-compose passes
the env var through with a non-empty default, so this is safe in
normal operation. If you run Traefik outside of docker-compose, make
sure `LETSENCRYPT_EMAIL` is exported in the shell before starting it.

### acme.json is empty after restart

The `acme.json` file must exist with mode `0600` **before** the
container starts. If it doesn't, Traefik will create it on first
write, but if the host filesystem doesn't allow the right mode
(e.g. tmpfs with default umask) the container will fail to read it.
Run `./scripts/manage-certs.sh bootstrap-acme` to be safe.

### Rollback from a failed LE cert

Until Stage 3, just revert the `tls:` block from the affected
router file. After Stage 3, you have to either re-add a static
certs.yml block or restore acme.json from `./acme/backups/`.

---

## References

- [Traefik ACME / Let's Encrypt docs](https://doc.traefik.io/traefik/https/acme/)
- [Traefik DNS-01 challenge](https://doc.traefik.io/traefik/https/acme/#dnschallenge)
- [Cloudflare API tokens](https://dash.cloudflare.com/profile/api-tokens)
- [Let's Encrypt rate limits](https://letsencrypt.org/docs/rate-limits/)
