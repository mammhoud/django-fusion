# Pro Edition — Local Completion Record

**Canonical product:** `projects/formints/formint-pro/`
**Legacy aliases:** `pos-full`, `pos-solo`, and `formint/` are compatibility names only.

**Status:** Local work complete (Standard-parity `Currency`/`TaxProfile` models
+ migration + Ninja CRUD, read-only CSV/JSON export, regression tests, and
scoped API-key enforcement preserved). Only environment/operator-gated items
remain.

## Remaining work

- [ ] Pro `make check` — BLOCKED: `server/.venv/bin/python3` is absent in this checkout.
- [ ] Pro `make test` — BLOCKED: same missing local Python environment.

After the repository owner provisions the existing Pro environment, run:

```bash
cd projects/formints/formint-pro
make check
make test
```

External publishing, release tags, and git commits remain owner actions.
