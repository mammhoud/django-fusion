# 🌐 Project Repositories

This document provides links to all repositories and variants associated with the **Xellent Hub** platform.

## 🚀 Main Platform (Unified)
The core application is hosted in a single unified repository. Different tiers and use cases are managed via specialized branches and release tags.

**Repository URL**: https://github.com/mammhoud/xellent

### 🌿 Branch Strategy
The repository uses a simplified two-branch workflow:
- **dev**: Development and demo environment (active development)
- **main**: Production-ready releases (stable code)

### 📦 Variant Branches
Each variant branch represents a filtered version of the platform:
- **Release/Core**: Framework and infrastructure only (No LMS/Blog).
- **Release/Blog**: Content-focused variant (Includes Blog, No LMS).
- **Release/LMS**: Dedicated LMS variant (No Blog/Newsletter).

### 🏷️ Version Tags
Releases are tagged for easy tracking:
- `v1.0.3-all`
- `v1.0.3-core`
- `v1.0.3-blog`
- `v1.0.3-lms`

---

## 📦 Shared Infrastructure
The underlying framework that powers the component system and model pipelines.

**Repository URL**: [https://github.com/mammhoud/django-fusion](https://github.com/mammhoud/django-fusion)

### Features
- **Component System**: Advanced HTML-in-Python rendering.
- **Pipelines**: Reusable models, managers, and service layers for Django/Wagtail.
- **Generic Tags**: HTMX and Alpine.js integration utilities.

---

## 🛠️ Management Commands
You can publish updates to these repositories using the following commands:
```bash
make publish-all   # Updates main branch
make publish-core  # Updates release/core branch
make publish-blog  # Updates release/blog branch
make publish-lms   # Updates release/lms branch
```
