---
title: Syntara
description: محادثة الذكاء الاصطناعي، اكتشاف القوالب، تخصيص الكود، استجابات متدفقة — بيئة تشغيل Cypercloud.
navigation:
  title: Syntara
  icon: i-lucide-bot
---

# 🤖 Syntara — مُخصّص دردشة الذكاء الاصطناعي

> **أسماء ذات صلة:** `cypercloud.localhost`، `دردشة الذكاء الاصطناعي`، `مخصّص القوالب`، `ceptor-ai`، `Ollama`، `OpenAI`، `Claude`، `Gemini`
> **الوسوم:** #site #cypercloud #ai #chat #customizer

**المسار المعياري:** `projects/syntara/`  
**النطاق:** localhost (افتراضي: cypercloud.localhost)  
**المنفذ:** 5073  
**المكدس:** Django 4.2+ · Webpack + SCSS · HTMX · Monaco Editor

---

## نظرة عامة

Syntara (المعروفة تاريخياً باسم Cypercloud) هي بيئة تشغيل دردشة الذكاء الاصطناعي ومخصّص القوالب. تتيح للمستخدمين اكتشاف القوالب، تخصيص الكود، وتدفق الاستجابات من موفري ذكاء اصطناعي متعددين (Ollama، OpenAI، Claude، Gemini).

---

## البدء السريع

```bash
cd projects/syntara
make dev
```

---

## التكوين

- **موفرو الذكاء الاصطناعي:** تُضبط عبر متغيرات البيئة (Ollama، OpenAI، Claude، Gemini)
- **اكتشاف القوالب:** مسح تلقائي لـ `templates/` و `projects/syntara/templates/`
- **تخصيص الكود:** محرر Monaco المدمج مع تمييز بناء الجملة

---

## البنية التحتية

- **Django 4.2+** — الإطار الخلفي
- **Webpack + SCSS** — تجميع الأصول
- **HTMX** — التفاعل الأمامي
- **Monaco Editor** — محرر الكود داخل المتصفح

---

## الأدلة ذات الصلة

- [التكوين](/docs/ar/syntara/configuration)
- [الميزات](/docs/ar/syntara/features)
- [البنية التحتية](/docs/ar/syntara/infrastructure)
- [حالات الاستخدام](/docs/ar/syntara/use-cases)

---

## ملاحظات وإرشادات

- الاسم التاريخي `cypercloud` محفوظ حيث يتطلبه اسم مستعير وقت التشغيل أو عقد خارجي.
- Syntara هي المسار الحالي لنظام الملفات للمنتج المعروف تاريخياً باسم Cypercloud.

<!-- AI-generated: review needed -->
