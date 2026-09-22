# Precis product documentation

> **Canonical docs root:** `projects/precis/docs/`
> **Product group:** Precis
> **Public documentation mirror:** [`docs/precis/`](../../../docs/precis/)

<!-- AI-generated: review needed -->

This is the canonical project-local documentation root for the Precis product
group. It keeps the three runtimes separated while making their relationships,
shared conventions, deployment boundaries, and historical duplication explicit:

```text
projects/precis/docs/
├── precis-main/       # unified LMS + marketing/catalog runtime
├── precis-landing/    # retained legacy Precis Landing copy
├── precis-ctc/        # standalone medical research center
├── CHANGES.md         # change ledger and verification record
├── RELATIONSHIPS.md   # runtime, dependency, and documentation relationships
└── DUPLICATES.md      # duplicate/legacy register and source-of-truth policy
```

## Product documentation

| Product | Canonical runtime | Documentation | Responsibility |
|---|---|---|---|
| Precis unified | `projects/structa.cloud/` | [`precis-main/`](precis-main/README.md) | LMS courses, enrollment, progress, profile, marketing and catalog shell |
| Precis Landing legacy copy | `projects/precis/precis-landing/` | [`precis-landing/`](precis-landing/README.md) | Retained compatibility copy; new product work belongs in Precis unified |
| CTC Research | `projects/precis/precis-ctc/` | [`precis-ctc/`](precis-ctc/README.md) | Medical research, learning, Wagtail content, Astro shell, and public site |

## Cross-product references

- [Change ledger](CHANGES.md) — separated implementation changes and validation evidence.
- [Relationships](RELATIONSHIPS.md) — ownership, shared framework, data, proxy, and deployment boundaries.
- [Duplicate register](DUPLICATES.md) — what was consolidated, what remains intentionally separate, and where to edit.
- [Root Precis docs](../../../docs/precis/README.md) — reader-facing product overview.
- [CTC public docs](../../../docs/precis-ctc/README.md) — publishing and strategy references.
- [Shared django-fusion guide](../../../docs/libs/django-fusion.md) — framework usage across products.

## Command entry points

```bash
# Product dispatcher
cd projects
make check WEBSITE=precis-main
make test WEBSITE=precis-main
make check WEBSITE=precis-ctc
make test WEBSITE=precis-ctc

# CTC full stack
cd projects/precis/precis-ctc
make check
make frontend-check
make redeploy

# Nx orchestration from the repository root
cd ../..
npx nx run precis-ctc:check
npx nx run precis-ctc:redeploy
```

## Source-of-truth rule

- Edit the product-specific document under this directory when the subject is
  runtime-specific.
- Edit `docs/precis/` when the subject is reader-facing portfolio/product
  documentation.
- Link to the other source; do not copy the same procedure into both locations.
- Keep `projects/precis/precis-landing/docs/` and the old product-local paths out
  of new references; they are documented compatibility locations only.

## Remarks & Notes

- `precis-main` is the canonical unified Precis runtime. `precis-landing` is not a second active unified product.
- CTC Research is in the Precis product group but has an independent backend, database, frontend, and release lifecycle.
- This index intentionally separates implementation docs from the public docs mirror to prevent content drift.
