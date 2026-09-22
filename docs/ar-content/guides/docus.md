---
title: دليل تنفيذ Docus
description: كيف تُؤلف وثائق Structa Cloud وتُثرى وتُتحقق وتُبنى وتُنشر.
navigation:
  title: تنفيذ Docus
  icon: i-lucide-book-marked
---

# دليل تنفيذ Docus

<!-- AI-generated: review needed -->

هذا الدليل هو المرجع التشغيلي المعياري لتطبيق Docus. الصفحات المؤلفة تعيش
تحت `docs/**/*.md` و`docs/**/*.mdx`؛ تطبيق Docus في جذر `docs/` يولّدها ويخدمها.
لا تنشئ نسخة منشورة ثانية داخل `docs/content/`.

## حدود المصدر والمولّد

```text
docs/**/*.md أو *.mdx
        │ مصدر مؤلف
        ▼
docs/scripts/prepare-content.mjs
        │ يضيف بيانات وصفية وينسخ المصادر العربية
        ▼
docs/content/en/ وdocs/content/ar/
        │ محتوى مولّد مهمل
        ▼
خادم Nuxt/Docus SSR
        │
shared-proxy + Traefik
        ├── /docs/ على مضيف التوثيق المشترك
        └── docs.structa.cloud/
```

`docs/content/` و`.nuxt/` و`.output/` و`dist/` و`node_modules/` نواتج بناء.
إذا كان محتواها خاطئاً، أصلح Markdown المؤلف أو سكربت الإعداد. `docs/index.html`
في الجذر إعادة توجيه توافق فقط.

## بيانات وصفية لكائن المستند

يجب أن تستخدم الصفحات المؤلفة الجديدة هذا الشكل من frontmatter:

```yaml
object:
  type: guide | architecture | runbook | api | decision | reference
  id: stable.document.identifier
attributes:
  source_path: guides/example.md
  canonical_route: /docs/en/guides/example
  source_of_truth: repository-markdown
  owner: product-or-team
  status: maintained | proposed | deprecated
tags:
  - architecture
  - product-or-system
links:
  - label: Related document
    to: /docs/en/guides/00-project-awareness
    icon: i-lucide-link
```

## الأوامر المحلية

من جذر المستودع:

```bash
cd docs
make check
npm run prepare-content
npm run validate-content
make build
make build-static
make serve
make preview
```

استخدم `make check` قبل البناء. يتحقق من تكوين Nuxt ومصادر اللغة وبيانات
الوثائق المولّدة وروابط Docus الأصلية. البناء الإنتاجي هو بناء خادم SSR؛
التصدير الثابت اختياري وقد يكون أبطأ لأنه يعرض كل مسار مطلوب.

## المسارات واللغات المحلية

- الإنجليزية: `http://localhost:3000/docs/en/`
- العربية RTL: `http://localhost:3000/docs/ar/`
- إعادة توجيه توافق الجذر: `docs/index.html`

## عقد النشر

```text
Dockerfile: docs/Dockerfile
التطبيق: docs/ (جذر التطبيق)
الحاوية: docus:3000
الوكيل: application/proxy/configs/traefik/dynamic/docs.yml
Nginx: application/tools/nginx/default.conf.template
```

الصورة تنسخ شجرة `docs/` الكاملة لأن سكربت الإعداد يمشي شجرة Markdown المؤلفة
الشقيقة. ثم تشغّل `npm run build` وتطلق `.output/server/index.mjs`.

## قواعد الربط وإزالة التكرار

1. أضف أو عدّل صفحة Markdown المعيارية تحت `docs/`.
2. أضف بيانات وصفية frontmatter وقسماً أخيراً `## Remarks & Notes`.
3. اربط بصفحة أو مسار مصدر موجود بدلاً من تكرار محتواه.
4. شغّل `make -C docs check` لإعادة توليد شجرة العرض المهملة.
5. لا تلتزم أبداً أو تعدّل محتوى Docus المولّد يدوياً.

## Remarks & Notes

- تطبيق Docus يعيش في جذر `docs/`؛ هذه الصفحة هي دليل التوثيق المنشور.
- مسارات Docus أحرف صغيرة حتى لو استخدم اسم الملف المصدر أحرفاً كبيرة مثل `ARCHITECTURE.md`.
- النسخة العربية الكاملة: [`/docs/ar/guides/config-cascade`](/docs/ar/guides/config-cascade) — النسخة الإنجليزية: [`/docs/en/guides/09-docus`](/docs/en/guides/09-docus).
