---
title: POS — تطبيق نقاط البيع لسطح المكتب
description: فهرس توثيق POS — إصدارات Formint، الحالة، البدء السريع، والمصادر المعيارية.
navigation:
  title: POS (Formints)
  icon: i-lucide-shopping-cart
---

# POS — تطبيق نقاط البيع لسطح المكتب

> **أسماء مرتبطة:** `pos`, `نظام نقاط البيع`, `تطبيق سطح مكتب`, `Tauri`, `React`, `Rust`, `SQLite`, `offline-first`, `i18n`
> **الوسوم:** #site #pos #desktop #tauri #rust #react #offline

**المسار المعياري:** `projects/formints/` \
**التقنية:** Tauri 2 + React 19 + Rust (Diesel ORM) + SQLite (+ Django لـ Pro/Cloud) \
**المنصات:** Windows, macOS, Linux, Android, iOS

> **نموذج الإصدارات الحالي (21 أغسطس 2026):** Community ✅ منجز · Standard ✅
> منجز · Pro ✅ منجز · Cloud 🟡 مرحلة التجربة · pos-client 🔵 تطوير. نموذج
> الإصدارات الثلاثة القديم (Minimal/Solo/Full) مع sidecar Robyn أُزيل؛ الصفحات
> أدناه التي ما زالت تصفه محفوظة للتاريخ فقط.

---

## نظرة عامة

POS (الآن **Formints**) عائلة نقاط بيع حديثة لسطح المكتب تعمل دون اتصال
للمطاعم والمقاهي وخدمات الطعام. إصدارات سطح المكتب (Community, Standard)
تعمل دون اتصال بالكامل — Tauri `invoke` → Rust/Diesel → SQLite محلي، بلا
خادم. إصدارا Pro وCloud يضيفان خلفية Django (django-fusion, Unfold admin,
مزامنة Channels) وسيداً مستضافاً متعدد المستأجرين.

## الإصدارات في لمحة

| الإصدار | المجلد | الخلفية | الحالة |
|---------|--------|---------|--------|
| **Community** | `formint-community/` | Rust/Diesel + SQLite (بلا خادم) | ✅ منجز |
| **Standard** | `formint-standard/` | Rust/Diesel + SQLite (+ sidecar Django اختياري) | ✅ منجز |
| **Pro** | `formint-pro/` | Django + django-fusion + Unfold (مطلوب) | ✅ منجز |
| **Cloud** | `formint-cloud/` | Django (متعدد المستأجرين، Channels) — سيد مستضاف | 🟡 تجربة |
| **pos-client** | `formint-client/` | Vue 3 + Tauri + خلفية متجر Django | 🔵 تطوير |
| **SDK JS/TS** | `packages/formints-client/` | TypeScript (`@formints/client`) | ✅ منجز |

## البدء السريع (الحالي)

```bash
# Community / Standard (سطح مكتب دون اتصال)
cd projects/formints/formint-community    # أو formint-standard
pnpm install && cd src-tauri && cargo fetch && cd ..
pnpm dev            # خادم Vite على localhost:1420

# Pro (حزمة مدمجة — خلفية + ويب + سطح مكتب)
cd projects/formints/formint-pro
just install && make seed && make env    # خلفية :8767 + واجهة :4321

# Cloud (سيد مستضاف)
cd projects/formints/formint-cloud
just install && make migrate
make dev-backend && make dev-api && make dev-frontend

# pos-client (سطح مكتب Vue 3)
cd projects/formints/formint-client && make dev
```

## المصادر المعيارية

| الموضوع | الوثيقة المعيارية |
|---------|-------------------|
| خطط الإصدارات + لوحة الإنجاز | [`docs/plans/editions/README.md`](/docs/en/plans) |
| مصفوفة الميزات + دليل المشتري | [`docs/plans/editions/comparison.md`](/docs/en/plans) |
| مكونات وميزات كل إصدار | [`projects/formints/docs/`](/docs/en/pos) |
| الإعداد والبناء لكل إصدار | [`projects/formints/docs/GETTING_STARTED.md`](/docs/en/pos) |
| أوامر CLI / Makefile | [`projects/formints/docs/COMMANDS.md`](/docs/en/pos) |
| سجل التغييرات | [`changelog.md`](/docs/en/pos) |
| الاستراتيجية (خاصة) 🔒 | [`../startup/formints.md`](/docs/en/startup/formints) |

## Remarks

| # | ملاحظة |
|---|--------|
| ⚠️ | يتطلب POS **سلسلة أدوات Rust** + Tauri CLI (`cargo install tauri-cli`) |
| ⚠️ | المصادقة اختيارية — اضبط عبر `SUPERUSER_EMAIL` + `SUPERUSER_PASSWORD` |
| 🌐 | i18n في Community: الإنجليزية والفرنسية والعربية · pos-client: الإنجليزية والصينية |
| ⛔ | **sidecar Robyn/Sanic أُزيل** — راجع `sidecar/README.md` (مؤرشف) |
| 📁 | صفحات الإصدارات المتقاعدة (Minimal/Solo/Full, sidecar, Sanic) مؤرشفة |

## Remarks & Notes

- الوثائق المعيارية للمنتج تعيش في [`projects/formints/docs/`](/docs/en/pos).
- النسخة الإنجليزية الكاملة: [`/docs/en/pos`](/docs/en/pos).
