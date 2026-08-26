---
title: البنية المعمارية
description: سير العمل، المكونات، المهام، الأصول، MCP، وسير عمل التوثيق عبر Structa Cloud.
navigation:
  title: البنية المعمارية
  icon: i-lucide-landmark
---

# 🏗️ البنية المعمارية — Structa Cloud

> مرجع بنية شامل: دورة حياة الطلب، نظام المكونات، خط أنابيب الهيكل، المهام الخلفية، تكامل MCP، توثيق Docus، وسلسلة البناء الكاملة.
> مُحدّث: 18 أغسطس 2026

<!-- AI-generated: review needed -->

---

## 1. دورة حياة الطلب

كل طلب HTTP عبر مشروع django-fusion يتبع هذا المسار:

```
Client (Browser / Astro / HTMX / MCP)
  │
  ▼
┌─ Traefik / خادم التطوير المحلي ──────────────────────────────────────┐
│  SSL termination، التوجيه، rate limiting، تحدي ACME                │
└─────────────────────────────────────────────────────────────────────┘
  │
  ▼
┌─ Django (WSGI) ──────────────────────────────────────────────────────┐
│  Middleware (الجلسات، المصادقة، CSRF، اللغة، HTMX، middleware الموقع)│
└─────────────────────────────────────────────────────────────────────┘
  │
  ▼
┌─ التوجيه ────────────────────────────────────────────────────────────┐
│  PageHandler / Viewset / صفحة Wagtail / نقطة نهاية API             │
└─────────────────────────────────────────────────────────────────────┘
  │
  ▼
┌─ طبقة النموذج/الخدمة/الاستعلام ───────────────────────────────────────┐
│  PostgreSQL (أساسي) · Redis (ذاكرة التخزين المؤقت/الصفوف)           │
└─────────────────────────────────────────────────────────────────────┘
  │
  ▼
┌─ الاستجابة ──────────────────────────────────────────────────────────┐
│  قالب، شظية، JSON، أو استجابة متدفقة                               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. نظام المكونات (django-fusion)

`django-fusion` يوفر مكونات قابلة لإعادة الاستخدام، توجيه، شظايا، نماذج، جداول، وأصول:

| مكون | الموقع | الغرض |
|---------|----------|---------|
| `fragments` | `django_fusion.fragments` | نقاط نهاية HTML الجزئية لـ HTMX |
| `routes` | `django_fusion.routes` | توجيه RESTful مبني على الاتفاقيات |
| `comp` | `django_fusion.comp` | مكونات القالب المسجلة (`{% comp %}`) |
| `tables` | `django_fusion.tables` | جداول DataTables جاهزة للإنتاج |
| `forms` | `django_fusion.forms` | نماذج نموذجية مع عرض HTMX |
| `assets` | `django_fusion.core.assets` | manifest الأصول، كسر الكاش |

> 💡 **نصيحة:** استورد من `django_fusion.*` — لا توجد إعادة تصدير أو وحدات وسيطة.

---

## 3. خط أنابيب الهيكل (Skeleton Pipeline)

```
مصدر SCSS/JS (projects/*/assets/, libs/django-fusion/assets/)
    │
    ▼
تجميع (make css / npm run build)
    │
    ▼
Manifest JSON (assets/static/bundles/bundles.json)
    │
    ▼
Collectstatic (python manage.py collectstatic)
    │
    ▼
مجلد Staticfiles → Proxy المشترك (Nginx) → CDN / المتصفح
```

- `fusion.css` — ورقة أنماط نظام التصميم المجمعة الوحيدة (جميع المشاريع تشاركها)
- `bundles.json` — مصدر الحقيقة لعناوين URL مع كسر الكاش
- `{% asset "name" %}` — وسم القالب لعناوين URL مع كسر الكاش

---

## 4. المهام الخلفية

- **Dramatiq** — عامل المهام الأساسي (Redis broker)
- **APScheduler** — جدولة المهام الدورية
- **العامل المشترك** — `shared-worker` للمهام عبر المشاريع
- **المجدول المشترك** — `shared-scheduler` للمهام الدورية عبر المشاريع

---

## 5. تكامل MCP

- خادم Kilo MCP في `application/agents/`
- الأدوات المسجلة: النشر، فحص الصحة، استعلام DB، عمليات الملفات
- إعداد الوكيل في `.agents/kiro/settings/mcp.json`

---

## 6. توثيق Docus

- التطبيق في `docs/` (Nuxt + Docus)
- إنجليزي/عربي عبر `@nuxtjs/i18n`
- `scripts/prepare-content.mjs` يولد `content/en/` + `content/ar/`
- التحقق عبر `scripts/validate-content.mjs`

---

## ## ملاحظات وإرشادات

- PostgreSQL هو قاعدة البيانات العلائقية المشتركة الأساسية في البيئات المنتشرة.
- Redis يدعم الصفوف/الذاكرة المؤقتة ويستخدم بواسطة عمال Celery/Dramatiq ذات الصلة.
- لا تشغل الهجرات، أو تحميل البيانات التدميري، أو تقليم الأحجام، أو أوامر الإنتاج ضد بيئة مشتركة دون توجيه مستخدم صريح.

---

→ [الوعي بالمشروع](/docs/ar/guides/00-project-awareness) | [بنية المشروع](/docs/ar/project-structure) | [الأوامر](/docs/ar/COMMANDS)

<!-- AI-generated: review needed -->