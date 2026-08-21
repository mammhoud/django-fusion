---
title: Documentation Reference Map
description: The complete index of the docs/ tree — every directory and subdirectory, its owning project, and what each file references.
navigation:
  title: Reference map
  icon: i-lucide-map
object:
  type: "reference"
  id: "docs.reference"
attributes:
  source_path: "REFERENCE.md"
  canonical_route: "/docs/en/reference"
  source_of_truth: "repository-markdown"
  owner: "workspace"
  status: "maintained"
tags:
  - structa-cloud
  - reference
  - index
  - docs
links:
  - label: "Documentation home"
    to: "/docs/en/"
    icon: "i-lucide-house"
  - label: "Project structure"
    to: "/docs/en/project-structure"
    icon: "i-lucide-folder-tree"
---

# 🗺️ Documentation Reference Map

> One index for the whole `docs/` tree: every directory, the **owning
> project**, and what each file **references**. Use this to find where a
> subject lives before creating a new page (link, don't duplicate).

<!-- AI-generated: review needed -->

## Top-level documents

| File | Owning project | References |
|------|----------------|------------|
| [`README.md`](README.md) | workspace | Documentation home, product table, quick links, Docus source note |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | workspace | Monorepo architecture, request lifecycle, skeleton pipeline, Docus docs architecture |
| [`project-structure.md`](project-structure.md) | workspace | Directory map, ownership and placement rules |
| [`overview.md`](overview.md) | workspace | High-level overview |
| [`recommendations.md`](recommendations.md) | workspace | Recommended priorities and sequencing |
| [`setup-guides.md`](setup-guides.md) | workspace | Per-project setup/build indexes |
| [`recent-changes.md`](recent-changes.md) | workspace | Recent change log |
| [`REFERENCE.md`](REFERENCE.md) | workspace | This reference map |
| [`COMMANDS.md`](COMMANDS.md) | workspace | Unified verb naming, delegation chain, deploy cascade |

## Product docs

| Dir | Owning project | Files → what they reference |
|-----|----------------|-----------------------------|
| [`precis/`](precis/README.md) | `precis-main` | README (index) · ARCHITECTURE (LMS + landing architecture) · configuration · courses · deployment |
| [`precis/precis-landing/`](precis/precis-landing/) | `precis-landing` (legacy) | backend-api · deployment · frontend |
| [`precis-ctc/`](precis-ctc/README.md) | `precis-ctc` | README (index) · content-strategy (editorial ICP/research) · publishing-and-production (release workflow) · client-production (case study) |
| [`syntara/`](syntara/README.md) | `syntara` | README (index) · configuration · features · infrastructure · use-cases |
| [`pos/`](pos/README.md) | `formints` | README (index) · editions (pointer → `plans/editions/`) · cloud-edition (pointer → `04-cloud.md`) · legacy topic pages — canonical product docs live in [`projects/formints/docs/`](../../projects/formints/docs/) |
| [`pos/backend/`](pos/backend/README.md) | `formints` | rust-auth · rust-backend · rust-database · rust-data-flow · rust-operations · rust-seed-data (legacy reader-facing; canonical Rust docs in `projects/formints/docs/`) |
| [`pos/frontend/`](pos/frontend/README.md) | `formints` | typescript-api · typescript-components · typescript-contexts-hooks · typescript-frontend (legacy reader-facing; canonical TS docs in `projects/formints/docs/`) |
| [`pos/sidecar/`](pos/sidecar/README.md) | `formints` | django-bolt-integration · django-orm · network-architecture · robyn-migration · sidecar-api · sidecar-readme · sidecar-websocket (legacy reader-facing) |
| [`loop-crm/`](loop-crm/README.md) | `loop-crm` | README (index) · design-system · setup-and-build |

## Shared & framework docs

| Dir | Owning project | Files → what they reference |
|-----|----------------|-----------------------------|
| [`libs/`](libs/README.md) | `django-fusion` | README (index) · django-fusion (where/how used) · django-fusion-enhancements · auth-customization · configuration · django-tags · js-structure · python-readme · reusable-libraries · templates-architecture |
| [`shared/`](shared/README.md) | workspace | README (index) · configuration · shared-methods · use-cases |

## Guides, dev, features, AI, publishing

| Dir | Owning project | Files → what they reference |
|-----|----------------|-----------------------------|
| [`guides/`](guides/README.md) | workspace | README (index) · 00-quickstart → 09-fusion-assets-health (numbered walkthroughs) · auth-webauthn-passkeys · fixture-loading |
| [`guides/auth/`](guides/auth/) | workspace | adapter · social-login · style-audit · templates · testing |
| [`dev/`](dev/README.md) | workspace | README (index) — development topics |
| [`dev/back-env/`](dev/back-env/README.md) | workspace | README (index) · settings-reference |
| [`dev/customization/`](dev/customization/README.md) | workspace | README (index) · customization-methods · design-system |
| [`dev/databases/`](dev/databases/README.md) | workspace | README (index) · fixture-pipeline · pos-schema |
| [`dev/infrastructure/`](dev/infrastructure/README.md) | infrastructure | README (index) · deployment · proxy · routing-proxy · shared-worker · worker-stack |
| [`dev/infrastructure/docker/`](dev/infrastructure/docker/README.md) | infrastructure | README (index) — container overview, networks, compose files |
| [`dev/infrastructure/troubleshooting/`](dev/infrastructure/troubleshooting/) | infrastructure | ASSET_HEALTH_VERIFICATION · CONTAINER_LOGS_ANALYSIS |
| [`features/`](features/README.md) | workspace | README (index) · data-token-sync-tagging · feature-roadmap |
| [`ai/`](ai/README.md) | workspace/agents | README (index) · agents · documentation-authoring · mcp-integration · PROMPT_CATALOG · prompts · skills-catalog · templates-and-request-flows |
| [`publish/`](publish/README.md) | workspace | README (index) · ci-cd · docker-deploy · pos-release |
| [`tests/`](tests/README.md) | workspace | README (index) · e2e-test-report · testing-strategies |
| [`changelogs/`](changelogs/README.md) | workspace | README (index) · libs · pos · repo · session notes |

## Plans (ADR-style decisions)

| Dir | Owning project | Files → what they reference |
|-----|----------------|-----------------------------|
| [`plans/`](plans/README.md) | workspace | README (registry) · deletion-manifest · document-lifecycle · precis-landing · marketing-claims · DJANGO_BOLT_FUSION_CASE_STUDY · THEME_DIRECTORY_STRATEGY |
| [`plans/django-fusion/`](plans/django-fusion/) | `django-fusion` | comp-htmx-fusionproxy-analysis · analyzer-skeleton-assets · enhancements · llm-mcp · tasks-mcp · webpack plans · fusion-assets-templates-cleanup |
| [`plans/editions/`](plans/editions/README.md) | `formints` | README (index) · comparison (feature matrix) · 01-community → 08-tenant-schemas · 09-completion-plan · finish-community-standard (archived) |
| [`plans/loop-crm/`](plans/loop-crm/) | `loop-crm` | demo-state-gap-fixing · formint-integration-finance · merge-plan · twenty-postiz-comparison · wagtail-landing-plan |
| [`plans/repository/`](plans/repository/) | workspace | monorepo consolidation · project closeout · ctc publish · enhancement plans · migration cleanup · worker consolidation · startup-docs-enhancement-plan |
| ~~`plans/legacy-archive/`~~ | deleted (DOC-0024, 2026-08-19) | dead-code-audit · deployment-reports · dev-notes — superseded by the plans registry; git history is the archive |

## Startup strategy (private) 🔒

| Dir | Owning project | Files → what they reference |
|-----|----------------|-----------------------------|
| [`startup/`](startup/README.md) | workspace | README (index) · STRATEGY · comparison · PLAN · PRICING · SALES · company-profile · product-profiles · revenue-model · presentation · precis · precis-ctc · syntara · formints · loop-crm · _template |

## Arabic translations (authored source)

| Dir | Owning project | Files → what they reference |
|-----|----------------|-----------------------------|
| [`ar-content/`](ar-content/index.md) | workspace | index (home) · architecture · guides/quickstart · guides/deployment · guides/config-cascade · libs/django-fusion · startup/index · startup/strategy · startup/planning · startup/pricing · startup/sales · startup/company-profile · startup/product-profiles · startup/revenue-model · startup/presentation · navigation |

## Remarks & Notes

- This map is generated by hand from the live `docs/` tree; keep it in sync
  when a directory is added, renamed, or removed.
- Each product directory has its own `README.md` index — follow the same
  pattern for new products (index + topic files + a `## Remarks & Notes`).
- The `content/`, `scripts/`, `public/`, and `assets/` dirs are build products
  or tooling, not authored documentation — they are intentionally omitted.
- Prefer linking to an existing page over duplicating it; see the
  deduplication rules in [`guides/09-docus.md`](guides/09-docus.md).