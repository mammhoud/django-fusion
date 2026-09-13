---
title: لوحة الأدوات والمصادقة
description: بوابة أدوات داخلية مستضافة ذاتياً — قائمة اللوحة، نافذة تسجيل الدخول، بوابة فتح لكل أداة، كوكيز الجلسة، ونقاط الـ API.
navigation:
  title: لوحة الأدوات والمصادقة
  icon: i-lucide-wrench
---

# لوحة الأدوات والمصادقة

> **المالك:** أدوات المساحة · **النطاق:** بوابة داخلية
> **مسار المصدر:** `application/tools/tools-web/`
> **آخر تحديث:** 2026-09-12

---

## نظرة عامة

تقدّم هذه الخدمة:

1. **لوحة الأدوات** على الجذر — تُدرج كل أداة مستضافة ذاتياً تحت application/tools/
2. **نافذة تسجيل الدخول** — تتم المصادقة في نافذة منبثقة على اللوحة
3. **بوابة فتح لكل أداة** — النقر على أداة يطلب كلمة مرور فتح مشتركة قبل الانتقال
4. **مبدّل السمة** — تبديل فاتح/داكن محفوظ في تخزين المتصفح، وافتراضياً يتبع تفضيل النظام
5. **إدارة الجلسة** — كوكيز HTTP-only موقّعة (HMAC)
6. **نقاط الـ API** — تسجيل الدخول، تسجيل الخروج، فحص الجلسة، التحقق من الفتح

الواجهة الأمامية مبنية بـ Alpine.js + htmx (مضمّنة محلياً تحت `public/vendor/`) بلا خطوة بناء.

---

## البنية المعمارية

```
┌─────────────────────────────────────────────────────────────┐
│  tools.structa.cloud (Traefik TLS)                          │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  tools-proxy (Nginx)                                        │
│  ├── / → tools-web:4321 (dashboard)                         │
│  ├── /login → tools-web:4321 (redirects to /)               │
│  ├── /api/* → tools-web:4321 (auth + unlock API)            │
│  ├── /adminer/ → adminer:8080                               │
│  ├── /mailpit/ → mailpit:8025                               │
│  ├── /grafana/ → grafana:3000                               │
│  ├── /docs/ → docus:3000                                    │
│  └── /notes/ → blinko:1111                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## تكوين المستخدمين

يُعرَّف المستخدمون في `application/tools/tools-web/users.yml`:

```yaml
users:
  - username: "admin"
    password_hash: "$2a$10$..."  # bcrypt hash of "admin"
    role: "admin"
    name: "Administrator"
    email: "admin@structa.cloud"
    enabled: true

  - username: "supervisor"
    password_hash: "$2a$10$..."  # bcrypt hash of "supervisor"
    role: "supervisor"
    name: "Supervisor"
    email: "supervisor@structa.cloud"
    enabled: true
```

### بيانات الاعتماد الافتراضية

| اسم المستخدم | كلمة المرور | الدور |
|----------|----------|------|
| admin | admin | admin |
| supervisor | supervisor | supervisor |

### توليد تجزئات كلمات المرور

```bash
cd application/tools/tools-web
node -e "console.log(require('bcryptjs').hashSync('your-password', 10))"
```

حدِّث `users.yml` بالتجزئة الجديدة وأعِد بناء صورة Docker.

---

## كلمة مرور الفتح (`TOOLS_UNLOCK_PASSWORD`)

كل بطاقة أداة تطلب **كلمة مرور فتح مشتركة** قبل الانتقال. تأتي كلمة المرور من
متغير البيئة `TOOLS_UNLOCK_PASSWORD` (انظر `application/tools/.env.example`)،
وليس من `users.yml`.

```bash
# Generate a strong random value
openssl rand -base64 18 | tr -d '/+=' | head -c 20
```

أضِفها إلى ملف `.env` في جذر المستودع (أو `application/tools/.env`) وأعِد النشر:

```env
TOOLS_UNLOCK_PASSWORD=<random value>
TOOLS_SESSION_SECRET=<random value>   # optional; signs session cookies
```

إذا لم تُضبط `TOOLS_UNLOCK_PASSWORD`، تُعيد `/api/unlock` الرمز 500 برسالة
واضحة، وتُظهر نافذة الفتح «غير مُهيَّأة».

---

## نظام التصميم

**Swiss Industrial Print** — متسق مع صفحة الهبوط في `tools-proxy` Nginx:
- ورق مطفي (`#F4F4F0`) + حبر كربوني (`#0A0A0A`) (السمة الداكنة تتحول إلى `#12120F` / `#EDEBE6`)
- لون تمييز أحمر طيراني (`#E61919`، وأكثر سطوعاً `#FF3B30` في الوضع الداكن)
- انحناء حدود صفري
- ظلال إزاحية صلبة (4px × 4px)
- تسميات قياس أحادية المسافة بأحرف كبيرة
- أصناف مكوّنات بنمط BEM

### الخطوط
- **العناوين:** Archivo Black / Arial Black
- **النصوص:** Inter
- **أحادي المسافة:** IBM Plex Mono

---

## نقاط الـ API

### `POST /api/login`
مصادقة المستخدم وإنشاء كوكي جلسة موقّع.

**الطلب:**
```http
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin
```

**الاستجابة (200):**
```json
{
  "success": true,
  "user": { "username": "admin", "role": "admin", "name": "Administrator", "email": "admin@structa.cloud" }
}
```

**الاستجابة (401):**
```json
{ "error": "Invalid username or password" }
```

### `POST /api/unlock`
التحقق من كلمة مرور الفتح المشتركة لأداة وضبط كوكي فتح قصير الأجل. تُعيد هدف
إعادة التوجيه (مسار الأداة أو مضيفها).

**الطلب:**
```http
Content-Type: application/x-www-form-urlencoded

password=<TOOLS_UNLOCK_PASSWORD>&tool=/notes/
```

**الاستجابة (200):**
```json
{ "success": true, "redirect": "/notes/" }
```

**الاستجابة (401):**
```json
{ "error": "Incorrect password for this tool" }
```

### `POST /api/logout`
مسح كوكيز الجلسة والفتح.

**الاستجابة (200):**
```json
{ "success": true }
```

### `GET /api/session`
فحص الجلسة الحالية.

**الاستجابة (200):**
```json
{
  "authenticated": true,
  "user": { "username": "admin", "role": "admin", "name": "Administrator", "email": "admin@structa.cloud" },
  "unlocked": false
}
```

أو إذا لم تكن مصادَقاً:
```json
{ "authenticated": false, "unlocked": false }
```

---

## إدارة الجلسة

- **كوكي الجلسة:** `tools_auth_session` — حمولة موقّعة (`base64url(JSON).hmac`)
- **كوكي الفتح:** `tools_unlocked` — علامة `ok` موقّعة، انتهاء بعد 12 ساعة
- **التخزين:** HTTP-only، SameSite=Lax، Secure في الإنتاج (TLS على Traefik)
- **الانتهاء:** 7 أيام (الجلسة)
- **التوقيع:** HMAC-SHA256 مع `TOOLS_SESSION_SECRET` (يرجع إلى `TOOLS_UNLOCK_PASSWORD`)

---

## النشر

### تشغيل محلي
```bash
cd application/tools/tools-web
npm install
TOOLS_UNLOCK_PASSWORD=yourpass node server.mjs
# → http://localhost:4321
```

### Docker
```bash
# From repository root
docker compose -f application/tools/docker-compose.yml build tools-web
docker compose -f application/tools/docker-compose.yml up -d tools-web
```

### الشبكات
- `traefik-net` — توجيه Traefik
- `common` — التواصل بين الحاويات

### فحص الصحة
```bash
wget -qO- http://localhost:4321/health/   # → healthy
```

---

## بنية المشروع

```
application/tools/tools-web/
├── server.mjs                  # Vanilla Node HTTP server (static + API)
├── public/
│   ├── index.html              # Dashboard + sign-in/unlock modals (Alpine)
│   ├── app.js                  # Alpine component (session, unlock, theme)
│   ├── styles.css              # Swiss Industrial Print + dark theme
│   ├── logo.svg
│   └── vendor/
│       ├── htmx.min.js         # Vendored htmx 2.x
│       └── alpine.min.js       # Vendored Alpine.js 3.x
├── users.yml                   # Sign-in accounts (bcrypt)
├── package.json                # bcryptjs + js-yaml only
└── Dockerfile                  # node:22-alpine, no build step
```

---

## إضافة أدوات جديدة إلى اللوحة

حرِّر مصفوفة `TOOLS` في **كلا** الملفين `server.mjs` و`public/app.js` (يُحافَظ
على تزامنهما مع مسارات nginx):

```javascript
{
  category: 'category-name',
  name: 'Display Name',
  description: 'Tool description',
  path: '/tool-path/',          // for internal tools
  // OR
  host: 'https://external.com', // for external tools
  external: true                // if external
}
```

---

## ملاحظات أمنية

1. **HTTPS فقط** — الكوكيز `Secure`، ويتطلّب إنهاء TLS على Traefik
2. **كوكيز HTTP-only** — تمنع سرقة الرمز عبر XSS
3. **جلسات موقّعة** — HMAC-SHA256 يمنع تزوير الكوكيز
4. **bcrypt** — لا تُخزَّن كلمات المرور أبداً بصيغة واضحة
5. **كلمة فتح مشتركة** — بوابة واحدة لكل الأدوات، تُخزَّن في متغيرات البيئة فقط
6. **بلا basic auth** — أُزيل `auth_basic` من nginx؛ تتولّى tools-web المصادقة

---

## استكشاف الأخطاء

### فشل تسجيل الدخول
- تحقّق من صحة تجزئات bcrypt في `users.yml`
- تأكّد من نسخ `users.yml` إلى صورة Docker
- تأكّد من `NODE_ENV=production`

### الفتح يقول «غير مُهيَّأ»
- `TOOLS_UNLOCK_PASSWORD` مفقودة في بيئة الحاوية — أضِفها إلى `.env` وأعِد
  النشر (`make deploy-tools` / compose up -d tools-web)

### الجلسة لا تستمر
- تحقّق من مطابقة علامة `Secure` للكوكي مع HTTPS
- تحقّق من أن `SameSite=Lax` يسمح بالعبور بين النطاقات الفرعية عند الحاجة
- تأكّد من تمرير Traefik لترويسة `X-Forwarded-Proto`

### اللوحة تُحمَّل لكن النوافذ لا تعمل
- تأكّد من وجود `public/vendor/alpine.min.js` و`htmx.min.js`
  (فهي مضمَّنة في الصورة وقت البناء)

---

## ملفات ذات صلة

| الملف | الغرض |
|------|---------|
| `application/tools/tools-web/users.yml` | حسابات المستخدمين |
| `application/tools/tools-web/server.mjs` | خادم HTTP + واجهة المصادقة/الفتح |
| `application/tools/nginx/default.conf.template` | توجيه Nginx |
| `application/tools/docker-compose.yml` | تنسيق الخدمات |
| `application/tools/tools-web/Dockerfile` | بناء الحاوية |
| `application/tools/tools-web/docker-compose.yml` | تعريف خدمة tools-web |
| `application/tools/.env.example` | مرجع `TOOLS_UNLOCK_PASSWORD` |

---

## ملاحظات وإرشادات

- استُبدل تطبيق Astro SSR (`astro-tools`) بخادم Node بلا إطار في 2026-08-26؛
  وأُزيل `application/tools/astro-tools/`.
- الواجهة الأمامية Alpine.js + htmx بلا خطوة بناء — حرِّر `public/` مباشرة.
- انتقل تسجيل الدخول من صفحة `/login` مستقلة إلى نافذة على اللوحة.
- أُضيفت بوابة كلمة مرور فتح لكل أداة: فتح أي أداة يتطلّب
  `TOOLS_UNLOCK_PASSWORD` من متغيرات البيئة.
- يستمر مبدّل السمة في `localStorage` (`tools-theme`) وافتراضياً يتبع تفضيل
  نظام التشغيل؛ ورموز الوضع الداكن مُعرَّفة في `styles.css` تحت `.dark`.

<!-- AI-generated: review needed -->
