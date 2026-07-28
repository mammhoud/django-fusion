# Development Overview

Welcome to the development guide for VResume. This section covers the project structure, development workflow, and tools used by **mammhoud** and the **Structa** team.

## 🏗️ Project Structure

VResume follows a modular Django architecture:

- **`v1/projects/`**: Shared utilities, base models, and core application logic.
- **`v1/pages/`**: All Wagtail page models (Home, About, Contact, etc.) and their specific logic.
- **`v1/configs/`**: Global settings, environment configuration, and project-wide constants.
- **`v1/webpack/`**: Frontend build configuration for styles and scripts.

## 🛠️ Development Workflow

We use a modern development workflow centered around **uv** for Python management and **npm** for frontend assets.

1. **Automation**: We use a [Makefile](development/makefile.md) to automate almost every task.
2. **Quality Control**: All code must pass `ruff` linting and formatting checks.
3. **Testing**: We use a custom test runner powered by `pytest` for comprehensive page and logic validation.

## 🚀 Key Resources

- **[Makefile Commands](development/makefile.md)**: A complete list of all automation shortcuts.
- **[Architecture & Flow](architecture/index.md)**: Deep dive into how the system works.
- **[Design System](design/index.md)**: Documentation for our UI components and Tailwind setup.

---

### Contribution Guidelines

When adding new features:
1. Ensure new models are documented in the [Data Models](architecture/models.md) section.
2. If changing the UI, update the [Design System](design/index.md).
3. Always run `make fix` before committing code.