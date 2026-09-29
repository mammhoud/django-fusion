# Wagtail Integration — DF-010

> Source of truth: `src/django_fusion/builder/blocks.py`,
> `src/django_fusion/fragments/viewsets.py`,
> `src/django_fusion/contrib/admin/wagtail_hooks.py`,
> `src/django_fusion/routes/pages/mixins.py`.
>
> **There is no `django_fusion.wagtail` package in this checkout**, and
> `pyproject.toml` declares no `wagtail` extra (extras: `test`, `dev`,
> `webpack`, `bolt`, `tables`, `tasks`, `auth`). Earlier revisions of this page
> documented `django_fusion.wagtail.{blocks,snippets,viewsets}` — those module
> paths never resolved. The real surface is the four modules above.
>
> **Verified 2026-09-22.** Corrected from the tree; the two dangling imports
> found while verifying are recorded under [Remarks](#remarks--notes).

## Install

Wagtail support needs no dedicated app entry — it ships inside
`django_fusion`. Add the bundled blocks only if you use them:

```python
INSTALLED_APPS = [
    # ...
    "wagtail",
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.routablepage",
    "wagtail.snippets",

    # django-fusion — no separate Wagtail app exists
    "django_fusion",
    "django_fusion.builder",     # only if you use the bundled StreamField blocks
]
```

## Custom StreamField block — worked example

Adding a new block is a three-step pattern:

1. Write the `StructBlock` subclass in `src/django_fusion/builder/blocks.py`
   *or* locally in your site.
2. Render it through `{% comp "wagtail/blocks/<name>.html" %}` from your page
   template.
3. Add the block to `StreamField`'s `use_json_field=True` content list.

### Site-local block (recommended for site-specific UI)

```python
# mysite/wagtail_blocks.py
from wagtail.blocks import StructBlock, CharBlock, URLBlock, ChoiceBlock

class CallToActionBlock(StructBlock):
    heading = CharBlock(required=True, max_length=120)
    description = CharBlock(required=False, max_length=400)
    button_text = CharBlock(required=True, max_length=40, default="Learn more")
    button_url = URLBlock(required=True)

    class Meta:
        template = "wagtail/blocks/call_to_action.html"
        icon = "bullhorn"
        label = "Call to action"
        group = "Calls to action"
```

> Remark: a site-local block is **preferred** over editing
> `src/django_fusion/builder/blocks.py` directly — the latter ships with the
> library and is overwritten on upgrade.

### Bundled blocks

`django_fusion.builder.blocks` ships **14 `StructBlock` subclasses**:

| Class | Class | Class |
|-------|-------|-------|
| `LinkBlock` | `ButtonBlock` | `HeroBlock` |
| `FeatureBlock` | `FeaturesSectionBlock` | `StepBlock` |
| `StepsSectionBlock` | `StatBlock` | `StatsSectionBlock` |
| `PricingTierBlock` | `PricingSectionBlock` | `FaqItemBlock` |
| `FaqSectionBlock` | `CtaBlock` | |

> Corrected 2026-09-22: this page previously listed `TimelineItemBlock` and
> `SkillBlock` as the bundled blocks. Neither is defined in the library —
> `TimelineItemBlock` appears nowhere in the checkout, and `SkillBlock` is a
> product-level block (`projects/Clients/platform/backend/apps/domain/blocks/profile/details.py`),
> not a library one.

### Wire it into a page

`routes/pages/mixins.py` provides `WagtailPageMixin` (a `FragmentHandlerMixin`
subclass) for pages that must render both a full document and a fragment.

```python
# mysite/models.py
from wagtail.fields import StreamField
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.models import Page
from django.db import models
from mysite.wagtail_blocks import CallToActionBlock

class MarketingPage(Page):
    body = StreamField([
        ("heading", blocks.CharBlock()),
        ("paragraph", blocks.RichTextBlock()),
        ("call_to_action", CallToActionBlock()),
    ], use_json_field=True)

    content_panels = Page.content_panels + [FieldPanel("body")]
```

### Render it

```django
{# templates/wagtail/blocks/call_to_action.html #}
{% load wagtailcore_tags %}
<section class="cta cta--{{ self.button_label|default:'primary' }}">
    <h2 class="cta__heading">{{ self.heading }}</h2>
    {% if self.description %}
        <p class="cta__description">{{ self.description }}</p>
    {% endif %}
    <a href="{{ self.button_url }}" class="cta__button">
        {{ self.button_text }}
    </a>
</section>
```

## Snippet viewsets — `django_fusion.fragments.viewsets`

```python
from django_fusion.fragments.viewsets import BaseSnippetViewSet, export_to_csv
```

`BaseSnippetViewSet(SnippetViewSet)` contributes two bulk actions and three
display helpers:

| Member | Kind | Purpose |
|--------|------|---------|
| `duplicate(request, queryset)` | bulk action | Clone the selected rows |
| `export_csv(request, queryset)` | bulk action | Stream the selected rows as CSV |
| `icon_boolean(field_name)` | display helper | Render a boolean column as an icon in the listing |
| `link_display(field_name)` | display helper | Render a `URLField` as a clickable link |
| `image_display(field_name)` | display helper | Render an image field as a thumbnail in the listing |

### Use it for one snippet

```python
# mysite/wagtail_hooks.py
from wagtail.snippets.models import register_snippet
from django_fusion.fragments.viewsets import BaseSnippetViewSet
from .models import Subscriber

class SubscriberViewSet(BaseSnippetViewSet):
    model = Subscriber
    list_display = ["email", "subscribed_at", "is_confirmed"]

register_snippet(SubscriberViewSet)
```

> Corrected 2026-09-22: the examples previously set `duplicate_enabled = False`
> and `export_csv_fields = [...]`. **Neither attribute exists** anywhere in
> `src/` — the two actions are always available on `BaseSnippetViewSet`, so
> there is nothing to toggle.

### `export_to_csv` utility

```python
from django_fusion.fragments.viewsets import export_to_csv

class UserExportView(BaseSnippetViewSet):
    model = User

    def export(self, request, queryset):
        return export_to_csv(queryset, fields=["email", "first_name", "last_name"])
```

`export_to_csv` writes directly to an `HttpResponse` with
`Content-Type: text/csv` and a sensible filename based on the model name and
timestamp.

## Auth email templates

The email-template model lives in **`django_fusion.models.email`**
(`EmailTemplate`), and the Wagtail snippet hook is
`django_fusion.contrib.admin.wagtail_hooks` (`AuthEmailTemplateViewSet`,
`AuthEmailSnippetGroup`, registered through `register_snippet`).

```python
# mysite/wagtail_hooks.py
from wagtail.snippets.models import register_snippet
from django_fusion.fragments.viewsets import BaseSnippetViewSet
from django_fusion.models.email import EmailTemplate

class EmailTemplateViewSet(BaseSnippetViewSet):
    model = EmailTemplate
    icon = "mail"
    menu_label = "Email Templates"
    menu_name = "email-templates"

register_snippet(EmailTemplateViewSet)
```

> **Do not import `AuthEmailTemplate`** — there is no such model. The shipped
> `AuthEmailTemplateViewSet` points `model` at a class imported from
> `contrib/admin/models.py`, a module that does not exist. See Remarks.

## Cross-references

- [DF-005 Routing](./05-routing.md) — non-snippet Wagtail integration via viewsets
- [DF-002 Architecture](./02-architecture.md) — module boundaries
- [DF-018 Slot & Prop Render Contract](./18-render-contract.md) — how a block's
  fragment renders

---

## Remarks & Notes

- **Two dangling imports in `contrib/admin/` were found while verifying this
  page** and are *not* fixed here (they are code defects, not doc defects):
  - `contrib/admin/wagtail_hooks.py:20` → `from .models import AuthEmailTemplate`.
    `contrib/admin/models.py` does not exist, and no `AuthEmailTemplate` class is
    defined anywhere in the checkout. Importing this module raises
    `ModuleNotFoundError` once Wagtail/unfold are installed. The real model is
    `django_fusion.models.email.EmailTemplate`.
  - `contrib/admin/email_admin.py:24` → `from .email_config import EmailConfiguration`.
    `contrib/admin/email_config.py` does not exist either, and
    `EmailConfiguration` is not defined anywhere.
  Both look like the tail of a package move — the same class of defect the rest
  of this page was corrected for.
- **Wagtail is not an install-time dependency of django-fusion.** There is no
  `wagtail` extra in `pyproject.toml`; the modules above import `wagtail.*` at
  module level, so a site that imports them must install Wagtail itself
  (5.x/6.x).
- **Verify paths with `make check`.** `python scripts/generate_design_docs.py
  --check` fails on stale module paths in the *generated* docs; it cannot catch
  a stale path inside hand-written prose such as this page, which is why the
  corrections here had to be made by hand against the tree.
- **Tested with:** nothing in this page executed Wagtail — the module paths,
  class names, block inventory and viewset members were read from the tree on
  2026-09-22. Re-verify with `rg "class .*Block" src/django_fusion/builder/blocks.py`
  and `rg "^class |^def " src/django_fusion/fragments/viewsets.py` before relying on them.
