# CTC Research — AI Prompt Catalog

Prompts for the CTC Research site at `applications/ctc-research/`. For monorepo-wide prompts
see `/home/structa.cloud/PROMPTS.md`.

**Docs:** `docs/websites/ctc-research/index.md` · `applications/ctc-research/AGENTS.md`

---

## 1. Adding a New Blog Post Field (CTC Research)

**Prompt:**
> Add a `<field_name>` field of type `<FieldType>` to the CTC Research blog Post model.
> Add the Wagtail panel, create the migration, and update the blog list/detail templates.

**Expected input:**
- Field name and Django field type (`RichTextField`, `ImageChooserPanel`, `TaggableManager`, etc.)
- Whether optional or required
- Whether to display on list view, detail view, or both

**Expected output:**
- Field on the Post model with correct Wagtail panel
- Migration at `ctc-research/plugins/blog/migrations/` or `ctc-research/www/apps/blog/migrations/`
- Template update in `ctc-research/plugins/blog/templates/blog/`
- `make -C applications migrate WEBSITE=ctc-research` command confirmed to run clean

**Sample — adding a `featured_image` to the blog Post model:**
```python
# applications/ctc-research/plugins/blog/models.py
from django.db import models
from wagtail.images.models import Image
from wagtail.admin.panels import FieldPanel, ImageChooserPanel

class Post(Page):
    featured_image = models.ForeignKey(
        Image, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="blog_posts"
    )

    content_panels = Page.content_panels + [
        ImageChooserPanel("featured_image"),
    ]
```
Template in `blog/post_detail.html`:
```html
{% if page.featured_image %}
<figure class="post__hero">
  {% image page.featured_image width-1200 class="post__hero-img" %}
</figure>
{% endif %}
```

---

## 2. Adding an LMS Course (CTC Research)

**Prompt:**
> Add a new `<CourseName>` course page or course module to the CTC Research LMS plugin.
> The course should be accessible at `/courses/<slug>/` and include a progress-tracking
> fragment at `/courses/<slug>/progress/`.

**Expected input:**
- Course model fields (title, description, duration, prerequisites)
- Whether this is a top-level `CoursePage` or a nested `CourseModule`
- Template location: `ctc-research/plugins/lms/templates/lms/`

**Expected output:**
- Model added to `ctc-research/plugins/lms/models.py` or a new sub-module
- Migration run under `WEBSITE=ctc-research`
- Course viewset registered in the lms Application
- Progress fragment as a `FragmentComponent` with `fragment_name="ctc.fragments.lms.course_progress"`

**Sample — course progress fragment:**
```python
# applications/ctc-research/plugins/lms/viewsets.py
from django_fusion.comp.routes import FragmentComponent
from .models import CourseEnrollment

class CourseProgressFragment(FragmentComponent):
    route_path = "courses/<slug:slug>/progress/"
    fragment_name = "ctc.fragments.lms.course_progress"
    template_name = "lms/fragments/course_progress.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["enrollment"] = CourseEnrollment.objects.get(
            user=self.request.user,
            course__slug=self.kwargs["slug"],
        )
        return ctx
```

---

## 3. Overriding a Shared Component for CTC Research

**Prompt:**
> The shared `components/pagination/numbers.html` needs a CTC-specific variant that adds
> course category filtering links below the pagination. Create the override in
> `ctc-research/plugins/components/` and switch the LMS list template to use it.

**Expected input:**
- The shared template path being overridden
- New context variables the override needs
- Whether this override should eventually be contributed back to `assets/templates/`

**Expected output:**
- `ctc-research/plugins/components/pagination/numbers-lms.html` (new file, not overwriting shared)
- LMS list template updated: `{% comp "pagination/numbers-lms.html" page_obj=page_obj categories=categories / %}`

**Sample — category-aware pagination component:**
```html
{# ctc-research/plugins/components/pagination/numbers-lms.html #}
{% load components %}
{% comp "components/pagination/numbers.html" page_obj=page_obj / %}

{% if categories %}
<nav class="course-filter" aria-label="Filter by category">
  {% for cat in categories %}
  <a class="course-filter__tag {% if cat.slug == active_category %}course-filter__tag--active{% endif %}"
     href="?category={{ cat.slug }}">{{ cat.name }}</a>
  {% endfor %}
</nav>
{% endif %}
```


---

## 4. Adding a Social Auth Provider (CTC Research)

**Prompt:**
> Enable `<provider>` social auth for CTC Research. Update `plugins/accounts/adapters.py`,
> add the provider to settings, and update the login modal template.

**Expected input:**
- Provider (e.g., `linkedin_oauth2`, `github`, `google`)
- Required `SOCIALACCOUNT_PROVIDERS` settings block
- Whether existing `AuthHTMXSocialAccountAdapter` needs a new method

**Expected output:**
- Provider in `INSTALLED_APPS` and `SOCIALACCOUNT_PROVIDERS` in `ctc-research/settings.py`
- `adapters.py` updated if a custom `social_login` redirect is needed
- Login modal in `ctc-research/plugins/accounts/templates/auth/login_modal.html` updated with provider button
- Env var keys added to `ctc-research/.env.example`

---

## 5. Running a CTC Research Data Migration

**Prompt:**
> Run a data migration to populate `<field>` on existing `<Model>` records with
> `<default_value>`. Use Django's `RunPython` migration operation.

**Expected output — migration skeleton:**
```python
# applications/ctc-research/plugins/lms/migrations/XXXX_populate_<field>.py
from django.db import migrations

def populate_field(apps, schema_editor):
    Model = apps.get_model("lms", "Course")
    Model.objects.filter(<field>=None).update(<field>=<default_value>)

def reverse_migration(apps, schema_editor):
    pass  # Non-reversible

class Migration(migrations.Migration):
    dependencies = [("lms", "XXXX_previous")]
    operations = [migrations.RunPython(populate_field, reverse_migration)]
```
Run: `make -C applications migrate WEBSITE=ctc-research`

---

## 6. Updating CTC Research Auth Email Templates

**Prompt:**
> Update the `email_confirmation` auth email for CTC Research. The email content is managed
> as a Wagtail snippet (`AuthEmailTemplate`). Update the snippet in Wagtail admin or via fixture.

**Expected output:**
- Wagtail snippet updated via admin or `applications/ctc-research/assets/fixtures/auth_email_templates.json`
- Fallback template at `ctc-research/assets/emails/email_confirmation.html` also updated
- Adapter in `plugins/accounts/adapters.py` confirmed to fall back correctly

**Confirm adapter fallback:**
```python
from django_fusion.wagtail.snippets import AuthEmailTemplate

snippet = AuthEmailTemplate.objects.filter(email_type="account/email/email_confirmation").first()
assert snippet is not None, "Snippet not found — create it in Wagtail admin"
```
