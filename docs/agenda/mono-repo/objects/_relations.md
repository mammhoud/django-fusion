# Relations — Canonical Anytype Graph

> **Description:** Relations connect workspace, product, planning, go-to-market, evidence, delivery, and people objects. Create these exact property names in Anytype.
> **Container note:** These relations are scoped to the Structa Cloud **Channel** (Anytype container — formerly Space). Create them under **Channel Settings → Content Model → Properties**. Relations do not cross Channels; a separate Channel needs its own Content Model. See [`guides/channel-structure.md`](../guides/channel-structure.md).

## Naming disambiguation

- **Channel (container)** — Anytype's workspace container (Vault → Channel → Objects). Not an object in this graph.
- **Channel (marketing)** — a go-to-market or distribution surface, modeled as an `Integration` object with `Category` values (`Social`, `Community`, `Commerce`, `Partner`…). Do not confuse the two in frontmatter or Graph View.

## Cardinality rule

- Plural names are multi-value relations.
- Singular names are one accountable or parent relation.
- Do not create aliases such as `Related Product` for `Related Products`.

## Workspace and planning

| Name | Source → Target | Cardinality | Use |
|---|---|---:|---|
| `Related Projects` | Workspace/Team → Project | many | Initiatives grouped by a hub or team |
| `Related Project` | Product/Plan → Project | one | Bounded initiative for one product or plan |
| `Related Workspace` | Project/Plan → Workspace | one | Parent portfolio or initiative hub |
| `Related Products` | Workspace/Project/Plan/Team/Integration → Product | many | Products served or affected |
| `Related Plans` | Workspace/Project/Product/Team/Edition → Plan | many | Delivery, operating, or commercial plans |
| `Related Goals` | Project/Plan/Product/Edition → Goal | many | Strategic outcomes |
| `Related Milestones` | Project/Plan/Goal → Milestone | many | Checkpoints and phase gates |
| `Related Tasks` | Plan/Goal/Milestone/Sprint → Task | many | Actionable work |
| `Related Teams` | Workspace/Project/Plan/Product/Integration → Team | many | Collective ownership |
| `Owner` | Workspace/Project/Plan/Product/Team/Tool → Person | one | Accountable individual |
| `Lead` | Team → Person | one | Team lead |
| `Member Of` | Person → Team | many | Team membership |

## Product and evidence

| Name | Source → Target | Cardinality | Use |
|---|---|---:|---|
| `Related Editions` | Architecture/Reference/Product/Feature/Plan/Market Research → Edition | many | Current customer-facing scope |
| `Related Features` | Product/Edition/Plan/Goal → Feature | many | Included or planned capabilities |
| `Excluded Features` | Edition → Feature | many | Explicit scope boundary |
| `Related Research` | Workspace/Product/Edition/Plan → Market Research | many | Evidence behind decisions |
| `Related Decisions` | Architecture/Plan/Product → Decision | many | Rationale and accepted choices |
| `Related Products` | Market Research → Product | many | Offerings covered by research |
| `Depends On` | Task/Feature/Tool → Any | many | Delivery or capability dependency |
| `Supersedes` | Decision/Plan → Any | one or many | Replaced decision or plan |

## Go-to-market and channels
| Name | Source → Target | Cardinality | Use |
|---|---|---:|---|
| `Related Campaigns` | Product/Team/Plan → Plan | many | Marketing Campaign plans |
| `Related Sales` | Product/Plan → Plan | many | Sales plans and handoffs |
| `Related Commerce` | Product/Plan → Plan | many | Online selling and fulfillment plans |
| `Related Channels` | Workspace/Plan/Campaign → Integration | many | Website, email, social, community, partner, or commerce channels |
| `Related Integrations` | Product/Feature/API → Integration | many | External connectors |
| `Related APIs` | Feature/Tool/Integration → API | many | API contracts |
| `Related Guides` | Architecture/Feature/Plan → Guide | many | Operating and implementation methods |
| `Part Of` | Guide/Feature → Plan | one | Parent delivery or product plan |

## Delivery and design

| Name | Source → Target | Cardinality | Use |
|---|---|---:|---|
| `Related Releases` | Project/Feature → Release | many | Delivered versions |
| `Related Changelog` | Release → Changelog | one | Version notes |
| `Related Pipelines` | Release/Reference → Pipeline | many | Automation and deployment |
| `Related Components` | Feature/API → Component | many | Reusable implementation units |
| `Related Styles` | Component → Style | many | Design tokens and UI patterns |
| `Related Tools` | Feature/Plan → Tool | many | Methods or utilities used |
| `Related Architecture` | Feature/Plan/Guide → Architecture | many | System context |

## Story and narrative

| Name | Source → Target | Cardinality | Use |
|---|---|---|---:|
| `Author` | Story → Person | one | Who tells the story |
| `Related Goals` | Story → Goal | many | Achievements the story phase drove |
| `Related Plans` | Story → Plan | many | Plans informed by the narrative |
| `Related Products` | Story → Product | many | Products born from the journey |
| `Related Features` | Story → Feature | many | Capabilities created along the way |
| `Related Decisions` | Story → Decision | many | Key recorded choices |

## POS graph

| Path | Flow |
|------|------|
| Products | Workspace → Project → Product → Edition → Feature → Release; Product → Campaign → Channel, Sales → Commerce, Team → Person |
| Delivery | Workspace → Plan → Goal → Milestone → Task; Plan → Market Research → Decision |

## Related

- → `_object-types.md` — Type definitions
- → `_templates.md` — Object templates
- → `../guides/pos-documentation-system.md` — Import method
- → `../README.md` — Master index
