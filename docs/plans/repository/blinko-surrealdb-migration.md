# Blinko — Prisma → SurrealDB Migration (Auth-First Milestone)

> **Tags:** #blinko #migration #surrealdb #prisma
> **Last updated:** 2026-08-26 | **Status:** Proposed
> **Scope:** Incremental migration of the `mammhoud/blinko` backend from Prisma/PostgreSQL to SurrealDB, starting with accounts/auth.
> **Repo:** vendored checkout at `application/tools/blinko/blinko/` (own git repo, branch `main`, origin `https://github.com/mammhoud/blinko`)

---

## 1. Purpose

Add SurrealDB as a supported datastore for the Blinko server and prove it out by
moving the **accounts/auth** flows (login, register, OAuth, 2FA, profile, token
regen) onto a Surreal-backed repository adapter. Everything else stays on
Prisma. Provide an idempotent data-migration script and documentation so the
rest of the models can be moved in later milestones. Prisma is **kept fully
intact** until the whole migration is verified — rollback is unsetting a single
env var.

This plan is the execution-ready version of the upstream migration brief,
corrected against the actual checkout (real paths, real endpoints, real
tooling).

---

## 2. Current State (verified in checkout)

| Aspect | Reality |
|---|---|
| Package manager | `bun` 1.2.8 (workspaces: `app`, `server`, `shared`) + turbo |
| Server | Express + tRPC, bootstrap in `server/index.ts`, port 1111 |
| Prisma client | singleton in `server/prisma.ts`, Postgres provider |
| Schema | `prisma/schema.prisma` — model `accounts`: `id Int @id @default(autoincrement())`, `name`, `nickname`, `password`, `image`, `apiToken`, `description`, `note`, `role`, `loginType`, `linkAccountId Int?`, `createdAt`, `updatedAt` |
| Auth — Express | `server/routerExpress/auth/config.ts` (passport local + JWT + OAuth strategies) and `server/routerExpress/auth/index.ts` (login, verify-2fa, profile, validate-token) |
| Auth — tRPC | `server/routerTrpc/user.ts`: `register`, `canRegister`, `regenToken`, `genLowPermToken`, `upsertUser`, `upsertUserByAdmin` |
| Other account writes | `server/jobs/dbjob.ts` (~line 281) creates an account (admin reset/demo job) |
| Signup endpoint | **tRPC `user.register`** → `POST /api/trpc/user.register`, OpenAPI `POST /v1/user/register` (there is **no** `/api/auth/signup` route) |
| Sessions | Prisma `session` model exists in schema but **no active session store** — auth is stateless JWT + Bearer apiToken; sessions are out of scope |
| Env | `.env.tmpl` has `NEXTAUTH_URL`, `NEXTAUTH_SECRET`, `DATABASE_URL`; server runs `bun --env-file ../.env --watch index.ts` |
| SurrealDB | not present anywhere in the repo |
| Tests | `server/__tests__/{unit,integration,e2e}`; root `bun run test` → `turbo run test` |

### Prisma call sites in auth/account flows (targets for this milestone)

- `config.ts` — local strategy `prisma.accounts.findMany({ where: { name } })`,
  JWT strategy `prisma.accounts.findUnique({ where: { id } })` (wrapped in
  `cache.wrap('user_by_id_<id>')`), OAuth callback `findFirst`, `create`,
  `update` (apiToken / image / linkAccountId lookup).
- `auth/index.ts` — `verify-2fa` (`findUnique` + `update` apiToken), `profile`
  (`findUnique`).
- `user.ts` — `register` (`count`, `create` superadmin/user, `update` apiToken,
  plus `prisma.config.create` + `createSeed`), `canRegister` (`count`),
  `regenToken` / `genLowPermToken` / `upsertUser` / `upsertUserByAdmin`
  (`findFirst`, `findUnique`, `create`, `update`).
- `dbjob.ts` — admin reset creates a fresh account.

---

## 3. Goals & Non-Goals (Milestone 1)

**Goals**

1. `server/lib/db/surreal.ts` — env-driven Surreal client initializer.
2. `server/lib/repos/accounts.ts` — repository adapter for `accounts`
   (create / find by id / email-name / apiToken / count / update / delete).
3. Wire Surreal during bootstrap, **opt-in** so Prisma-only startup is unchanged.
4. Route the auth/account flows above through the adapter.
5. `scripts/migrate/prisma-to-surreal.ts` — idempotent copy of accounts
   (and optionally notes) from Prisma/Postgres into Surreal.
6. `.env.tmpl`, `README.md`/`DEV.md` updates + root scripts.

**Non-goals (later milestones)**

- Migrating `notes`, `attachments`, `tags`, `conversations`, `config`, jobs.
- Removing Prisma or the `prisma/` directory.
- Surreal-backed sessions (none exist today).
- Changing the deployed `application/tools/blinko` compose stack (it runs the
  `blinkospace/blinko:latest` image against shared Postgres; Surreal runtime
  provisioning is a follow-up milestone).

---

## 4. Architecture Decision: ID mapping

Prisma `accounts.id` is an integer and it is embedded in JWTs as `sub`
(`user.id.toString()`) and in cache keys (`user_by_id_<id>`). SurrealDB
generates string record IDs (`accounts:<uuid>`).

**Decision (Option A — minimal disruption):** keep the numeric id on every
Surreal record as `legacyPrismaId` and look accounts up by that field. JWT
`sub` stays numeric, existing tokens stay valid, and callers that currently
pass `id: number` keep working. Later milestones can switch to Surreal-native
IDs (Option B) once the whole graph is migrated.

Adapter contract (mirrors the Prisma shapes the call sites already use):

```ts
createAccount(data: AccountData)                      // → Surreal record
findAccountById(id: number)                           // SELECT * FROM accounts WHERE legacyPrismaId = $id LIMIT 1
findAccountsByName(name: string)                      // SELECT * FROM accounts WHERE name = $name
findAccountByNameAndLoginType(name, loginType)        // OAuth lookup
findAccountByApiToken(token: string)                  // SELECT * FROM accounts WHERE apiToken = $token LIMIT 1
countAccounts(): Promise<number>
updateAccount(id: number, patch: Partial<AccountData>)
deleteAccount(id: number)
```

Dates: convert Prisma `Date` → Surreal `datetime` (ISO strings are accepted);
keep `linkAccountId` as a plain number until relations are migrated.

---

## 5. Environment Variables

Add to `.env.tmpl` (and document in `README.md` / `DEV.md`):

```bash
# SurrealDB (migration step 1: auth/accounts). Unset SURREALDB_URL to run Prisma-only.
SURREALDB_URL=http://127.0.0.1:8000/rpc
SURREALDB_USER=root
SURREALDB_PASS=root
SURREALDB_NS=test
SURREALDB_DB=test
```

Also add `SURREALDB_URL`, `SURREALDB_USER`, `SURREALDB_PASS`, `SURREALDB_NS`,
`SURREALDB_DB` to `turbo.json` → `globalEnv` so turbo passes them through.

**Connectivity rule (rollback safety):** `connectSurreal()` runs only when
`SURREALDB_URL` is set, and a connection failure **logs a warning and does not
crash bootstrap** when the flag is absent — the app continues on Prisma.
When explicitly enabled and unreachable, fail fast with a clear error.

---

## 6. Implementation Steps

### 6.1 Branch (inside the blinko checkout)

```bash
cd application/tools/blinko/blinko
git fetch origin main
git checkout -b surrealdb/migration-auth-first
```

### 6.2 Add dependency (server workspace)

```bash
cd application/tools/blinko/blinko/server
bun add surrealdb.js
```

Use the latest stable `surrealdb.js` (v1.x). Commit `server/package.json` +
`bun.lock` changes. Match the installed SDK's API — v1 uses
`await db.connect(url)`, `await db.signin({ username, password })`,
`await db.use({ ns, db })`, `db.query()`, `db.create()`, `db.merge()`,
`db.select()`, `db.delete()`.

### 6.3 Surreal client initializer — `server/lib/db/surreal.ts`

Responsibilities:

- Read `SURREALDB_URL` / `SURREALDB_USER` / `SURREALDB_PASS` / `SURREALDB_NS` /
  `SURREALDB_DB` (defaults as in §5).
- Export `connectSurreal(): Promise<void>` — connect, signin, `use(ns, db)`,
  log the target, and mark readiness. Export a `isSurrealEnabled` / readiness
  helper for the bootstrap gate.
- Export the connected client as default for the adapter and migration script.

### 6.4 Accounts adapter — `server/lib/repos/accounts.ts`

Implement the functions from §4 with Surreal query strings (parameterized,
never string-interpolated user input). Normalize Surreal records to the Prisma
record shape the call sites consume (add `legacyPrismaId` mapping, `id` as
number where callers call `Number(...)`). Keep behavior identical: validation,
password hashing, token generation all stay in the call sites.

### 6.5 Bootstrap wiring — `server/index.ts`

In `bootstrap()`, before `setupApiRoutes`:

```ts
if (isSurrealEnabled()) {
  await connectSurreal(); // fail fast here if explicitly enabled
}
```

### 6.6 Swap auth/account flows to the adapter

Replace Prisma calls **only** in:

- `server/routerExpress/auth/config.ts` (local + JWT + OAuth strategies —
  keep `cache.wrap` keys, but the wrapped loader queries the adapter).
- `server/routerExpress/auth/index.ts` (`verify-2fa`, `profile`).
- `server/routerTrpc/user.ts` (`register`, `canRegister`, `regenToken`,
  `genLowPermToken`, `upsertUser`, `upsertUserByAdmin`).
- `server/jobs/dbjob.ts` admin-reset account creation.

Notes:

- `register` wraps logic in `prisma.$transaction`; keep the transaction wrapper
  but issue adapter calls inside it (the first milestone has no Surreal
  transactions; `prisma.config.create` + `createSeed` stay on Prisma).
- First-register bootstrap (superadmin + seed) must still write the `config`
  row and seed data through Prisma — only the `accounts` rows go to Surreal.
- The JWT/cache path is the riskiest: the wrapped loader must return the same
  shape (including numeric `id`) so `generateToken`/`generateApiToken` and 2FA
  checks are unchanged.

### 6.7 Migration script — `scripts/migrate/prisma-to-surreal.ts` (repo root)

Reads via Prisma, writes via Surreal. Idempotent by `legacyPrismaId` (accounts
have no email; `apiToken` can be `''`, so it is not a reliable unique key).

```bash
cd application/tools/blinko/blinko
bun scripts/migrate/prisma-to-surreal.ts
```

Behavior:

- Connect to Surreal (env vars from §5), connect Prisma (`DATABASE_URL`).
- Batch-read `prisma.accounts.findMany({ skip, take: 500 })`; for each account
  skip if `legacyPrismaId` already exists, else `db.create('accounts', payload)`
  with `legacyPrismaId: a.id` plus all scalar fields (dates → ISO strings).
- Report counts (created / skipped / failed) per table; exit non-zero on
  failure. Repeatable — safe to run after partial failures.
- `prisma.$disconnect()` at the end.
- Root `package.json` script: `"migrate:prisma-to-surreal": "bun scripts/migrate/prisma-to-surreal.ts"`.
  (No `tsx` needed — bun runs TS natively; add `tsx` only if a non-bun runner is required.)

### 6.8 Docs

- `.env.tmpl` — §5 vars with comments.
- `README.md` / `DEV.md` — new "Using SurrealDB (migration)" section: start
  Surreal locally (`docker run --rm -p 8000:8000 surrealdb/surreal:latest`),
  env vars, run the migration, smoke-test auth against Surreal, rollback note.

---

## 7. Tests & Manual Validation

Automated:

- `cd application/tools/blinko/blinko && bun run test` (turbo) — existing
  suite must stay green; add unit tests for the adapter (create/find/update/
  count) against a local Surreal instance, skipped when `SURREALDB_URL` unset.
- `bunx tsc --noEmit` (or the repo's typecheck) on `server/` and the script.

Manual smoke (auth against Surreal):

1. Start Surreal: `docker run --rm -p 8000:8000 surrealdb/surreal:latest`.
2. Start the server with `SURREALDB_URL` set.
3. `curl -X POST http://localhost:1111/api/trpc/user.register -H 'content-type: application/json' -d '{"name":"admin","password":"admin123"}'` → first user becomes superadmin.
4. `curl -X POST http://localhost:1111/api/auth/login -H 'content-type: application/json' -d '{"username":"admin","password":"admin123"}'` → expect token.
5. `curl http://localhost:1111/api/auth/profile -H "authorization: Bearer <token>"` → returns the user.
6. Verify records landed in Surreal: `SELECT * FROM accounts` via the Surreal HTTP endpoint or a tiny `db.select('accounts')` script.
7. Run the migration script against a Postgres DB with existing accounts and confirm create/skip counts.

Rollback check: unset `SURREALDB_URL`, restart — server boots Prisma-only and
login/register work against Postgres again.

---

## 8. Rollback Plan

1. **Code:** `git checkout main` in the blinko checkout (or revert the branch).
   Prisma code is untouched by milestone 1, so nothing else is required.
2. **Runtime:** unset `SURREALDB_URL` (or remove the env block) — bootstrap
   skips Surreal entirely and every auth flow falls back to Prisma/Postgres.
3. **Data:** Postgres is never written to or deleted by this milestone. The
   migration script is additive; re-running is idempotent. Delete the Surreal
   namespace/db to clean up.

---

## 9. PR Checklist (for the blinko repo PR)

- [ ] Branch `surrealdb/migration-auth-first` created from latest `main`.
- [ ] `server/lib/db/surreal.ts` added, gated on `SURREALDB_URL`.
- [ ] `server/lib/repos/accounts.ts` added with `legacyPrismaId` mapping.
- [ ] Auth/account flows (Express auth + tRPC user + dbjob) use the adapter.
- [ ] `scripts/migrate/prisma-to-surreal.ts` added and idempotent.
- [ ] `.env.tmpl` and `turbo.json` updated with Surreal vars.
- [ ] `README.md` / `DEV.md` updated with Surreal instructions.
- [ ] Root `package.json` script `migrate:prisma-to-surreal` added.
- [ ] `bun run test` passes; manual smoke steps documented in the PR body.
- [ ] PR title: `feat(db): add SurrealDB + migrate auth/accounts to Surreal (step 1)`, with run instructions + rollback notes in the description.

---

## 10. Follow-up Milestones

1. **M2 — content graph:** migrate `notes`, `attachments`, `tags`,
   `tagsToNote`, `comments`, `noteReference`; convert FK ints to Surreal
   record refs (`notes:<surreal-id>`).
2. **M3 — AI/conversation:** `conversation`, `message`, `aiScheduledTask`,
   `aiProviders`, `aiModels`, `mcpServers`, `cache`, `fonts`.
3. **M4 — final Prisma removal:** delete `prisma/`, drop the client, remove
   `prisma:*` scripts and `@prisma/client` deps; switch ID handling to
   Surreal-native IDs (Option B) and update JWT `sub` semantics.
4. **M5 — runtime:** add a Surreal service to `application/tools/blinko`
   compose + backup/restore story before enabling in the deployed stack.
