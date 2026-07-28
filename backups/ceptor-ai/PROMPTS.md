# Structa Cloud — AI Prompt Catalog

This file documents prompts for working with the Structa Cloud monorepo. Each entry includes the
exact prompt text, expected inputs, expected outputs, a working sample, related docs references,
and related tags. Prompts are organised by use-case category.

**Docs:** `AGENTS.md` · `docs/README.md` · `applications/libs/django-fusion/docs/INDEX.md`

---

## CRUD Operations

### 1. Adding a Field to an Existing Model

**Prompt:**
> Add a `<field_name>` field of type `<FieldType>` to the `<ModelName>` model in
> `applications/<site>/<app_path>/models.py`. Add the admin/Wagtail panel, create the migration,
> update the relevant templates, and verify with `make check`.

**Expected input:**
- Field name and type (`CharField`, `BooleanField`, `RichTextField`, `ImageChooserPanel`, `ForeignKey`, etc.)
- Whether optional or required; default value if applicable
- Site name (`ctc-research`, `lms-demo`, `vresume`)
- Which templates need updating (list, detail, form, or all)

**Expected output:**
- Field added to model with correct panel
- Migration via `make -C applications makemigrations WEBSITE=<site>` and `migrate`
- Template updated with guard: `{% if object.field_name %}...{% endif %}`
- `make -C applications check WEBSITE=<site>` passes

**Sample — adding `featured` boolean to CTC Research blog Post:**
```python
# ctc-research/plugins/blog/models.py
from wagtail.admin.panels import FieldPanel

class Post(Page):
    featured = models.BooleanField(default=False)
    content_panels = Page.content_panels + [FieldPanel("featured")]
```
```html
{# Template: if page.featured %}...{% endif %} #}
```
```bash
make -C applications makemigrations WEBSITE=ctc-research && make -C applications migrate WEBSITE=ctc-research && make -C applications check WEBSITE=ctc-research
```

**Related docs:** `AGENTS.md#CRUD Sample` · `applications/ctc-research/AGENTS.md` · `applications/libs/django-fusion/docs/COMPONENT_SYSTEM.md`
**Related tags:** `ModelViewset`, `Wagtail`, `FieldPanel`, `migration`, `template`

---

### 2. Creating a New Model and Wiring the Viewset

**Prompt:**
> Create a new `<ModelName>` model in `applications/<site>/www/apps/<app>/models.py` with
> fields `<field_list>`. Wire it up with a `ModelViewset`, register in an `Application`,
> create list/detail/form templates, and verify the URLs work.

**Expected input:**
- Model name and field definitions
- App name and site name
- Whether the viewset needs search, filters, or bulk delete

**Expected output:**
- Model class with `__str__` and `Meta.ordering`
- Migration generated and applied
- `ModelViewset` subclass with `model`, `paginate_by`, `template_name`
- `Application` registration in site `www/urls.py`
- Three template stubs: `_list.html`, `_detail.html`, `_form.html`
- URLs browsable at `/<app_name>/`

**Sample — `Event` model with viewset for lms-demo:**
```python
# 1. Model — lms-demo/plugins/lms/models.py
class Event(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateTimeField()
    location = models.CharField(max_length=300)
    is_published = models.BooleanField(default=False)
    class Meta:
        ordering = ["-date"]

# 2. Viewset
from django_fusion.comp.routes import ModelViewset
class EventViewset(ModelViewset):
    model = Event
    paginate_by = 20
    template_name = "events/event"

# 3. Register
events_app = Application(title="Events", app_name="events", viewsets=[EventViewset])
```

**Related docs:** `AGENTS.md#CRUD Sample: Creating a New Model` · `applications/libs/django-fusion/docs/ROUTING_SYSTEM.md` · `applications/libs/django-fusion/docs/COMPONENT_SYSTEM.md`
**Related tags:** `ModelViewset`, `Application`, `migration`, `template`, `URL routing`

---

### 3. Adding a FragmentComponent (HTMX Partial Update)

**Prompt:**
> Add an HTMX fragment for `<feature>` in `applications/<site>/`. The fragment is triggered by
> clicking a button and loads into `#<target-id>`. Use `FragmentComponent` from
> `django_fusion.comp.routes` and the `fragment_name` kwarg.

**Expected input:**
- Fragment name (dot-notation: `<site>.fragments.<app>.<name>`)
- Trigger element and HTMX attributes (`hx-get`, `hx-target`, `hx-swap`, `hx-trigger`)
- Target div ID and context variables

**Expected output:**
- `FragmentComponent` subclass with `route_path`, `fragment_name`, `template_name`
- Fragment template file
- Trigger button/div in the parent template

**Sample — enrollment status fragment (LMS Demo):**
```python
class EnrollmentStatusFragment(FragmentComponent):
    route_path = "courses/<slug:slug>/status/"
    fragment_name = "lms.fragments.lms.enrollment_status"
    template_name = "lms/fragments/enrollment_status.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["enrollment"] = Enrollment.objects.get(
            user=self.request.user, course__slug=self.kwargs["slug"])
        return ctx
```
```html
<!-- Trigger -->
<button hx-get="{% url 'lms:lms:enrollment_status' course.slug %}"
        hx-target="#enrollment-panel" hx-swap="innerHTML" hx-trigger="click, load">
  Check Progress
</button>
<div id="enrollment-panel"></div>
```

**Related docs:** `applications/libs/django-fusion/docs/COMPONENT_SYSTEM.md#FragmentComponent` · `applications/libs/django-fusion/docs/ROUTING_SYSTEM.md` · `AGENTS.md#Component System`
**Related tags:** `FragmentComponent`, `HTMX`, `hx-get`, `hx-target`, `fragment_name`

---

### 4. Adding a Wagtail StreamField Block

**Prompt:**
> Add a new StreamField block `<BlockName>` to `django_fusion.wagtail.blocks` or to
> `applications/<site>/www/<app>/blocks.py`. Document the block fields and template.

**Expected input:**
- Block name, field definitions (CharBlock, URLBlock, ChoiceBlock, etc.)
- Whether shared or site-specific
- Template location

**Expected output:**
- Block class with `Meta.template` and `Meta.icon`
- Template file at `components/blocks/<name>.html`
- Panel added to the parent Page model's `body` StreamField

**Sample — `CallToActionBlock`:**
```python
from wagtail.blocks import StructBlock, CharBlock, URLBlock, ChoiceBlock
class CallToActionBlock(StructBlock):
    heading = CharBlock(max_length=120)
    button_text = CharBlock(max_length=60)
    button_url = URLBlock()
    style = ChoiceBlock(choices=[("primary", "Primary"), ("secondary", "Secondary")])
    class Meta:
        template = "components/blocks/call_to_action.html"
        icon = "pick"
```

**Related docs:** `applications/libs/django-fusion/docs/WAGTAIL_INTEGRATION.md` · `applications/libs/django-fusion/docs/COMPONENT_SYSTEM.md`
**Related tags:** `StreamField`, `StructBlock`, `Wagtail`, `FieldPanel`

---

## Component System

### 5. Creating a Component with Props and Slots

**Prompt:**
> Create a reusable card component at `applications/assets/templates/components/blocks/card.html`
> with props for `title`, `summary`, `image`, and named slots for `header` and `footer`.
> Use BEM classes and the `{% comp %}` tag.

**Expected input:**
- Component name and template path
- Prop names with defaults
- Named slot names
- BEM class prefix

**Expected output:**
- Component template with `{% prop %}`, `{% slot %}`, `{{ attrs }}`
- Auto-registered at startup (no manual registration needed)
- Usage example showing both self-closing and pair-tag forms

**Sample:**
```django
{# components/blocks/card.html #}
{% load components %}
{% prop title %}
{% prop summary="" %}
{% prop image=None %}
<article class="card {{ attrs }}">
  {% if props.image %}<img class="card__image" src="{{ props.image }}" alt="{{ props.title }}">{% endif %}
  <h3>{{ props.title }}</h3>
  {% if props.summary %}<p>{{ props.summary }}</p>{% endif %}
  {% slot header %}{% endslot %}
  <div class="card__body">{% slot %}{{ slot }}{% endslot %}</div>
  {% slot footer %}{% endslot %}
</article>
```

**Related docs:** `applications/libs/django-fusion/docs/COMPONENT_TAG.md` · `applications/libs/django-fusion/docs/COMPONENT_SYSTEM.md` · `AGENTS.md#Component Tag`
**Related tags:** `{% prop %}`, `{% slot %}`, `{{ attrs }}`, `{% comp %}`, `BEM`

---

### 6. Using Self-Closing Components (No Slots)

**Prompt:**
> Create a badge/status indicator component that only needs props, no slots. Use self-closing
> `{% comp "name" / %}` syntax.

```django
{# components/badges/status.html #}
{% load components %}
{% prop status="default" %}
{% prop label="" %}
<span class="badge badge--{{ props.status }} {{ attrs }}" aria-label="{{ props.status }}">
  {{ props.label|default:props.status }}
</span>
```
```django
{% comp "components/badges/status.html" status="active" label="Active" / %}
{% comp "components/badges/status.html" status="draft" / %}
```

**Related docs:** `applications/libs/django-fusion/docs/COMPONENT_TAG.md#Self-Closing`
**Related tags:** `self-closing`, `{% comp / %}`

---

### 7. django-bird / django-cotton → `{% comp %}` Migration

**Prompt:**
> Convert this cotton/django-bird component to django-fusion `{% comp %}` syntax.

**Conversion table:**
| Cotton/bird | django-fusion `{% comp %}` |
|-------------|---------------------------|
| `<c-vars title="Hi" />` | `{% prop title="Hi" %}` |
| `<c-slot name="header">` | `{% slot header %}...{% endslot %}` |
| `{{ slot }}` | `{% slot %}{{ slot }}{% endslot %}` |
| `{{ attrs }}` | `{{ attrs }}` (identical) |
| `:title="var"` (colon) | `title=var` (standard Django) |
| `<c-card />` | `{% comp "card.html" / %}` |

**Related docs:** `applications/libs/django-fusion/docs/VIEWFLOW_MAPPING.md` · `applications/libs/django-fusion/docs/COMPONENT_TAG.md`
**Related tags:** `django-bird`, `django-cotton`, `viewflow`, `migration`

---

## Site Scaffolding

### 8. Adding a New Site to the Monorepo

**Prompt:**
> Scaffold a new site `<site-name>` in `applications/<site-name>/` following monorepo
> conventions. Set up `settings.py`, `manage.py`, `Makefile`, `docker-compose.yml`, `AGENTS.md`,
> `PROMPTS.md`, and wire it into `applications/Makefile`.

**Expected input:** Site name, domain, required plugins
**Expected output:** Full site directory, Makefile alias, AGENTS.md with template tree, PROMPTS.md with stubs, updated `docs/per-app-docs/index.md` inventory

**Related docs:** `AGENTS.md#Site Paths` · `applications/lms-demo/AGENTS.md` (reference template)
**Related tags:** `scaffold`, `Site`, `settings.py`, `Makefile`

---

### 9. Adding a New Plugin to a Site

**Prompt:**
> Add a new `<plugin-name>` plugin to `applications/<site>/plugins/<plugin-name>/` with
> `models.py`, `viewsets.py`, and `templates/`. Register the plugin in the site's settings.

**Sample structure:**
```
<site>/plugins/<name>/
├── __init__.py
├── apps.py
├── models.py
├── viewsets.py
└── templates/<name>/
    ├── <name>_list.html
    └── <name>_detail.html
```

**Related docs:** `AGENTS.md#Template Conventions` · site-specific `AGENTS.md`
**Related tags:** `plugin`, `Django app`, `AppConfig`

---

### 10. Adding a Shared Config Module

**Prompt:**
> Create `applications/configs/base/<name>.py` with shared settings for `<feature>`.
> Import it from `applications/configs/settings/conf.py` or site `settings.py`.
> Never duplicate settings across sites.

**Related docs:** `AGENTS.md#Shared Settings` · `applications/configs/settings/conf.py`
**Related tags:** `settings`, `configuration`, `Dynaconf`

---

## Default Template Tags

### 11. Using Built-In Component Tags

**Prompt:**
> Use the django-fusion `{% comp %}` tag or Unfold admin tags in a template without adding `{% load %}`.

**Context:**
`applications/configs/base/templates.py` registers these tag libraries as Django builtins:
- `django_fusion.comp.templatetags.components` → `{% comp %}`, `{% prop %}`, `{% slot %}`, `{% var %}`, `{% css %}`, `{% js %}`
- `django_fusion.templatetags.ui_tags` → table, pagination, search, form helpers
- `unfold.templatetags.unfold` → Unfold admin tags
- `django.templatetags.static` → `{% static %}`

**Expected output:**
- Template uses `{% comp "components/button.html" label="Save" / %}` directly.
- No `{% load components %}` required, though it remains harmless.
- `make -C applications check WEBSITE=ctc-research` passes.

**Sample:**
```django
{# No {% load %} needed #}
{% comp "components/cards/card.html" title="Hello" %}
  <p>Slot content</p>
{% endcomp %}
```

**Related docs:** `AGENTS.md#Default Template Tags` · `applications/configs/base/templates.py`
**Related tags:** `builtins`, `{% comp %}`, `django-fusion`, `unfold`

---

## Documentation Maintenance

### 12. Updating the Docsify Sidebar

**Prompt:**
> Add/update a section in `docs/_sidebar.md`. Ensure the target file exists.
> Run `make docs-check` to verify no broken links.

**Sample sidebar entry:**
```markdown
- **Reference**
  - [New Reference Page](reference/new-page.md)  ← add this line
```
**Sample run:**
```bash
python3 applications/scripts/check_markdown_links.py --scope docs/
# BROKEN  docs/_sidebar.md:14  →  docs/changelog/index.md  (file not found)
# Fix: create docs/changelog/index.md or correct the path
```

**Related docs:** `docs/README.md` · `docs/_sidebar.md`
**Related tags:** `Docsify`, `sidebar`, `markdown`, `links`

---

### 12. Checking and Fixing Markdown Link Errors (CI)

**Prompt:**
> Run the markdown link checker scoped to `docs/` and fix all reported broken links.
> Use `python3 applications/scripts/check_markdown_links.py --scope docs/`.

**Expected input:** Output of the link checker (list of file:line → broken target)
**Expected output:** Each broken relative link either rewritten to correct path, or missing file created

**Sample run:**
```bash
python3 applications/scripts/check_markdown_links.py --scope docs/
# Example output:
# BROKEN  docs/_sidebar.md:14  →  docs/changelog/index.md  (file not found)
# Fix: create docs/changelog/index.md as a stub, or correct the path
```

**Related docs:** `scripts/check_markdown_links.py` · `docs/README.md#Local Preview`
**Related tags:** `CI`, `markdown`, `links`, `validation`

---

### 13. Adding a Documentation Reference to AGENTS.md

**Prompt:**
> Add a documentation reference row to `AGENTS.md` Documentation References table.
> Include Topic, File path, and Description columns.

```markdown
| Component tag API | `applications/libs/django-fusion/docs/COMPONENT_TAG.md` | Props, slots, vars, attrs |
```

**Related docs:** `AGENTS.md#Documentation References`
**Related tags:** `AGENTS.md`, `docs reference`, `table`

---

## Auth & Email

### 15. Adding/Updating Auth Email Templates

**Prompt:**
> Add or update an `AuthEmailTemplate` Wagtail snippet for `<email_type>`.
> The adapter in `plugins/accounts/adapters.py` reads it at render time.

**Sample adapter check:**
```python
from django_fusion.wagtail.snippets import AuthEmailTemplate
snippet = AuthEmailTemplate.objects.filter(email_type="account/email/email_confirmation").first()
```

**Related docs:** `applications/libs/django-fusion/docs/WAGTAIL_INTEGRATION.md` · `applications/ctc-research/AGENTS.md`
**Related tags:** `AuthEmailTemplate`, `Wagtail snippet`, `allauth`, `email`

---

### 16. Adding a Social Auth Provider

**Prompt:**
> Enable `<provider>` social auth for `<site>`. Update settings, add provider to
> `SOCIALACCOUNT_PROVIDERS`, update login modal template, and add env vars.

**Related docs:** `docs/auth/README.md` · site-specific `AGENTS.md`
**Related tags:** `django-allauth`, `social auth`, `SOCIALACCOUNT_PROVIDERS`, `OAuth`

---

## Website-Specific Prompts

### CTC Research
| Prompt | File | Related Tags |
|--------|------|-------------|
| Add blog post field | `applications/ctc-research/PROMPTS.md#1` | Blog, Post, FieldPanel, Wagtail |
| Add LMS course section | `applications/ctc-research/PROMPTS.md#2` | LMS, Course, Viewset, Plugin |
| Override shared component | `applications/ctc-research/PROMPTS.md#3` | Component, Override, plugins/components |
| Add social auth provider | `applications/ctc-research/PROMPTS.md#4` | Auth, Social, OAuth |
| Run data migration | `applications/ctc-research/PROMPTS.md#5` | Migration, RunPython |
| Update auth email | `applications/ctc-research/PROMPTS.md#6` | Email, AuthEmailTemplate, Snippet |

### LMS Demo
| Prompt | File | Related Tags |
|--------|------|-------------|
| Add course field | `applications/lms-demo/PROMPTS.md#1` | Course, Model, Field |
| Add enrollment fragment | `applications/lms-demo/PROMPTS.md#2` | HTMX, FragmentComponent, Enrollment |
| Add home section | `applications/lms-demo/PROMPTS.md#3` | Home, Component, Blocks |
| Configure WebSocket | `applications/lms-demo/PROMPTS.md#4` | WebSocket, Channels, Consumer |
| Create certification page | `applications/lms-demo/PROMPTS.md#5` | Certification, RoutableComponent |

### VResume
| Prompt | File | Related Tags |
|--------|------|-------------|
| Add portfolio field | `applications/VResume/PROMPTS.md#1` | Portfolio, Field, Wagtail |
| Add blog post fragment | `applications/VResume/PROMPTS.md#2` | Blog, FragmentComponent, HTMX |
| Update CV section | `applications/VResume/PROMPTS.md#3` | CV, Resume, Page |
| Debug template resolution | `applications/VResume/PROMPTS.md#4` | Template, Resolution, Debug |
| Rebuild frontend assets | `applications/VResume/PROMPTS.md#5` | Webpack, SCSS, Build |
