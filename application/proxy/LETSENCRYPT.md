# Let's Encrypt (HTTP-01) Deployment Runbook

**Scope:** `application/proxy/configs/traefik/*` and `application/proxy/docker-compose.traefik.yml`
(the `default-proxy` Traefik stack).

**Provider:** Let's Encrypt — HTTP-01 challenge (`letsencrypt-http`). **No DNS
provider token is required.** DNS for `structa.cloud` is hosted at Hostinger
(`ns1/ns2.dns-parking.com`), not Cloudflare.

**Client:** Traefik v3 native `certificatesResolvers` (no external
`dehydrated` / `lego` / `acme.sh` container required).

---

## DNS topology

`structa.cloud` is the apex domain and points directly at this server. Every
product subdomain is a `CNAME` to `structa.cloud`, so it inherits the apex A
and AAAA records:

```text
structa.cloud            A      187.77.166.222          (this server, IPv4)
structa.cloud            AAAA   2a02:4780:28:4cb8::1    (this server, IPv6 — or leave unset)
space.structa.cloud      CNAME  structa.cloud
docs.structa.cloud       CNAME  structa.cloud
media.structa.cloud      CNAME  structa.cloud
```

Because the subdomains are CNAMEs, fixing the **single** apex A/AAAA record
fixes every subdomain at once.

> **Retired aliases — remove from DNS:** `coder.structa.cloud` and
> `code.structa.cloud` no longer have Traefik routers (the workspace control
> plane is served at `space.structa.cloud`). Delete their `CNAME` records at
> Hostinger to stop the stale resolvers; they are not checked by
> `check-dns-records.py` and serve no cert.

---

## Why HTTP-01?

- The proxy binds `0.0.0.0:80` / `[::]:80` on the public host, and port 80 is
  reachable from Let's Encrypt, so HTTP-01 issues certs directly with no
  external credential.
- No API token, no DNS provider integration, no wildcard requirement.

---

## Prerequisites

1. DNS at Hostinger (hPanel → DNS / Nameservers):
   - apex `A` → `187.77.166.222`
   - apex `AAAA` → `2a02:4780:28:4cb8::1` (this host's IPv6), **or delete the
     AAAA record entirely** so Let's Encrypt uses IPv4.
   - each product subdomain → `CNAME structa.cloud`
2. `application/proxy/configs/acme.json` exists with mode `0600` (run
   `./scripts/production/manage-certs.sh bootstrap-acme`).
3. Inbound TCP 80/443 open on the host firewall / hosting security group.
4. A valid contact email for the Let's Encrypt account (used for expiry
   notifications). `admin@structa.cloud` is the default.

---

## Pre-issuance DNS gate

Before triggering issuance, resolve every HTTP-01 domain and confirm the
records point at this host:

```bash
make -C application/proxy proxy-dns-check
# or: python3 application/proxy/scripts/check-dns-records.py
```

Exit `0` means all domains resolve to this host. Any off-host A/AAAA or
NXDOMAIN is printed and the command exits non-zero.

---

## File layout

```text
application/proxy/
├── .env.example                  # template — copy to .env (optional; no tokens needed)
├── .env                          # gitignored; LETSENCRYPT_EMAIL + DB passwords
├── .gitignore                    # excludes .env and configs/acme.json
├── configs/
│   ├── acme.json                 # gitignored; mode 0600; LE store
│   └── traefik/
│       ├── dynamic.yml           # static config — certificatesResolvers
│       └── dynamic/
│           ├── space.yml         # space.structa.cloud / space.localhost (Coder)
│           ├── docs.yml          # docs.structa.cloud
│           └── ...               # one file per product host
│                               (affine.yml + dashboard.yml removed 2026-08-21
│                                as dead: legacy alias + no-DNS dashboard)
├── data/
│   └── certs/                    # local mkcert/self-signed fallback for .localhost
├── scripts/
│   ├── check-dns-records.py      # pre-issuance DNS gate
│   ├── validate-traefik-config.py
│   └── production/manage-certs.sh # bootstrap-acme, status, check-expiry
└── docker-compose.traefik.yml    # local compose — mounts ./configs/acme.json
```

---

## Local setup

```bash
cd <repo-root>

# 1. (Optional) configure the ACME contact email
cp application/proxy/.env.example application/proxy/.env
$EDITOR application/proxy/.env           # set LETSENCRYPT_EMAIL (no token required)

# 2. Bootstrap ACME storage (creates ./configs/acme.json, mode 0600)
./application/proxy/scripts/production/manage-certs.sh bootstrap-acme

# 3. Start the proxy
docker compose -f application/proxy/docker-compose.traefik.yml up -d
docker logs -f default-proxy | grep -i acme
```

On the first HTTPS request to a configured host, Traefik runs the HTTP-01
challenge and stores the cert in `acme.json`.

---

## Verify the certificate is served

```bash
for h in space.structa.cloud docs.structa.cloud structa.cloud; do
  iss=$(echo | openssl s_client -connect "$h:443" -servername "$h" 2>/dev/null \
        | openssl x509 -noout -issuer 2>/dev/null | sed 's/^issuer=//')
  echo "$h -> $iss"
done
```

All should report `Let's Encrypt` (or `R3` / `R10` / `R11`).

Inspect the store:

```bash
./application/proxy/scripts/production/manage-certs.sh status
./application/proxy/scripts/production/manage-certs.sh check-expiry
```

---

## Troubleshooting

### `acme: error: tls :: <ipv6>: ... remote error: tls: internal error`

Let's Encrypt resolved the hostname to an IPv6 address that is **not this
server**, followed the HTTP→HTTPS redirect on the wrong box, and failed the
TLS handshake.

Root cause: the apex `structa.cloud` has an `AAAA` record pointing at a
Hostinger edge (`2a02:4780:41:3f58::1`) instead of this host's IPv6
(`2a02:4780:28:4cb8::1`). Because the subdomains are `CNAME structa.cloud`,
they inherit the wrong record and lego tries IPv6 first.

Fix (Hostinger hPanel → DNS): set the apex `AAAA` to
`2a02:4780:28:4cb8::1`, **or** delete it so Let's Encrypt falls back to the
`A` record `187.77.166.222`.

Then reload:

```bash
docker restart default-proxy
```

### `acme: error: dns :: DNS problem: NXDOMAIN`

The domain has no public A record, so Let's Encrypt can't route the challenge.
Add the `A` record (or a `CNAME` to `structa.cloud`) and re-check.

### Rate limits

Let's Encrypt has aggressive rate limits (5 duplicate certs per week per
domain). Use the pre-issuance DNS gate and fix DNS before triggering repeated
issuance attempts.

### acme.json is empty after restart

`acme.json` must exist with mode `0600` **before** the container starts. Run
`./scripts/production/manage-certs.sh bootstrap-acme`, then start the proxy
and hit an HTTPS endpoint to trigger issuance.

### `LETSENCRYPT_EMAIL` must be set

The resolver `email` field is required for ACME account registration. The
static config uses `structa.cloud@gmail.com`; the compose file passes
`LETSENCRYPT_EMAIL` through with an `admin@structa.cloud` default, so this is
safe in normal operation.

---

## References

- [Traefik ACME / Let's Encrypt docs](https://doc.traefik.io/traefik/https/acme/)
- [Traefik HTTP-01 challenge](https://doc.traefik.io/traefik/https/acme/#httpchallenge)
- [Let's Encrypt rate limits](https://letsencrypt.org/docs/rate-limits/)
