---
title: سير عمل تحميل الملفات
description: كيفية تحميل محتوى صفحات Wagtail وبيانات البذر في قواعد بيانات مواقع fusion.
navigation:
  title: تحميل الملفات
  icon: i-lucide-package
---

# 📦 سير عمل تحميل الملفات

كيفية تحميل محتوى صفحات Wagtail وبيانات البذر في قواعد بيانات مواقع fusion.

---

## نظرة عامة

مواقع fusion (`cms-fusion`, `precis-lms`) تأتي مع ملفات JSON تملأ قاعدة بيانات
Wagtail بالصفحات واللغات والمستخدمين وكتل محتوى الرئيسية. تُحمَّل الملفات عبر
أمر الإدارة `load_fusion_fixtures`، الذي يغلّف `loaddata` في Django مع ترتيب
التبعيات.

```
ملفات الملفات ──→ load_fusion_fixtures ──→ Django loaddata ──→ قاعدة Wagtail
  assets/fixtures/     أمر الإدارة        JSON → ORM         الجداول
```

> **ترتيب التبعيات مهم.** تُحمَّل اللغات أولاً، ثم المستخدمون، ثم أنواع
> المحتوى، ثم الصفحات. يتعامل أمر الإدارة مع هذا تلقائياً.

## البدء السريع

```bash
# تحميل ملفات الاختبار (لغات ← مستخدمون ← اختيارات ← صفحات)
cd projects/cms-fusion/backend
python manage.py load_fusion_fixtures

# تحميل ملفات الاختبار + محتوى الرئيسية
python manage.py load_fusion_fixtures --full

# معاينة ما سيُحمَّل (آمن، بلا تغييرات)
python manage.py load_fusion_fixtures --full --dry-run
```

## مرجع الأمر

### `load_fusion_fixtures`

| العلم | الوصف |
|-------|--------|
| `-c test` | **افتراضي.** تحميل ملفات الاختبار (4 ملفات) |
| `-c seed` | تحميل seed/homepage_content.json فقط |
| `-c production` | تحميل تفريغات الإنتاج (اللغات + البيانات النظيفة) |
| `-c by-model` | تحميل تفريغات لكل نموذج |
| `-c all` | تحميل كل شيء (⚠️ تداخل PK عبر الفئات) |
| `--full` | تحميل الاختبار + البذر (مكافئ `-c test` + `-c seed`) |
| `--fixture PATH` | تحميل ملف واحد نسبي إلى `assets/fixtures/` |
| `-n` / `--dry-run` | معاينة الملفات بالحجم دون تحميل |
| `--skip-missing` | تخطي ملفات الملفات المفقودة بدلاً من الخطأ |
| `--dir DIR` | تجاوز مسار مجلد الملفات |

### أمثلة

```bash
# معاينة كل ملفات الاختبار + البذر
python manage.py load_fusion_fixtures --full --dry-run

# تحميل بيانات اللغة فقط
python manage.py load_fusion_fixtures --fixture test/locales.json

# تحميل بيانات الإنتاج، تخطي الملفات المفقودة
python manage.py load_fusion_fixtures -c production --skip-missing
```

## متى تُحمَّل الملفات

| السياق | المحفّز | ملاحظات |
|--------|---------|---------|
| **تطوير محلي** | `python manage.py load_fusion_fixtures` | يدوي، مرة واحدة أو بعد إعادة تعيين DB |
| **نشر Docker** | `RUN_SETUP=true` في docker-compose | يعمل داخل حاوية الخلفية عند الإقلاع |
| **CI/CD** | `manage.py load_fusion_fixtures --dry-run` | يتحقق من قابلية تحليل JSON |
| **الاختبار** | نماذج DB عبر ORM في `setUpTestData` | لا تُستخدم ملفات JSON في الاختبارات |

## الاختبار مقابل الملفات

مجموعة اختبار `test_fixture_content.py` **لا تستخدم** `loaddata`. بدلاً من ذلك،
تنشئ نماذج Wagtail مباشرة عبر ORM في `setUpTestData`. هذا مقصود:

- قاعدة بيانات الاختبار تستخدم SQLite في الذاكرة مع تعطيل الترحيلات
- `loaddata` يتطلب قاعدة بيانات مرحَّلة بالكامل مع أنواع محتوى
- بيانات الاختبار عبر ORM تتجنب هذه القيود وتعمل أسرع

## استكشاف الأخطاء

| المشكلة | السبب المحتمل | الحل |
|---------|---------------|------|
| `CommandError: Fixture directory not found` | دليل عمل خاطئ | استخدم `--dir` أو شغّل من `backend/` |
| `IntegrityError` عند التحميل | مفاتيح PK مكررة من فئات متداخلة | لا تخلط فئتي `test` + `production` |
| `ContentType matching query does not exist` | لا ترحيل لنماذج الصفحات المخصصة | أنشئ سجلات `ContentType` يدوياً أو شغّل `migrate` أولاً |
| ملف الملفات غير موجود | مسار أساسي خاطئ | تحقق من `--dir` أو من وجود الملف تحت `assets/fixtures/` |

## Remarks & Notes

- النسخة الإنجليزية الكاملة: [`/docs/en/guides/fixture-loading`](/docs/en/guides/fixture-loading).
- راجع تكوين الوكيل الكامل: [`/docs/en/dev/infrastructure/proxy`](/docs/en/dev/infrastructure/proxy).
