---
Object type: Market Research
Tags: market-research, pos, community, professional, saas, mena, egypt, saudi-arabia, uae, gulf, validation
Status: Active
Type: Product
Editions: Community, Formint Professional, POS Cloud
Related Plans: formint-pos-professional-plan, cloud
---

# Restaurant POS Market Research

> **Description:** Working market hypothesis for the three customer-facing editions. It guides discovery and pricing; it is not a claim of verified market share.

## Regional context

Prioritize Egypt first, then Saudi Arabia and the UAE, followed by Kuwait, Qatar, and Bahrain. Validate language, VAT/e-invoicing, payment, delivery, support, and connectivity requirements with local specialists before making compliance claims.

## Edition research

### Community — self-hosted

**Buyer:** single-location restaurants, cafés, food trucks, budget-conscious operators, developers, and organizations with local IT support.

**Need:** no recurring license fee, data ownership, offline continuity, Arabic/RTL customization, and a simple path to core checkout, catalog, inventory, and reports.

**Positioning:** useful free core with transparent documentation and optional paid support, updates, integrations, or migration.

**Risks:** self-hosting, backups, hardware support, regulatory updates, and lack of 24/7 assistance can block adoption.

**Validation:** ask who maintains the server, what outage recovery means, and which local invoice/tax integrations are mandatory.

### Formint Professional — offline desktop

**Buyer:** growing restaurants, QSRs, cafés, cloud kitchens, and remote or connectivity-sensitive branches that need local speed plus optional synchronization.

**Need:** reliable offline checkout, printer/scanner/KDS hardware, multi-terminal operation, branch workflows, Arabic invoices, recipes, waste, loyalty, and controlled migration from existing systems.

**Positioning:** a commercial self-hosted license or annual plan that combines local control with professional restaurant operations.

**Risks:** upgrade distribution, multi-branch reporting, support cost, hardware compatibility, and proving that offline reconciliation cannot duplicate sales.

**Validation:** run a paid pilot that measures service continuity, reconnect success, KDS throughput, staff training time, and total cost from one to five branches.

### POS Cloud — SaaS

**Buyer:** chains, franchises, multi-branch operators, delivery-heavy businesses, and owners who value remote visibility and managed operations.

**Need:** tenant isolation, branch dashboards, central catalog and purchasing, analytics, backups, billing, partner APIs, delivery/payment integrations, and automatic updates.

**Positioning:** tiered subscription by branches and service level, with transparent limits and a migration path from Formint.

**Risks:** recurring cost, vendor lock-in, internet dependence, data export, support load, and compliance responsibilities.

**Validation:** compare willingness to pay, branch expansion cost, acceptable outage behavior, integration requirements, and restore expectations with real operators.

## Competitive signals

- Open-source and self-hosted tools compete on ownership and low license cost but require technical responsibility.
- Desktop and hybrid tools compete on speed, hardware integration, and offline reliability.
- Regional SaaS tools compete on onboarding, Arabic support, delivery/payment integrations, centralized reporting, and compliance updates.
- Formint should differentiate through Arabic-first UX, offline-first operations, restaurant-specific KDS/catalog depth, and a credible self-hosted-to-cloud path.

## Research method

Use interviews, a representative service pilot, pricing conversations, competitor trials, and support-cost measurement. Record evidence by country and edition. Do not convert assumptions into market-size or revenue claims until the source and sample are documented.

## Decision metrics

| Metric | Community | Professional | SaaS |
|---|---|---|---|
| Activation | Clean install to first sale | First sale with hardware | Tenant to first active branch |
| Reliability | Backup/restore success | Offline and reconnect correctness | Availability and restore time |
| Value | Support conversion | Pilot renewal and branch expansion | Net revenue retention and support cost |
| Product fit | Core workflow completion | KDS, catalog, waiter, loyalty adoption | Branch, API, analytics, and integration usage |

## Sources to verify during discovery

- Saudi ZATCA e-invoicing guidance: https://zatca.gov.sa/en/E-Invoicing/
- UAE Federal Tax Authority: https://tax.gov.ae/
- Foodics company and product materials: https://www.foodics.com/
- SambaPOS community and documentation: https://v2.sambapos.org/en
- TastyIgniter project: https://tastyigniter.com/

## Related

- → `formint-pos-professional-plan.md` — Product and launch contract
- → `cloud.md` — SaaS control plane
- → `../architecture/editions.md` — Edition boundaries
- → `../objects/market-research.md` — Market Research object type
- → `../objects/edition.md` — Edition object type
