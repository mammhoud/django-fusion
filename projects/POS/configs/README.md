# Formint configuration contracts

This directory contains product-level configuration metadata shared by the
Formint editions. It does not replace an edition’s runtime settings module.

## Files

- `assets.yml` — shared asset roots, frontend aliases/public directories,
  backend static input, and edition overlays.

## Precedence

1. The contract in this directory defines stable repository paths.
2. Each frontend/backend resolves the contract relative to its own location.
3. Environment variables override runtime paths where supported, especially
   `FORMINT_SHARED_ASSETS`, backend URLs, and Django settings.
4. Build output remains owned by the edition that produced it.

Keep YAML metadata path-only and secret-free. Credentials, databases, and
runtime-generated manifests must stay in the owning edition’s environment or
ignored output directories.
