# VResume — AI Prompt Catalog

Prompts specific to the VResume site at `applications/VResume/`. For monorepo-wide prompts
see `/home/structa.cloud/PROMPTS.md`.

**Docs:** `docs/websites/vresume/index.md` · `applications/VResume/AGENTS.md`

---

## 1. Adding a New Portfolio Entry Field

**Prompt:**
> Add a `<field_name>` field of type `<FieldType>` to the `PortfolioPage` model in
> `applications/VResume/www/pages/portfolio/models.py`. Add the Wagtail panel,
> update the template to display it, and run migrations.

**Expected input:**
- Field name and Django field type (e.g., `RichTextField`, `URLField`, `ForeignKey` to Image)
- Whether optional or required
- Template location: `VResume/www/pages/portfolio/templates/portfolio/main.html`

**Expected output:**
- Field added to `PortfolioPage` with correct Wagtail panel
- Migration via `make -C applications makemigrations WEBSITE=vresume`
- Template updated with `{% if page.field_name %}…{% endif %}` guard

**Sample — adding a `live_url` URLField:**
```python
# applications/VResume/www/pages/portfolio/models.py
from django.db import models
from wagtail.admin.panels import FieldPanel

class PortfolioPage(Page):
    live_url = models.URLField(blank=True, verbose_name="Live project URL")

    content_panels = Page.content_panels + [
        FieldPanel("live_url"),
    ]
```
Template addition in `portfolio/main.html`:
```html
{% if page.live_url %}
<a class="portfolio-card__link portfolio-card__link--live"
   href="{{ page.live_url }}" target="_blank" rel="noopener">
  View Live ↗
</a>
{% endif %}
```

---

## 2. Adding a Blog Post Fragment

**Prompt:**
> Add a `PostDetailFragment` to `applications/VResume/www/pages/blog/` that renders
> a single blog post via HTMX when a title is clicked. Use `FragmentComponent` with
> `fragment_name="vresume.fragments.blog.post_detail"`.

**Expected input:**
- Blog model location: `VResume/www/pages/blog/models.py`
- Fragment target div: `#blog-content`
- Template: `VResume/www/pages/blog/templates/blog/fragment.html`

**Expected output:**
- `PostDetailFragment` class registered in blog Application in `www/urls.py`
- Trigger button in `blog/main.html` using `hx-get` / `hx-target="#blog-content"`

**Sample:**
```python
from django_fusion.comp.routes import FragmentComponent
from .models import BlogPost

class PostDetailFragment(FragmentComponent):
    route_path = "blog/<slug:slug>/"
    fragment_name = "vresume.fragments.blog.post_detail"
    template_name = "blog/fragment.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["post"] = BlogPost.objects.get(slug=self.kwargs["slug"])
        return ctx
```
Trigger in list template:
```html
<button class="blog-card__title"
        hx-get="{% url 'vresume:blog:post_detail' post.slug %}"
        hx-target="#blog-content"
        hx-swap="innerHTML"
        hx-push-url="true">
  {{ post.title }}
</button>
```

---

## 3. Updating the CV/Resume Section

**Prompt:**
> Add a `<section_name>` section (e.g., `certifications`, `open_source`) to the VResume
> CV page. Requires a new `ResumePage` field or a Wagtail orderable, plus a template block.

**Expected input:**
- Section type (inline field, orderable, or separate snippet)
- Template: `VResume/www/pages/cv/templates/cv/main.html`

**Expected output:**
- Model change + migration under `WEBSITE=vresume`
- Template block guarded by `{% if page.section_name %}…{% endif %}`

---

## 4. Checking Template Resolution for VResume

**Prompt:**
> A template is not being found for VResume. List the template resolution order and
> verify each layer.

**Resolution order:**
1. `applications/VResume/templates/` — site overrides (highest)
2. `applications/VResume/www/pages/<app>/templates/` — page app templates
3. `applications/VResume/plugins/<name>/templates/` — plugin templates
4. `applications/assets/templates/` — shared templates (lowest)

**Debug command:**
```bash
make -C applications shell WEBSITE=vresume
# In shell:
# from django.template.loader import get_template
# get_template("blog/fragment.html")  # raises TemplateDoesNotExist if missing
```

---

## 5. VResume Asset Build

**Prompt:**
> Rebuild VResume frontend assets after SCSS or JS changes.

**Commands:**
```bash
make -C applications/VResume build       # webpack build for VResume
make -C applications collectstatic WEBSITE=vresume
```
