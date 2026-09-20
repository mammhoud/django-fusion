# `scripts/production`

> Part of **Structa proxy** — Traefik edge and TLS termination for `*.structa.cloud`

Certificate and ACME lifecycle operations. Production certificates are obtained
by Traefik itself over Let's Encrypt **HTTP-01** — there is no DNS provider token
anywhere in this stack — so these scripts exist to bootstrap, back up, restore
and audit the ACME storage rather than to issue anything.

> The ACME account key and issued certificates live in
> `configs/acme.json`, which is **gitignored** and mounted read-write at
> `/etc/traefik/acme/acme.json`. A backup tarball contains private keys.

## Contents

- `manage-certs.sh` - primary entrypoint: `bootstrap-acme`, plus inspect/rotate helpers
- `backup-certs.sh` - archive the ACME storage and any manual certs
- `cert-backup.sh` - lighter-weight certificate backup helper
- `restore-certs.sh` - restore from a backup produced by the scripts above

## Public API

- `manage-certs.sh bootstrap-acme` — create `configs/acme.json` with mode `0600`
  (required before the proxy container's first start)
- `manage-certs.sh` (other subcommands) — inspect / rotate ACME state
- `backup-certs.sh`, `restore-certs.sh` — archive and restore under `data/backups/` (gitignored)

## Usage

```bash
# One-time, before the first proxy start
./scripts/production/manage-certs.sh bootstrap-acme

# Before any risky change
./scripts/production/backup-certs.sh

# Restore
./scripts/production/restore-certs.sh <archive>
```

## Notes

- Run `make proxy-dns-check` before triggering issuance. A missing record or an
  off-host `AAAA` is the usual cause of a failed HTTP-01 challenge.
- Backups land in `data/backups/`, which is gitignored. Verify the archive is
  readable before relying on it; a truncated tarball is a silent failure at
  restore time.
