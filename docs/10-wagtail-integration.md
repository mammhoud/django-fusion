# Wagtail Integration — DF-010

> Source of truth: `src/django_fusion/wagtail/blocks.py`,
> `snippets.py`, `viewsets.py`.

## Add to `INSTALLED_APPS`

```python
INSTALLED_APPS = [
    # ...
    "wagtail",
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.contrib.routablepage",
    "wagtail.sites",
    # django-fusion
    "django_fusion.wagtail",
]
```

## Custom StreamField block — worked example

Adding a new block is a three-step pattern:

1. Write the `StructBlock` subclass in `django_fusion/wagtail/blocks.py`
   *or* locally in your site.
2. Render it through `{% comp "wagtail/blocks/<name>.html" %}` from
   your page template.
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

> Remark: A site-local block is **preferred** over editing
> `django_fusion/wagtail/blocks.py` directly — the latter is shipped
> with the library and is overwritten on upgrade.

### Bundled blocks

`django_fusion.wagtail.blocks` ships:

| Class | Block type | Icon |
|-------|------------|------|
| `TimelineItemBlock` | `StructBlock` (date / title / body) | `date` |
| `SkillBlock` | `StructBlock` (label / level 1-5) | `pick` |

### Wire it into a page

```python
# mysite/models.py
from wagtail.fields import StreamField
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
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

## Snippets — `AuthEmailTemplate`

`AuthEmailTemplate` is a snippet for storing email subject + body +
HTML templates used by allauth on signup / password reset. Register
its viewset in `wagtail_hooks.py`:

```python
# mysite/wagtail_hooks.py
from django_fusion.wagtail.snippets import BaseSnippetViewSet
from django_fusion.wagtail.snippets import AuthEmailTemplate

class AuthEmailTemplateViewSet(BaseSnippetViewSet):
    model = AuthEmailTemplate
    icon = "mail"
    menu_label = "Auth Emails"
    menu_name = "auth-emails"

# wagtail.snippets.register_snippet(AuthEmailTemplateViewSet)
```

## Custom snippet viewset

`BaseSnippetViewSet` adds four opt-in features:

| Method / attr | Purpose |
|---------------|---------|
| `duplicate` | Bulk-action: clone n selected rows. |
| `export_csv` | Bulk-action: stream selected rows as CSV. |
| `icon_boolean(field_name)` | Render a boolean column as an icon in the listing. |
| `link_display(field_name)` | Render a URLField as a clickable link. |
| `image_display(field_name)` | Render an image field as a thumbnail in the listing. |

### enable `duplicate` for one snippet

```python
class TagViewSet(BaseSnippetViewSet):
    model = Tag
    list_display = ["name", "slug"]
    duplicate_enabled = True
```

### `export_to_csv` utility

```python
from django_fusion.wagtail.viewsets import export_to_csv

class UserExportView(BaseSnippetViewSet):
    model = User
    export_csv_fields = ["email", "first_name", "last_name", "date_joined"]
```

`export_to_csv` writes directly to `HttpResponse` with
`Content-Type: text/csv` and a sensible filename based on the model
name and timestamp.

## Cross-references

- [DF-005 Routing](./05-routing.md) — for non-snippet Wagtail integration
  via viewsets
- [DF-002 Architecture](./02-architecture.md) — module boundaries
