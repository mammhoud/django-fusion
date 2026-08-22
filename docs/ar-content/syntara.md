---
title: Syntara — مخصص دردشة الذكاء الاصطناعي
description: فهرس توثيق Syntara — دردشة وتخصيص قوالب بالذكاء الاصطناعي (Cypercloud سابقاً).
navigation:
  title: Syntara
  icon: i-lucide-bot
---

# Syntara — مخصص دردشة الذكاء الاصطناعي

> **أسماء مرتبطة:** `cypercloud.localhost`, `دردشة الذكاء الاصطناعي`, `مخصص القوالب`, `ceptor-ai`, `Ollama`, `OpenAI`, `Claude`, `Gemini`
> **الوسوم:** #site #cypercloud #ai #chat #customizer

**المسار المعياري:** `projects/syntara/` \
**النطاق:** localhost (الافتراضي: cypercloud.localhost) \
**المنفذ:** 5073 \
**التقنية:** Django 4.2+ · Webpack + SCSS · HTMX · Monaco Editor

---

## نظرة عامة

Syntara (سابقاً Tinker/Customizer) أداة دردشة وتخصيص قوالب مدعومة بالذكاء
الاصطناعي. توفر واجهة دردشة مدعومة بنماذج ذكاء اصطناعي متعددة (Ollama,
OpenAI, Claude, Gemini) مع اكتشاف قوالب متعدد المواقع لـ CTC Research وLMS
وVResume.

---

## الدليل

### التطوير

```bash
cd projects/syntara

# خادم التطوير
make run                    # خادم Django على :5073

# Docker
make docker-run             # تشغيل في حاوية Docker

# الإنتاج
make build                  # بناء أصول الواجهة
make deploy                 # كامل: بناء ← collectstatic ← migrate
```

### أوامر Makefile الشائعة

| الأمر | الوصف |
|-------|--------|
| `make run` | تشغيل خادم Django على :5073 |
| `make check` | فحوصات نظام Django |
| `make migrate` | تطبيق الترحيلات المعلقة |
| `make shell` | قشرة Django (shell_plus) |
| `make collectstatic` | جمع الملفات الثابتة |
| `make build` | بناء أصول الواجهة (webpack) |
| `make docker-run` | تشغيل حاوية Docker |
| `make docker-down` | إيقاف حاوية Docker |
| `make deploy` | نشر كامل (بناء ← collectstatic ← migrate) |

---

## خريطة الكود

### الملفات الرئيسية

| المسار | الغرض | التخصيص |
|--------|-------|:---:|
| `cypercloud/settings.py` | إعدادات Django للموقع | ⚪ إعداد فقط |
| `cypercloud/server.py` | نقطة دخول تطبيق ASGI/WSGI | 🔴 غير قابل للتخصيص |
| `cypercloud/Makefile` | أوامر خاصة بالموقع | 🟢 قابل للتخصيص |
| `cypercloud/assets/static/styles/` | أوراق SCSS (دردشة، محرر، تخطيط، إدخال، تنقل) | 🟢 قابل للتخصيص |
| `cypercloud/assets/static/scripts/` | JS الواجهة (دردشة، محرر، تكامل HTMX) | 🟢 قابل للتخصيص |
| `cypercloud/www/` | تطبيقات Django للدردشة واكتشاف القوالب وإعداد الوكيل | 🟢 قابل للتخصيص |
| `cypercloud/templates/` | قوالب Django/Wagtail | 🔵 قالب |
| `cypercloud/plugins/` | إضافات الموقع | 🟢 قابل للتخصيص |

---

## Remarks

| # | ملاحظة |
|---|--------|
| ⚠️ | انسخ `.env.example` إلى `.env` واضبط على الأقل `CYPERCLOUD_SECRET_KEY` و`OLLAMA_BASE_URL` |
| 💡 | يدعم **4 خلفيات ذكاء اصطناعي**: Ollama (محلي)، OpenAI، Anthropic Claude، Google Gemini — اضبط عبر متغيرات البيئة |
| 🔌 | تكامل **Monaco Editor** يتيح تحرير الكود مع تلوين الصياغة وعرض Markdown |
| 🔗 | اكتشاف القوالب يمسح قوالب مواقع CTC Research وLMS وVResume |
| 🤖 | إطار الذكاء الاصطناعي يستخدم **Ceptor-AI** (بروتوكول MCP) لتنفيذ الأدوات وإعداد الوكيل |

## Remarks & Notes

- النسخة الإنجليزية الكاملة: [`/docs/en/syntara`](/docs/en/syntara).
- راجع إعدادات Syntara: [`configuration.md`](/docs/en/syntara).
