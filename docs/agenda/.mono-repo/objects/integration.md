---
Object type: Integration
Tags: integration, channel, commerce, partnerships
Status: Published
---

# Integration — External Services & Channels

> **Description:** A connector or external channel used by a product, plan, campaign, sales motion, commerce flow, or community operation.

## Properties

| Property | Type | Options | Description |
|---|---|---|---|
| `Status` | Select | Active, Planned, Deprecated, Broken | Connector or channel lifecycle |
| `Category` | Select | Payment, CRM, Email, SMS, Analytics, Auth, Storage, Social, Community, Commerce, Partner, Delivery | Service or channel role |
| `Provider` | Text | — | Provider, network, or platform name |
| `Auth Type` | Select | API Key, OAuth, JWT, Basic, None | Authentication method |
| `Edition` | Relation → Edition | — | Edition using the connector |
| `Related Products` | Relation → Product | — | Products using the connector |
| `Related Features` | Relation → Feature | — | Capabilities enabled |
| `Related Plans` | Relation → Plan | — | Campaigns, sales, commerce, or operations using it |
| `Related Teams` | Relation → Team | — | Accountable owners |
| `Tags` | Multi-select | — | Cross-cutting labels |

## Use

Create one Integration object for a meaningful external service or channel. Use `Category: Social` for a social network, `Community` for a community space, `Commerce` for a selling or checkout channel, and `Partner` for a referral or alliance channel. Do not create an integration object for an ordinary internal relation.

## Graph

A Product, Plan, or Campaign connects to an Integration that reaches an external provider or channel. The integration involves a Team/Owner on one side and an API, credential, or consent boundary on the other.

## Guardrails

Record owner, purpose, data exchanged, consent requirements, credential boundary, status, and replacement when deprecated. Never place secrets in Anytype documentation.

## Related

- → `_object-types.md` — Type definitions
- → `_relations.md` — Relation guide
- → `../plans/marketing-campaigns.md` — Campaign channels
- → `../plans/online-commerce.md` — Commerce channels
- → `../plans/social-networks.md` — Social channels
- → `api.md` — API object
- → `feature.md` — Feature object
