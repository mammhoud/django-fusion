# Formint Marketing Claims Register

> **Status:** Active working register
> **Updated:** 2026-08-04
> **Owner:** Product marketing
> **Rule:** Objective claims require evidence before publication.

## Claim levels

| Level | Meaning | Publication rule |
|---|---|---|
| **Capability** | The product is designed or implemented to do something | Say “supports” or “includes” only when release evidence exists |
| **Pilot evidence** | Observed in a named internal or customer pilot | Include scope, date, sample, and limitation |
| **Measured claim** | Reproducible benchmark or operational metric | Include method, baseline, environment, and review date |
| **Regulated claim** | Compliance or legal outcome | Require local specialist/legal review |

## Approved positioning language

| Claim | Audience | Evidence required | Safe wording now | Review |
|---|---|---|---|---|
| Arabic-first | MENA restaurant operators | RTL, translation, invoice UX tests | “Designed for Arabic and bilingual restaurant workflows.” | Each release |
| Offline-first | Operators with unstable connectivity | Offline/reconnect acceptance tests | “Continue core operations during interruptions and reconcile later.” | Before launch |
| KDS | Restaurant operators | KDS workflow and pilot evidence | “Route and prioritize kitchen tickets across stations.” | Before feature launch |
| Multi-branch | Chains and franchises | Branch permissions, publishing, sync tests | “Manage branch operations from a shared control view.” | Before commercial release |
| Loyalty | Customer-focused restaurants | Ledger, reversal, and consent tests | “Build repeat-visit programs with an auditable rewards ledger.” | Before feature launch |
| API access | Partners and developers | Versioned schema, auth, rate-limit tests | “Integrate through a versioned API without direct database access.” | Before public API |
| Local-to-cloud path | Growing operators | Migration and restore pilot | “Start locally and move to managed cloud services when ready.” | Quarterly |

## Claims requiring evidence before use

- “Guaranteed uptime” or numerical availability.
- “X% faster checkout/KDS/preparation.”
- “Fully compliant” with ZATCA, UAE FTA, VAT, or another regulator.
- “Saves X%” or “increases revenue/retention by X%.”
- “Market leader,” “best,” “only,” or comparative competitor claims.
- “Production-ready” for a feature still marked planned or in migration.
- Pricing or margin promises that have not been validated against support, hosting, payment, and storage costs.

## Evidence record template

```text
Claim:
Audience:
Release/version:
Evidence type: capability | pilot | measured | regulated
Source or test:
Sample/environment:
Limitations:
Owner:
Confidence:
Review date:
Approval:
```

## Marketing benefits

Lead with customer outcomes:

- fewer service interruptions;
- clearer kitchen coordination;
- easier Arabic and bilingual service;
- controlled branch operations;
- traceable customer rewards;
- safer integrations;
- a migration path that preserves local control.

Avoid selling a technology list. Tauri, Django, Astro, HTMX, and cloud transport are supporting details; the marketing story is continuity, clarity, control, and measurable restaurant outcomes.

## Related

- → `document-lifecycle.md` — Lifecycle and deletion policy
- → `editions/README.md` — Formint editions index
- → `editions/03-pro.md` — Professional product contract
