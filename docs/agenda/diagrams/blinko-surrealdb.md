# 🗒️ Blinko — SurrealDB Topology & Data Flow

> **Purpose:** Document the self-hosted Blinko AI-notes service
> (`application/tools/blinko/`) — service topology, the SurrealDB storage
> layer, and how auth/content/query flow through it.
> **Status:** Active · **Owner:** Infrastructure

---

## 1. Service topology

```mermaid
graph LR
    subgraph "Public"
        P["tools.structa.cloud/notes/"]
    end
    subgraph "Proxy"
        TP["tools-proxy Nginx"]
    end
    subgraph "Docker: application/tools/blinko"
        B["blinko:1111<br/>NextAuth + App (Next.js)"]
        S["surrealdb:v1.5.6<br/>:8000 file:/data/blinko.db"]
        V["blinko-data/surreal<br/>(persistent volume)"]
    end

    P --> TP
    TP --> B
    B -->|"SurrealDB client (surrealdb.js ^1.0.0)"| S
    S --> V
```
![Rendered diagram](/agenda/diagrams/diagrams-blinko-surrealdb-1.svg)

## 2. Data flow — auth, content graph, queries

```mermaid
sequenceDiagram
    autonumber
    participant U as User (browser)
    participant B as Blinko app (:1111)
    participant S as SurrealDB (:8000)
    participant V as blinko-data/surreal

    U->>B: login (NextAuth)
    B->>S: auth lookup (surreal record)
    S->>V: read blinko.db
    V-->>S: record
    S-->>B: session token
    B-->>U: authenticated session

    U->>B: create note
    B->>S: INSERT content node (graph)
    S->>V: write record
    V-->>S: ok
    S-->>B: record id
    B-->>U: note saved

    U->>B: query / search notes
    B->>S: graph query (relations)
    S->>V: read
    V-->>S: results
    S-->>B: rows
    B-->>U: rendered results
```
![Rendered diagram](/agenda/diagrams/diagrams-blinko-surrealdb-2.svg)

## 3. SurrealDB migration (M1–M4)

Per the Compose header, Blinko migrated off Prisma + PostgreSQL onto SurrealDB:

| Migration | What changed |
|-----------|--------------|
| **M1** | Auth moved to SurrealDB records |
| **M2** | Content graph (notes, links, tags) moved to SurrealDB |
| **M3** | Query engine moved to SurrealDB |
| **M4** | PostgreSQL no longer required at runtime |

**Constraints to respect:**
- **Pin SurrealDB to the 1.x line** — the bundled server pins
  `surrealdb.js@^1.0.0`, which rejects v2/v3 engines
  (`UnsupportedVersion`).
- `server/lib/scheduler.ts` uses v1-compatible upsert semantics
  (`UPDATE ... MERGE` on an explicit record ID).
- The `surrealdb` image is shell-less (scratch) — readiness uses the binary's
  built-in `/surreal isready` probe, not `wget`/`curl`.
- Credentials come from `.env` (`SURREALDB_PASS`, `BLINKO_NEXTAUTH_SECRET`, …).

## 4. Related

- Compose + Makefile: `application/tools/blinko/`
- Database registry: `application/databases/README.md` (`blinko` database row)
- Docs quickstart: `docs/guides/01-quickstart.md` (Blinko Notes service)

<!-- AI-generated: review needed -->