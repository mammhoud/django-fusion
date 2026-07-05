# 🔍 Django Grep - AI-Powered Development Plugin

## 🏗️ Product Description
Django Grep is a specialized developer tool designed to bridge the gap between Django applications and AI agents. It provides a suite of tools for codebase exploration, automatic UI generation, and architectural analysis.

### Features:
- **Grep Search:** High-speed regex search optimized for Python/Django projects.
- **Component Engine:** Advanced Wagtail StreamField blocks (Headings, Media, Layouts).
- **MCP Designer:** Integrates with Model Context Protocol to allow AI to design and modify your project structure.
- **Schema Discovery:** Automated tools for mapping Django models and relationships.

---

## 🤖 MCP Usage
Django Grep provides the core logic for the **MCP Django Server**.
By including this plugin, your AI assistant gains the ability to:
- Browse your project's files autonomously.
- Propose and apply architectural changes.
- Generate specialized Wagtail hooks and models based on existing patterns.

To enable MCP, ensure `django_fusion.mcp_designer` is in your `INSTALLED_APPS`.
