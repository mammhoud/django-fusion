# Operations (PX-005)

> Part of **Structa proxy** — Traefik edge and TLS termination for `*.structa.cloud`

## Routine commands

```bash
make help          # annotated target list
make status        # what is running
make logs          # tail proxy logs (watch for `acme` errors)
make validate      # gate: validate every dynamic config
make restart       # apply dynamic config changes without dropping connections
make deploy        # proxy-validate → proxy-up
```

`make deploy` runs `proxy-validate` first, so a config that fails validation
cannot reach a running edge.

## Which action applies my change?

| Change | Action |
| --- | --- |
| Router, service, middleware, TLS store | `make validate && make restart` — file watcher, no downtime |
| Entrypoints, ACME resolver, dashboard | `make up` — recreate; static config is read at start |
| `Dockerfile` | `make build && make up` |

## Before and after every change

```bash
# Before
make validate
make proxy-dns-check      # only when a new hostname is involved

# After
make proxy-site-check     # status + certificate per route
```

## Rollback

Each site has its own file, so a bad change rolls back by reverting **one file**:

```bash
git checkout -- configs/traefik/dynamic/<site>.yml
make validate && make restart
```

Parking a site without deleting it: rename the file to `<site>.yml.disabled`. The
file provider only reads `*.yml`, so `precis-dev.yml.disabled` is inert until
renamed back. That is how `dev.structa.cloud` is kept out of rotation while its
routers remain reviewable.

## Interpreting failures

| Observation | Meaning |
| --- | --- |
| `502`/`503` for one host | Backend not reachable — usually not on the `common` network |
| Brief `502` → `503` **during** a container recreate | Health-check interval catching up; verify with `make status`, not by editing config |
| Browser cert warning on a `.localhost` host | Host missing from `LOCAL_CERT_SANS` |
| A host serving the **dev** certificate | Its router has no `certResolver`, or a sibling name in the same request failed validation |
| Recurring `acme` errors in `make logs` | A routed name has no DNS record, or has an off-host `AAAA` |
| Everything down on 80 and 443 | The proxy is not running. Check `make status` and whether something else binds those ports |

## Networks

`traefik-net` and `common` are declared `external: true` — compose will not create
them. If a deploy fails with "network not found":

```bash
docker network create traefik-net
docker network create common
```

Confirm a backend is reachable **from a peer on `common`**, which isolates routing
problems from application problems:

```bash
docker run --rm --network common curlimages/curl -fsS http://<container>:<port>/health
```

## Certificate operations

See [`PX-004`](./03-certificates.md). Back up ACME state before any risky change.

## Related

- [`PX-002`](./01-architecture.md) — static vs dynamic
- [`PX-006`](./05-validation-and-health-checks.md) — the gates in detail
