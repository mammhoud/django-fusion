# Context Map

The structa.cloud monorepo is a set of Django/Wagtail sites, a desktop POS product,
and shared Python libraries, all sharing one repository and one CI pipeline.

## Contexts

- [Landing Fusion](./projects/landing-fusion/CONTEXT.md) — the public structa.cloud site: a product catalog and the documentation of everything the monorepo ships
- [Forge POS](./projects/pos/CONTEXT.md) — a desktop point-of-sale application sold in four editions (Community · Standard · Pro · Cloud)
- [LMS](./projects/lms/) — a content-driven learning platform (courses, enrollments, payments)
- [Cypercloud](./projects/cypercloud/) — an AI chat customizer platform built on ceptor-ai
- [Portfolio / vResume](./projects/portfolio/) — a cloud resume platform
- [Shared libraries](./libs/) — django-fusion (component system + routing), ceptor-ai (AI chat + MCP), django-bolt (Rust-backed API)

## Relationships

- **Landing Fusion → Forge POS / LMS / Cypercloud / Portfolio**: the catalog documents these products, sells their editions, and publishes reference snippets for reuse
- **Landing Fusion → Shared libraries**: every site is built on django-fusion; Cypercloud and the AI tooling are built on ceptor-ai
- **Forge POS → Landing Fusion**: the catalog is the commercial front door for Forge POS editions
- **Forge POS ↔ Cloud**: Standard and Pro terminals sync to a cloud master; Cloud is the fully hosted variant of the same model

Glossaries for LMS, Cypercloud, Portfolio, and the libraries do not exist yet — they get
created lazily when terms in those contexts crystallize.
