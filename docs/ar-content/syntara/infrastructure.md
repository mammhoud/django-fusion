---
title: Syntara — البنية التحتية
description: الحاوية، النشر، وبنية نماذج الذكاء الاصطناعي لمنصة Syntara.
navigation:
  title: البنية التحتية
  icon: i-lucide-server
---

# 🔧 Syntara — البنية التحتية

> تفاصيل البنية التحتية الخاصة بمنصة Syntara للذكاء الاصطناعي.

---

## الحاوية

| الخاصية | القيمة |
|----------|-------|
| الحاوية | `cypercloud-web` |
| المنفذ الداخلي | `5073` |
| الصورة | مبنية من `projects/compose/Dockerfile` |
| الشبكات | `common`، `traefik-net`، `ollama-net` |

## النشر

```bash
make deploy-cypercloud    # Build webpack + collectstatic + migrate
cd projects && make dev WEBSITE=cypercloud   # Local dev server
```

## بنية نماذج الذكاء الاصطناعي

```
┌──────────────────────┐
│   Syntara Web     │
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

### تكوين النماذج

```yaml
# projects/syntara/configs/settings.yml
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

## خطة المنصة (مستقبلاً)

انظر [`platform-plan.md`](./platform-plan.md) لرؤية منصة الاشتراكات متعددة الأنظمة:
- المرحلة 1: ذكاء اصطناعي كخدمة (SaaS) مع فوترة Stripe
- المرحلة 2: باني الأنظمة (قوالب POS وCRM وLMS)
- المرحلة 3: منصة كاملة متعددة المستأجرين مع متجر تطبيقات

---

## ذات صلة

| الموضوع | المسار |
|-------|------|
| خطة المنصة | [`platform-plan.md`](./platform-plan.md) |
| تكوين Syntara | [`configuration.md`](./configuration.md) |
| حالات استخدام Syntara | [`use-cases.md`](./use-cases.md) |
| البنية التحتية الرئيسية | [`dev/infrastructure/`](/docs/en/dev/infrastructure/) |

<!-- AI-generated: review needed -->
