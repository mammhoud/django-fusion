# Template Architecture & Flow

## Directory Structure

All templates live in a single root: `v1/pages/templates/`

```
pages/templates/
├── base.html                   Root layout
├── skeleton.html               Thin extends-base wrapper
├── navigator.html              Tab navigation bar
├── sidebar.html                Profile sidebar (avatar, contacts, social)
├── base_page.html              Standalone page base (newsletter, errors)
├── base_email.html             Email base
├── contact_success.html        Contact form success page
├── robots.txt
│
├── layout/                     Shared layout partials
│   ├── meta.html               <head> meta tags
│   ├── footer.html             Footer + theme toggle
│   ├── cookie-popup.html       GDPR cookie consent
│   └── partials/
│       ├── logo.html
│       └── navigations.html
│
├── errors/                     HTTP error pages
│   ├── 400.html … 504.html
│
├── email/                      Transactional email templates
│   ├── base.html
│   ├── welcome.html
│   ├── password_reset.html
│   ├── completion.html
│   └── enrollment.html
│
├── home/
│   ├── fragment.html           HTMX fragment
│   ├── main.html               Full-page (extends base.html)
│   └── sections/
│       ├── slider.html
│       ├── hero.html
│       ├── about.html
│       ├── services.html
│       ├── skills.html
│       ├── team.html
│       ├── clients.html
│       ├── testimonials.html
│       ├── features.html
│       ├── listing.html
│       ├── newsletter.html
│       ├── slider.html
│       └── why_choose.html
│
├── about/
│   ├── fragment.html
│   ├── main.html
│   └── sections/
│       ├── intro.html
│       ├── services.html
│       ├── experience.html
│       ├── testimonials.html
│       ├── clients.html
│       └── team.html
│
├── resume/
│   ├── fragment.html
│   ├── main.html
│   └── sections/
│       ├── education.html
│       ├── experience.html
│       └── skills.html
│
├── portfolio/
│   ├── fragment.html
│   ├── main.html
│   ├── sections/
│   │   ├── projects.html       Composes filter + grid + modal
│   │   ├── filter.html         Category filter + search + view toggle
│   │   ├── grid.html           Project cards (grid & list variants)
│   │   └── modal.html          Overlay container
│   └── modals/
│       └── project_detail.html Loaded via HTMX into modal
│
├── blog/
│   ├── fragment.html
│   ├── sections/
│   │   ├── filter.html         Category filter + search + view toggle
│   │   ├── posts.html          Post cards (grid & list variants)
│   │   └── modal.html          Overlay container
│   ├── modals/
│   │   ├── blog_detail.html    Loaded via HTMX (from /pages/blog/<id>/)
│   │   └── blog_preview.html   Loaded via HTMX (from /blog/preview/<pk>/)
│   └── standalone/
│       ├── blog_index.html     Full-page blog listing
│       └── blog_detail.html    Full-page blog post
│
├── skills/
│   ├── fragment.html
│   ├── main.html
│   └── sections/
│       ├── skills_grid.html
│       └── skills_by_category.html
│
└── connect/                    Contact + newsletter + emails + blocks
    ├── fragment.html           Contact tab HTMX fragment
    ├── main.html
    ├── sections/
    │   ├── form.html           Contact form
    │   ├── map.html            Map embed
    │   ├── faq.html
    │   └── info.html
    ├── newsletter/
    │   ├── subscribe.html
    │   ├── confirmed.html
    │   ├── unsubscribe_confirm.html
    │   ├── unsubscribed.html
    │   └── email/
    │       ├── campaign.html
    │       └── confirmation.html
    ├── emails/
    │   ├── base.html
    │   ├── blog_post.html
    │   ├── campaign.html
    │   ├── newsletter.html
    │   ├── subscription_confirmation.html
    │   └── form_submission_notification.html
    └── blocks/                 Wagtail StreamField block templates
        ├── client.html
        ├── contact_form.html
        ├── project.html
        ├── service.html
        ├── skill.html
        ├── testimonial.html
        └── timeline_item.html
```

---

## Django Settings

```python
# configs/base/templates.py
TEMPLATES_DIRS = [
    BASE_DIR / "pages" / "templates",  # Single source of truth
]
# APP_DIRS = True  — Wagtail and third-party app templates still load
```

---

## Request Flow

### Full-page load (browser navigation)

```
GET /pages/about/
  └─ tab_view("about")
       └─ is_htmx=False → render("skeleton.html")
            └─ extends base.html
                 ├─ includes layout/meta.html
                 ├─ includes layout/cookie-popup.html
                 ├─ includes sidebar.html
                 ├─ includes navigator.html
                 └─ block vresume_content
                      └─ includes about/fragment.html
                           └─ includes about/sections/intro.html
                           └─ includes about/sections/testimonials.html
                           └─ includes about/sections/clients.html
```

### HTMX tab switch

```
hx-get="/pages/about/"  hx-target="article"  hx-swap="outerHTML"
  └─ tab_view("about")
       └─ is_htmx=True → render("about/fragment.html")
            └─ <article class="about"> ... </article>
```

### Portfolio modal

```
User clicks project card
  └─ hx-get="/pages/project/<id>/"
       hx-target="#project-modal-container"
       hx-swap="innerHTML"
       hx-on::after-request → adds .project-modal__overlay--active
  └─ project_detail_view(project_id)
       └─ render("portfolio/modals/project_detail.html", {project})
```

### Blog modal

```
User clicks blog card
  └─ hx-get="/blog/preview/<pk>/"
       hx-target="#blog-modal-container"
       hx-swap="innerHTML"
       hx-on::after-request → adds .blog-modal__overlay--active
  └─ post_preview(pk)
       └─ render("blog/modals/blog_preview.html", {post})
```

---

## Template Naming Conventions

| Pattern | Purpose |
|---------|---------|
| `<section>/fragment.html` | HTMX partial — returned for tab switches |
| `<section>/main.html` | Full-page wrapper — extends `base.html` |
| `<section>/sections/<name>.html` | Sub-section included by fragment |
| `<section>/modals/<name>.html` | Modal content loaded via HTMX |
| `<section>/standalone/<name>.html` | Full standalone pages (blog list/detail) |
| `connect/emails/<name>.html` | Transactional email bodies |
| `connect/blocks/<name>.html` | Wagtail StreamField block renderers |

---

## Include Hierarchy

```
base.html
├── layout/meta.html
├── layout/cookie-popup.html
├── sidebar.html
├── navigator.html
└── [active_tab]/fragment.html
     └── [active_tab]/sections/*.html

skeleton.html
└── extends base.html

[section]/main.html
└── extends base.html
     └── block vresume_content
          └── [section]/fragment.html
```
