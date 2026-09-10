---
Object type: Product
Tags: product, positioning, pricing, sales, marketing, development
Status: Active
---

# Product — Description & Positioning

> **Description:** A customer-facing product definition connecting its promise, audience, editions, features, pricing, sales assets, and delivery plan.

## Properties

| Property | Type | Description |
|---|---|---|
| `Status` | Select | Draft, Active, Planned, Deprecated |
| `Product Type` | Select | Platform, Application, Library, Service, Edition |
| `Positioning` | Text | Problem, audience, promise, and differentiator |
| `Target Audience` | Text | Primary customer segments |
| `Pricing` | Text | Pricing hypothesis or approved pricing |
| `Related Editions` | Relation → Edition | Product editions and tiers |
| `Related Features` | Relation → Feature | Included capabilities |
| `Related Plans` | Relation → Plan | Product and delivery plans |
| `Related Research` | Relation → Market Research | Evidence behind product decisions |
| `Related Campaigns` | Relation → Plan | Marketing campaigns for the product |
| `Related Teams` | Relation → Team | Accountable product team |
| `Tags` | Multi-select | Product, audience, market, and lifecycle labels |

## Use

Use one Product object for a customer-facing offering such as Formint POS, POS Cloud, or a shared platform. Keep a product description outcome-focused; link technical implementation to Plans and Features rather than embedding code.

## Related

- → `_object-types.md` — Type definitions
- → `_relations.md` — Relation guide
- → `../products/formint-pos.md` — Formint product object
- → `../plans/marketing-campaigns.md` — Campaign plan
- → `../plans/sales.md` — Sales plan
