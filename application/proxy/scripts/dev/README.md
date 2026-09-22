# `scripts/dev`

> Part of **Structa proxy** — Traefik edge and TLS termination for `*.structa.cloud`

Local-development helpers. Nothing here touches production: these produce the
self-signed certificate that lets the `.localhost` vhosts come up over HTTPS
without a browser warning.

## Contents

- `generate-certs.sh` - generates a self-signed certificate bundle into `data/certs/`

## Public API

- `generate-certs.sh [production|staging]` — writes PEM/crt/key bundles with the
  correct CN per host

## Usage

```bash
# Preferred: go through make, which also syncs the SAN list
make proxy-certs-selfsigned

# Direct invocation
./scripts/dev/generate-certs.sh production
```

## Notes

- The SAN list is duplicated in the Makefile as `LOCAL_HOSTS` / `LOCAL_CERT_SANS`
  because `configs/traefik/dynamic/certs.yml`'s default certificate points at
  `localhost.crt`. Keep the two in sync — a vhost missing from the list silently
  gets the default certificate and warns in the browser.
- To step back from self-signed certs, use
  `make proxy-certs-default` (removes the static cert) or
  `make proxy-certs-mkcert` (locally trusted via mkcert).
