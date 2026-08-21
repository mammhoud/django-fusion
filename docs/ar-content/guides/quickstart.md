---
title: البدء السريع
description: تشغيل Structa Cloud محلياً والوصول إلى الوثائق.
navigation:
  title: البدء السريع
  icon: i-lucide-rocket
---

# البدء السريع

## المتطلبات

ثبت الأدوات التالية قبل تشغيل المشروع:

- Docker وDocker Compose
- Python 3.11 أو أحدث مع `uv`
- Node.js 22 أو أحدث
- مدير الحزم المستخدم في كل مشروع، مثل `pnpm`

## تثبيت تبعيات مساحة العمل

```bash
uv sync
npm install
```

تظل تبعيات المنتجات المحلية مستقلة. راجع ملف `package.json` داخل كل منتج
واستخدم مدير الحزم المحدد فيه عند الحاجة.

## تشغيل فحوصات الوثائق

```bash
cd docs
npm install
npm run build
```

ينشئ Docus موقعاً ثابتاً داخل مخرجات Nuxt. لا تعدّل مجلد `content/` الناتج؛
يتم توليده من Markdown الإنجليزي وملفات `ar-content/` في كل تشغيل.

## تشغيل البنية المحلية

```bash
docker compose -f application/databases/docker-compose.yml up -d postgres default-redis
docker compose -f application/proxy/docker-compose.nginx.yml up -d --build shared-proxy
```

بعد تشغيل الوكيل العكسي افتح:

- `https://docs.structa.cloud/en/`
- `https://docs.structa.cloud/ar/`
- `https://media.structa.cloud/docs/en/`

## استكشاف الأخطاء

إذا ظهرت صفحة قديمة، أعد بناء صورة `shared-proxy`. وإذا ظهرت صفحة بلغة
خاطئة، امسح ملف تعريف اللغة `structa-docs-locale` من المتصفح ثم أعد فتح رابط
اللغة المطلوب.
