---
title: Syntara — مرجع التكوين
description: المنفذ، قاعدة البيانات، المكدس، تسجيل الموقع، متغيرات البيئة، وتكوين خلفيات الذكاء الاصطناعي في Syntara.
navigation:
  title: التكوين
  icon: i-lucide-settings
---

# Syntara — مرجع التكوين

> **المنفذ:** 5073 | **قاعدة البيانات:** SQLite | **المكدس:** Django + Ceptor-AI + Monaco Editor

## تسجيل الموقع

```yaml
# projects/configs/settings/ENV/sites.yml
sites:
  cypercloud:
    port: 5073
    path: cypercloud
```

## متغيرات البيئة

| المتغير | مطلوب | الغرض |
|----------|:--------:|---------|
| `CYPERCLOUD_SECRET_KEY` | ✅ | مفتاح Django السرّي |
| `CYPERCLOUD_DEBUG` | — | وضع التصحيح (افتراضي: 0) |
| `CYPERCLOUD_ALLOWED_HOSTS` | — | أسماء المضيفين المسموح بها (افتراضي: *) |
| `CYPERCLOUD_WORKERS` | — | عدد عمّال Gunicorn (افتراضي: 2) |
| `OLLAMA_BASE_URL` | — | عنوان واجهة Ollama (افتراضي: http://localhost:11434) |
| `OLLAMA_MODEL` | — | نموذج Ollama الافتراضي (افتراضي: gemma3:4b) |
| `OPENAI_API_KEY` | — | مفتاح OpenAI API |
| `ANTHROPIC_API_KEY` | — | مفتاح Anthropic/Claude API |
| `GEMINI_API_KEY` | — | مفتاح Google Gemini API |

## تكوين خلفية الذكاء الاصطناعي

```python
# settings.py — CUSTOMIZER_APPS
CUSTOMIZER_APPS = [
    {"slug": "precis-ctc", "name": "CTC Research", "template_root": "..."},
    {"slug": "lms", "name": "LMS", "template_root": "..."},
    {"slug": "vresume", "name": "VResume", "template_root": "..."},
]
```

## عامل WWW المشترك

انظر [`projects/lms/shared-integration.md`](../lms/shared-integration.md) — لا يعتمد Syntara على أي مهام خلفية، لكنه يشارك بنية إعدادات Django الشائعة.

## ذات صلة

| المورد | المسار |
|----------|------|
| README الخاص بـ Syntara | [`README.md`](./README.md) |
| الذكاء الاصطناعي والوكلاء | [`ai/`](/docs/en/ai/) |
| بيئة الخلفية | [`back-env/`](/docs/en/dev/back-env/) |

<!-- AI-generated: review needed -->
