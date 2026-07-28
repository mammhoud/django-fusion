# CRM — Prompt Catalog

> **Related Code**
> * **Domain:** AI prompt catalog (CRM)
> * **Paths:** `applications/crm/www/`, `applications/libs/ceptor-ai/`
> * **Stack:** ceptor-ai prompt registry (see `../libs/ceptor-ai/INDEX.md`)

## Site context

The CRM exercise the ceptor-ai catalog for deal-pipeline synthesis and account-summarization. Each prompt is registered with `agent_id="crm.<capability>"` and lives in `applications/crm/plugins/prompts/<capability>.py`.

## Capability → Prompt map

| Capability             | agent_id                | Template                                                  |
|------------------------|-------------------------|-----------------------------------------------------------|
| Deal-pipeline summary  | `crm.deal.summary`      | `applications/crm/plugins/prompts/deal_summary.py`        |
| Contact outreach       | `crm.contact.outreach`  | `applications/crm/plugins/prompts/contact_outreach.py`    |
| Account enrichment     | `crm.account.enrich`    | `applications/crm/plugins/prompts/account_enrich.py`      |
| Risk flagging          | `crm.risk.flag`         | `applications/crm/plugins/prompts/risk_flag.py`           |

## Usage

```python
from ceptor_ai import get_prompt
rendered = get_prompt("crm.deal.summary").render(
    deal=deal_obj, tone="executive", lang="en",
)
```

See [`../libs/ceptor-ai/INDEX.md`](../libs/ceptor-ai/INDEX.md) for the registry contract.
