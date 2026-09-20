# `scripts`

> Part of **Structa proxy** — Traefik edge and TLS termination for `*.structa.cloud`

Operational tooling for the edge. The three Python scripts here are wired into
`make` targets and are the gate between editing a config and applying it:

| Script | Make target | Purpose |
| --- | --- | --- |
| `validate-traefik-config.py` | `make validate` | Parse every file under `configs/traefik/dynamic/`, resolve routers against services and middlewares, fail on dangling references. |
| `check-dns-records.py` | `make proxy-dns-check` | Pre-issuance gate: every host in the routers must resolve to this server, and a stray `AAAA` that points elsewhere is a failure (it makes Let's Encrypt validate over IPv6 and fail). |
| `check-site-health.py` | `make proxy-site-check` | Post-apply gate: HTTP status per route **and** whether the TLS certificate a host actually serves is real and covers that name — catches a site silently falling back to the dev certificate. |

All three use the Python standard library only, so they run on a bare host with
no virtualenv. All three exit non-zero on failure, which is what makes them
usable as a deploy gate.

## Contents

- `validate-traefik-config.py` - router/service/middleware reference validation
- `check-dns-records.py` - DNS pre-issuance gate
- `check-site-health.py` - post-apply HTTP + certificate check
- `dev/` - local development helpers
- `production/` - certificate and ACME lifecycle operations

## Public API

- `validate-traefik-config.py [--config-dir DIR] [--quiet]`
- `check-dns-records.py [--json]`
- `check-site-health.py [--host HOST ...] [--timeout SECONDS] [--json]`

## Usage

```bash
make validate              # before applying a router change
make proxy-dns-check       # before requesting a certificate
make proxy-site-check      # after applying, to confirm status + cert
```

## Conventions

- Stdlib-only, no third-party imports.
- `--quiet`/`--json` for machine consumption; human output otherwise.
- Non-zero exit for any failure, including stale/missing documentation.
