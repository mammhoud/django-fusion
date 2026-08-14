# Formints JS/TS Client Bundle — Local Completion Record

**Canonical package:** `projects/formints/packages/formints-client/`  
**Consumer:** `projects/formints/formint-cloud/frontend/`

## Contract

`@formints/client` is a framework-agnostic, fetch-only TypeScript package for
Standard/Cloud API surfaces. It has no runtime dependencies and emits ESM plus
`.d.ts` files through the package exports map.

## Completed local work

- [x] Core `createClient(baseUrl)` and `ApiError` implementation.
- [x] Currency module: `listCurrencies`, `createCurrency`.
- [x] Tax module: `listTaxProfiles`.
- [x] Export module: `exportUrl` for products, sales, customers, and inventory
  in CSV or JSON mode.
- [x] Monitor module: `getMonitorStatus` with typed backup and queue payload.
- [x] Barrel exports and subpath exports for every module.
- [x] Cloud frontend consumes the monitor module through its telemetry surface.

## Verification

```bash
cd projects/formints/packages/formints-client
pnpm test       # 6 tests passed
pnpm typecheck  # passed
pnpm build      # passed; ESM + declaration output generated
```

Framework neutrality and the no-runtime-dependency constraint are preserved.
No publishing, registry release, or git commit was performed; those remain
repository-owner actions.
