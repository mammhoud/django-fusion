---
title: التوصيات أولاً
description: أقصر مسار من حالة المستودع الحالية إلى العمل الآمن والقيم التالي — الأولويات والتسلسل.
navigation:
  title: التوصيات
  icon: i-lucide-star
---

# ⭐ التوصيات أولاً

> **الغرض:** أقصر مسار من حالة المستودع الحالية إلى العمل الآمن والقيم التالي.
> **مُحدّث:** 2026-08-10

هذه الصفحة هي طبقة القرار لتوثيق Structa Cloud. اقرأها قبل فتح الخطط التفصيلية.

## الترتيب الموصى به

1. **الوعي بالمشروع** — افهم البنية والمنتجات والأوامر
2. **البدء السريع** — استنساخ → `uv sync` → `just install` → نشر → تحقق
3. **الإعداد والبناء** — لكل مشروع: التبعيات، الهجرات، البذر، الخوادم
4. **المصادقة** — allauth، شظايا HTMX، OAuth، TOTP، WebAuthn
5. **التطوير** — سير العمل المحلي، إعادة تحميل ساخنة، تصحيح، Sidecar
6. **النشر** — Docker، Traefik، Let's Encrypt، فحوصات الصحة، نسخ DB الاحتياطية
7. **التخصيص** — ما هو آمن للتغيير (🟢)، قابل للتوسيع (🟡)، قالب (🔵)، تكوين (⚪)، نواة (🔴)
8. **استنساخ الموقع** — نسخ موقع موجود كقالب لمشروع جديد
8. **أفضل الممارسات** — الأنماط للتبني، الأنماط المضادة للتجنب، قائمة مراجعة مراجعة الكود
9. **Docus** — تكوين Docus/Nuxt، i18n، خط أنابيب المحتوى، التحقق
10. **صحة أصول Fusion** — خط أنابيب الأصول الثابتة، فحوصات CSS/JS، تحليل الحزم

## مصفوفة القرار السريع

| أريد العمل على… | ابدأ بـ |
|------------------|---------|
| منتج التسويق + نظام التعلم | [Precis (الموحد)](../projects/precis/docs/precis-main/SETUP_AND_BUILD.md) |
| اسم مستعار LMS تاريخي | [نشر Precis Main](../precis/deployment.md) — `precis-lms`/`lms` أسماء توافق |
| شريحة التسويق/الكتالوج | [Precis Landing](../projects/precis/docs/precis-landing/SETUP_AND_BUILD.md) |
| موقع مركز الأبحاث الطبية | [CTC Research](../projects/precis/docs/precis-ctc/SETUP_AND_BUILD.md) |
| أداة الدردشة/تخصيص القوالب بالذكاء الاصطناعي | [Syntara / Cypercloud](../projects/syntara/docs/SETUP_AND_BUILD.md) |
| أي إصدار POS (سطح مكتب، Pro، سحابة) | [Formint POS](../projects/formints/docs/GETTING_STARTED.md) |
| منصة المبيعات والتسويق | [Loop-CRM](../projects/loop-crm/docs/SETUP_AND_BUILD.md) |
| مكونات Django/Wagtail المشتركة | [django-fusion](../libs/django-fusion/docs/SETUP_AND_BUILD.md) |

## خطوات أولى مشتركة (كل المشاريع)

1. **Python:** `python3 --version` (≥ 3.11) وتثبيت [uv](https://docs.astral.sh/uv/).
2. **Node:** `node --version` (18–22) و `npm --version`.
3. **تبعيات الخلفية:** مشاريع Django تُزامن من `projects/pyproject.toml` للمساحة (`uv sync`).
4. **تبعيات الواجهة:** `npm install` / `pnpm install` في `frontend/` الخاصة بالمشروع (أو `assets/` لـ Syntara).
5. **قاعدة البيانات:** `make migrate` ثم هدف البذر الخاص بالمشروع (`make seed` / `make seed-demo` / `make populate-data`).
6. **التشغيل:** خادم تطوير الخلفية + خادم تطوير الواجهة (المنافذ في الجدول أعلاه).
7. **التحقق:** `make check` و `make test` لكل مشروع.

## ذات صلة

- [الوعي بالمشروع](../guides/00-project-awareness.md)
- [الأدلة](../guides/)
- [الخطط](../plans/README.md)

## ملاحظات وإرشادات

- `uv sync` يدير تبعيات Python للمساحة. إذا لم يكن لديك، `pip install uv` يعمل أيضاً.
- أول تشغيل يسحب ~2 جيجابايت من صور Docker؛ `make deploy` اللاحقة تزايدية.
- تعارض المنافذ: إذا كانت 80/443 مشغولة، لن يبدأ Traefik. أوقف الخدمات الأخرى أو استخدم منافذ مخصصة عبر `.env`.
- هجرات قاعدة البيانات تعمل تلقائياً في أول نشر عبر `make deploy`. للتحكم اليدوي: `cd projects/precis/precis-main/backend && make migrate`.
- تحديثات submodule: عندما تتغير `libs/django-fusion/`، شغّل `git submodule update --remote libs/django-fusion` ثم `uv sync`.
- التنظيف: `make cleanup` يزيل الحاويات المتوقفة، الصور المعلقة، وذاكرة البناء المؤقتة (يحتفظ بالأحجام).

<!-- AI-generated: review needed -->