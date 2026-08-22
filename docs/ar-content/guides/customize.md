---
title: دليل التخصيص
description: ما يمكنك تخصيصه بأمان عبر مشاريع Structa Cloud وما لا يجب أن تلمسه.
navigation:
  title: التخصيص
  icon: i-lucide-sliders-horizontal
---

# دليل التخصيص

> **مرتبط:** كل وثائق المنصة — راجع أقسام التخصيص لكل منصة
> **الوسوم:** #customization #override #extend #config #templates

ما يمكنك تخصيصه بأمان عبر مشاريع Structa Cloud، وما لا يجب أن تلمسه.

---

## نظام وسوم التخصيص

كل وثيقة تستخدم هذه الوسوم:

| الوسم | المعنى | مثال |
|-------|--------|------|
| 🟢 `customizable` | آمن للتعديل والتوسيع والتجاوز | صفحات POS، قوالب مواقع Django |
| 🔴 `not-customizable` | إطار أساسي — استخدم الواجهة العامة فقط | `django-fusion/`, `auth.rs`, `App.tsx` |
| 🟡 `delegate` | توسعة عبر الخطافات/الإضافات | إضافة أمر Tauri، إضافة تطبيق Django |
| 🔵 `template` | مستوى القالب فقط | تعديل SCSS، JSON i18n، قوالب HTML |
| ⚪ `config` | متغيرات البيئة أو الإعدادات فقط | `SUPERUSER_EMAIL`, `POSTGRES_HOST` |

---

## تخصيص POS

### 🟢 ما يمكنك تغييره

| المنطقة | كيف |
|---------|-----|
| تخطيطات الصفحات | عدّل `src/pages/*.tsx` بحرية |
| مكونات الواجهة | عدّل `src/components/*.tsx` |
| الأنماط | عدّل ملفات SCSS في `src/styles/` |
| الترجمات | أضف مفاتيح إلى `src/i18n/*.json` |
| تصميم الفاتورة | عدّل `INVOICE_TEMPLATE` في `sidecar/server.py` |
| أنماط الفاتورة | أضف مداخل إلى `DESIGN_CONFIGS` في `sidecar/server.py` |
| بيانات البذر | عدّل `src-tauri/src/bin/seed.rs` |
| أمر Tauri جديد | أنشئه في `operations/` ← سجّله في `lib.rs` |
| نقطة نهاية API جديدة | أضف مساراً في `sidecar/server.py` |

### 🔴 ما لا يجب أن تغيّره

| المنطقة | لماذا |
|---------|-------|
| `auth.rs` (Rust) | حاسم أمنياً: bcrypt، التحقق من الجلسة |
| `AuthContext.tsx` | تدفق المصادقة، إدارة الجلسة |
| `App.tsx` | بنية التوجيه، بوابة المصادقة |
| `sidecar.rs` | دورة حياة عملية الـ sidecar |
| بروتوكول WebSocket | `chat.ts` في الواجهة يعتمد على التنسيق الدقيق |

### 🔵 تغييرات مستوى القالب

| المنطقة | تخصيص عبر |
|---------|-----------|
| CSS/SCSS | `src/styles/_variables.scss` |
| الترجمات | `src/i18n/en.json`, `fr.json`, `ar.json` |
| HTML الفاتورة | سلسلة `INVOICE_TEMPLATE` في `server.py` |

### ⚪ إعداد فقط

| الإعداد | أين |
|---------|-----|
| بيانات المستخدم الفائق | `projects/pos/.env` (`SUPERUSER_*`) |
| مضيف/منفذ الـ sidecar | `POS_SIDECAR_HOST`, `POS_SIDECAR_PORT` |
| إعدادات SMTP | متغيرات `SMTP_*` |
| مسار قاعدة البيانات | متغير `DATABASE_URL` |

---

## تخصيص مواقع Django

### 🟢 ما يمكنك تغييره

| المنطقة | كيف |
|---------|-----|
| قوالب الموقع | تجاوز في `projects/<site>/templates/` |
| إعدادات الموقع | عدّل `projects/<site>/settings.py` |
| إضافة تطبيق Django | أنشئه في `projects/<site>/www/` |
| إضافة إضافة | أنشئها في `projects/<site>/plugins/` |
| إضافة موقع للسجل | عدّل `configs/settings/ENV/sites.yml` |
| قوالب المصادقة | أنشئ `templates/auth/` ← أضف إلى `TEMPLATE_MAP` |
| المصادقة الاجتماعية | اضبط متغيرات `GOOGLE_OAUTH_*`, `FACEBOOK_OAUTH_*` |

### 🔴 ما لا يجب أن تغيّره

| المنطقة | لماذا |
|---------|-------|
| `django-fusion/` | الإطار الأساسي — استخدم واجهته العامة |
| `configs/base/` | الإعدادات الأساسية — تجاوز في إعدادات الموقع |
| `www/` (الأساسي) | كود التطبيق المشترك |
| `ceptor-ai/` | نواة المساعد الذكي |

### 🟡 نمط التفويض

| المهمة | كيف |
|--------|-----|
| تجاوز قالب | انسخ من `assets/templates/` ← عدّل في `templates/` الخاص بالموقع |
| إضافة مكوّن | أنشئه في `components/` ← استخدم `{% comp "name" %}` |
| تسجيل مسار تضمين | `register_include_path()` في `AppConfig.ready()` |
| إضافة viewset | وسّع `ModelViewset` في `www/` الخاص بالموقع |

### ⚪ إعداد فقط

| الإعداد | أين |
|---------|-----|
| اسم قاعدة البيانات | متغيرات `DB_NAME_CTC`, `DB_NAME_LMS`, `DB_NAME_VRESUME` |
| المضيفات المسموحة | `settings.py` الخاص بالموقع أو البيئة |
| وضع التصحيح | متغير `DJANGO_DEBUG=0|1` |
| المفتاح السري | متغير `DJANGO_SECRET_KEY` |

---

## تخصيص البنية التحتية

### 🟢 ما يمكنك تغييره

| المنطقة | كيف |
|---------|-----|
| إضافة خدمة Docker | أنشئ `docker-compose.custom.yml` في `application/compose/` |
| إضافة شهادة SSL | `manage-certs.sh bootstrap-acme` |
| إضافة موجّه موقع | عدّل `proxy/configs/traefik/dynamic/<site>.yml` |
| نصوص نسخ قاعدة البيانات | أضف إلى `application/scripts/` |

### 🔴 ما لا يجب أن تغيّره

| المنطقة | لماذا |
|---------|-------|
| `proxy/configs/traefik/dynamic.yml` | تعريفات نقاط الدخول — يكسر التوجيه |
| `databases/docker-compose.yml` | خدمات قاعدة البيانات الأساسية |
| تدفق ACME للوكيل | يجب اتباع المراحل بالترتيب |

---

## مصفوفة القرار السريع

| أريد أن… | افعل هذا… | الوسم |
|----------|-----------|-------|
| أغير تخطيط صفحة | عدّل `src/pages/*.tsx` | 🟢 |
| أغير ألوان الموقع | عدّل متغيرات SCSS | 🔵 |
| أضيف ميزة POS جديدة | عملية Rust ← أمر Tauri ← صفحة TS | 🟡 |
| أتجاوز قالب موقع | انسخ إلى مجلد `templates/` الخاص بالموقع | 🟡 |
| أغير سلوك المصادقة | ❌ لا — استخدم متغيرات البيئة أو المحوّلات | 🔴 |
| أضيف موقع Django | أضف إلى `sites.yml` ← أنشئ المجلد | 🟢 |
| أغير مخطط قاعدة البيانات | أنشئ ترحيل Diesel/Django | 🟢 |
| أضيف نقطة نهاية API | أضف مساراً في `server.py` | 🟢 |

## Remarks & Notes

- النسخة الإنجليزية الكاملة: [`/docs/en/guides/05-customize`](/docs/en/guides/05-customize).
- راجع أيضًا [`/docs/en/project-structure`](/docs/en/project-structure) لمصفوفة التخصيص الكاملة.
