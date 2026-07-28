# Customizer — Prompt Catalog

> **Related Code**
> * **Domain:** AI prompt catalog (Customizer / Theme preview)
> * **Paths:** `applications/customizer/`, `applications/libs/ceptor-ai/`

## Site context

The Customizer prompt catalog generates short marketing copy for each previewed theme and drives the AI-suggested tagline displayed beneath the live preview.

## Capability → Prompt map

| Capability          | agent_id                    | Template                                                |
|---------------------|-----------------------------|----------------------------------------------------------|
| Preview tagline     | `customizer.tagline`        | `applications/customizer/plugins/prompts/tagline.py`     |
| Theme description   | `customizer.description`    | `applications/customizer/plugins/prompts/description.py` |
| Color-palette name  | `customizer.palette.name`   | `applications/customizer/plugins/prompts/palette.py`    |

## See also

* [`../libs/ceptor-ai/INDEX.md`](../libs/ceptor-ai/INDEX.md) — registry contract.
