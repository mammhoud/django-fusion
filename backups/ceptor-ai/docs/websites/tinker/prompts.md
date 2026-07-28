# Tinker — Prompt Catalog

> **Related Code**
> * **Domain:** AI prompt catalog (Tinker / experimentation)
> * **Paths:** `applications/tinker/www/`, `applications/libs/ceptor-ai/`

## Site context

Tinker serves as a sandbox for prototyping ceptor-ai prompt templates before they are promoted to CTC, LMS, or VResume.

## Capability → Prompt map

| Capability               | agent_id                  | Template                                                |
|--------------------------|---------------------------|----------------------------------------------------------|
| Component-name suggest  | `tinker.comp.name`        | `applications/tinker/plugins/prompts/component_name.py`  |
| Slot description         | `tinker.slot.desc`        | `applications/tinker/plugins/prompts/slot_desc.py`       |
| Wagtail block copy       | `tinker.block.copy`       | `applications/tinker/plugins/prompts/block_copy.py`      |

## See also

* [`../libs/ceptor-ai/INDEX.md`](../libs/ceptor-ai/INDEX.md) — registry contract.
