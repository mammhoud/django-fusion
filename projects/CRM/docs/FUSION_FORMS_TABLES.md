# Loop-CRM — django-fusion Forms & Tables

Product-level documentation for how Loop-CRM uses the django-fusion component
system. The framework reference lives in
[`libs/django-fusion/docs/06-forms-and-tables.md`](../../../libs/django-fusion/docs/06-forms-and-tables.md)
and `COMPONENT_FORMS_TABLES.md`; this page only documents Loop-CRM's own usage
and the rules a new resource must follow. Link, don't duplicate.

## 1. Component overrides (why DIRS-before-APP_DIRS matters)

Loop-CRM shadows two django-fusion built-in components with project templates:

| Framework component | Loop-CRM override |
|---|---|
| fusion table | `backend/templates/fusion/components/table.html` |
| fusion form | `backend/templates/components/form/form.html` |

`TEMPLATES['DIRS'] = [BASE_DIR / "templates"]` is searched before `APP_DIRS`,
so the project template wins over the package default. This is how the tactical
telemetry treatment (mono uppercase headers with `+` ticks, hard corners, red
accent rows, type-driven cells) applies to **every** Django-rendered table/form
without editing the framework.

**Single-line `{% comp %}` rule.** Multi-line `{% comp %}` tags break the
Django template lexer in this setup — every form partial uses single-line tags.

## 2. Schema-aware tables (`apps/core/resource_tables.py`)

`RowGenerator` + `resource_table()` produce one table contract consumed by
three surfaces:

1. Django render-first screens (`ResourceListView`),
2. `GET /bolt/tables/{resource}` (canonical, JWT, workspace-scoped),
3. `GET /api/v1/tables/{resource}/` (deprecated compatibility, session cookie).

Contract:

```json
{
  "resource": "companies",
  "headers": [{ "key": "name", "label": "Name", "type": "text", "sortable": true }],
  "rows": [["Acme", "Fintech", "…"]],
  "count": 8
}
```

`type` is one of `text | money | date | pill | link`. Cells are plain strings;
the frontend `ResourceTable` island applies styling from the type metadata.

`RESOURCE_TABLE_COLUMNS` maps each resource to its columns, formatters
(`_money`, `_date`, `_person`), and per-column types. A resource not in that
map falls back to its `read_fields` projection with all-`text` types.

## 3. The two API roads

- **Bolt road** — `GET /bolt/tables/{resource}` (JWT bearer, workspace-scoped).
  Uses `apps/core/bolt_api.py`.
- **Deprecated compatibility road** — `GET /api/v1/tables/{resource}/` (session cookie, carries Deprecation/Sunset headers). Migrate to `/bolt/tables/{resource}`.
  Uses `apps/core/api.py::tables_api`.

Both resolve through `apps/core/resources.RESOURCES` and `resource_table()` so
the projection never drifts between roads.

## 4. Frontend renderer (`ResourceTable.tsx`)

`frontend/src/components/dashboard/ResourceTable.tsx` is a bolt-first React
island with a `/api/v1` (deprecated) fallback. Per-road path shape is handled explicitly:
`/bolt` uses `/tables/{resource}` (no trailing slash), `/api/v1` (deprecated) uses
`/tables/{resource}/`.

The island is wrapped in `StoreProvider` (same as `PipelineBoard` and
`RevOpsDashboard`) because `useSelector` requires a Redux context even during
the Astro static build.

## 5. Adding a new resource (employees, §14 pattern)

1. **Model** — add (or reuse a custom object) in the owning app.
2. **Resource** — register it in `apps/core/resources.py` (`read_fields`,
   `write_fields`, `required_fields`, label/description).
3. **Table columns** — add an entry to `RESOURCE_TABLE_COLUMNS` in
   `apps/core/resource_tables.py`.
4. **Bolt road** — `apps/core/bolt_api.py` serves it automatically from the
   registry.
5. **Page map** — add the route to the `RESOURCE_BY_PATH` map (and the pages
   catalog) in `frontend/src/pages/[...path].astro`.

## 6. Form flows (create fragments)

Create flows are HTMX fragments: `POST /fragments/{module}/{resource}/create/`
returns the updated fragment with `hx-swap-oob="outerHTML"` and an
`HX-Trigger`. Forms validate cross-workspace relationships in `clean()` and
echo the `csrftoken` cookie as `X-CSRFToken` on mutations.

| Fragment | Form |
|---|---|
| `/fragments/crm/companies/create/` | `apps/crm.forms.CompanyForm` |
| `/fragments/crm/contacts/create/` | `apps/crm.forms.ContactForm` |
| `/fragments/crm/deals/create/` | `apps/crm.forms.DealForm` |
| `/fragments/finance/invoices/create/` | `apps.finance.forms.InvoiceForm` |
| `/fragments/finance/payments/create/` | `apps.finance.forms.PaymentForm` |
| `/fragments/posts/create/` | `apps.marketing.forms.PostComposerForm` |

## 7. Billing, reports, and the public landing

- **Billing** — `apps/billing` (`Plan`, `BillingAccount`, `Seat`) gates the
  workspace's subscription. `/apis/billing/plans/` (public catalog),
  `/apis/billing/account/` (authenticated state), `/billing/checkout/`,
  `/billing/portal/`, `/billing/webhook/stripe/`. See
  `docs/plans/loop-crm/wagtail-landing-plan.md` §7.
- **Reports** — `/apis/reports/` serves the report catalog rendered at
  `/reports/` (`frontend/src/components/dashboard/ReportCatalog.tsx`).
- **Landing** — Wagtail pages are served as JSON at `/apis/pages/<slug>/` and
  rendered by Astro; `/cms/` is the editor surface. See
  `docs/plans/loop-crm/wagtail-landing-plan.md`.
