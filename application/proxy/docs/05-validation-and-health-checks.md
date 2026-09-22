# Validation and Health Checks (PX-006)

> Part of **Structa proxy** — Traefik edge and TLS termination for `*.structa.cloud`

Three checks guard the edge. Each catches a failure the others cannot, and each
exits non-zero, which is what makes them usable as a deploy gate.

| Check | Target | Runs | Catches |
| --- | --- | --- | --- |
| `validate-traefik-config.py` | `make validate` | before applying | Dangling service/middleware references, malformed YAML, missing router fields |
| `check-dns-records.py` | `make proxy-dns-check` | before requesting a certificate | Missing A records, off-host `AAAA` records |
| `check-site-health.py` | `make proxy-site-check` | after applying | Wrong HTTP status, and a host silently serving the **wrong certificate** |

All three are Python standard library only, so they run on a bare host with no
virtualenv.

## Validate

```bash
make validate
python3 scripts/validate-traefik-config.py            # direct
python3 scripts/validate-traefik-config.py --quiet    # exit code only
```

Walks `configs/traefik/dynamic/` and checks that every router's `service` and
`middlewares` resolve, that entries referenced across files exist, and that each
router declares the fields Traefik requires.

> **Why this gate exists in this shape:** it previously globbed the wrong
> directory and validated **zero files**, always exiting 0 — while `make deploy`
> used it as its gate. A green check meant nothing. It now validates every config
> in the directory, so adding a file automatically brings it under validation.

## DNS gate

```bash
make proxy-dns-check
python3 scripts/check-dns-records.py --json
```

Reads every hostname out of the routers and requires it to resolve to this
server. A second pointing address — specifically an off-host `AAAA` — is a
**failure**, because Let's Encrypt prefers IPv6 when validating HTTP-01 and will
fail against a host that is not serving.

Run it whenever you add a hostname, and **before** expecting a certificate.

## Site health and certificate check

```bash
make proxy-site-check
python3 scripts/check-site-health.py --host notes.structa.cloud
python3 scripts/check-site-health.py --json --timeout 15
```

For each route this reports:

1. the HTTP status, and
2. whether the certificate the host actually presents is trustworthy **and covers
   that host's own name**.

The second half is the point. A host can return 200 while serving the shared
development certificate — that is exactly what happened to `crm.structa.cloud`,
where an unroutable sibling name (`www.crm.structa.cloud`) failed the ACME
request for the pair and the whole site quietly fell back to the self-signed cert.
Status-only monitoring would have called that healthy.

When the certificate is untrusted, the script decodes the presented DER rather
than relying on Python's parsed dict, so it can still list **which** names the bad
certificate covers — the most useful diagnostic in that situation.

## When to run what

| Situation | Command |
| --- | --- |
| Editing any router | `make validate` |
| Adding a hostname | `make validate && make proxy-dns-check` |
| After a restart | `make proxy-site-check` |
| Suspected cert problem | `python3 scripts/check-site-health.py --host <host>` |
| Wondering if a check still works | break a config deliberately and confirm the check fails |

That last one is not a joke: a validation gate that cannot fail is worse than no
gate, which is precisely how the validator bug above survived.

## Related

- [`PX-003`](./02-routing.md) — adding a site, step by step
- [`PX-004`](./03-certificates.md) — certificates
- [`../scripts/README.md`](../scripts/README.md) — script inventory
