# Loop-CRM Setup & Build

The canonical step-by-step setup guide lives in the product repo:

> [**`projects/loop-crm/docs/SETUP_AND_BUILD.md`**](../../projects/loop-crm/docs/SETUP_AND_BUILD.md)

Quick reference:

```bash
cd projects/loop-crm
make dev              # Astro frontend dev server
make backend-dev      # Django dev server
make backend-migrate  # apply migrations
make backend-seed     # seed demo workspace (demo@loop.dev / demo-pass-123)
make check            # frontend typecheck
make backend-check    # Django system checks
```

Requires `uv sync` at the repo root for Python deps and `npm install` inside
`projects/loop-crm/frontend` for the Astro shell. Nx targets (`make nx-check`)
need the root `npm install` as well.

See the [Loop-CRM index](README.md) for the full command reference and env
configuration.

## Remarks & Notes

- This page is a pointer only — edit `SETUP_AND_BUILD.md` in the product repo, not here.
