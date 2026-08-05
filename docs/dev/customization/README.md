# 🎨 Customization

> Customization tag system and per-project modification guide for the Structa Cloud monorepo.

---

## Customization Tags

Each file and component is tagged with a customization level:

| Tag | Level | Meaning |
|-----|-------|---------|
| 🟢 `customizable` | Safe | Modify, extend, override freely |
| 🟡 `delegate` | Hook | Extend through hooks/delegation |
| 🔵 `template` | Template | Template-level only changes |
| ⚪ `config` | Config | Configure via env vars/settings |
| 🔴 `not-customizable` | Core | Framework internals — modify at own risk |

---

## Per-Project Customization Matrix

### LMS (`projects/lms/`)

| Component | Level | How to Customize |
|-----------|-------|-----------------|
| Course models | 🟢 customizable | Add fields, create custom course types |
| Certification templates | 🔵 template | Override in site templates |
| Auth adapters | 🟡 delegate | Extend `RegistrationAdapter` |
| Blog plugins | 🟢 customizable | Add custom blog post types |
| Wagtail pages | 🔵 template | Override StreamField blocks |

### Portfolio (`projects/portfolio/`)

| Component | Level | How to Customize |
|-----------|-------|-----------------|
| Resume templates | 🔵 template | Override HTML/CSS templates |
| Resume sections | 🟢 customizable | Add custom section types |
| PDF export | 🟡 delegate | Extend PDF generation pipeline |
| Theme system | ⚪ config | Configure via settings.yml |

### Cypercloud (`projects/cypercloud/`)

| Component | Level | How to Customize |
|-----------|-------|-----------------|
| AI models | ⚪ config | Add models in settings.yml |
| Chat UI | 🔵 template | Override chat templates |
| Prompt templates | 🟢 customizable | Add custom prompt types |
| MCP servers | 🟡 delegate | Register new MCP providers |

### POS (`projects/pos/`)

| Component | Level | How to Customize |
|-----------|-------|-----------------|
| Store settings | ⚪ config | Configure via settings table |
| Receipt templates | 🔵 template | HTML/CSS receipt layouts |
| Tax rules | 🟢 customizable | Add custom tax calculators |
| Payment methods | 🟡 delegate | Implement payment provider interface |

---

## How to Customize

### 1. Template Override

```django
{# projects/lms/templates/components/course_card.html #}
{% extends "components/course_card.html" %}
{% block course_title %}
  <h3 class="my-custom-title">{{ course.title }}</h3>
{% endblock %}
```

### 2. Config Override

```yaml
# projects/cypercloud/configs/settings.yml
ai:
  models:
    - name: "llama3.2:latest"
      provider: "ollama"
    - name: "gpt-4o"
      provider: "openai"
      api_key: "${OPENAI_API_KEY}"
```

### 3. Hook Extension

```python
# projects/lms/plugins/courses/custom_hooks.py
from lms.plugins.courses.hooks import CourseEnrollmentHook

class CustomEnrollmentHook(CourseEnrollmentHook):
    def after_enroll(self, student, course):
        # Custom logic: send SMS, create calendar event, etc.
        pass
```

---

## Related

| Topic | Path |
|-------|------|
| Best practices | [`../guides/07-best-practices.md`](../guides/07-best-practices.md) |
| Per-project config | [`../projects/`](../projects/) |
| Clone a site | [`../guides/06-clone-site.md`](../guides/06-clone-site.md) |
| Repo overview | [`../repo-overview.md`](../repo-overview.md) |
