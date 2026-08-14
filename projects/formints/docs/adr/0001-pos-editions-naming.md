# Canonical POS edition names: Community · Standard · Pro · Cloud

Status: accepted

The product historically shipped as Minimal / Solo / Full (also `pos-mini` /
`pos-solo` / `pos-full` directories, later merged into `formint-pos`). The
commercial naming was changed to **Community, Standard, Pro, Cloud** and the codebase
(seed data, pricing page, tests, copy) now uses the canonical names.

Why: the new names match the real product tiers — Community signals the free
open-source tier, Standard the standalone tier with the embedded server + cloud sync
client, Pro the multi-terminal tier with the cloud master + django-bolt API, and Cloud
the fully hosted multi-terminal variant. "Minimal/Solo/Full" described directory shape,
not the product story.

Consequences: legacy docs still describe the old names (`docs/pos/editions.md`,
`projects/pos/docs/POS_ARCHITECTURE.md`, and friends) and must be updated to the
canonical naming to avoid confusing editors and buyers. `docs/pos/editions.md` is the
primary offender.
