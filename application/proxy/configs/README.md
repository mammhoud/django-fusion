# `configs`

> Part of **Structa proxy** — Traefik edge and TLS termination for `*.structa.cloud`

Everything the edge proxies are configured from. Two engines live here: Traefik
(the default, and the one that terminates TLS for production) and Caddy (an
optional alternative stack). Nothing in this directory is generated — it is all
hand-maintained and validated in CI-equivalent form by
`scripts/validate-traefik-config.py`.

## Contents

- `traefik/` - static config plus the dynamic router directory
- `caddy/` - optional Caddy edge (not active by default)
- `acme.json` - **runtime** ACME storage (gitignored; bind-mounted read-write)
- `.gitkeep` - keeps the directory present so bind mounts resolve

## Public API

- `traefik/dynamic.yml` - Traefik **static** configuration (entrypoints, providers, ACME resolver)
- `traefik/dynamic/*.yml` - Traefik **dynamic** configuration, one file per site
- `caddy/Caddyfile` - Caddy entrypoint

## Usage

```bash
# Validate every dynamic config before touching a running edge
make validate

# Reload without dropping connections
make restart
```

## Related

- [`traefik/README.md`](./traefik/README.md) — Traefik static vs dynamic split
- [`caddy/README.md`](./caddy/README.md) — the optional Caddy stack
- [`../LETSENCRYPT.md`](../LETSENCRYPT.md) — certificate issuance runbook
- [`../docs/INDEX.md`](../docs/INDEX.md) — full documentation map
