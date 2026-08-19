---
title: نشر الوثائق
description: بناء ونشر وثائق Docus عبر shared-proxy وTraefik.
navigation:
  title: النشر
  icon: i-lucide-cloud-upload
---

# نشر الوثائق

## مسار النشر

```text
Docus / Nuxt generate
        ↓
shared-proxy Nginx
        ↓
Traefik + Let's Encrypt
        ↓
docs.structa.cloud أو media.structa.cloud/docs/
```

## بناء الصورة

نفذ من جذر المستودع:

```bash
docker compose -f application/proxy/docker-compose.nginx.yml build shared-proxy
docker compose -f application/proxy/docker-compose.nginx.yml up -d shared-proxy
```

مرحلة Node داخل Docker تقوم بتثبيت Docus، وتوليد محتوى `en` و`ar`، ثم تنفيذ
`nuxt generate`. المرحلة النهائية تحتوي على Nginx والملفات الثابتة فقط.

## التحقق

```bash
docker compose -f application/proxy/docker-compose.nginx.yml config -q
docker inspect --format '{{json .State.Health}}' shared-proxy
curl -I https://docs.structa.cloud/en/
curl -I https://docs.structa.cloud/ar/
curl -I https://media.structa.cloud/docs/en/
```

لا تعِد تهيئة PostgreSQL أو وحدات Docker من أجل نشر الوثائق. صورة Docus ثابتة
ولا تحتاج إلى قاعدة بيانات تشغيلية.

## الترجمة

أضف الصفحة العربية في `docs/docus/ar-content/` مع الحفاظ على نفس مسار الصفحة
الإنجليزية. استخدم `dir: rtl` الذي توفره إعدادات i18n ولا تضف اتجاه RTL إلى
كود Markdown نفسه.
