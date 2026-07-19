# 🔧 Cypercloud — Infrastructure

> Infrastructure specifics for the Cypercloud AI platform.

---

## Container

| Property | Value |
|----------|-------|
| Container | `cypercloud-web` |
| Internal Port | `5073` |
| Image | Built from `projects/compose/Dockerfile` |
| Networks | `common`, `traefik-net`, `ollama-net` |

## Deployment

```bash
make deploy-cypercloud    # Build webpack + collectstatic + migrate
cd projects && make dev WEBSITE=cypercloud   # Local dev server
```

## AI Model Infrastructure

```
┌──────────────────────┐
│   Cypercloud Web     │
│   :5073              │
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│   Ollama Server      │
│   :11434             │
│   models: llama3.2   │
│   models: mistral    │
│   models: codellama  │
└──────────────────────┘
```

### Model Configuration

```yaml
# projects/cypercloud/configs/settings.yml
ai:
  backends:
    ollama:
      host: "http://ollama:11434"
      models: ["llama3.2:latest", "mistral:latest"]
    openai_compatible:
      api_key: "${OPENAI_API_KEY}"
      base_url: "https://api.openai.com/v1"
      models: ["gpt-4o", "gpt-4o-mini"]
```

---

## Platform Plan (Future)

See [`platform-plan.md`](platform-plan.md) for the multi-system subscription platform vision:
- Phase 1: AI SaaS with Stripe billing
- Phase 2: System builder (POS, CRM, LMS templates)
- Phase 3: Full multi-tenant platform with marketplace

---

## Related

| Topic | Path |
|-------|------|
| Platform plan | [`platform-plan.md`](platform-plan.md) |
| Cypercloud config | [`configuration.md`](configuration.md) |
| Cypercloud use cases | [`use-cases.md`](use-cases.md) |
| Main infrastructure | [`../../infrastructure/`](../../infrastructure/) |
