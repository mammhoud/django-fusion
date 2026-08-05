# Formint POS — Plan Index

> **Plan directory:** `projects/pos/`  
> **Lifecycle policy:** [`../document-lifecycle.md`](../document-lifecycle.md)  
> **Marketing claims:** [`../marketing-claims.md`](../marketing-claims.md)  
> **Canonical Professional plan:** [`formint-pos-professional-plan.md`](formint-pos-professional-plan.md)
> **Created:** 2026-07-25 | **Updated:** 2026-08-04 | **Branch:** `generic`

---

## Plans

| # | Plan | Status | Progress |
|---|------|:------:|:--------:|
| 1 | [Formint POS Professional Edition](./formint-pos-professional-plan.md) — canonical product scope, architecture, parity, roadmap, and launch gates | 🟡 Current | Phase 1 started |
| 2 | [Formint Phase 1 foundation](../../../projects/pos/formint-pos/README.md) — Astro shell, Django data boundary, shared assets, and compatibility manifest | 🟡 Started | Non-destructive |
| 3 | [Backup and migration record](./formint-backup-20260804.md) — verified POS archive and restore-first policy | ✅ Verified | Backup retained |
| 4 | [Dead-code baseline](./dead-code-baseline.md) — non-destructive inventory and removal gates | 🟡 Started | No deletion approved |
| 5 | [Forge POS parity](./forge-pos-plan.md) — migration inventory and retirement gates | 🟡 Migration source | Do not remove before Formint evidence |
| 6 | [POS Cloud](./cloud-plan.md) — multi-branch cloud, sync, and isolated cloud API transport | 🟡 Planned | Cloud-only transport boundary |
| 7 | [Tauri Plugins](./tauri-plugins-enhancement-plan.md) — Formint desktop/native migration reference | 🟡 Current migration | Selective port from Forge |
| 8 | POS Solo enhancement — historical migration inventory (working file removed; see deletion manifest) | 🗄️ Historical | Do not extend; use Formint plan |

---

## Current implementation boundary

```text
projects/pos/
├── formint-pos/   # New canonical Phase 1 product boundary
├── pos-solo/      # Preserved local parity source; legacy identifier accepted
├── pos-full/      # Preserved multi-branch/cloud parity source
├── forge-pos/     # Preserved UI/feature migration source
└── pos-cloud/     # Preserved cloud control-plane source
```

`formint-pos` is planned and foundation-started. It does not replace the legacy applications until the Professional Edition gates in the canonical plan pass.

## Related Plans

| Plan File | Project | Location |
|-----------|---------|----------|
| [POS architecture](../../../projects/pos/docs/POS_ARCHITECTURE.md) | POS (shared) | Current architecture reference |
| [Formint foundation](../../../projects/pos/formint-pos/README.md) | Formint POS | Phase 1 source boundary |
| [Backup record](./formint-backup-20260804.md) | POS workspace | Verified archive and restore policy |
| [Dead-code baseline](./dead-code-baseline.md) | POS workspace | Removal inventory and safety gates |
| [Cloud Server Plan](./cloud-plan.md) | POS Cloud | Multi-branch sync and cloud-only API transport |
| [django-fusion Enhancements](../django-fusion/django-fusion-enhancements.md) | POS + django-fusion | Component and sync reference |

## Progress Legend

| Symbol | Meaning |
|:------:|---------|
| ✅ | Complete / verified |
| 🟡 | In progress / planned |
| 🗄️ | Historical / archived |
| ⬜ | Not started |
| ❌ | Blocked |
