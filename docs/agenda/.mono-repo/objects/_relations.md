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

## Data analysis

| Name | Source → Target | Cardinality | Use |
|---|---|---:|---|
| `Methodology` | Report → Methodology | one | Analysis approach used |
| `Data Sources` | Report/Dashboard/Data Pipeline → Any | many | Evidence and inputs |
| `Findings` | Report → Text | — | What the analysis found |
| `Recommendations` | Report → Recommendation | many | Suggested next steps |
| `Related Reports` | Dashboard/Methodology/Insight → Report | many | Reports behind the view or method |
| `Related Dashboards` | Data Pipeline → Dashboard | many | Downstream consumers |
| `Related Insights` | Recommendation → Insight | many | Evidence behind the action |
| `Related Actions` | Insight → Recommendation | many | Actions the insight drives |
| `Related Training` | Methodology → Guide | many | How-to for the method |

## Monorepo structure

| Name | Source → Target | Cardinality | Use |
|---|---|---:|---|
| `Related Repositories` | Module/Documentation → Repository | many | Where code and docs live |
| `Related Libraries` | Repository → Module | many | Shared libraries inside |
| `Related Projects` | Repository → Project | many | Projects inside the repo |
| `Related Documentation` | Repository/Module → Documentation | many | Repo/module docs |
| `Dependencies` | Module → Module | many | Required modules |
| `Related Architecture` | Documentation/Guide → Architecture | many | System context |

## Sales and leads (added 2026-09-10)

> Grounds the sales pipeline (`docs/agenda/sales-pipeline.md`) in the graph.
> Property formats follow Anytype's current set: Text, Number, Date, Select,
> Multi-select, Email/Phone/URL, Checkbox, File & Media, Object (relation).

| Name | Source → Target | Format | Cardinality | Use |
|---|---|---|---:|---|
| `Stage` | Lead → Select | Select | one | Lead, Qualified, Demo/Trial, Proposal, Negotiation, Won, Lost |
| `Related Product` | Lead → Product | Object | one | What the lead may buy |
| `Source` | Lead → Integration | Object | one | Where the lead came from |
| `Owner` | Lead → Person | Object | one | Accountable salesperson |
| `Next Step` | Lead → Text | Text | one | Single next action, always with a date |
| `Next Step Date` | Lead → Date | Date | one | When the next step is due |
| `Deal Value` | Lead → Number | Number | one | Expected revenue (targets currency of `pricing-plans.md`) |
| `Converted To` | Lead → Edition | Object | one | Edition won on `Stage` = Won |
| `Lost Reason` | Lead → Select | Select | one | Price, Timing, Competitor, No decision, Other |
| `Captured` | Lead → Date | Date | one | Entry date into the pipeline |

**Cardinality rule extension:** a Lead sits in exactly one `Stage` at any time;
history is kept by moving the row to the closed/lost log (never by duplicating
the object).

## Assignment and accountability (added 2026-09-10)

> Complements the existing `Owner`/`Lead`/`Member Of` relations: who assigns
> what to whom, so any object's accountability chain is queryable.

| Name | Source → Target | Cardinality | Use |
|---|---|---|---:|
| `Assigned To` | Task/Feature → Person | one | Doer — complements `Owner` (accountable) |
| `Reviewer` | Task/Release/Decision → Person | one | Verification gate |
| `Blocked By` | Task/Feature → Task | many | Cross-object blocker, with reason in Notes |
| `Reported In` | Task/Feature → Sprint | one | Sprint the work was logged in |
| `Sign-off By` | Project/Plan → Person | one | Closeout approver (completion checklist) |

## Marketing claims evidence (added 2026-09-10)

> Grounds the claims register (`docs/plans/marketing-claims.md`, evidence
> levels in `data-analyst-plans.md`) in the graph.

| Name | Source → Target | Format | Cardinality | Use |
|---|---|---|---:|---|
| `Evidence Level` | Market Research/Claim → Select | Select | one | Capability, Pilot, Measured, Regulated |
| `Evidence Source` | Claim → Any | Object | many | Test, pilot, benchmark, or legal review backing it |
| `Review Date` | Claim → Date | Date | one | Quarterly claims gate |
| `Approved By` | Claim → Person | Object | one | Evidence reviewer |
| `Safe Wording` | Claim → Text | Text | one | Approved public phrasing |

## POS graph

| Path | Flow |
|------|------|
| Products | Workspace → Project → Product → Edition → Feature → Release; Product → Campaign → Channel, Sales → Commerce, Team → Person |
| Delivery | Workspace → Plan → Goal → Milestone → Task; Plan → Market Research → Decision |
| Sales | Source (Integration) → Lead → Product/Edition → Won (Revenue → pricing-plans targets) |
| Analysis | Report → Methodology → Insight → Recommendation → Task; Dashboard → Related Reports |
| Structure | Repository → Project/Module → Documentation → Guide |

## Related

- → `_object-types.md` — Type definitions
- → `_templates.md` — Object templates + assignment matrix
- → `_tags.md` — Shared tag vocabulary
- → `../guides/pos-documentation-system.md` — Import method
- → `../README.md` — Master index
