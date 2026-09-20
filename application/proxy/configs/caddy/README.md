# `configs/caddy`

> Part of **Structa proxy** — Traefik edge and TLS termination for `*.structa.cloud`

An **optional** Caddy edge. Traefik is the default and the only engine that
serves production; this stack exists as an alternative front door and is not
started by `make up` — `docker-compose.caddy.yml` is commented out of
`docker-compose.yml` and would need uncommenting *and* a port change (it binds
8081/8443, so it can run alongside Traefik rather than instead of it).

## Contents

- `Caddyfile` - active entrypoint; imports `/dynamic/*.caddy`
- `Caddyfile-main` - standalone Coolify-oriented example config, not imported
- `default_redirect_503.yaml` - Traefik-shaped fallback config kept for the 503 redirect case

## Public API

- `Caddyfile` — the file Caddy actually loads (`./Caddyfile:/etc/caddy/Caddyfile`)
- `Caddyfile-main` — reference only; nothing mounts it

## Usage

```bash
# Enable the optional stack (edit docker-compose.yml to uncomment the include)
docker compose -f docker-compose.caddy.yml up -d
```

## Notes

- `Caddyfile` imports `/dynamic/*.caddy`, but **no `.caddy` files are committed** —
  the import is currently a no-op, so the container would serve only Caddy's
  defaults until a dynamic file is added.
- `default_redirect_503.yaml` uses the old `http`/`https` entrypoint names and a
  `letsencrypt` resolver; it is Traefik-format, kept alongside for reference and
  **not** loaded by the Traefik file provider (which only reads
  `configs/traefik/dynamic/`).
