# LMS Demo — AI Prompt Catalog

Prompts for the LMS Demo site at `applications/lms-demo/`. For monorepo-wide prompts
see `/home/structa.cloud/PROMPTS.md`.

**Docs:** `docs/websites/lms-demo/index.md` · `applications/lms-demo/AGENTS.md`

---

## 1. Adding a New Course Type Field (LMS Demo)

**Prompt:**
> Add a `<field_name>` field to the LMS Demo `Course` model in
> `applications/lms-demo/plugins/lms/models.py`. Add the admin panel,
> create the migration, and update the course list and detail templates.

**Expected input:**
- Field name and type (`CharField`, `RichTextField`, `ForeignKey`, etc.)
- Whether optional or required
- Template files to update

**Expected output:**
- Field on the `Course` model with correct admin/Wagtail panel
- Migration generated and applied under `WEBSITE=lms-demo`
- Templates updated in `lms-demo/plugins/lms/templates/lms/`

**Sample — adding `difficulty_level` to Course:**
```python
# applications/lms-demo/plugins/lms/models.py
from django.db import models

class Course(models.Model):
    DIFFICULTY_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    ]
    difficulty_level = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default="beginner",
    )
```
Template addition in `lms/course_detail.html`:
```html
<span class="course-card__badge course-card__badge--{{ course.difficulty_level }}">
  {{ course.get_difficulty_level_display }}
</span>
```

---

## 2. Adding an Enrollment Status Fragment

**Prompt:**
> Add an HTMX enrollment status fragment for the LMS Demo. When a student clicks
> "Check Status", their enrollment progress loads into `#enrollment-panel`.
> Use `FragmentComponent` with `fragment_name="lms.fragments.lms.enrollment_status"`.

**Expected input:**
- Enrollment model location
- Context variables needed (`enrollment`, `progress_percentage`, `completed_modules`)
- Template: `lms-demo/plugins/lms/templates/lms/fragments/enrollment_status.html`

**Expected output:**
- `EnrollmentStatusFragment` class registered in the lms Application
- Trigger button in the course detail template
- Fragment template rendering progress bar via shared component

**Sample:**
```python
# applications/lms-demo/plugins/lms/viewsets.py
from django_fusion.comp.routes import FragmentComponent
from .models import Enrollment

class EnrollmentStatusFragment(FragmentComponent):
    route_path = "courses/<slug:slug>/status/"
    fragment_name = "lms.fragments.lms.enrollment_status"
    template_name = "lms/fragments/enrollment_status.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["enrollment"] = Enrollment.objects.get(
            user=self.request.user,
            course__slug=self.kwargs["slug"],
        )
        return ctx
```
Trigger:
```html
<button hx-get="{% url 'lms:lms:enrollment_status' course.slug %}"
        hx-target="#enrollment-panel"
        hx-swap="innerHTML"
        hx-trigger="click, load">
  Check Progress
</button>
<div id="enrollment-panel" class="enrollment-panel"></div>
```

---

## 3. Adding a Home Page Marketing Section

**Prompt:**
> Add a new `<section-name>` section to the LMS Demo home page at
> `applications/lms-demo/templates/home/main.html`. The section should use a
> shared component from `assets/templates/components/blocks/` or create a new
> site-specific block in `lms-demo/plugins/components/blocks/`.

**Expected input:**
- Section name and BEM class prefix
- Whether to use a shared component or create a site-specific one
- Context variables the section needs (passed from the home view)

**Expected output:**
- Template block in `home/main.html`
- Component file created if new
- Home view's `get_context_data` updated to pass any new context vars

---

## 4. Configuring LMS Demo WebSocket Events

**Prompt:**
> Add a WebSocket event handler in `lms-demo/www/websocket.py` for the `<event_type>`
> event (e.g., `lesson_completed`, `quiz_passed`). The handler should update the
> student's progress record and broadcast the update to connected clients.

**Expected input:**
- Event type identifier
- Data payload schema
- Model to update on receipt

**Expected output:**
- Handler function added to `lms-demo/www/websocket.py`
- Consumer routing updated
- Test in `lms-demo/tests/` verifying the handler updates the model correctly

**Sample — `lesson_completed` handler:**
```python
# applications/lms-demo/www/websocket.py
from channels.generic.websocket import JsonWebsocketConsumer
from plugins.lms.models import LessonProgress

class LMSConsumer(JsonWebsocketConsumer):
    def lesson_completed(self, data):
        LessonProgress.objects.update_or_create(
            user=self.scope["user"],
            lesson_id=data["lesson_id"],
            defaults={"completed": True},
        )
        self.send_json({"type": "progress_updated", "lesson_id": data["lesson_id"]})
```

---

## 5. Creating an LMS Demo Certification Page

**Prompt:**
> Add a certification detail page to the LMS Demo at `/certification/<uuid>/`.
> The page renders via a `RoutableComponent` and shows the student's certificate
> with a shareable public URL. Use `fragment_name="lms.fragments.certification.detail"`.

**Expected output:**
- `CertificationComponent` in `plugins/lms/viewsets.py`
- Template at `lms-demo/plugins/accounts/templates/certification/detail.html`
- Public URL included in the rendered template
- Registered in the accounts Application in `lms-demo/www/urls.py`

**Sample:**
```python
from django_fusion.comp.routes import RoutableComponent
from plugins.lms.models import Certificate
import uuid

class CertificationComponent(RoutableComponent):
    route_path = "certification/<uuid:token>/"
    template_name = "certification/detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["certificate"] = Certificate.objects.get(token=self.kwargs["token"])
        return ctx
```
