---
title: مرجع الأوامر والتفويض
description: كل أمر make في المستودع، اصطلاح تسمية الأفعال الموحد، وسلسلة التفويض من Makefile الجذري إلى كل مكوّن.
navigation:
  title: الأوامر
  icon: i-lucide-terminal
---

# 🛠️ مرجع الأوامر والتفويض

> مصدر الحقيقة الوحيد لكل أمر `make` في المستودع: تسمية الأفعال الموحدة،
> وسلسلة التفويض، والتسلسل (`deploy` → `deploy-all` → `deploy-*` لكل خدمة)
> الذي يرفع المجموعة بأكملها بترتيب حتمي.

<!-- AI-generated: review needed -->

## 1. تسمية الأفعال الموحدة

كل Makefile مكوّن تحت `application/` و`docs/` و`projects/` و`libs/` يكشف نفس
أفعال دورة الحياة حتى يكون التفويض متوقعاً:

| الفعل | المعنى | مثال التفويض من الجذر |
|-------|--------|------------------------|
| `up` | تشغيل الخدمة (idempotent) | `make -C application/tools/affine up` |
| `deploy` | بناء + تشغيل (تحقق أولاً عند الاقتضاء) | `make deploy-docs` |
| `down` | إيقاف الخدمة وإزالتها | `make -C application/tools/ollama down` |
| `build` | بناء الصور فقط دون تشغيل | `make -C docs build` |
| `status` | عرض حالة الحاوية/compose | `make status` |
| `logs` | تتبع السجلات | `make logs` |
| `restart` | `down` + `up` | `make restart` |
| `ps` | اسم بديل لـ `status` | `make -C application/proxy ps` |
| `check` | التحقق من الإعداد / فحوصات النظام | `make check` |
| `help` | طباعة أوامر هذا الـ Makefile | `make -C application/proxy help` |

الانقسام `up` ↔ `deploy` ثابت: **`up` يشغّل، `deploy` يبني ثم يشغّل.**

## 2. خريطة التفويض (الجذر ← المكوّن)

| هدف الجذر | يفوض إلى | أمر المكوّن |
|-----------|----------|-------------|
| `deploy-proxy` | `application/proxy` | `deploy` (تحقق ← `proxy-up`) |
| `deploy-databases` | `application/databases` | `deploy-db` (`build` + `up`) |
| `deploy-coder` | `application/` | `up-coder` |
| `deploy-docs` | `docs/docker-compose.yml` | `docker compose up -d --build` |
| `deploy-app` | `projects/` | `docker-up` |
| `deploy-tools` | `application/tools/<name>` | `up` لكل أداة |
| `status` / `logs` / `stop` / `restart` | `application/proxy` | نفس الفعل |

```text
root Makefile
 ├─ deploy-databases ──► application/databases  (deploy-db → build + up)
 ├─ deploy-coder     ──► application/           (up-coder)
 ├─ deploy-media     ──► application/tools      (nginx compose)
 ├─ deploy-app       ──► projects/              (docker-up)
 ├─ deploy-tasks     ──► projects/docker-compose.tasks.yml
 ├─ deploy-docs      ──► docs/docker-compose.yml
 ├─ deploy-proxy     ──► application/proxy      (deploy → validate + up)
 └─ deploy-tools     ──► application/tools/*    (up per tool)
```

## 3. عنصر التسلسل (`deploy` → `deploy-all`)

الترتيب الافتراضي هو `postgres-first` (عبر `DEPLOY_ORDER`):

```text
databases → coder → media → app → tasks → docs → proxy → anytype → tools → coolify
```

`DEPLOY_ORDER=legacy` محفوظ للتوافق الخلفي لكنه **يحذّر** — يشغّل proxy/app/media
قبل قواعد البيانات، فتنهار تطبيقات Django عند أول إقلاع. فضّل الافتراضي.

### بوابات ما قبل النشر (تُشغَّل قبل أي تغيير Docker)

- `preflight-network` — يفحص أسماء الشبكات ويستكشف Docker daemon.
- `deploy-preflight` — يتحقق من `DEPLOY_ORDER` ويحلل `PREFLIGHT_COMPOSE_FILES`.
- `validate-deploy-order` — يضمن أن `DEPLOY_ORDER` في القائمة المسموحة.
- `create-networks` — ينشئ `common` و`traefik-net` وغيرها (idempotent).

## 4. موزّع المشاريع (`projects/Makefile`)

```bash
cd projects
make check WEBSITE=precis-ctc     # فحص الخلفية للموقع المحدد
make test  WEBSITE=precis-main    # اختبار الخلفية
make run-dev WEBSITE=precis-ctc   # خوادم التطوير
make migrate WEBSITE=loop-crm
```

`WEBSITE=` يحلّ الموقع (`precis-main`, `precis-ctc`, `loop-crm`, `syntara`
بالإضافة إلى الأسماء البديلة القديمة `structa`/`lms`/`core` → `precis-main`).

## 5. سلسلة الإعدادات وأوامر الملفات الثابتة

المشاريع التي تملك مجلد `configs/` (Precis Main أولاً) تكشف أوامر سلسلة تعرض
مزيج YAML + `.env` + متغيرات البيئة وخطة الملفات الثابتة (قراءة ← إخراج ← نشر).

```bash
cd projects/precis/precis-main
make config-show     # السلسلة المدمجة + خطة الملفات الثابتة
make config-check    # التحقق من حل مفاتيح الهوية المطلوبة
make css             # تجميع نظام التصميم Tailwind → assets/static/css/fusion.css
make collectstatic   # نسخ STATICFILES_DIRS → STATIC_ROOT
```

### تدفق الملفات الثابتة (إجراء بإجراء)

`make css` → `assets/static/css/fusion.css` → `collectstatic` ينسخ
`STATICFILES_DIRS` (`backend/assets/static`, `assets/static`, `frontend/public`)
إلى `STATIC_ROOT` (`backend/assets/staticfiles`) → وحدة التخزين المسماة
(`precis-main-static`) → يخدمها whitenoise `/static/` خلف Traefik؛ `/media/`
يُخدم عبر shared-proxy nginx. أمر تشغيل الحاوية ينفذ
`migrate → collectstatic → seed_pages → seed_learning → gunicorn` عند كل إقلاع.

## 6. أهداف nx المجمّعة

```bash
make check-all    # npx nx run-many -t check --all
make test-all     # npx nx run-many -t test --all
make nx-build-all # npx nx run-many -t build --all
make nx-run T=<target>
```

## Remarks & Notes

- هدف `%:` الشامل في الجذر يعيد توجيه الأهداف غير المعروفة إلى
  `projects/Makefile` (مثل `make community-test`)، لكن الأهداف الصريحة
  (مثل `check-all`) لها الأولوية.
- `docker compose down --volumes` و`docker system prune` واستعادة قواعد البيانات
  و`make deploy*` فعّالة — تتطلب نية صريحة وليست جزءاً من التحقق للقراءة فقط.
- النسخة الإنجليزية الكاملة: [`/docs/en/commands`](/docs/en/commands).
