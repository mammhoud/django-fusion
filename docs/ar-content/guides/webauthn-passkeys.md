---
title: إعداد WebAuthn / Passkey MFA
description: تسجيل الدخول بمفاتيح المرور (WebAuthn) عبر القياسات الحيوية للمنصة أو مفاتيح الأمان.
navigation:
  title: WebAuthn / Passkeys
  icon: i-lucide-fingerprint
---

# WebAuthn / إعداد Passkey MFA

مصادقة Passkey (WebAuthn) تسمح للمستخدمين بتسجيل الدخول باستخدام القياسات
الحيوية للمنصة (Face ID, Touch ID, Windows Hello) أو مفاتيح الأمان (YubiKey)
بدلاً من كلمات المرور أو بالإضافة إليها.

## الإعداد

تسجيل الدخول بـ Passkey مُفعَّل عبر وحدة `allauth.mfa` الخاصة بـ django-allauth.
الإعدادات مضبوطة في `projects/cms-fusion/configs/base/auth.py` و
`projects/precis/precis-main/configs/base/auth.py` (مشتركة عبر كل المواقع):

```python
# allauth.mfa يجب أن يكون في INSTALLED_APPS
INSTALLED_APPS += ["allauth.mfa"]

# تفعيل تسجيل الدخول القائم على المفتاح
MFA_PASSKEY_LOGIN_ENABLED = True

# اشتراك Passkey فقط (يتطلب تحقق البريد + رمز): الافتراضي False
MFA_PASSKEY_SIGNUP_ENABLED = False

# أنواع MFA المدعومة: TOTP (تطبيق مصادق)، WebAuthn (مفاتيح المرور)، رموز الاسترداد
MFA_SUPPORTED_TYPES = ["totp", "webauthn", "recovery_codes"]
```

## ما الذي تغيّر

| الملف | التغيير |
|-------|---------|
| `projects/cms-fusion/configs/base/apps.py` | أُضيف `"allauth.mfa"` إلى `THIRD_PARTY_APPS` |
| `projects/precis/precis-main/configs/base/apps.py` | أُضيف `"allauth.mfa"` إلى `THIRD_PARTY_APPS` |
| `projects/cms-fusion/configs/base/auth.py` | `MFA_PASSKEY_LOGIN_ENABLED` → `True`; أُضيف `"webauthn"` إلى `MFA_SUPPORTED_TYPES` |
| `projects/precis/precis-main/configs/base/auth.py` | نفسه أعلاه |
| `tests/unit/test_auth_features.py` | أُضيف اختبار `test_passkey_mfa_enabled` |

## متطلبات المتصفح

تتطلب مفاتيح المرور أن تُقدَّم الصفحة عبر HTTPS (أو `localhost` للتطوير).
المتصفحات التي تدعم WebAuthn:

- Chrome 108+ (Windows, macOS, Android)
- Safari 16+ (macOS, iOS)
- Firefox 118+
- Edge 108+

## تفعيل اشتراك المفتاح

للسماح للمستخدمين بالاشتراك بمفتاح مرور فقط (بدون كلمة مرور)، اضبط:

```python
MFA_PASSKEY_SIGNUP_ENABLED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True
```

## استكشاف الأخطاء

- **«Passkey is not supported»**: يجب تقديم الصفحة عبر HTTPS.
- **«The operation either timed out or was not allowed»**: ألغى المستخدم
  موجه المفتاح في المتصفح — حاول مجدداً.
- **المفتاح لا يستمر عبر الأجهزة**: مفاتيح المرور مقيدة بالمصادق المنصبي
  للجهاز. يجب على المستخدمين إعداد مفتاح على كل جهاز يستخدمونه.

## Remarks & Notes

- النسخة الإنجليزية الكاملة: [`/docs/en/guides/auth-webauthn-passkeys`](/docs/en/guides/auth-webauthn-passkeys).
- راجع دليل المصادقة الأوسع: [`/docs/ar/guides/auth`](/docs/ar/guides/auth).
