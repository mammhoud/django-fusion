# Landing Fusion

The public structa.cloud site: a single catalog document that presents every
product the monorepo ships, plus the projects behind them, all managed as
Wagtail content and rendered as finished server-side HTML.

## Catalog

**Catalog**:
The single merged document (the Products page) that lists every product and every project in one place.
_Avoid_: product listing, products page, the line

**Product**:
A commercial offering with its own reference page: editions & pricing, tech stack, and reference snippets.
_Avoid_: offering, solution, line item

**Project**:
A repository artifact in the monorepo inventory, described by what it is and what it shares. Distinct from Product: products are sold in editions, projects exist in the repo.
_Avoid_: repo entry, module

**Category**:
How a product is positioned in the catalog: application, platform, or library.
_Avoid_: type, kind

**Flagship**:
The product given featured treatment at the top of the catalog (Forge POS). Determined by product identity, not by tree order.

**Edition**:
A priced tier of a product, each with its own name, price, and feature set.
_Avoid_: tier, plan, version

## Reuse

**Reference snippet**:
Reusable code or model material published on a product page so other products and projects can copy the pattern.
_Avoid_: code sample, example

**Shared feature / Own feature**:
On a project, whether a capability is reused across the monorepo (shared) or standalone to that project (own).
_Avoid_: common, unique

## Delivery

**Render mode**:
How a page is delivered — either as finished HTML from the server (fusion-render) or as data for the frontend to render (data-api). One content source serves both.
_Avoid_: server-side vs client-side, mode

**AHA stack**:
The server-first architecture every site ships on: Astro renders the document, HTMX swaps fragments, Alpine hydrates micro-interactions.
_Avoid_: the stack, AHA
