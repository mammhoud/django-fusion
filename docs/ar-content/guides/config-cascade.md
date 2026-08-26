---
title: سلسلة الإعدادات والبيئات
description: كيف تتسلسل الإعدادات عبر المستودع — ملفات بيئة Docker، طبقات YAML (dynaconf)، مجلدات configs، ومسارات الملفات الثابتة (قراءة ← إخراج ← نشر).
navigation:
  title: سلسلة الإعدادات
  icon: i-lucide-layers
---

# 🧅 سلسلة الإعدادات والبيئات

> المرتبط: `guides/04-deploy.md`، `commands.md`،
> `libs/django-fusion/src/django_fusion/config/project.py`
> **الوسوم:** #الإعدادات #dynaconf #docker #البيئة #الملفات-الثابتة

كل منتج في Structa Cloud يجيب عن «أي قيمة تُستخدم ومن أين تأتي؟» عبر **سلسلة
طبقات واحدة**: القيم الافتراضية في YAML، والتخصيص في `.env`، وحقيقة النشر في
Compose، والحاوية تفوز دائماً.

## 1. الطبقات (من الأدنى إلى الأعلى أولوية)

| # | الطبقة | الموقع | المحتوى |
|---|--------|--------|---------|
| 1 | الإعدادات المشتركة | `projects/precis/configs/Env/*.yml` | سجل المواقع، قاعدة البيانات، الأمان، التخزين، البريد، السجلات، المدفوعات |
| 2 | إعدادات المشروع | `<project>/configs/*.yml` | افتراضيات التطوير المحلي، هوية الموقع والنطاقات، لوحة الإدارة، لوحة CSS |
| 3 | تجاوزات الموقع | `<project>/Env/_site.yml` | عقد الهوية والميزات لكل موقع |
| 4 | ملفات `.env` | `<repo>/.env` ← `<project>/.env` | الأسرار والتخصيص المحلي غير المرفوع |
| 5 | متغيرات البيئة | `DJANGO_*` / المفاتيح المباشرة (Compose) | حقيقة النشر — **تفوز دائماً** |

**القاعدة:** YAML للافتراضيات، `.env` للتخصيص، وCompose للحقيقة. لا تُرفع
الأسرار إلى YAML أبداً.

## 2. سلسلة Docker البيئية

- **الاستيفاء:** يقرأ Compose `${VAR:-default}` من `.env` في مجلد العمل الحالي.
- **`env_file`:** تُحقن الملفات بالترتيب — اللاحق يتجاوز السابق، و`required: false`
  يتجاهل الملف المفقود.
- **الأولوية داخل الخدمة (أدنى ← أعلى):** `ENV` في الصورة ← `env_file:` ←
  كتلة `environment:` ← خيارات سطر الأوامر.
- **ملفات التجاوز:** `docker-compose.override.yml` هي المكان الرسمي لفروق
  التطوير المحلي (منافذ، debug، تثبيتات مباشرة)؛ لا تُستخدم في نشر الإنتاج.

```bash
cd projects/precis/precis-main
docker compose up -d --build   # يحمّل override تلقائياً
```

## 3. سلسلة YAML (Django-Fusion)

`django_fusion.config.project.load_config()` يقرأ افتراضيات قراءات البيئة من
مجلد `configs/` الخاص بالمشروع (بجانب `frontend/` و`backend/`):

| الملف | المحتوى |
|-------|---------|
| `defaults.yml` | افتراضيات التطوير + مرجع الملفات الثابتة (`STATIC:`) |
| `site.yml` | الهوية: الاسم، النطاقات، المضيفات المسموحة |
| `admin.yml` | لوحة الإدارة + لوحة CSS (مصدر ← ملف مُجمّع ← رابط الخدمة) |
| `theme.yml` | *(اختياري)* رموز التصميم |

كل ملف قد يستخدم أقسام البيئة (`default:`، `development:`، `production:`).
ترتيب التحميل: `defaults.yml` ← `site.yml` ← `admin.yml` ← `theme.yml` ثم
`Env/_site.yml` ثم `.env` ثم متغيرات البيئة.

### حل الأولوية حسب رابط الأساس (front/back)

`ProjectConfig.resolve(base_url, side)` يجد هوية الموقع المطابقة للنطاق
(مثل `https://lms.structa.cloud` أو `http://localhost:3000`) ويطبّقها فوق
السلسلة — مع بقاء متغيرات البيئة أعلى أولوية. `make config-show` يعرض
النتائج للرابطين (الخلفي والأمامي).

## 4. مرجع الملفات الثابتة (قراءة ← إخراج ← نشر)

| المرحلة | الإعداد | المسار (precis-main) |
|---------|---------|----------------------|
| **قراءة** | `STATICFILES_DIRS` | `backend/assets/static`، `assets/static`، `frontend/public` |
| **حزمة** | `WEBPACK_LOADER` | `backend/assets/static/bundles/bundles.json` |
| **لوحة CSS** | مخرجات `make css` | `assets/static/css/fusion.css` |
| **إخراج** | `STATIC_ROOT` | `backend/assets/staticfiles/` |
| **وسائط** | `MEDIA_ROOT` | `backend/assets/media/` |
| **نشر** | وحدات التخزين | `precis-main-static`، `precis-main-media` |
| **خدمة** | `/static/` + `/media/` | whitenoise خلف Traefik + shared-proxy nginx |

### تدفق collectstatic مع الحزمة (خطوة بخطوة)

```text
frontend/src/styles/globals.css ← make css ← assets/static/css/fusion.css
webpack bundles.json + assets/static ← collectstatic ← STATIC_ROOT
STATIC_ROOT ← وحدة التخزين ← whitenoise /static/ ← Traefik
```

| الأمر | ماذا يفعل |
|-------|-----------|
| `make css` | يجمّع نظام التصميم إلى `fusion.css` |
| `make build-assets` | يحزم SCSS/JS عبر webpack إلى `bundles/` |
| `make skeleton-manifest` | يولّد manifest الهيكل لـ Astro |
| `python manage.py collectstatic --noinput` | ينسخ المصادر إلى `STATIC_ROOT` |
| بدء الحاوية | `migrate ← collectstatic ← seed_pages ← seed_learning ← gunicorn` |

## أوامر التحقق

```bash
make config-show     # السلسلة المدمجة + خطط الملفات الثابتة + رؤى front/back
make config-check    # تحقق من وجود مفاتيح الهوية المطلوبة
make config-front    # توليد frontend/src/config/site-config.json لـ Astro
```

## Remarks & Notes

- متغيرات البيئة هي مصدر الحقيقة وقت التشغيل؛ السلسلة توفّر الافتراضيات فقط.
- لا تطبع الأسرار أو ترفعها: `.env` مستثنى من git؛ و`DJANGO_SECRET_KEY`
  وكلمات مرور SMTP تبقى خارج YAML.
- النسخة الإنجليزية الكاملة: [`/docs/en/guides/config-cascade`](/docs/en/guides/config-cascade).
