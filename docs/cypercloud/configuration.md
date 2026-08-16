# Cypercloud — Configuration Reference

> **Port:** 5073 | **DB:** SQLite | **Stack:** Django + Ceptor-AI + Monaco Editor

## Site Registration

```yaml
# projects/configs/settings/ENV/sites.yml
sites:
  cypercloud:
    port: 5073
    path: cypercloud
```

## Environment Variables

| Variable | Required | Purpose |
|----------|:--------:|---------|
| `CYPERCLOUD_SECRET_KEY` | ✅ | Django secret key |
| `CYPERCLOUD_DEBUG` | — | Debug mode (default: 0) |
| `CYPERCLOUD_ALLOWED_HOSTS` | — | Allowed hostnames (default: *) |
| `CYPERCLOUD_WORKERS` | — | Gunicorn worker count (default: 2) |
| `OLLAMA_BASE_URL` | — | Ollama API URL (default: http://localhost:11434) |
| `OLLAMA_MODEL` | — | Default Ollama model (default: gemma3:4b) |
| `OPENAI_API_KEY` | — | OpenAI API key |
| `ANTHROPIC_API_KEY` | — | Anthropic/Claude API key |
| `GEMINI_API_KEY` | — | Google Gemini API key |

## AI Backend Configuration

```python
# settings.py — CUSTOMIZER_APPS
CUSTOMIZER_APPS = [
    {"slug": "precis-ctc", "name": "CTC Research", "template_root": "..."},
    {"slug": "lms", "name": "LMS", "template_root": "..."},
    {"slug": "vresume", "name": "VResume", "template_root": "..."},
]
```

## Shared WWW Worker

See [`projects/lms/shared-integration.md`](../lms/shared-integration.md) — Cypercloud has no background task dependency but shares the common Django settings infrastructure.

## Related

| Resource | Path |
|----------|------|
| Cypercloud README | [`README.md`](README.md) |
| AI & Agents | [`../../ai/`](../../ai/) |
| Backend environment | [`../../back-env/`](../../back-env/) |
