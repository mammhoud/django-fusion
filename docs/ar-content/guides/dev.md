---
title: دليل تطوير POS
description: كيفية تطوير وبناء وتصحيح تطبيق POS لسطح المكتب — Rust/Tauri وReact وSidecar.
navigation:
  title: تطوير POS
  icon: i-lucide-code-2
---

# دليل تطوير POS

> **مرتبط:** `rust/`, `typescript/`, `server/`, `databases/`, `tests/`
> **الوسوم:** #development #pos #tauri #react #rust #sidecar #workflow

كيفية تطوير وبناء وتصحيح تطبيق POS لسطح المكتب.

---

## نظرة على البنية

```
┌──────────────────────────────────────────────────┐
│                 تطبيق POS لسطح المكتب              │
│                                                  │
│  ┌──────────────────┐    ┌──────────────────────┐│
│  │  React (Vite)    │    │  خلفية Rust/Tauri    ││
│  │  src/pages/*.tsx  │◄──►│  src-tauri/src/      ││
│  │  src/components/  │    │  operations/*.rs     ││
│  └────────┬─────────┘    └──────────┬───────────┘│
│           │                         │             │
│           │  HTTP/WS                │  Diesel ORM │
│           ▼                         ▼             │
│  ┌──────────────────┐    ┌──────────────────────┐│
│  │  Sidecar (Sanic) │◄──►│  SQLite (restaurant.db)││
│  └──────────────────┘    └──────────────────────┘│
└──────────────────────────────────────────────────┘
```

> 💡 **نصيحة:** الـ sidecar عملية Python/Sanic تُطلقها Rust. توفر الدردشة
> والتذاكر وواجهات البيانات التي تستهلكها الواجهة عبر HTTP/WebSocket.

---

## سير عمل التطوير

### 1. ابدأ التطوير

```bash
cd projects/pos

# طرفية 1: خادم Vite
pnpm dev

# طرفية 2: تطوير Tauri (يبني Rust ويفتح نافذة التطبيق)
pnpm tauri dev
```

### 2. فحص TypeScript

```bash
npx tsc --noEmit
```

### 3. فحص بناء Rust

```bash
cd src-tauri
cargo check
```

### 4. تشغيل الاختبارات

```bash
# الواجهة
pnpm vitest run

# الخلفية (تسلسلي — اختبارات متغيرات البيئة تحتاج هذا)
cd src-tauri && cargo test -- --test-threads=1
```

> ⚠️ **تحذير:** اختبارات متغيرات البيئة في Rust تتطلب `--test-threads=1` لأنها
> تعدّل البيئة العامة. التشغيل المتوازي يسبب حالات سباق.

---

## تشريح المشروع

### الواجهة (`src/`)

| المجلد | الغرض | قابل للتخصيص؟ |
|--------|-------|:---:|
| `api/` | عميل HTTP + WebSocket للـ sidecar | 🟡 توسعة |
| `components/` | مكونات واجهة قابلة لإعادة الاستخدام | 🟢 نعم |
| `contexts/` | مزوّدو Auth وTheme وLanguage | 🔴 لا |
| `hooks/` | خطافات React مخصصة | 🟢 نعم |
| `i18n/` | ملفات ترجمة JSON (en/fr/ar) | 🟢 نعم |
| `pages/` | مكونات صفحات مستوى المسار | 🟢 نعم |
| `styles/` | SCSS (أساسي، مكونات، أدوات) | 🟢 نعم |
| `utils/` | تصدير PDF، تصدير CSV | 🟢 نعم |

### الخلفية (`src-tauri/src/`)

| الوحدة | تغطي | قابل للتخصيص؟ |
|--------|-------|:---:|
| `db/mod.rs` | الاتصال والترحيلات وحل المسار | 🔴 لا |
| `db/models.rs` | كل بنى Rust (أكثر من 50 نوعاً) | 🔴 لا |
| `db/schema.rs` | تعريفات جداول Diesel | 🔴 لا (مولّد تلقائياً) |
| `operations/auth.rs` | تسجيل الدخول والمستخدم الفائق وتجزئة كلمة المرور | 🔴 لا |
| `operations/products.rs` | CRUD المنتجات | 🟢 نعم |
| `operations/sales.rs` | CRUD المبيعات + البنود | 🟢 نعم |
| `operations/categories.rs` | CRUD الفئات | 🟢 نعم |
| `operations/inventory_transactions.rs` | حركات المخزون | 🟢 نعم |
| `operations/ingredients.rs` | CRUD المكونات | 🟢 نعم |
| `operations/recipes.rs` | CRUD الوصفات والمكونات | 🟢 نعم |
| `operations/employees.rs` | CRUD الموظفين | 🟢 نعم |
| `operations/customers.rs` | CRUD العملاء + الولاء | 🟢 نعم |
| `operations/suppliers.rs` | CRUD الموردين | 🟢 نعم |
| `operations/analytics.rs` | تحليلات لوحة المعلومات | 🟢 نعم |
| `operations/sidecar.rs` | دورة حياة عملية الـ sidecar | 🔴 لا |
| `operations/settings.rs` | CRUD الإعدادات | 🟢 نعم |
| `operations/roles.rs` | أدوار RBAC | 🟢 نعم |
| `operations/transactions.rs` | المعاملات المالية | 🟢 نعم |
| `operations/tax_reports.rs` | تقارير الضرائب | 🟢 نعم |
| `operations/payrolls.rs` | إدارة الرواتب | 🟢 نعم |
| `operations/kitchen_tickets.rs` | تذاكر عرض المطبخ | 🟢 نعم |
| `operations/purchase_orders.rs` | أوامر الشراء + البنود | 🟢 نعم |
| `operations/receipt_templates.rs` | CRUD قوالب الإيصالات | 🟢 نعم |
| `operations/reports.rs` | بيانات وصفية للتقارير | 🟢 نعم |
| `operations/dump.rs` | تصدير البيانات (JSON dump) | 🟢 نعم |
| `email.rs` | إرسال البريد SMTP | 🟢 نعم |
| `bin/seed.rs` | باذر قاعدة البيانات | 🟢 نعم |

---

## تطوير الـ Sidecar

```bash
cd projects/pos/sidecar
pip install -r requirements.txt

# تشغيل مستقل مع الوصول لقاعدة البيانات
python server.py --db ../restaurant.db --port 8765

# اختبار النقاط النهائية
curl http://127.0.0.1:8765/health
curl http://127.0.0.1:8765/api/sales
```

> 💡 **نصيحة:** عند إضافة نقطة نهاية API جديدة للـ sidecar، أضف أيضاً عميل
> TypeScript المقابل في `src/api/`.

---

## إضافة ميزة جديدة

### 1. عملية Rust

```rust
// projects/pos/src-tauri/src/operations/my_feature.rs
pub fn my_operation(db_path: &PathBuf) -> Result<MyType, String> {
    let conn = &mut open_conn(db_path)?;
    // ... استعلام Diesel ...
}
```

### 2. أمر Tauri

```rust
// projects/pos/src-tauri/src/lib.rs
#[tauri::command]
fn my_command(state: tauri::State<AppState>) -> Result<MyType, String> {
    let db_path = &state.db_path;
    operations::my_feature::my_operation(db_path)
}
```

### 3. صفحة TypeScript

```tsx
// projects/pos/src/pages/MyFeature.tsx
import { invoke } from '@tauri-apps/api/core';

export default function MyFeature() {
  const data = await invoke<MyType>('my_command');
  // ... عرض ...
}
```

> 💡 **نصيحة:** اتبع النمط: عملية Rust ← أمر Tauri ← صفحة TypeScript. كل طبقة
> قابلة للاختبار بشكل مستقل.

## Remarks & Notes

- ملاحظة: الـ sidecar القديم (Robyn/Sanic) أُزيل في نموذج الإصدارات الحالي؛
  المسارات أعلاه تاريخية للمرجع. الوثائق المعيارية الحالية في
  [`projects/formints/docs/`](/docs/en/pos).
- النسخة الإنجليزية الكاملة: [`/docs/en/guides/03-dev`](/docs/en/guides/03-dev).
