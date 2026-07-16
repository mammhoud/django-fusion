# django-fusion shared Wagtail viewsets

`django-fusion` owns reusable Wagtail admin behavior that is not tied to a single
Structa Cloud site. Site projects should import shared snippet functionality
from `django_fusion.wagtail.viewsets` and keep site-specific configuration next
to the site models.

## Shared import

```python
from django_fusion.wagtail.viewsets import BaseSnippetViewSet
```

`BaseSnippetViewSet` provides generic snippet actions and display helpers:

- `duplicate` bulk action.
- `export_csv` bulk action driven by `list_export` and `csv_filename`.
- `icon_boolean`, `link_display`, and `image_display` admin display helpers.

## Site responsibilities

Each site should define its own model references, labels, icons, menu names, and
export field lists in local viewset classes. Do not add CTC Research, LMS Demo,
or VResume model imports to `django-fusion`.

### CTC Research

```python
from django.utils.translation import gettext_lazy as _
from django_fusion.wagtail.viewsets import BaseSnippetViewSet

from ctc_research.models import ResearchPartner


class ResearchPartnerViewSet(BaseSnippetViewSet):
    model = ResearchPartner
    icon = "group"
    menu_label = _("Research partners")
    menu_name = "research-partners"
    list_export = ["name", "website"]
    csv_filename = "research-partners.csv"
```

### LMS Demo

```python
from django.utils.translation import gettext_lazy as _
from django_fusion.wagtail.viewsets import BaseSnippetViewSet

from lms_demo.models import CourseProvider


class CourseProviderViewSet(BaseSnippetViewSet):
    model = CourseProvider
    icon = "academic-cap"
    menu_label = _("Course providers")
    menu_name = "course-providers"
    list_export = ["name", "is_active"]
    csv_filename = "course-providers.csv"
```

### VResume

```python
from django.utils.translation import gettext_lazy as _
from django_fusion.wagtail.viewsets import BaseSnippetViewSet

from pages.portfolio.models import Project


class ProjectViewSet(BaseSnippetViewSet):
    model = Project
    icon = "folder-open-inverse"
    menu_label = _("Projects")
    menu_name = "portfolio-projects"
    list_export = ["title", "client", "is_featured"]
    csv_filename = "vresume-projects.csv"
```

During migration, VResume also re-exports the shared base from
`core/VResume/www/core/snippets/` for older imports. New code should use
`django_fusion.wagtail.viewsets` directly.
