# 📝 Alliance Blog — Advanced CMS Plugin

## 🏗️ Product Description

A production-ready blogging engine built on Wagtail. It supports categorized content, multi-author workflows, and SEO-optimized pages.

### Features

- **Modular Body:** Uses `BaseStreamBlock` for rich media storytelling.
- **Categorization:** Hierarchical category management for easy navigation.
- **Translatable:** Full support for internationalization (i18n).
- **Social Ready:** Pre-configured meta tags for OpenGraph and Twitter cards.

---

## 🤖 MCP Integration

The Blog module provides several hooks for AI-assisted content strategy:

- **Automatic Tagging:** Use AI to suggest tags based on body content.
- **Layout Suggestions:** Use `mcp-designer` to create custom blog templates.

---

## 📂 Location

```
apps/blog/
├── models.py        # BlogPage, BlogCategory, BlogIndexPage
├── blocks.py        # StreamField block definitions
├── views.py
└── templates/
```

---

## Further Reading

- [MCP Integration](../integrations/mcp.md)
- [Alliance PRODUCT.md](../PRODUCT.md)
