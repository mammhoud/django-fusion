# Django Component Tags

Structa Cloud uses the `django-fusion` component system for reusable UI pieces.

## `{% comp %}`

Renders a registered component by dotted name.

```django
{% comp "contact.sections.form" block=block / %}
```

Component names use dot notation and map to template paths:

```text
contact.sections.form → components/blocks/contact/sections/form.html
```

## `{% comp_include %}`

Drop-in replacement for `{% include %}` that registers the include path for tracking.

```django
{% comp_include "components/form/form.html" form=my_form %}
```

Use `{% include %}` only for truly dynamic template names:

```django
{% include template_name %}
```

## Component directories

Templates are resolved from (in order):

1. `projects/<site>/templates/components/`
2. `projects/<site>/assets/templates/components/`
3. `projects/assets/templates/components/`
4. `projects/<site>/www/**/templates/`

## Per-page component inventory

> **Notation:** component names use dot notation (e.g., `home.sections.slider`) and map to template paths under `components/` by replacing dots with slashes (e.g., `components/home/sections/slider.html`). Paths shown in the tables are relative to `projects/assets/templates/` unless prefixed with a site path.

### Shared CMS pages (`projects/assets/templates/`)

| Page | Fragment | Components used |
|---|---|---|
| Home | `home/main.html` | `home/sections/slider`, `home/sections/features`, `home/sections/about`, `home/sections/services`, `home/sections/clients`, `home/sections/why_choose`, `contact.sections.card`, `contact.sections.form` |
| About | `about/main.html` | `content/page_title`, `about/sections/about`, `about/sections/testimonials`, `about/sections/clients` |
| Services | `services/main.html` | `services/includes/page_title`, `services/includes/services_section`, `services/includes/counter_section`, `services/includes/testimonial_section`, `services/includes/pricing_section`, `services/includes/clients_section` |
| Team | `team/main.html` | `content/page_title`, `team/sections/team` |
| Contact | `contact/main.html` | `content/page_title`, `contact.sections.info`, `contact.sections.map`, `contact.sections.faq`, `contact.sections.form` |
| Products | `products/main.html` | `products/page_title`, `products/products`, `products/clients` |
| Courses | `courses/main.html` | `content.page_title`, `courses/sections/courses` |
| Learning | `learning/index.html` | `learning/video_player`, `learning/lesson_resources`, `learning/discussion_comments`, `learning/lesson_notes`, `learning/course_sidebar` |

### VResume pages (`projects/portfolio/www/pages/templates/`)

| Page | Fragment | Components used |
|---|---|---|
| Home | `home/main.html` | `home/sections/slider`, `home/sections/services`, `home/sections/newsletter` |
| About | `about/main.html` | `about/sections/intro`, `about/sections/team`, `about/sections/testimonials`, `about/sections/clients` |
| Resume | `resume/main.html` | `resume/sections/education`, `resume/sections/experience`, `resume/sections/skills` |
| Skills | `skills/main.html` | `resume/sections/skills`, `skills/sections/skills_grid`, `skills/sections/skills_by_category` |
| Portfolio | `portfolio/main.html` | `portfolio/fragment` → `portfolio/sections/projects`, `search.filter_form` |
| Blog | `blog/main.html` | `blog/fragment` → `blog/sections/posts`, `search.filter_form` |
| Connect | `connect/main.html` | `connect/sections/map`, `connect/sections/form` |
| Team | `team/main.html` | `content.page_title`, `team/sections/team` |
| Services | `services/main.html` | `services/includes/page_title`, `services/includes/services_section`, `services/includes/counter_section`, `services/includes/testimonial_section`, `services/includes/pricing_section`, `services/includes/clients_section` |
| Events | `events/main.html` | `events/includes/page_title`, `events/sections/grid` |

### LMS pages (`projects/lms/`)

| Page | Fragment | Components used |
|---|---|---|
| Home | `home/main.html` | `home/sections/slider`, `home/sections/about`, `home/sections/services`, `home/sections/team`, `home/sections/clients`, `home/sections/why_choose` |
| Courses | `plugins/lms/models/courses/index.py` | `courses.main` |
| Profile | `plugins/profile/views/dashboard.py` | `profile.dashboard` |
| Blog | `plugins/blog/components.py` | `blog.fragments.post_list`, `blog.fragments.post_create_form` |

### Auth / Account pages

| View | Fragment | Components used |
|---|---|---|
| Login | `auth/login.html` | `auth/privacy_modal.html`, `account/snippets/messages.html` |
| Register | `auth/register.html` | `account/snippets/messages.html` |
| Forgot password | `auth/forgot_page.html` | `account/snippets/messages.html` |
| Reset password | `auth/reset_password.html` | `account/snippets/messages.html` |
| Password reset done | `auth/password_reset_done.html` | `account/snippets/messages.html` |
| Password reset key done | `auth/password_reset_key_done.html` | `account/snippets/messages.html` |
| Email manage | `auth/email_manage.html` | `account/snippets/messages.html` |
| Password change | `auth/password_change.html` | `account/snippets/messages.html` |
| Password set | `auth/password_set.html` | `account/snippets/messages.html` |
| Social signup | `auth/social_signup.html` | `account/snippets/messages.html` |
| Social connections | `auth/social_connections.html` | `account/snippets/messages.html` |
| Profile | `base_profile.html` | `profile/partials/navigator`, `profile/profile.html`, `profile/partials/avatar`, `profile/partials/user-info`, `profile/partials/modals/*` |

## What could be added

The following reusable component slots are common across pages but not always present:

| Slot | Suggested component | Notes |
|---|---|---|
| Page hero / banner | `content/hero` | Add to any page that needs a hero section |
| Breadcrumb | `navigation/breadcrumb` | Useful for nested pages |
| Call-to-action | `content/cta` | Reusable CTA block |
| FAQ accordion | `content/faq` | Use on contact / about pages |
| Testimonial carousel | `content/testimonials` | Already used on about/services |
| Newsletter signup | `forms/newsletter` | Already used on VResume home |
| Social share | `blog/components/social_share` | Add to blog detail pages |
| Pagination | `components/pagination` | Use on list views |
| Cookie consent | `components/cookies/cookie-consent` | Already in base.html |

## Fragment naming convention

Use `fragment_name` only for fragment identifiers and context keys. Do not introduce alternate names such as `fragment`, `name`, `fragment_slug`, or `fragment_key` for the same concept unless maintaining backwards compatibility.

## Recommendations

1. Keep component names in dotted notation and avoid repeating the folder name twice. Prefer `components/blocks/contact/contact_profile.html` over `components/blocks/contact/contact/contact_profile.html`.
2. Register include paths in `AppConfig.ready()` or via `COMPONENTS_INCLUDE_PATH_ROOTS` setting.
3. Add a `components/README.md` in each site documenting site-specific components.
