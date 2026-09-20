# Certificates (PX-004)

> Part of **Structa proxy** — Traefik edge and TLS termination for `*.structa.cloud`

Two certificate regimes run side by side.

| Regime | Serves | Issued by | Stored in |
| --- | --- | --- | --- |
| **Production** | real hostnames | Let's Encrypt via **ACME HTTP-01** | `configs/acme.json` |
| **Local development** | `.localhost` hosts | a static self-signed certificate | `data/certs/localhost.{crt,key}` |

There is **no DNS provider token** anywhere in this stack. Issuance is HTTP-01
only, resolved by Traefik natively, with automatic renewal.

## Prerequisites for issuance

1. `configs/acme.json` exists with mode `0600`:
   ```bash
   ./scripts/production/manage-certs.sh bootstrap-acme
   ```
   Mounted read-write at `/etc/traefik/acme/acme.json`.
2. Every hostname has a DNS **A** record pointing at this host.
3. **No off-host `AAAA` record.** If one exists, Let's Encrypt resolves IPv6
   first and validation fails with a TLS internal error — an especially
   confusing failure because the A record looks correct.
4. Port 80 is reachable from the internet.
5. Run the gate first:
   ```bash
   make proxy-dns-check
   ```

## The certificate resolver

Declared once in the static config (`configs/traefik/dynamic.yml`):

```yaml
certificatesResolvers:
  letsencrypt-http:
    acme:
      storage: /etc/traefik/acme/acme.json
      caServer: https://acme-v02.api.letsencrypt.org/directory
      httpChallenge:
        entryPoint: web
```

Site routers opt in with `certResolver: letsencrypt-http`. A router that omits it
serves the default certificate instead — which is exactly the failure
`make proxy-site-check` is built to catch.

## The development certificate

`.localhost` cannot pass public ACME validation, so
`configs/traefik/dynamic/certs.yml` points both the certificate list and the
default store at `data/certs/localhost.crt`.

The subjectAltName list is generated from `LOCAL_CERT_SANS` in the Makefile and
must cover **every `.localhost` vhost the routers declare**:

```
notes.localhost  ops.localhost  precis-lms.localhost  space.localhost  tools.localhost
localhost  127.0.0.1  ::1
```

Keep the Makefile lists and the `certs.yml` comment in sync. A host missing from
the list silently falls back to the default certificate and warns in the browser.

Certificate strategy is switchable:

```bash
make proxy-certs-selfsigned   # static self-signed cert (default for local dev)
make proxy-certs-mkcert       # locally-trusted certs via mkcert
make proxy-certs-default      # remove the static cert, use Traefik's default
make proxy-certs-info         # inspect what is currently configured
```

## Backups

ACME state contains the account private key and every issued certificate.

```bash
./scripts/production/backup-certs.sh     # → data/backups/ (gitignored)
./scripts/production/restore-certs.sh <archive>
```

Verify an archive is readable before relying on it — a truncated tarball fails
silently at restore time.

## Gotchas

- **A stale ACME request for a name with no DNS record** shows up as recurring
  `acme` errors in the log and can prevent a sibling name in the same certificate
  request from validating. `www.crm.structa.cloud` did exactly this: because the
  pair failed, `crm.structa.cloud` was served the **development** certificate.
  Removing the unroutable name let `crm.structa.cloud` obtain its own real cert.
- Deleting an entry from `acme.json` does not stop a router from re-requesting a
  certificate. Remove the *name* from the router, or disable the router file.
- Renewal is automatic; a failure is only visible in the logs.

## Related

- [`PX-003`](./02-routing.md) — where `certResolver` is set per site
- [`PX-006`](./05-validation-and-health-checks.md) — the DNS gate and the cert check
- [`../LETSENCRYPT.md`](../LETSENCRYPT.md) — the long-form runbook
