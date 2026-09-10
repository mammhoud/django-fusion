---
Object type: Plan
Tags: forge, formint-pos, migration, parity, retirement, kds, loyalty, design
Status: Active
Type: Migration
Edition: Formint Professional
Related Plans: formint-pos-professional-plan
---

# Forge POS → Formint Migration

> **Description:** Controlled transfer of Forge capabilities into Formint Professional. Forge is a temporary source of behavior and design evidence, not a second product authority.

## Migration journey

The detailed migration journey — including the transfer inventory, migration method, and lessons learned — is documented in the founder story:

→ `../stories/starting-the-project.md` — Phase 9: Forge → Formint: The Great Rename

## Key principles

| Principle | Detail |
|---|---|
| **Temporary source** | Forge is a development label, not a product authority |
| **Controlled transfer** | Each capability must pass evidence before removal |
| **Old for speed** | Keep old names in development for fast iteration |
| **New for public** | Change to new names for customer-facing release |
| **Open for opinion** | Make naming decisions open for team input |

## Removal rule

Documentation or a planned replacement is not evidence of parity. Keep Forge available for one release cycle after the Formint replacement passes, unless a security or data-loss issue requires earlier removal.

## Related

- → `formint-pos-professional-plan.md` — Destination plan
- → `tauri-desktop.md` — Desktop parity
- → `../architecture/editions.md` — Edition boundaries
- → `../stories/starting-the-project.md` — Migration journey story
- → `../objects/feature.md` — Feature object type
