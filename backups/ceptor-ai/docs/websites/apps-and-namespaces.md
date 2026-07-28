# Website Apps & Packages — Features & Namespaces

Overview of all Django apps, plugins, and their route namespaces across Structa Cloud sites.

## CTC Research (`applications/ctc-research/`)

### Apps (`www/`)

| App | Module | Features | Namespace |
|-----|--------|----------|-----------|
| Core content | `www.core.content` | Wagtail Page models: Home, About, Contact, Team, Services, Events | `ctc:` |
| Blog | `www.apps.blog` / `plugins/blog` | BlogPost model, category/tag filtering, FragmentComponent detail | `ctc:blog` |
| LMS | `plugins/lms` | Courses, modules, lessons, enrollment tracking | `ctc:lms` |
| Products | `plugins/products` | Product listings, categories | `ctc:products` |

### Plugins

| Plugin | Path | Features | Fragment Namespace |
|--------|------|----------|-------------------|
| Accounts | `plugins/accounts/` | Allauth login/signup, RegistrationAdapter, social auth (Google, GitHub) | `ctc.fragments.accounts` |
| Blog | `plugins/blog/` | Blog post models, list/detail views | `ctc.fragments.blog` |
| LMS | `plugins/lms/` | Course catalog, module pages, enrollment | `ctc.fragments.lms` |
| Profile | `plugins/profile/` | User profile, 2FA (TOTP), settings | `ctc.fragments.profile` |
| Components | `plugins/components/` | Site-specific blocks, contact forms, common partials | N/A (components) |

---

## LMS Demo (`applications/lms-demo/`)

### Apps (`www/`)

| App | Module | Features | Namespace |
|-----|--------|----------|-----------|
| Core | `www.core` | RoutableComponent-based pages (no Wagtail Page tree) | `lms:` |
| WebSocket | `www.websocket` | Real-time learning progress events | N/A (WS) |

### Plugins

| Plugin | Path | Features | Fragment Namespace |
|--------|------|----------|-------------------|
| Accounts | `plugins/accounts/` | Allauth login/signup, RegistrationAdapter, social auth | `lms.fragments.accounts` |
| Blog | `plugins/blog/` | Blog post models, list/detail views | `lms.fragments.blog` |
| LMS | `plugins/lms/` | Courses, modules, enrollment (mirrors CTC LMS) | `lms.fragments.lms` |
| Profile | `plugins/profile/` | User profile, 2FA, certifications, learning progress | `lms.fragments.profile` |
| Components | `plugins/components/` | Auth components, profile partials, content blocks | N/A (components) |

---

## VResume (`applications/VResume/`)

### Apps (`www/pages/`)

| App | Module | Features | Namespace |
|-----|--------|----------|-----------|
| Home | `www.pages.home` | HomePage model, intro/hero sections | `vresume:home` |
| About | `www.pages.about` | AboutPage model, skills, timeline | `vresume:about` |
| CV/Resume | `www.pages.cv` | ResumePage model, experience, education | `vresume:cv` |
| Portfolio | `www.pages.portfolio` | PortfolioPage model, project showcases | `vresume:portfolio` |
| Blog | `www.pages.blog` | BlogPage model, post list/detail (FragmentComponent) | `vresume:blog` |
| Contact | `www.pages.connect` | ContactPage model, form, social settings | `vresume:connect` |
| Events | `www.pages.events` | EventPage model (stub — 0 models, 2 views) | `vresume:events` |

### Plugins

| Plugin | Path | Features | Fragment Namespace |
|--------|------|----------|-------------------|
| Accounts | `plugins/accounts/` | Allauth login/signup, RegistrationAdapter, social auth | `vresume.fragments.accounts` |

### Site Settings

| Setting | Model | Features |
|---------|-------|----------|
| VResume Settings | `www.pages.home.models.snippets.vresume_settings` | Brand config (logo, favicon, site name, description, meta tags, title suffix) and social config (address, phone, email) via `@register_setting` |

---

## CRM (`applications/crm/`)

### Apps

| App | Features | Namespace |
|-----|----------|-----------|
| `accounts/` | User authentication, profile management | `crm:accounts` |
| `bills/` | Bill creation, tracking, management | `crm:bills` |
| `invoice/` | Invoice generation, templates, sending | `crm:invoice` |
| `store/` | Product catalog, inventory | `crm:store` |
| `transactions/` | Payment tracking, transaction history | `crm:transactions` |

---

## Packages (`applications/libs/`)

### django-fusion

| Module | Features | Namespace |
|--------|----------|-----------|
| `comp.routes` | Site, Application, ModelViewset, RoutableComponent, FragmentComponent, Route, menu_path | `django_fusion.comp.routes` |
| `comp.generic` | ListModelView, CreateModelView, DeleteModelView, TableView, ListBulkActionsMixin | `django_fusion.comp.generic` |
| `core` | PageHandler, BaseService, TimeStampedModel, CacheService, middlewares | `django_fusion.core` |
| `health` | HealthCheckView, DatabaseHealthView, AssetsHealthView | `django_fusion.health` |
| `site` | Auth mixins, context processors (brand_settings, social_settings), paginators | `django_fusion.site` |
| `wagtail` | StreamField blocks, AuthEmailTemplate snippet, Wagtail viewsets | `django_fusion.wagtail` |
| `contrib` | Admin, cache, debug_tools, email_config, enums, privacy, utils | `django_fusion.contrib` |
| `infrastructure` | Management commands, scripts, templatetags, locale | `django_fusion.infrastructure` |
| `analyzer` | Component scanner, parser, schemas | `django_fusion.analyzer` |

### ceptor-ai

| Module | Features | Namespace |
|--------|----------|-----------|
| `chat.client` | CeptorClient — OpenAI + Anthropic chat client | `ceptor_ai.chat.client` |
| `chat.bubble` | ChatBubble — Django component for rendering chat | `ceptor_ai.chat.bubble` |
| `mcp` | MCP (Model Context Protocol) server | `ceptor_ai.mcp` |

### Merged Packages

| Original Package | Merged Into | What Was Absorbed |
|-----------------|-------------|-------------------|
| django-grep | django-fusion legacy docs | Template component scanning, property-based testing |
| django-osoul | django-fusion | Wagtail admin customization, snippet patterns |
| django-rseal | django_fusion.web | Email sending, view mixins (FilterMixin, SearchMixin) |
