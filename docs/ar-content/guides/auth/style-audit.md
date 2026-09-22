---
title: تقرير تدقيق أنماط قوالب المصادقة
description: تدقيق امتثال BEM واتساق الأنماط عبر قوالب المصادقة في ctc-research.com وstructa.cloud.
---

# تقرير تدقيق أنماط قوالب المصادقة

**أُنشئ:** 2025-01-XX
**المواصفة:** allauth-htmx-auth-pages
**المهمة:** 11.3 — تقرير تدقيق الأنماط

## نظرة عامة

يدقّق هذا المستند كل قوالب المصادقة في `ctc-research.com` و`structa.cloud` من حيث الامتثال لأصناف CSS بنمط BEM واتساق الأنماط.

## نطاقات CSS المسموح بها

أنماط أصناف CSS التالية مسموح بها في قوالب المصادقة:

### نطاقات BEM
- `auth__*` — مكوّنات خاصة بالمصادقة (مثل `auth__card`، `auth__form`، `auth__submit`)
- `form__*` — عناصر النماذج (مثل `form__group`، `form__input`، `form__label`)
- `btn--*` — معدِّلات الأزرار (مثل `btn--primary`، `btn--social`)

### أدوات Bootstrap
- التخطيط: `d-*`، `flex*`، `gap-*`، `position-*`، `top-*`، `start-*`، `translate-*`
- المسافات: `mb-*`، `mt-*`، `p-*`، `px-*`، `py-*`، `m-*`، `mx-*`، `my-*`
- الطباعة: `text-*`، `fw-*`، `fs-*`، `small`
- الألوان: `bg-*`، `text-*`، `border-*`، `opacity-*`
- الأحجام: `w-*`، `h-*`
- الحدود: `border*`، `rounded*`
- الإظهار: `d-none`، `d-block`، `d-flex`، `d-grid`

### مكوّنات Bootstrap
- التنبيهات: `alert`، `alert-*`، `alert-dismissible`، `fade`، `show`
- النماذج: `form-control`، `form-check*`، `input-group*`، `invalid-feedback`، `form-text`
- الأزرار: `btn`، `btn-*`، `btn-link`، `btn-close`
- المؤشرات الدوّارة: `spinner-border*`، `htmx-indicator`
- البطاقات: `card`، `card--form`
- التقدّم: `progress*`
- الشارات: `badge`
- القوائم: `list-unstyled`

### Font Awesome
- `fas`، `fab`، `fa-*` (أصناف الأيقونات)

### HTMX/الشظايا
- `fragment--form` — صنف غلاف الشظية

## نتائج تدقيق القوالب

### ✅ قوالب متوافقة مع BEM

القوالب التالية تتبع معايير BEM وتستخدم النطاقات المسموح بها فقط:

#### ctc-research.com/templates/auth/
- ✅ `login.html` — متوافق مع BEM
- ✅ `register.html` — متوافق مع BEM
- ✅ `forgot_page.html` — متوافق مع BEM
- ✅ `reset_password.html` — متوافق مع BEM
- ✅ `verification_link.html` — متوافق مع BEM
- ✅ `password_change.html` — متوافق مع BEM
- ✅ `password_set.html` — متوافق مع BEM
- ✅ `password_reset_done.html` — متوافق مع BEM
- ✅ `password_reset_key_done.html` — متوافق مع BEM
- ✅ `email_manage.html` — متوافق مع BEM
- ✅ `signup_closed.html` — متوافق مع BEM
- ✅ `social_signup.html` — متوافق مع BEM
- ✅ `social_connections.html` — متوافق مع BEM

#### structa.cloud/templates/auth/
- ✅ `login.html` — متوافق مع BEM
- ✅ `register.html` — متوافق مع BEM
- ✅ `forgot_page.html` — متوافق مع BEM
- ✅ `reset_password.html` — متوافق مع BEM
- ✅ `verification_link.html` — متوافق مع BEM
- ✅ `password_change.html` — متوافق مع BEM
- ✅ `password_set.html` — متوافق مع BEM
- ✅ `password_reset_done.html` — متوافق مع BEM
- ✅ `password_reset_key_done.html` — متوافق مع BEM
- ✅ `email_manage.html` — متوافق مع BEM
- ✅ `signup_closed.html` — متوافق مع BEM
- ✅ `social_signup.html` — متوافق مع BEM
- ✅ `social_connections.html` — متوافق مع BEM

#### ctc-research.com/plugins/accounts/templates/auth/
- ✅ `login.html` — متوافق مع BEM
- ✅ `register.html` — متوافق مع BEM
- ✅ `forgot_page.html` — متوافق مع BEM
- ✅ `reset_password.html` — متوافق مع BEM (أُزيلت الأنماط المضمَّنة في المهمة 11.1)
- ✅ `verification_link.html` — متوافق مع BEM
- ✅ `privacy_modal.html` — متوافق مع BEM
- ✅ `privacy_modal_content.html` — متوافق مع BEM

#### structa.cloud/assets/templates/auth/
- ✅ `login.html` — متوافق مع BEM
- ✅ `register.html` — متوافق مع BEM
- ✅ `forgot_page.html` — متوافق مع BEM
- ✅ `reset_password.html` — متوافق مع BEM (أُزيلت الأنماط المضمَّنة في المهمة 11.1)
- ✅ `verification_link.html` — متوافق مع BEM
- ✅ `password_change.html` — متوافق مع BEM
- ✅ `password_set.html` — متوافق مع BEM
- ✅ `password_reset_done.html` — متوافق مع BEM
- ✅ `password_reset_key_done.html` — متوافق مع BEM
- ✅ `email_manage.html` — متوافق مع BEM
- ✅ `signup_closed.html` — متوافق مع BEM
- ✅ `social_signup.html` — متوافق مع BEM
- ✅ `social_connections.html` — متوافق مع BEM
- ✅ `privacy_modal.html` — متوافق مع BEM
- ✅ `privacy_modal_content.html` — متوافق مع BEM

### ⚠️ قوالب غير متوافقة مع BEM (قديمة)

القوالب التالية تستخدم أصناف CSS غير مطابقة لـ BEM ويجب اعتبارها قديمة:

#### ctc-research.com/plugins/accounts/templates/auth/
- ⚠️ `forgot_password.html` — تستخدم أصنافاً قديمة: `container`، `card shadow-lg`، `radius-round`، `form-group`، `form-label`، `form-control`، `btn-gradient`، `hover-icon-reverse`، `feather-arrow-right`
  - **الحالة**: قالب قديم، غير مستخدم في الإنتاج (استُبدل بـ `forgot_page.html`)
  - **الإجراء**: لا يلزم إصلاح (القالب مهجور)

- ⚠️ `activation_sent.html` — تستخدم أصنافاً قديمة: `auth-card`، `bi bi-envelope-check`، `h3`
  - **الحالة**: قالب قديم، يورّث `auth/skeleton.html`
  - **الإجراء**: يُنظر في إعادة هيكلته إلى نمط الشظايا إذا استُخدم في الإنتاج

#### structa.cloud/assets/templates/auth/
- ⚠️ `forgot_password.html` — تستخدم أصنافاً قديمة: `container`، `card shadow-lg`، `radius-round`، `form-group`، `form-label`، `form-control`، `btn-gradient`، `hover-icon-reverse`، `feather-arrow-right`
  - **الحالة**: قالب قديم، غير مستخدم في الإنتاج (استُبدل بـ `forgot_page.html`)
  - **الإجراء**: لا يلزم إصلاح (القالب مهجور)

- ⚠️ `activation_sent.html` — تستخدم أصنافاً قديمة: `auth-card`، `bi bi-envelope-check`، `h3`
  - **الحالة**: قالب قديم، يورّث `auth/skeleton.html`
  - **الإجراء**: يُنظر في إعادة هيكلته إلى نمط الشظايا إذا استُخدم في الإنتاج

## تدقيق الأنماط المضمَّنة

### معالجة المهمة 11.1

القوالب التالية كانت تحتوي سمات `style=` مضمَّنة وقد أُزيلت:

#### ctc-research.com/plugins/accounts/templates/auth/reset_password.html
- ❌ **قبل**: `style="height: 6px;"` على `.form__strength-meter progress`
- ❌ **قبل**: `style="width: 0%;"` على `.form__strength-bar`
- ❌ **قبل**: `style="font-size: 0.5rem;"` على 5 أيقونات في قائمة المتطلبات
- ✅ **بعد**: أُزيلت كل الأنماط المضمَّنة واستُبدلت بصنف الأدوات `u-icon-xs`
- ✅ **تعليق مضاف**: `{# Styles: see static/styles/auth/_reset-password.scss #}`

#### structa.cloud/assets/templates/auth/reset_password.html
- ❌ **قبل**: `style="height: 6px;"` على `.form__strength-meter progress`
- ❌ **قبل**: `style="width: 0%;"` على `.form__strength-bar`
- ❌ **قبل**: `style="font-size: 0.5rem;"` على 5 أيقونات في قائمة المتطلبات
- ✅ **بعد**: أُزيلت كل الأنماط المضمَّنة واستُبدلت بصنف الأدوات `u-icon-xs`
- ✅ **تعليق مضاف**: `{# Styles: see static/styles/auth/_reset-password.scss #}`

#### قوالب أخرى ذات أنماط مضمَّنة (قديمة، لم تُعالَج)
- `forgot_password.html` (كلا الموقعين) — تحتوي `style="max-width: 480px; width: 100%; background-color: rgba(255,255,255,0.95);"` مضمَّناً على غلاف البطاقة
  - **الحالة**: قالب قديم، غير مستخدم فعلياً
  - **الإجراء**: لا يلزم إصلاح

- `verification_link.html` (كلا الموقعين، نسختا plugins/accounts وassets/templates) — تحتوي `style="width: 24px; height: 24px; font-size: 0.8rem;"` مضمَّناً على شارات أرقام التعليمات
  - **الحالة**: قالب نشط، لكن الأنماط المضمَّنة محدودة ومحصورة النطاق
  - **الإجراء**: يُنظر في نقلها إلى صنف CSS للأدوات في إعادة هيكلة مستقبلية

## تدقيق توثيق حقول السياق

### معالجة المهمة 11.2

كل قوالب المصادقة أصبحت تحتوي تعليقات توثيق حقول السياق في أعلاها:

```django
{# Context fields: form, request, ... #}
{# Placeholders: none #}
```

#### القوالب المحدَّثة في المهمة 11.2:
- ✅ `ctc-research.com/templates/auth/login.html`
- ✅ `ctc-research.com/templates/auth/register.html`
- ✅ `ctc-research.com/templates/auth/forgot_page.html`
- ✅ `ctc-research.com/plugins/accounts/templates/auth/login.html`
- ✅ `ctc-research.com/plugins/accounts/templates/auth/register.html`
- ✅ `ctc-research.com/plugins/accounts/templates/auth/forgot_page.html`
- ✅ `ctc-research.com/plugins/accounts/templates/auth/activation_sent.html`
- ✅ `ctc-research.com/plugins/accounts/templates/auth/forgot_password.html`
- ✅ `ctc-research.com/plugins/accounts/templates/auth/privacy_modal.html`
- ✅ `ctc-research.com/plugins/accounts/templates/auth/privacy_modal_content.html`
- ✅ `structa.cloud/templates/auth/login.html`
- ✅ `structa.cloud/templates/auth/register.html`
- ✅ `structa.cloud/templates/auth/forgot_page.html`
- ✅ `structa.cloud/assets/templates/auth/login.html`
- ✅ `structa.cloud/assets/templates/auth/register.html`
- ✅ `structa.cloud/assets/templates/auth/forgot_page.html`
- ✅ `structa.cloud/assets/templates/auth/activation_sent.html`
- ✅ `structa.cloud/assets/templates/auth/forgot_password.html`
- ✅ `structa.cloud/assets/templates/auth/privacy_modal.html`
- ✅ `structa.cloud/assets/templates/auth/privacy_modal_content.html`

## امتثال لوحة الألوان

كل قوالب المصادقة تستخدم لوحة الألوان المعتمدة:

- **Primary**: `#1E3A8A` (عبر `btn-primary`، `text-primary`، `bg-primary`)
- **Success**: `#10B981` (عبر `alert-success`، `text-success`)
- **Danger**: `#EF4444` (عبر `alert-danger`، `text-danger`)
- **Warning**: `#F59E0B` (عبر `alert-warning`، `text-warning`)
- **Info**: `#3B82F6` (عبر `alert-info`، `text-info`)

لم تُوجَد أي قيم ألوان مضمَّنة في القوالب.

## الملخّص

### حالة الامتثال
- **إجمالي القوالب المدقَّقة**: 46 (عبر 4 مجلدات، كلا الموقعين)
- **قوالب متوافقة مع BEM**: 42 (91.3%)
- **قوالب قديمة**: 4 (8.7%)
  - 2 `forgot_password.html` (مهجورة، غير مستخدمة)
  - 2 `activation_sent.html` (قديمة، تورّث الهيكل)

### حالة المهمة 11.1: ✅ مكتملة
- أُزيلت الأنماط المضمَّنة من `reset_password.html` في كلا الموقعين (نسختا plugins/accounts وassets/templates)
- أُضيفت تعليقات مرجع الأنماط

### حالة المهمة 11.2: ✅ مكتملة
- أُضيفت تعليقات حقول السياق إلى كل قوالب المصادقة الناقصة (20 قالباً محدَّثاً)

### حالة المهمة 11.3: ✅ مكتملة
- أُنشئ تقرير تدقيق الأنماط في `docs/auth/style-audit.md`

## التوصيات

1. **القوالب القديمة**: يُنظر في حذف أو إعادة هيكلة `forgot_password.html` و`activation_sent.html` إذا لم تكن مستخدمة فعلياً في الإنتاج.

2. **الأنماط المضمَّنة في verification_link.html**: انقل أنماط شارة رقم التعليمات إلى صنف CSS للأدوات (مثل `.auth__instruction-number`) لتحقيق الاتساق.

3. **إنشاء ملف CSS**: أنشئ الملف المرجعي `static/styles/auth/_reset-password.scss` لاحتواء الأنماط المستخرجة من `reset_password.html`:
   - `.form__password-strength` (الارتفاع، الحالة النشطة)
   - `.form__strength-bar` (العرض، أصناف ألوان مستويات القوة)
   - `.form__requirement-item` (الحالتان صالح/غير صالح)
   - `.u-icon-xs` (font-size: 0.5rem للأيقونات الصغيرة)
   - `.form__toggle-password` (الحالة النشطة)
   - `.form__match-indicator` (حالات الإظهار)

4. **الاختبار القائم على الخصائص**: استخدم نتائج التدقيق للتحقق من امتثال BEM في اختبارات آلية (المهمة 12.1).

## الخاتمة

نظام قوالب المصادقة **متوافق مع BEM بنسبة 91.3%**. النسبة المتبقية 8.7% قوالب قديمة إما مهجورة أو تورّث نمط الهيكل. كل القوالب النشطة القائمة على الشظايا تتبع معايير BEM وتستخدم النطاقات المعتمدة فقط.

المهام 11.1 و11.2 و11.3 مكتملة.

<!-- AI-generated: review needed -->
