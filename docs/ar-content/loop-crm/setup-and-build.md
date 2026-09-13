---
title: إعداد وبناء Loop-CRM
description: مؤشر إلى دليل الإعداد والبناء المعياري في مستودع المنتج مع مرجع سريع للأوامر.
navigation:
  title: الإعداد والبناء
  icon: i-lucide-hammer
---

# إعداد وبناء Loop-CRM

يوجد دليل الإعداد خطوة بخطوة المعياري في مستودع المنتج:

> [**`projects/loop-crm/docs/SETUP_AND_BUILD.md`**](../../../projects/loop-crm/docs/SETUP_AND_BUILD.md)

مرجع سريع:

```bash
cd projects/loop-crm
make dev              # Astro frontend dev server
make backend-dev      # Django dev server
make backend-migrate  # apply migrations
make backend-seed     # seed demo workspace (demo@loop.dev / demo-pass-123)
make check            # frontend typecheck
make backend-check    # Django system checks
```

يتطلّب `uv sync` في جذر المستودع لتبعيات Python، و`npm install` داخل
`projects/loop-crm/frontend` لغلاف Astro. كما تحتاج أهداف Nx (`make nx-check`)
إلى `npm install` في الجذر أيضاً.

انظر [فهرس Loop-CRM](./README.md) لمرجع الأوامر الكامل وتكوين متغيرات البيئة.

## ملاحظات وإرشادات

- هذه الصفحة مؤشر فقط — حرِّر `SETUP_AND_BUILD.md` في مستودع المنتج، لا هنا.

<!-- AI-generated: review needed -->
