---
title: دليل المصادقة
description: كيف تعمل المصادقة عبر مشاريع Structa Cloud — POS سطح المكتب ومواقع Django.
navigation:
  title: المصادقة
  icon: i-lucide-shield
---

# دليل المصادقة

> **مرتبط:** `projects/pos/backend/rust-auth.md`, `libs/auth-customization.md`
> **الوسوم:** #auth #login #superuser #oauth #mfa #session

كيف تعمل المصادقة عبر مشاريع Structa Cloud وكيفية إعدادها.

---

## مصادقة تطبيق POS لسطح المكتب

### كيف تعمل

```
إطلاق التطبيق
  └── check_auth_required(db_path)
       ├── SUPERUSER_EMAIL+PASSWORD مضبوطان؟ → شاشة تسجيل الدخول
       ├── SMTP مضبوط؟ → تدفق رمز تأكيد البريد
       └── لا شيء؟ → تخطي المصادقة، افتح الرئيسية مباشرة
```

> 💡 **نصيحة:** للتطوير، اضبط `SUPERUSER_EMAIL=dev@test.com` و
> `SUPERUSER_PASSWORD=dev` في `projects/pos/.env`. يُنشأ المستخدم الفائق تلقائياً
> عند أول إطلاق بكلمة مرور مشفرة bcrypt.

### تفعيل المصادقة

1. اضبط متغيري البيئة في `projects/pos/.env`:
   ```bash
   SUPERUSER_EMAIL=admin@restaurant.com
   SUPERUSER_PASSWORD=your-secure-password
   SUPERUSER_NAME=Admin              # اختياري
   ```

2. أطلق التطبيق — تصبح الشاشة الأولى تسجيل دخول
3. سجّل الدخول ببريد المستخدم الفائق وكلمة مروره
4. يظهر زر الملف الشخصي أعلى اليمين يعرض بريد المستخدم

> ⚠️ **تحذير:** إذا ضُبط واحد فقط من `SUPERUSER_EMAIL`/`SUPERUSER_PASSWORD`،
> فلن تُفعَّل المصادقة. يجب ضبط الاثنين معاً.

### زر الملف الشخصي/تسجيل الخروج

- يعرض دائرة الصورة الرمزية (الحرف الأول من الاسم) + البريد في الشريط العلوي
- النقر → قائمة منسدلة بمعلومات المستخدم + زر **تسجيل الخروج**
- يُغلق عند النقر خارج القائمة
- يظهر فقط عندما تكون المصادقة مفعّلة والمستخدم مسجلاً

### تحذير الخمول

عند تفعيل المصادقة، يتتبع التطبيق خمول المستخدم:
- شريط تحذير أصفر ينزلق بعد مهلة قابلة للتهيئة
- انقر **البقاء** لتجاهله
- ❌ **غير قابل للتخصيص** — السلوك في `AuthContext.tsx`

### مصادقة البريد SMTP

بديل لمصادقة المستخدم الفائق:
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_USERNAME=your@email.com
SMTP_PASSWORD=your-app-password
SMTP_RECIPIENT='Support <support@site.com>'
```

يتلقى المستخدمون رموز تأكيد عبر البريد.

---

## مصادقة مواقع Django (CTC Research, LMS, VResume)

### الإطار

تستخدم جميع المواقع `django-allauth` مع mixins المصادقة الخاصة بـ django-fusion.

### تدفق المصادقة

```
Browser GET /auth/login/
├── HX-Request: true  → AuthHTMXAdapter → شظية مجردة (auth/login.html)
└── لا يوجد رأس HX  → AuthHTMXAdapter → skeleton.html يلف الشظية
```

### المحوّلات

| المحوّل | الموقع | الدور |
|---------|--------|-------|
| `AuthHTMXAdapter` | `plugins/accounts/adapters.py` | يربط قوالب allauth بشظايا HTMX |
| `AuthHTMXSocialAccountAdapter` | نفس الملف | معالجة تسجيل الدخول الاجتماعي |
| `RegistrationAdapter` | نفس الملف | توجيه تأكيدات البريد |

> 💡 **نصيحة:** المحوّلات الثلاثة تعيش في `plugins/accounts/adapters.py` في كل
> موقع. تتبع النمط نفسه — انسخ من موقع إلى آخر عند الحاجة.

### تسجيل الدخول الاجتماعي

مدعوم OAuth من Google وFacebook. اضبط متغيرات البيئة:
```bash
GOOGLE_OAUTH_CLIENT_ID=...
GOOGLE_OAUTH_SECRET=...
FACEBOOK_OAUTH_CLIENT_ID=...
FACEBOOK_OAUTH_SECRET=...
```

> ⚠️ **تحذير:** أزرار تسجيل الدخول الاجتماعي يجب أن تستخدم وسوم `<a>` أبداً
> وليس `hx-post`. إعادة توجيه OAuth لا تعمل مع HTMX.

### MFA / 2FA

2FA مخصص قائم على TOTP متاح في إعدادات الملف الشخصي:
- علم `two_factor_enabled` على نموذج الملف الشخصي
- `two_factor_secret` يخزن سر TOTP
- `allauth.mfa` اختياري لدعم WebAuthn/passkey

### مرجع سريع

| المهمة | POS | Django |
|--------|--------|--------|
| تفعيل المصادقة | اضبط متغيرات `SUPERUSER_*` | مضبوط افتراضياً |
| إضافة مستخدم | يُنشأ تلقائياً من البيئة | `manage.py createsuperuser` أو الإدارة |
| تغيير كلمة المرور | `ensure_superuser_exists` تحدّث التجزئة | عبر صفحة الملف أو الإدارة |
| تسجيل الدخول الاجتماعي | غير متاح | Google, Facebook OAuth |
| MFA | غير متاح | TOTP (الملف الشخصي) + WebAuthn اختياري |
| إعادة تعيين كلمة المرور | غير متاح | عبر البريد (يتطلب SMTP) |

## ملاحظات وإرشادات

- النسخة الإنجليزية الكاملة: [`/docs/en/guides/03-auth`](/docs/en/guides/03-auth).
- راجع دليل WebAuthn/Passkeys: [`/docs/en/guides/auth/webauthn-passkeys`](/docs/en/guides/auth/webauthn-passkeys).
