# `configs/traefik`

> Part of **Structa proxy** — Traefik edge and TLS termination for `*.structa.cloud`

Traefik configuration, split the way Traefik itself requires:

| Kind | File | Mounted to | Reloaded by |
| --- | --- | --- | --- |
| **Static** | `dynamic.yml` | `/etc/traefik/dynamic.yml` | container restart only |
| **Dynamic** | `dynamic/*.yml` | `/etc/traefik/dynamic` | file watcher, live |

The static file is copied into the image by the `Dockerfile`; the dynamic
directory is bind-mounted read-only by `docker-compose.traefik.yml`. That is why
a router change only needs `make restart` and never a rebuild, while a change to
entrypoints or the ACME resolver needs the container recreated.

`dynamic.yml` declares: `web` (:80, permanently redirecting to `web-secure`) and
`web-secure` (:443) entrypoints, the file provider pointed at
`/etc/traefik/dynamic` with `watch: true`, the API/ping endpoint on :8080, and
the `letsencrypt-http` ACME resolver (HTTP-01, no DNS tokens).

## Contents

- `dynamic.yml` - Traefik static configuration
- `dynamic/` - dynamic routers, one file per site

## Public API

- **Entrypoints:** `web` (:80), `web-secure` (:443), dashboard/ping (:8080)
- **Provider:** file provider rooted at `/etc/traefik/dynamic`, watch enabled
- **Cert resolver:** `letsencrypt-http` (ACME HTTP-01, storage `/etc/traefik/acme/acme.json`)

## Usage

```bash
# Static config change (entrypoints, resolver) → needs a recreate
make up

# Dynamic config change (routers, middlewares) → file watcher picks it up
make validate && make restart
```

## Gotchas

- `configs/traefik/dynamic.yml` is the **static** config despite the name; the
  dynamic configs are the files *inside* `dynamic/`.
- `configs/acme.json` must exist with mode `0600` before the container starts,
  otherwise the ACME resolver fails to initialise. Create it with
  `./scripts/production/manage-certs.sh bootstrap-acme`.
- A DNS record pointing off-host — including a stray `AAAA` — breaks HTTP-01.
  Run `make proxy-dns-check` before triggering issuance.
