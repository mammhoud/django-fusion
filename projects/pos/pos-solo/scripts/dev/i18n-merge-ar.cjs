#!/usr/bin/env node
// Idempotent: adds Modern Standard Arabic translations for the enterprise-module
// UI keys that were missing in src/i18n/ar.json. Refuses to overwrite existing
// keys so a human translator can fix collisions manually.
//
// Usage:
//   node scripts/i18n-merge-ar.cjs [path-to-ar.json]
//
// Defaults to ./src/i18n/ar.json (relative to CWD).
//
// Conventions used (documented in docs/i18n-gaps.md):
//   • Titles   → plural form (العملاء, الموردون, الأدوار, ...).
//   • Buttons  → إضافة + indefinite singular noun (إضافة عميل, إضافة مورد).
//   • Sort     → الاسم (أ→ي) / الاسم (ي→أ) — anchored to productManager.sortNameAsc
//                precedent already in src/i18n/ar.json.
//   • RBAC     → الصلاحيات (NOT الأذونات; صلاحيات is the enterprise convention).
//   • Body     → المحتوى (NOT الجسم; جسم reads as a biological body).
//   • Overtime → ساعات إضافية (NOT ساعات العمل الإضافي; the latter reads awkwardly).
//   • Statuses → participle phrases (قيد الانتظار, قيد التحضير, جاهز, مُسلَّم).
//   • Placeholders end with U+2026 `…`.

const fs = require('fs');
const path = require('path');

const TARGET = process.argv[2] || path.join(process.cwd(), 'src', 'i18n', 'ar.json');
const ar = JSON.parse(fs.readFileSync(TARGET, 'utf8'));

const translations = {
  nav: {
    customers: 'العملاء',
    suppliers: 'الموردون',
    kitchen: 'شاشة المطبخ',
    schedule: 'الجدول الزمني',
    payroll: 'الرواتب',
    receiptTemplates: 'قوالب الإيصالات',
    taxReports: 'التقارير الضريبية',
    roles: 'الأدوار',
  },
  customers: {
    title: 'العملاء',
    addCustomer: 'إضافة عميل',
    name: 'الاسم',
    phone: 'الهاتف',
    email: 'البريد الإلكتروني',
    notes: 'ملاحظات',
    points: 'نقاط الولاء',
    noCustomers:
      'لا يوجد عملاء بعد. أضف عميلك الأول للبدء.',
    searchPlaceholder: 'بحث بالاسم، رقم الهاتف، أو البريد الإلكتروني…',
  },
  suppliers: {
    title: 'الموردون',
    addSupplier: 'إضافة مورد',
    name: 'الاسم',
    contactName: 'اسم جهة الاتصال',
    phone: 'الهاتف',
    email: 'البريد الإلكتروني',
    address: 'العنوان',
    taxId: 'الرقم الضريبي',
    paymentTerms: 'شروط الدفع',
    noSuppliers: 'لا يوجد موردون بعد.',
    searchPlaceholder: 'بحث عن موردين…',
    sortBy: 'ترتيب حسب',
    sortNewest: 'الأحدث',
    sortNameAsc: 'الاسم (أ→ي)',
    sortNameDesc: 'الاسم (ي→أ)',
  },
  kitchen: {
    title: 'شاشة المطبخ',
    ticket: 'تذكرة',
    allTickets: 'جميع التذاكر',
    pending: 'قيد الانتظار',
    preparing: 'قيد التحضير',
    ready: 'جاهز',
    delivered: 'مُسلَّم',
    startPreparing: 'بدء التحضير',
    markReady: 'تحديد كجاهز',
    deliver: 'تسليم',
    noTickets: 'لا توجد تذاكر حالياً.',
    searchPlaceholder: 'بحث برقم التذكرة أو الملاحظة…',
    statusFilter: 'الحالة',
  },
  schedule: {
    title: 'الجدول الزمني',
    addShift: 'إضافة وردية',
    selectEmployee: 'اختر الموظف',
    notes: 'ملاحظات',
    noShifts: 'لا توجد ورديات مجدولة.',
  },
  payroll: {
    title: 'الرواتب',
    addPayroll: 'إضافة راتب',
    selectEmployee: 'اختر الموظف',
    regularHours: 'الساعات العادية',
    overtimeHours: 'الساعات الإضافية',
    totalPay: 'إجمالي الدفع',
    noPayrolls: 'لا توجد سجلات رواتب بعد.',
  },
  receiptTemplates: {
    title: 'قوالب الإيصالات',
    addTemplate: 'إضافة قالب',
    name: 'الاسم',
    body: 'المحتوى',
    setAsDefault: 'تعيين كافتراضي',
    default: 'افتراضي',
    noTemplates: 'لا توجد قوالب إيصالات بعد.',
    searchPlaceholder: 'بحث عن قوالب…',
    sortBy: 'ترتيب حسب',
    sortDefaultFirst: 'الافتراضي أولاً',
    sortNameAsc: 'الاسم (أ→ي)',
    sortNameDesc: 'الاسم (ي→أ)',
    sortNewest: 'الأحدث',
  },
  taxReports: {
    title: 'التقارير الضريبية',
    addReport: 'إضافة تقرير',
    totalSales: 'إجمالي المبيعات',
    totalTax: 'إجمالي الضريبة',
    transactionCount: 'عدد المعاملات',
    transactions: 'المعاملات',
    noReports: 'لا توجد تقارير ضريبية بعد.',
    searchPlaceholder: 'بحث عن تقارير…',
    sortBy: 'ترتيب حسب',
    sortNewest: 'الأحدث',
    sortOldest: 'الأقدم',
    sortSalesDesc: 'المبيعات (من الأعلى للأقل)',
    sortSalesAsc: 'المبيعات (من الأقل للأعلى)',
  },
  roles: {
    title: 'الأدوار',
    addRole: 'إضافة دور',
    name: 'الاسم',
    permissions: 'الصلاحيات',
    noRoles: 'لم يتم تحديد أدوار بعد.',
    searchPlaceholder: 'بحث عن أدوار…',
    sortBy: 'ترتيب حسب',
    sortNewest: 'الأحدث',
    sortNameAsc: 'الاسم (أ→ي)',
    sortNameDesc: 'الاسم (ي→أ)',
  },
};

// Type-safe deep merge with translator-friendly overwrite protection:
//   • Plain object ← plain object: recursively merge leaves, never clobber.
//   • Missing target leaf: insert the source value (deep-cloned if object/array).
//   • Existing target leaf (string/number/boolean): leave alone — owned by a
//     human translator who may need to fix it manually.
//   • Existing target leaf is an array/object: NEVER clobber a non-object leaf
//     into a fresh {}; that would silently wipe a human-edited value. The
//     merge only proceeds when the existing slot is a plain object.
function deepMerge(target, source) {
  for (const k of Object.keys(source)) {
    const sv = source[k];
    const tv = target[k];
    const svObj = sv && typeof sv === 'object' && !Array.isArray(sv);
    if (svObj) {
      const tvObj = tv && typeof tv === 'object' && !Array.isArray(tv);
      if (tvObj) {
        deepMerge(tv, sv);
      } else if (tv === undefined) {
        target[k] = JSON.parse(JSON.stringify(sv)); // deep-clone nested object
      }
      // else: existing leaf is a non-object (string/number/array/etc) — leave it
    } else {
      if (tv === undefined) target[k] = sv; // never overwrite — translator-owned
    }
  }
}

const before = JSON.stringify(ar);
deepMerge(ar, translations);
const after = JSON.stringify(ar);

if (before === after) {
  console.log(`✓ ${TARGET}: already contains the 93 enterprise-module keys — no change needed`);
} else {
  fs.writeFileSync(TARGET, JSON.stringify(ar, null, 2) + '\n');
  console.log(`✓ ${TARGET}: merged 93 enterprise-module keys (idempotent re-runs are no-ops).`);
}
