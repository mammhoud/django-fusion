---
title: بنية المشروع
description: خريطة نظام الملفات المعيارية، وحدود المنتجات، والأوامر، ونقاط التخصيص.
navigation:
  title: بنية المشروع
  icon: i-lucide-folder-tree
---

# 🏛️ بنية المشروع — المرجع الكامل

> شجرة الدليل الكاملة مع الملاحظات والمراجع وأدلة التخصيص وملاحظات إعداد
> المثيل والتوصيات لاستخدام البنية الأحدث.

---

## شجرة المشروع الكاملة

```text
structa.cloud/
├── AGENTS.md                               # 🔴 تعليمات الوكلاء للمستودع كاملاً
├── Makefile                                # موزّع نشر الجذر (deploy, deploy-databases…)
├── pyproject.toml                          # مساحة عمل بايثون (uv + pytest + ruff)
├── .github/                                # سير عمل CI/CD
├── docs/                                   # 📚 مشروع التوثيق (Docus)
├── projects/                               # 🔵 كل كود المنتجات + إعداد Django المشترك
│   ├── precis/                             # 📘 مجموعة Precis — LMS والتسويق والبحث
│   │   ├── precis-main/                    #     Precis LMS (WEBSITE=structa.cloud)
│   │   ├── precis-landing/                 #     Precis Landing (WEBSITE=precis-landing)
│   │   ├── precis-ctc/                     #     CTC Research (WEBSITE=precis-ctc)
│   │   ├── assets/                         #     قوالب/ملفات ثابتة مشتركة للمجموعة
│   │   └── configs/                        #     إعدادات Django المشتركة
│   ├── formints/                           # 💰 FORMINTS — منصة POS متعددة الإصدارات
│   │   ├── formint-community/              #     مجتمع (Tauri + React + Rust)
│   │   ├── formint-standard/               #     الإصدار القياسي
│   │   ├── formint-pro/                    #     الاحترافي (Django + Astro + Tauri)
│   │   ├── formint-cloud/                  #     السحابي (Django + Channels)
│   │   ├── formint-client/                 #     عميل POS (Tauri + Vue 3)
│   │   ├── packages/                       #     حزم SDK الخاصة بـ @formints/*
│   │   ├── tests/                          #     اختبارات POS المشتركة
│   │   └── docs/                           #     بنية POS + لقطات الشاشة
│   ├── syntara/                            # 🤖 SYNTARA — دردشة/تخصيص بالذكاء الاصطناعي
│   ├── loop-crm/                           # 🧩 LOOP-CRM — CRM موحد + جدولة اجتماعية
│   ├── assets/                             # 🎨 ملفات ثابتة/قوالب/لغة مشتركة
│   └── webpack/                            # 📦 إعداد أصول مشترك/قديم
├── libs/                                   # 📚 مكتبات قابلة لإعادة الاستخدام
│   └── django-fusion/                      #   مكونات Django/Wagtail المشتركة
├── application/                            # 🏗️ البنية التحتية والأدوات
│   ├── proxy/                              #   تكوينات وكيل Traefik
│   ├── databases/                          #   PostgreSQL + Redis compose
│   ├── tools/                              #   shared-proxy (Nginx) + أدوات
│   └── scripts/                            #   نصوص الأتمتة
├── tests/                                  # 🧪 اختبارات تكامل مساحة العمل
└── .agents/                                # 🤖 مهارات الوكلاء والتكوين
```

---

## مرجع حدود المنتجات

| المنتج | المسار | التقنية | AGENTS.md الرئيسي |
|---|---|---|---|
| **Precis LMS** | `projects/structa.cloud/` | Django + Wagtail + django-fusion | `projects/structa.cloud/backend/AGENTS.md` |
| **Precis Landing** | `projects/precis/precis-landing/` | Astro 5 + Django + Wagtail | `projects/precis/precis-landing/AGENTS.md` |
| **CTC Research** | `projects/precis/precis-ctc/` | Django + Wagtail + Astro | `projects/precis/precis-ctc/AGENTS.md` |
| **Syntara** | `projects/syntara/` | Django + CeptorAI + Ollama | `projects/syntara/AGENTS.md` |
| **Loop-CRM** | `projects/loop-crm/` | Django + django-fusion + Astro | `projects/loop-crm/backend/AGENTS.md` |
| **Formint Community** | `projects/formints/formint-community/` | Tauri 2 + React 19 + Rust/Diesel | `projects/formints/formint-community/AGENTS.md` |
| **Formint Standard** | `projects/formints/formint-standard/` | Tauri + Astro | `projects/formints/formint-standard/AGENTS.md` |
| **Formint Professional** | `projects/formints/formint-pro/` | Astro + Django + Tauri | `projects/formints/formint-pro/AGENTS.md` |
| **Formint Cloud** | `projects/formints/formint-cloud/` | Django + Channels + Unfold | `projects/formints/formint-cloud/AGENTS.md` |
| **Formint Client** | `projects/formints/formint-client/` | Tauri 2 + Vue 3 | `projects/formints/formint-client/AGENTS.md` |
| **django-fusion** | `libs/django-fusion/` | حزمة Python | `libs/django-fusion/AGENTS.md` |

---

## دليل التخصيص

### مصفوفة التخصيص لكل منتج

| الطبقة | ماذا تخصّص | أين | مستوى الأمان |
|---|---|---|---|
| **ألوان/شعارات العلامة** | متغيرات SCSS، أصول ثابتة | `projects/<product>/assets/` | 🟢 آمن |
| **القوالب** | قوالب المكونات والتخطيطات | `projects/<product>/assets/templates/` | 🟢 آمن |
| **Wagtail StreamFields** | تعريفات الكتل وصفحات النماذج | `backend/apps/pages/` | 🟡 قابل للتوسيع |
| **إعدادات Django** | إعداد الموقع والتطبيقات | `backend/settings.py` أو `projects/precis/configs/` | 🟡 إعداد فقط |
| **URLs/التوجيه** | تسجيل المسارات | `backend/urls.py` | 🟡 قابل للتوسيع |
| **مكونات django-fusion** | قوالب وسلوك المكونات | `libs/django-fusion/` | 🔵 مستوى القالب |
| **مخطط قاعدة البيانات** | النماذج والترحيلات | `backend/apps/*/models.py` | 🔴 أساسي — يحتاج ترحيلات |
| **نظام المصادقة** | محوّلات Allauth | `backend/apps/auth/` | 🟡 قائم على المحولات |
| **البنية التحتية** | الوكيل، Docker، Compose | `application/` | 🔴 بنية تحتية |
| **أدوات البناء** | Webpack، pnpm، Cargo | Makefile الخاص بالمنتج | 🟡 إعداد فقط |

### دليل إعداد المثيل

```bash
git clone --recurse-submodules <repo-url>
cd structa.cloud
uv sync

# Precis LMS
cd projects/structa.cloud/backend
make check && make migrate && make seed

# Precis Landing
cd projects/precis/precis-landing
just install && make backend-migrate && make backend-seed

# Loop-CRM
cd projects/loop-crm/backend
make check && make migrate && make test

# Formint Cloud
cd projects/formints/formint-cloud
just install && make migrate

# Formint Community
cd projects/formints/formint-community
pnpm install && pnpm tauri dev

# Syntara
cd projects/syntara
python manage.py migrate
```

### تشغيل خوادم التطوير

```bash
# Precis Landing (واجهة + خلفية)
cd projects/precis/precis-landing
make dev                     # واجهة Astro
make backend-dev             # خلفية Django

# Loop-CRM
cd projects/loop-crm
make dev                     # Django + Astro + worker

# Formint Professional
cd projects/formints/formint-pro
make env                     # خلفية + واجهة

# Formint Cloud
cd projects/formints/formint-cloud
make dev-backend
make dev-frontend
```

### تشغيل الاختبارات

```bash
# لكل منتج
cd projects/structa.cloud/backend && make test
cd projects/precis/precis-landing && make backend-test
cd projects/loop-crm/backend && make test
cd projects/formints/formint-cloud && make test

# المكتبة
cd libs/django-fusion && uv run pytest

# موزّع مساحة العمل
cd projects && make test WEBSITE=loop-crm
cd projects && make check WEBSITE=structa.cloud
```

---

## مرجع سريع لهجرة الأسماء

| الاسم القديم | الاسم الحالي | المسار الحالي | ملاحظات |
|---|---|---|---|
| `precis-lms` / `lms` | Precis LMS (اسم بديل) | `projects/structa.cloud/` | اسم بديل للموزّع `WEBSITE=structa.cloud` |
| `precis-landing` | Precis Landing | `projects/precis/precis-landing/` | `WEBSITE=precis-landing` |
| `precis-ctc` / `ctc` | CTC Research | `projects/precis/precis-ctc/` | `WEBSITE=precis-ctc` |
| `cms-fusion` | دُمج | — | انقسم إلى Precis + Precis Landing |
| `portfolio` / `VResume` | دُمج في Precis | `projects/structa.cloud/` | دُمج منشئ السيرة |
| `cypercloud` | Syntara | `projects/syntara/` | اسم التشغيل محفوظ |
| `pos-mini` / `forge-pos` / `formintA` / `formint-community` | Formint Community | `projects/formints/formint-community/` | إصدار offline-first |
| `pos-solo` / `pos-full` / `formint` / `formint-pro` | Formint Professional | `projects/formints/formint-pro/` | إصدارات مدمجة |
| `pos-cloud` / `formintB` / `formint-cloud` | Formint Cloud | `projects/formints/formint-cloud/` | السيد السحابي |
| `pos-client` / `formintC` / `formint-client` | Formint Client | `projects/formints/formint-client/` | |
| `core/` | `projects/` | `projects/` | أُعيدت التسمية 2026 |
| `core/libs/` | `libs/` | `libs/` | نُقلت إلى جذر المستودع |
| `core/configs/` | `projects/precis/configs/` | `projects/precis/configs/` | إعدادات Django المشتركة |

---

## Remarks & Notes

- **LMS/التسويق/البحث مجموعة واحدة:** `projects/precis/` تضم `precis-main/`
  و`precis-landing/` و`precis-ctc/`، وإعدادات Django المشتركة في
  `projects/precis/configs/`. الهوية التشغيلية ثابتة — استخدم `WEBSITE=structa.cloud`
  أو `WEBSITE=precis-landing` أو `WEBSITE=precis-ctc` واترك `projects/Makefile`
  يحلّ مسار نظام الملفات.
- **إصدارات POS تستخدم أسماء حالية صريحة:** `formint-community/`,
  `formint-standard/`, `formint-pro/`, `formint-cloud/`, `formint-client/`
  تحت `projects/formints/`. الأسماء التاريخية أسماء بديلة فقط — لا تضف كوداً جديداً تحتها.
- **Loop-CRM أحادي متحد خاص به** في `projects/loop-crm/`.
- **استخدم الموزّع لا المسارات المرمزة:** `cd projects && make check WEBSITE=loop-crm`
  بدلاً من `cd` المباشر، حتى يبقى `SITE`/`PROJECT_DIR` مصدر الحقيقة الوحيد.
- **مصدر واحد للحقيقة لكل مسار** — حدّث `projects/Makefile` و`AGENTS.md`
  و`docs/project-structure.md` معاً عند إعادة تسمية مجلد.
- النسخة الإنجليزية الكاملة: [`/docs/en/project-structure`](/docs/en/project-structure).
