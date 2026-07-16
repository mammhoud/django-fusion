# Core Utilities & Base Classes

The `v1/core/` directory contains the foundation upon which all other VResume apps are built. It provides abstract base classes, shared components, and utility functions.

## 📄 Pages Base (`pages_base.py`)

Every page in VResume (Home, Blog, Portfolio, etc.) inherits from custom base classes defined here. This ensures consistency in metadata, SEO, and layout.

### `VResumeBasePage`
The root abstract class for all pages. It includes:
- **SEO Fields**: Custom title, meta description, and social sharing images.
- **Layout Control**: Toggles for sidebar visibility and header/footer styles.
- **Context Management**: Automatically injects global settings (Site name, Social links) into every template.

## 🧱 Page Blocks (`page_blocks.py`)

VResume uses Wagtail's **StreamField** for flexible content creation. Reusable blocks are defined in `core` to be used across multiple page types.

- **HeroBlock**: Large header with background images and CTA buttons.
- **ServiceBlock**: Icon + Title + Description grid.
- **SkillBlock**: Visual progress bars with category grouping.
- **TimelineBlock**: Chronological items (Education/Experience).

## 🧩 Snippets

Snippets are small pieces of content that can be reused throughout the site but aren't pages themselves.

- **SocialLink**: Centralized management of GitHub, LinkedIn, Twitter, etc.
- **NavbarItem**: Dynamic navigation menu management.
- **FooterConfig**: Custom text and links for the site footer.

## 🍪 Cookies & Tracking

The `cookies.py` and `middleware.py` files handle:
- **Cookie Consent**: A built-in popup and consent management system.
- **Visitor Tracking**: Lightweight, privacy-conscious analytics tracking (stored in `FormSubmission` and `Visitor` models).
- **Environment Detection**: Passing runtime info to the frontend for conditional rendering.

## ⚡ Task Queue (Celery)

`celery_app.py` configures the background task worker. Tasks include:
- Sending transactional emails (Contact form, Newsletter).
- Generating PDF versions of the resume.
- Automated database backups.
