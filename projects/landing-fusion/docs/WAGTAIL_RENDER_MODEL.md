# Wagtail fields & component render model — landing-fusion

> **Status:** current as of 2026-08-12
> **Scope:** what each Wagtail page/field is for, where it renders, and the
> exact conditions that decide *when* and *on which road* it appears.

The one-sentence rule: **every page is a document, not an app.** The backend
renders finished HTML in one response (no SPA hydration waterfall); the Astro
frontend is a second render road that consumes the *same* Wagtail content as
JSON. Editors author once; two roads render it.

---

## 1 · The two render roads

| Road | Trigger | Template/response | Who consumes it |
|---|---|---|---|
| `fusion-render` (HTML) | No `X-Fusion-Render-First: data-api` header | Full document via `PageHandler` | Browsers, crawlers, the Django front |
| `data-api` (JSON) | `X-Fusion-Render-First: data-api` header | `apps/pages/api.py` JSON endpoints | The Astro build (`src/lib/api.ts`) |

The default is set by `FUSION_RENDER_FIRST_DEFAULT` in `backend/settings.py`
and can be overridden per request with the `X-Fusion-Render-First` header.
The client switch lives in `frontend/src/components/ui/RenderModeSwitch.astro`
(+ the `renderModeSwitch` Alpine component in `alpine.js`).

### Fragment vs full (on the HTML road)

`PageHandler` (via `FragmentHandlerMixin`) picks the template from the request:

- **HTMX request** (`HX-Request: true`, or UnPoly) → `pages/fragments/page.html`
  — only the content region, no `<html>`/`<head>`/scripts. Used by
  `hx-get`/`hx-swap` (LiveFragment, RenderModeSwitch HTML road).
- **Plain GET** → the full page template (`pages/<slug>.html`).

Fragment endpoints: `GET /fragment/pages/<slug>/` (see `apps/pages/api.py`).
**Never** hit a bare `/<slug>` with an `HX-Request` header — that returns a
full document and re-runs page scripts (the classic "page reloads itself"
bug).

---

## 2 · Page models → route → template

| Page model | Route | Template | Notes |
|---|---|---|---|
| `AboutPage` | `/about/` | `pages/about.html` | Hero + body + `SectionStackMixin` sections |
| `TeamPage` | `/about/team/` | `pages/team.html` | `team` StreamField (`TeamSectionBlock`) member cards |
| `FounderPage` | `/about/founder/` | `pages/founder.html` | Hero + `tech` band + `features` skills grid |
| `StartupPage` | `/about/startup/` | `pages/startup.html` | `process` timeline + `stats` band |
| `ProductsPage` | `/products/` | `pages/products.html` | Catalog listing driven by `get_product_cards()` |
| `ProductPage` | `/products/<slug>/` | `pages/product.html` | One product reference document |
| `ProductPage` preview | `/products/<slug>/preview/<edition>/` | `pages/product_preview.html` | One edition's visual gallery |
| `PricingPage` | `/pricing/` | `pages/pricing.html` | Tabbed editions via `get_product_pricing()` |
| `FeaturesPage` | `/features/` | `pages/features.html` | Stack/capability document |
| `ContactPage` | `/contact/` | `pages/contact.html` | `contact` StreamField + form |
| `BrandPage` | `/brand/` | `pages/brand.html` | Identity boards via `get_brand_boards()` |
| Blog / Learning / FAQ / Privacy | `/blog/…`, `/learning/…`, `/faq/`, `/privacy/` | own templates | Outside the catalog; same dual-road contract |

---

## 3 · `ProductPage` fields — where & when each renders

| Field | Purpose | Renders where | Condition |
|---|---|---|---|
| `category` | application / platform / library | Product card chip | Always, on listing + detail |
| `tagline` | One-line pitch | Card + detail hero + pricing tab | Always |
| `version` | e.g. `beta 0.2` | Card + detail | Always (empty string hides it) |
| `logo_style` | `crest`/`ribbon`/`isometric`/`orbit`/`ascent` | The constructed mark (`ProductLogo`) | Always; drives the SVG mark + brand hue |
| `status` | `live` / `development` | Amber caution badge + warning banner on detail | `status == "development"` |
| `hidden` | Hide from catalog | Excludes from `/products/`, `/pricing/`, home, nav, `/brand/` | `hidden is True` — **detail page stays reachable by direct link** |
| `show_on_home` | Curate the home grid | Homepage preview cards + nav dropdown | `show_on_home is False` → catalog/pricing yes, home/nav no (subproducts like vResume) |
| `body` | Overview prose (`RichTextField`) | Detail overview + fragment content region | Always |
| `tech` | `TechStackSectionBlock` | Detail "Built on" band | Present when seeded |
| `editions` | `EditionsSectionBlock` | Detail editions grid, pricing tabs, `/apis/pricing/`, `/apis/pages/<slug>/` | Always (the priced tiers) |
| `comparison` | `FeatureComparisonSectionBlock` | Detail feature table | Present when seeded |
| `applications` | `ApplicationsSectionBlock` | Detail "Built with this" | Present when seeded |
| `features` | `FeaturesSectionBlock` | Detail feature grid | Present when seeded |
| `gallery` | `MediaGalleryBlock` | Detail visual gallery + `/apis/pages/<slug>/` `gallery` | Present when seeded |
| `faq` | `FaqSectionBlock` | Detail FAQ | Present when seeded |
| `snippets` | `SnippetsSectionBlock` | **Nowhere** — legacy compatibility field, not exposed in `content_panels`; code belongs on `BlogPostPage` only | Never rendered on product pages |

### Visibility decision tree (`get_product_cards`)

```
ProductPage child, live
  ├─ hidden is True        → excluded from every catalog surface
  └─ hidden is False
       ├─ for_home=True and show_on_home is False → catalog/pricing only
       └─ otherwise → catalog + pricing (+ home/nav when show_on_home)
```

Same exclusion is applied in `products_api` (`/apis/products/`) by filtering
out hidden `detail_slug`s, and in `get_product_pricing()` / `get_brand_boards()`
(which reuse `get_product_cards()`).

### Edition block shape (`EditionsSectionBlock`)

Each edition: `name`, `tagline`, `price`, `period`, `offer_label`,
`offer_old_price`, `features`, `preview_images`, `cta_label`, `cta_href`,
`featured`, `tier` (`outline` / `default` / `featured` / `managed`).

- `offer_label` + `offer_old_price` render the discount badge + struck-through
  original price (e.g. "50% off · launch", was $258).
- `tier == "managed"` renders the corner ribbon; `featured is True` is the
  highlighted card ("most shipped").

---

## 4 · Components & blocks (where the markup lives)

| Component / block | Source | Render condition |
|---|---|---|
| Hero / CTA / stats / features / FAQ / testimonials | `apps/content/blocks.py` `*SectionBlock`s → `pages/partials/page_content.html` | Per-page `StreamField` presence |
| `TeamSectionBlock` → `TeamMemberBlock` | `apps/content/blocks.py` | `TeamPage.team` — name/role/bio/initials/links |
| `ProcessSectionBlock` (timeline) | `apps/content/blocks.py` | `StartupPage.process`, services `process` |
| `ProjectBlock` | `apps/content/blocks.py` | `ProductsPage.projects` |
| `LiveFragment` / `LiveFragmentTarget` | `frontend/src/components/ui/` | Reveal-triggered `hx-get` → fragment swap |
| `RenderModeSwitch` | `frontend/src/components/ui/` | Home/products/features — picks HTML vs data road |
| `ProductLogo` | `frontend/src/components/ui/` | Product cards + brand boards |
| `BrandModal` | shared partial (`page_content.html`) + `alpine.js` | `[data-open-brand]` triggers, `/apis/brand/` data |
| `OutcomeFramework` | `frontend/src/components/blocks/` | Homepage — incl. the illustrative ROI model (`data-roi-model`) |

---

## 5 · "Documents, not pages-content"

The phrase means the content contract is a **complete, self-contained
document** per URL:

1. **One response, finished HTML** — the HTML road returns the full page
   (meta, content region, styles) in one GET; no client-side hydration to
   assemble the page.
2. **Fragments are content-region-only** — HTMX asks for a fragment, it gets
   *only* the region (`pages/fragments/page.html`), never a nested `<html>`.
3. **Data API is a second view of the same document** — `/apis/pages/<slug>/`
   serializes the same Wagtail fields the HTML road renders, so the Astro
   build never maintains a parallel source of truth.
4. **Editorial fields are the source** — copy, editions, team, and blocks live
   in Wagtail (`seed_pages.py` only bootstraps); the frontend fallbacks exist
   solely to keep the build green before Django is healthy, and are
   deliberately mirrors of the seed, not separate content.

When a field should act as *document content* (rendered once, on both roads)
vs *application state* (interactive), prefer the former: put it in Wagtail,
render it server-side, and enhance with Alpine/HTMX only where interactivity
earns its place.
