# 🎯 Cypercloud — Features

> Feature set specific to the Cypercloud AI platform.

---

## Feature Inventory

| Feature | Status | Description |
|---------|--------|-------------|
| **AI Chat** | ✅ Live | Multi-model chat via CeptorAI |
| **Streaming AI** | ✅ Live | Server-Sent Events (SSE) for real-time responses |
| **Multi-Model** | ✅ Live | Ollama + OpenAI-compatible backends |
| **Conversation History** | ✅ Live | Persistent chat with Django models |
| **User Auth** | ✅ Live | django-allauth with social + email |
| **Wagtail CMS** | ✅ Live | Content management for prompts/docs |
| **MCP Integration** | 🟡 Planned | Model Context Protocol servers |
| **Stripe Billing** | 🟡 Planned | Subscription tiers |
| **API Tokens** | 🟡 Planned | Per-user API keys with rate limits |
| **Prompt Library** | 🟡 Planned | Save, share, template prompts |
| **System Builder** | 🟢 Roadmap | 1-click deploy POS/CRM/LMS |
| **App Marketplace** | 🟢 Roadmap | Third-party plugins |

---

## AI Backend Architecture

```
┌─────────────────────────────────┐
│          CeptorAI Client        │
│  ┌───────────┐ ┌──────────────┐ │
│  │  Ollama   │ │ OpenAI-comp. │ │
│  │  (local)  │ │  (cloud)     │ │
│  └───────────┘ └──────────────┘ │
│  ┌─────────────────────────────┐│
│  │      Model Router           ││
│  │  (fallback, load balancing) ││
│  └─────────────────────────────┘│
└─────────────────────────────────┘
```

---

## Related

| Topic | Path |
|-------|------|
| Platform plan | [`platform-plan.md`](platform-plan.md) |
| Cypercloud config | [`configuration.md`](configuration.md) |
| Cypercloud use cases | [`use-cases.md`](use-cases.md) |
| Feature matrix | [`../../features/`](../../features/) |
