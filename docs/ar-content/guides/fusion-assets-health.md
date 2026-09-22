---
title: صحة أصول Fusion
description: خط أنابيب الأصول الثابتة، فحوصات CSS/JS الصحية، تحليل الحزم، وعقود أصول django-fusion.
navigation:
  title: صحة أصول Fusion
  icon: i-lucide-activity
object:
  type: "guide"
  id: "guide.fusion-assets-health"
attributes:
  source_path: "guides/fusion-assets-health.md"
  canonical_route: "/docs/ar/guides/fusion-assets-health"
  source_of_truth: "repository-markdown"
  audience: "engineers, operators, and coding agents"
  status: "maintained"
  owner: "workspace"
tags:
  - structa-cloud
  - onboarding
  - assets
  - health
  - css
  - javascript
  - django-fusion
  - bundles
links:
  - label: "أفضل الممارسات"
    to: "/guides/best-practices"
    icon: "i-lucide-check"
  - label: "Docus"
    to: "/guides/docus"
    icon: "i-lucide-pencil"
  - label: "أصول django-fusion"
    to: "/libs/django-fusion"
    icon: "i-lucide-package"
---

# 💊 صحة أصول Fusion — خط أنابيب الأصول الثابتة

هذا الدليل هو نقطة الدخول للمونوريبو لعقود الصحة والأصول المشتركة. المرجع المفصل للمكتبة هو [`DF-017`](/docs/ar/libs/django-fusion/17-integration-modes).

---

## أين يوجد الكود

- `libs/django-fusion/src/django_fusion/core/assets/` — عروض JSON للأصول القياسية وأنماط URL
- `libs/django-fusion/src/django_fusion/templatetags/fusion_assets.py` — وسم القالب `{% asset %}`
- `projects/*/assets/` — SCSS، CSS المجمع، الصور، الوسائط الخاصة بالمشروع
- `projects/*/backend/assets/staticfiles/` — مخرجات collectstatic (مُتجاهلة في git)

---

## نظرة عامة على خط أنابيب الأصول

```
SCSS/JS المصدر (projects/*/assets/, libs/django-fusion/assets/)
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

---

## فحوصات الصحة

### 1. التحقق من Manifest الحزم

```bash
# التحقق من وجود bundles.json وقابليته للتحليل
cat projects/structa.cloud/backend/assets/static/bundles/bundles.json | jq .

# المفاتيح المتوقعة: main.css, main.js, vendor.css, vendor.js, fusion.css
```

### 2. صحة CSS

```bash
# التحقق من حجم CSS المجمع
wc -c projects/structa.cloud/backend/assets/staticfiles/css/fusion.css

# التحقق من عدم تكرار المحددات (تحقق تقريبي)
awk '/\{/{print}' projects/structa.cloud/backend/assets/staticfiles/css/fusion.css | sort | uniq -d
```

### 3. صحة حزم JS

```bash
# التحقق من أحجام الحزم
ls -lh projects/structa.cloud/frontend/dist/assets/

# التحقق من Source maps
file projects/structa.cloud/frontend/dist/assets/*.js.map
```

### 4. عروض أصول django-fusion

```bash
# اختبار نقطة نهاية manifest الأصول
curl -s https://structa.cloud/api/assets/manifest/ | jq .

# اختبار أصل فردي
curl -s https://structa.cloud/static/css/fusion.css | head -20
```

---

## تحليل الحزم

### محلل حزم Webpack

```bash
cd projects/structa.cloud/frontend
npx webpack-bundle-analyzer dist/stats.json
```

### Manifest أصول django-fusion

يتم توليد `bundles.json` بواسطة `django-fusion` أثناء `collectstatic`:

```json
{
  "fusion.css": "/static/css/fusion.css?v=abc123",
  "main.js": "/static/js/main.abc123.js",
  "vendor.js": "/static/js/vendor.def456.js"
}
```

يستخدمه وسم القالب `{% asset "main.js" %}` لعناوين URL مع كسر الكاش.

---

## المشاكل الشائعة والحلول

| العَرَض | السبب | الإصلاح |
|---------|-------|-------|
| 404 على `/static/css/fusion.css` | `collectstatic` لم يُشغل | `docker exec <container> python manage.py collectstatic --noinput` |
| CSS قديم في المتصفح | فشل كسر الكاش | تحقق من `bundles.json` به hash؛ أعد بناء الواجهة الأمامية |
| محددات CSS مكررة | عدة تشغيلات `make css` | نظف `assets/static/css/` قبل إعادة البناء |
| `fusion.css` مفقود في الـ manifest | `django-fusion` ليس في `INSTALLED_APPS` | أضف `'django_fusion'` إلى `INSTALLED_APPS` |
| عدم تطابق hash الأصل | الواجهة الأمامية + الخلفية غير متزامنتين | أعد بناء الواجهة الأمامية → `collectstatic` → انشر |

---

## المراقبة والتنبيهات

```bash
# فحص صحة يومي (cron)
#!/bin/bash
curl -sf https://structa.cloud/api/assets/manifest/ > /dev/null || alert "Asset manifest down"
curl -sf https://structa.cloud/static/css/fusion.css | grep -q "fu-" || alert "fusion.css missing tokens"
```

### مقاييس Prometheus (إذا مُمكّنة)

- `asset_manifest_requests_total`
- `asset_manifest_errors_total`
- `static_file_size_bytes{file="fusion.css"}`

---

## ذات صلة

- [تكامل أصول django-fusion](/docs/ar/libs/django-fusion/17-integration-modes) — مرجع المكتبة المفصل
- [تكوين الملفات الثابتة](/docs/ar/dev/infrastructure/deployment#static-files) — تكوين Nginx/Traefik
- [بناء الواجهة الأمامية](/docs/ar/guides/04-dev#frontend-build) — عملية بناء Vite/Astro

---

## ## ملاحظات وإرشادات

- `fusion.css` هو ورقة الأنماط المجمعة الوحيدة لنظام التصميم — جميع المشاريع تشاركها.
- `bundles.json` هو مصدر الحقيقة لعناوين URL مع كسر الكاش؛ لا تعدل يدويًا.
- فحوصات صحة الأصول تعمل في `make probe-health` و CI.
- التغييرات الجذرية في خط أنابيب الأصول تتطلب زيادة إصدار في `django-fusion`.

---

→ [العودة للأدلة](../) | [أفضل الممارسات](best-practices) | [Docus](docus) | [أصول django-fusion](/docs/ar/libs/django-fusion)

<!-- AI-generated: review needed -->