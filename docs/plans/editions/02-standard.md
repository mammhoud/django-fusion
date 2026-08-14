# Standard Edition — Local Completion Record

**Canonical source:** `projects/formints/formint-standard/`

**Status:** Local implementation complete (multi-currency, tax profiles, role
permissions, CSV/JSON export, offline sync queue, contract/build fixes). An
online server is optional and not required for core operation. Only
environment/operator-gated items remain.

## Remaining work

- [ ] Full browser/E2E suite — requires a desktop/browser runtime (environment
  gate only; not a missing Standard product feature).

## Optional / external work intentionally left pending

- Django sidecar sync endpoints and large-dataset async exports are additive
  integrations, not required for Standard's local contract.
- Release packaging, signing, publishing, and remote commits remain operator
  actions and are prepared locally only.
