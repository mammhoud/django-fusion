---
title: قوالب شظايا المصادقة
description: مرجع قوالب المصادقة كشظايا خالصة — بنية الشظية، معايير BEM، ومُدخلات النموذج المخفية المطلوبة.
---

# قوالب شظايا المصادقة

كل قوالب المصادقة هي **شظايا خالصة** — بلا `{% extends %}`، والعنصر الخارجي دائماً `<section class="fragment--form">`.

## نمط القالب

```html
{# Context fields: form, request #}
{# Placeholders: none #}
{% load i18n static %}
<section class="fragment--form">
  <section class="auth__card card card--form">
    <header class="auth__form-header">
      <h2 class="auth__form-title">{% trans "Title" %}</h2>
      <p class="auth__form-subtitle mb-4">{% trans "Subtitle" %}</p>
    </header>
    <form class="auth__form"
          hx-post="{% url 'plugins:...' %}"
          hx-target=".auth__form"
          hx-swap="innerHTML">
      {% csrf_token %}
      <input type="hidden" name="strategy"
             value="{% if request.htmx %}htmx{% else %}document{% endif %}">
      <input type="hidden" name="supports_sse"
             value="{{ request.supports_sse|yesno:'true,false' }}">
      {# form fields #}
    </form>
    <footer class="auth__footer">...</footer>
  </section>
</section>
```

## كل القوالب

| القالب | الغرض | السياق الأساسي |
|----------|---------|-------------|
| `auth/login.html` | تسجيل الدخول | `form` |
| `auth/register.html` | إنشاء حساب | `form` |
| `auth/forgot_page.html` | طلب إعادة تعيين كلمة المرور | `form` |
| `auth/reset_password.html` | تعيين كلمة مرور جديدة | `form`, `invalid_key_form` |
| `auth/verification_link.html` | التحقق من البريد الإلكتروني | `confirmation`, `messages` |
| `auth/password_change.html` | تغيير كلمة المرور (مسجَّل الدخول) | `form` |
| `auth/password_set.html` | تعيين كلمة المرور الأولى (اجتماعي) | `form` |
| `auth/email_manage.html` | إدارة عناوين البريد | `form`, `emailaddresses` |
| `auth/password_reset_done.html` | تم إرسال بريد إعادة التعيين | — |
| `auth/password_reset_key_done.html` | نجاح إعادة تعيين كلمة المرور | — |
| `auth/signup_closed.html` | التسجيل معطَّل | — |
| `auth/social_signup.html` | إكمال التسجيل الاجتماعي | `form` |
| `auth/social_connections.html` | إدارة الحسابات الاجتماعية | `form`, `connected_accounts`, `disconnectable_accounts` |

## معايير BEM للتنسيق

### النطاقات المسموح بها

- `auth__*` — مكوّنات المصادقة (`auth__card`، `auth__form`، `auth__submit`)
- `form__*` — عناصر النموذج (`form__group`، `form__input`، `form__label`)
- `btn--*` — معدِّلات الأزرار (`btn--primary`، `btn--social`)
- أدوات Bootstrap (`d-*`، `mb-*`، `text-*`، `bg-*`، إلخ)
- Font Awesome (`fas`، `fab`، `fa-*`)

### لوحة الألوان

| الرمز | القيمة | الاستخدام |
|-------|-------|-------|
| Primary | `#1E3A8A` | `btn-primary`, `text-primary` |
| Success | `#10B981` | `alert-success`, `text-success` |
| Danger | `#EF4444` | `alert-danger`, `text-danger` |
| Warning | `#F59E0B` | `alert-warning`, `text-warning` |

## المُدخلات المخفية المطلوبة

يجب أن يتضمّن كل `<form>` في قالب مصادقة ما يلي:

```html
<input type="hidden" name="strategy"
       value="{% if request.htmx %}htmx{% else %}document{% endif %}">
<input type="hidden" name="supports_sse"
       value="{{ request.supports_sse|yesno:'true,false' }}">
```

تتيح هذه الحقول للخادم اختيار استراتيجية الاستجابة الصحيحة.

<!-- AI-generated: review needed -->
