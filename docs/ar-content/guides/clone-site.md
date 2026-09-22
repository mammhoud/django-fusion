---
title: استنساخ موقع Django
description: استنساخ موقع موجود (LMS, CTC Research, Portfolio) كقالب لمشروع جديد.
navigation:
  title: استنساخ موقع
  icon: i-lucide-copy
---

# استنساخ موقع Django

> **الوقت:** ~15 دقيقة | **المستوى:** متوسط
> استنسخ موقعاً موجوداً (LMS, CTC Research, Portfolio) كقالب لمشروع جديد.

---

## نظرة عامة

مستودع Structa Cloud مصمم لتعدد الإيجارات — أنشئ موقع Django جديداً باستنساخ
موقع موجود. LMS هو القالب الموصى به (الأكثر اكتمالاً في الميزات).

---

## الخطوات السريعة

### 1. انسخ وأعد التسمية

```bash
cd projects
cp -r lms my-new-site
```

### 2. سجّل الموقع

أضف إلى `projects/configs/settings/ENV/sites.yml`:

```yaml
sites:
  my-new-site:
    domain: mysite.structa.cloud
    db_name: db_mysite
    port: 5074
```

### 3. أنشئ قاعدة البيانات

```sql
CREATE DATABASE db_mysite;
```

### 4. أضف إلى `.env`

```bash
DB_NAME_MYSITE=db_mysite
MYSITE_HOST=mysite.structa.cloud
```

### 5. أضف خدمة Docker

انسخ كتلة خدمة الموقع في `docker-compose.applications.yml`، وحدّث
`PROJECT_PATH` والمنفذ و`container_name` والـ labels والحجوم.

### 6. خصّص

- استبدل القوالب في `my-new-site/templates/`
- أزل الإضافات غير المستخدمة من `my-new-site/plugins/`
- حدّث `settings.py` بـ `SITE_ID` الجديد

### 7. انشر

```bash
make deploy-app
make probe-health
```

---

## مقارنة المواقع: أيها تستنسخ؟

| موقع المصدر | الأنسب لـ | يمتلك |
|-------------|-----------|-------|
| **LMS** | منصات الدورات ومواقع العضوية | مصادقة، دورات، مدفوعات، مدونة، ملفات شخصية، Wagtail CMS |
| **CTC Research** | الاستشارات والتدريب والبحث | مصادقة، مدونة، LMS خفيف، خدمات، نشرة، أحداث |
| **Portfolio** | منشئات السير والمواقع الشخصية | مصادقة، منشئ سيرة، معرض أعمال، تصدير PDF، مدونة |

## Remarks & Notes

- النسخة الإنجليزية الكاملة: [`/docs/en/guides/06-clone-site`](/docs/en/guides/06-clone-site).
- راجع دليل النشر: [`/docs/en/guides/04-deploy`](/docs/en/guides/04-deploy).
