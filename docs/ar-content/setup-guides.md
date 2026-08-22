---
title: أدلة الإعداد والبناء
description: أدلة خطوة بخطوة للإعداد والتشغيل والبناء واستكشاف الأخطاء لكل مشروع في المستودع.
navigation:
  title: أدلة الإعداد
  icon: i-lucide-toolbox
---

# 🛠️ أدلة إعداد وبناء المشاريع

أدلة **الإعداد والتشغيل والبناء واستكشاف الأخطاء** خطوة بخطوة لكل مشروع في
المستودع. يغطي كل دليل المتطلبات، وتثبيت التبعيات، وترحيل/بذر قاعدة البيانات،
وتشغيل التطوير (مع المنافذ)، والتحقق، والبناء الإنتاجي، وDocker، والمشاكل
الشائعة.

> الأدلة تعيش **بجانب مشاريعها** (في مجلد `docs/` داخل كل مشروع) لتبقى دقيقة
> مع تغيّر الكود. هذه الصفحة هي الفهرس الذي يربطها جميعاً.

## الأدلة

| المشروع | الدليل | التقنية | منافذ التطوير |
|---------|--------|---------|---------------|
| **Precis (نظام تعلم + تسويق موحّد)** | [`projects/precis/docs/precis-main/SETUP_AND_BUILD.md`](/docs/en/setup-guides) | Astro + Django + Wagtail + django-fusion | خلفية :8074 · واجهة :4321 · Docker :3000 |
| **Precis Landing** | [`projects/precis/docs/precis-landing/SETUP_AND_BUILD.md`](/docs/en/setup-guides) | Astro + Django + Wagtail + django-fusion | خلفية :8074 · واجهة :4321 |
| **CTC Research** | [`projects/precis/docs/precis-ctc/SETUP_AND_BUILD.md`](/docs/en/setup-guides) | Astro + Django + Wagtail + django-fusion | خلفية :5070 · واجهة :3002 |
| **Syntara / Cypercloud** | [`projects/syntara/docs/SETUP_AND_BUILD.md`](/docs/en/setup-guides) | Django + Ceptor-AI + Monaco + HTMX | تطبيق :5073 · HMR :5093 |
| **Formint POS (كل الإصدارات)** | [`projects/formints/docs/GETTING_STARTED.md`](/docs/en/setup-guides) | Tauri + React + Astro + Django Ninja + Vue | Community :1420 · Pro :8767/:4321 · Cloud :8082/:8767/:4323 |
| **Loop-CRM** | [`projects/loop-crm/docs/SETUP_AND_BUILD.md`](/docs/en/setup-guides) | Django + django-fusion + Dramatiq + Astro | خلفية :8000 · واجهة :4321 |
| **django-fusion (المكتبة)** | [`libs/django-fusion/docs/SETUP_AND_BUILD.md`](/docs/en/setup-guides) | مساعدات Django/Wagtail + Webpack 5 | — (مكتبة + بناء أصول) |

## دليل القرار السريع

| أريد العمل على… | ابدأ بـ |
|------------------|---------|
| منتج التسويق + نظام التعلم | [Precis (الموحّد)](/docs/en/setup-guides) |
| نسخة LMS تاريخية | [نشر Precis Main](/docs/en/precis/deployment) — `precis-lms`/`lms` أسماء توافق وليست مجموعة منفصلة |
| الجزء التسويقي/الكتالوجي | [Precis Landing](/docs/en/setup-guides) |
| موقع مركز الأبحاث الطبية | [CTC Research](/docs/en/setup-guides) |
| أداة الدردشة/تخصيص القوالب بالذكاء الاصطناعي | [Syntara / Cypercloud](/docs/en/setup-guides) |
| أي إصدار POS (سطح مكتب، Pro، سحابة) | [Formint POS](/docs/en/setup-guides) |
| منصة المبيعات والتسويق | [Loop-CRM](/docs/en/setup-guides) |
| مكونات Django/Wagtail المشتركة | [django-fusion](/docs/en/libs/django-fusion) |

## خطوات أولى مشتركة (كل المشاريع)

1. **Python:** `python3 --version` (≥ 3.11) وتثبيت [uv](https://docs.astral.sh/uv/).
2. **Node:** `node --version` (18–22) و`npm --version`.
3. **تبعيات الخلفية:** مشاريع Django تُزامن من `projects/pyproject.toml` للمساحة
   (`uv sync`) — راجع دليل المشروع.
4. **تبعيات الواجهة:** `npm install` / `pnpm install` في `frontend/` الخاصة
   بالمشروع (أو `assets/` لـ Syntara).
5. **قاعدة البيانات:** `make migrate` ثم هدف البذر الخاص بالمشروع
   (`make seed` / `make seed-demo` / `make populate-data`).
6. **التشغيل:** خادم تطوير الخلفية + خادم تطوير الواجهة (المنافذ في الجدول أعلاه).
7. **التحقق:** `make check` و`make test` لكل مشروع.

## Remarks & Notes

- روابط الأدلة الكاملة لكل مشروع متوفرة في النسخة الإنجليزية:
  [`/docs/en/setup-guides`](/docs/en/setup-guides).
- تظل ملفات `AGENTS.md` وMakefiles الخاصة بالمشاريع هي مصدر الحقيقة للمسارات والأوامر.
