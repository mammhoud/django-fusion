---
title: دليل الوعي بالمشروع والحساب
description: كيفية تحديد موقع وتشغيل والتحقق وتوسيع وتوثيق مستودع Structa Cloud.
navigation:
  title: الوعي بالمشروع
  icon: i-lucide-compass
---

# دليل الوعي بالمشروع والحساب

<!-- AI-generated: review needed -->

هذا هو أقصر مسار موثوق من «أريد تغيير شيء ما» إلى «أعرف أي منتج يملكه، وكيف
يعمل، وكيف أتحقق منه». Structa Cloud مستودع واحد، لكن المنتجات تطبيقات معزولة.
ابدأ بتحديد المالك؛ لا تستنتج الملكية من مسار تاريخي قديم.

## 1. اقرأ المستودع كمخطط

المستودع منظم ككائنات مترابطة بدلاً من تطبيق واحد مسطّح:

```text
workspace
├── projects/                 كائنات المنتجات وإعداد المشروع المشترك
│   ├── precis/               Precis LMS, Precis Landing, CTC Research
│   ├── formints/             إصدارات POS واختبارات POS المشتركة
│   ├── syntara/              بيئة الدردشة/التخصيص بالذكاء الاصطناعي
│   └── loop-crm/             أحادي CRM والجدولة الاجتماعية
├── libs/django-fusion/       كائن الإطار المشترك (git submodule)
├── application/              كائنات البنية التحتية والوكيل
├── tests/                    كائن التحقق عبر المشاريع
└── docs/                     مصدر التوثيق المعياري + تطبيق Docus
```

لكل كائن سمات يجب أن تتفق بين الكود والتوثيق: للمنتج المسار وهوية التشغيل
والتقنية والمالك والمنفذ/النطاق؛ وللخلفية وحدة الإعدادات وجذر URL وقاعدة
البيانات وجذور الوسائط/الملفات الثابتة؛ وللواجهة مدير الحزم ومصدر API وهدف
البناء والأصول الثابتة؛ وللمكتبة المشتركة التزام submodule والاستيرادات
العلنية والاختبارات؛ ولخدمة البنية التحتية خدمة Compose والشبكة والموجّه
ومسار الصحة والحجم.

## 2. الأوامر الأولى: وجّه نفسك قبل التحرير

شغّل هذه الأوامر للقراءة فقط من جذر المستودع:

```bash
pwd
find . -name AGENTS.md -print
git status --short --untracked-files=all
cd projects && make show-config WEBSITE=precis-ctc
```

ثم اقرأ بالترتيب: `AGENTS.md` في الجذر، ثم `projects/AGENTS.md`، ثم أقرب
`AGENTS.md` للمنتج، ثم README وMakefile الخاصين بالمنتج، ثم صفحة التوثيق
المعنية والمستدعين/الاختبارات الحالية.

الهويات المعيارية الحالية للمنتجات:

| هوية التشغيل | المسار المعياري | أسماء التوافق |
|---|---|---|
| `precis-main` | `projects/structa.cloud/` | `precis-lms`, `precis-landing` |
| `precis-landing` | `projects/precis/precis-landing/` | نسخة تشغيل Precis Landing القديمة |
| `precis-ctc` | `projects/precis/precis-ctc/` | `ctc`, `ctc-website`, `ctc-research.com` |
| `syntara` | `projects/syntara/` | `cypercloud` |
| إصدارات Formint | `projects/formints/<edition>/` | أسماء Formint/POS التاريخية |

## 3. مسار الحساب

لطلب ويب، احسب المالك والمسار قبل تغيير الكود:

```text
متصفح / Astro / HTMX / عميل API
        ↓ Host + path
Traefik أو خادم محلي
        ↓ router/service
Django ASGI/WSGI أو خادم Astro
        ↓ middleware
محلِّل URL
        ↓
صفحة Wagtail | مكوّن django-fusion | API | شظية HTMX
        ↓
نموذج/خدمة/استعلام + قالب أو تسلسل JSON
        ↓
HTML | شظية | JSON | تدفق
```

لعملية خلفية:

```text
طلب أو مجدول
        ↓
خدمة Django / actor مهمة
        ↓
وسيط Redis (إنتاج) أو خلفية داخل العملية (تطوير/اختبار)
        ↓
عامل Dramatiq
        ↓
سجل PostgreSQL أو بريد أو عملية وسائط أو تحديث ذاكرة تخزين
```

لبناء واجهة:

```text
مصدر Astro/TypeScript + CSS
        ↓
فحص وبناء محلي للحزمة
        ↓
مخرج ثابت / حزمة خادم
        ↓
صورة Compose أو جذر ملفات ثابتة مثبّت على المضيف
        ↓
Traefik + Nginx/وكيل ثابت
```

## 4. الأوامر المعيارية

### مساحة العمل والتوثيق

```bash
# من جذر المستودع
uv sync
uv run pytest

# تحقق وتوليد مصدر Docus
cd docs
make check
npm run prepare-content
make build             # بناء خادم Nuxt/Docus
make serve             # خادم محلي عند /docs/
```

### موزّع المشاريع

```bash
cd projects
make show-config WEBSITE=structa.cloud
make check WEBSITE=structa.cloud
make test WEBSITE=structa.cloud
make run-dev WEBSITE=precis-ctc
make check WEBSITE=precis-ctc
make test WEBSITE=precis-ctc
```

استخدم الموزّع لاختيار الموقع لأنه يملك أسماء التوافق ويربط هويات التشغيل
بمسارات نظام الملفات الحالية.

### Precis CTC

```bash
cd projects/precis/precis-ctc
make check
make test
make validate-config
make build

cd backend
python manage.py check
python manage.py test
python manage.py prepare_ctc_media --dry-run
```

لا تشغّل الترحيلات أو تحميل الملفات أو `load_data --replace` أو أوامر النشر
ضد بيانات مشتركة/إنتاجية دون موافقة صريحة.

### واجهات Precis ومشاريع POS

```bash
cd projects/structa.cloud/backend && make check && make test
cd projects/precis/precis-landing && make check && make backend-test
cd projects/formints/formint-pro && make check && make test
cd projects/formints/formint-cloud && make check && make test
cd projects/formints/formint-community && npm run check && npm test
cd projects/formints/formint-client && npm run lint
cd libs/django-fusion && uv run pytest
```

أكّد دائماً مدير الحزم المحلي للمشروع قبل التثبيت أو التشغيل.

## 5. كيفية توسيع المخطط بأمان

### سلوك خلفية جديد

1. ابحث عن حدود التطبيق المالك: `models`, `services`, `handlers`, `api`,
   `components`, أو `management`.
2. ابحث عن المسارات والمستدعين والمُسلسِلات والاختبارات الموجودة.
3. أبقِ تنسيق URLs رقيقاً؛ ضع قواعد العمل في خدمة/مدير.
4. استخدم استيرادات `django_fusion.*` المعيارية وأسماء شظايا ثابتة.
5. حدّث وثيقة API/البنية الخاصة بالمنتج وأضف اختباراً مركزاً.

### سلوك واجهة جديد

1. أكّد ما إذا كانت الصفحة Astro أو React/Vue أو سطح Tauri أصلياً.
2. حافظ على عقد render-first/data-API/HTMX الذي يكشفه المنتج.
3. أبقِ أصول المصدر منفصلة عن الحزم المولّدة والملفات الثابتة المجمّعة.
4. شغّل `check` واختباراً مركزاً وبناءً عند الإمكان.
5. اربط الميزة بنقطة نهاية الخلفية وتوثيق المنتج.

### سلوك بنية تحتية جديد

1. حدد خدمة Compose والشبكة والحجم وفحص الصحة والموجّه.
2. حدّث تكوين `application/` المالك ودليل التوجيه وكتيب النشر معاً.
3. تحقق من Compose/YAML دون إيقاف أو إعادة إنشاء الخدمات المشتركة.
4. تعامل مع تقليم الحجم والترحيل الإنتاجي وعمليات الشهادات والنشر كأفعال
   فعّالة تتطلب توجيهاً صريحاً من المستخدم.

## 6. التوثيق كمخطط معرفة بنمط Affine

استخدم Markdown كمصدر واحد وDocus كطبقة العرض/الفهرس. كل مستند جديد يجب أن
يصف:

```yaml
object:
  type: guide | architecture | runbook | api | decision | reference
  id: stable.document.identifier
attributes:
  source_of_truth: repository-markdown
  owner: product-or-team
  status: maintained | proposed | deprecated
  audience: reader description
tags:
  - architecture
  - product-or-system
links:
  - label: Related document
    to: "/docs/en/path/to/document"
    icon: "i-lucide-link"
```

هذه كائنات وسمات وثائق، وليست قاعدة بيانات ثانية. استخدم معرفات مستقرة عند
الإشارة إلى مستند من خطط أو وكلاء أو روابط Docus. فضّل الروابط على تكرار
الشروحات.

## 7. مصدر Docus ونموذج النشر

```text
docs/**/*.md أو *.mdx       محتوى مؤلف معياري
        ↓ prepare-content.mjs
 docs/content/en/           شجرة إنجليزية مولّدة مهملة + بيانات وصفية
 docs/ar-content/           مصدر عربي مؤلف
        ↓ بناء Nuxt/Docus
 .output/server/index.mjs  خدمة توثيق SSR
        ↓ shared-proxy + Traefik
 docs.structa.cloud/       توثيق مضيف الجذر
 media.structa.cloud/docs/ مضيف توثيق بادئة
```

لا تعدّل `docs/content/` أو `.nuxt/` أو `.output/` أو `dist/` أو
`node_modules/`. إذا كان المحتوى المولّد خاطئاً، أصلح Markdown المصدر أو
سكربت الإعداد.

## 8. العمل مع وكيل

أعطِ الوكيل إحداثيات مخطط الكائنات، وليس جملة ميزة فقط:

```text
المالك: projects/precis/precis-ctc/
السطح: خلفية API + واجهة Astro
العقد: /apis/content/media/ و/fragment/pages/<slug>/
البيانات: تفريغ Wagtail + جذر وسائط مشترك
الوثائق: docs/precis-ctc/ وdocs/guides/00-project-awareness.md
الفحوصات: cd projects/precis/precis-ctc/frontend && npm run check
السلامة: لا تحمّل/تستبدل ملفات مشتركة أو تنشر دون موافقة
```

## Remarks & Notes

- `AGENTS.md` في جذر المستودع هو سلطة السلامة؛ هذا الدليل طبقة توجيه وليس بديلاً
  عن التعليمات المحدودة النطاق.
- Markdown في `docs/` معياري. المحتوى المولّد من Docus مهمل عمداً وقابل للاستبدال؛
  حذفه آمن، والتأليف فيه ليس آمناً.
- النسخة الإنجليزية الكاملة: [`/docs/en/guides/00-project-awareness`](/docs/en/guides/00-project-awareness).
