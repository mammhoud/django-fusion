# ⚙️ Alliance Handlers — Profile & Security Plugin

## 🏗️ Product Description

This module handles the core business logic for user profiles, identity management, and secure settings. It serves as the bridge between Django's Auth system and the frontend user experience.

### Features

- **Identity Orchestration:** Custom adapters for Allauth and Wagtail Users.
- **Secure Settings:** Tab-based settings panel with support for Password Change, 2FA, and Session management.
- **Person Models:** Extended user profiles with biographic and social data.
- **Invitation System:** Secure, token-based invitation workflow.

---

## 🤖 MCP Integration

The Handlers module is the primary integration point for MCP-driven user management features.

- **Permission Mapping:** Use AI to analyze and suggest user permissions.
- **Workflow Automation:** Integrates with MCP to handle complex user onboarding scripts.

---

## 📂 Location

```
apps/handlers/
├── models.py             # Person, UserProfile, Invitation
├── adapters.py           # Allauth custom adapter
├── views.py
├── management/
│   └── commands/
│       └── sync_alliancecore.py   # Alliance sync management command
└── templates/
```

---

## Further Reading

- [MCP Integration](../integrations/mcp.md)
- [Profile Banner Options](./profile-banner.md)
- [Alliance PRODUCT.md](../PRODUCT.md)
