---
title: Formint POS
description: نقاط بيع مطاعم متعددة الإصدارات — Community، Standard، Pro، Cloud، Client. Tauri + React + Rust + Django.
navigation:
  title: Formint POS
  icon: i-lucide-credit-card
---

# 💳 Formint POS — نقاط بيع متعددة الإصدارات

> **أسماء ذات صلة:** `pos`، `نظام نقاط البيع`، `تطبيق سطح المكتب`، `Tauri`، `React`، `Rust`، `SQLite`، `نقطة-بيع`، `offline-first`، `i18n`
> **الوسوم:** #site #pos #desktop #tauri #rust #react #offline

**المسار المعياري:** `projects/formints/`  
**المكدس:** Tauri 2 + React 19 + Rust (Diesel ORM) + SQLite (+ Django لـ Pro/Cloud)  
**المنصات:** Windows، macOS، Linux، Android، iOS

---

## نموذج الإصدار الحالي (21 آب 2026)

- **Community** ✅ مكتمل — تاوري + React + Rust، SQLite محلي
- **Standard** ✅ مكتمل — Community + ميزات إضافية
- **Pro** 🔄 قيد التطوير — Django backend + مزامنة سحابية
- **Cloud** 📋 مخطط — Django backend متعدد المستأجرين
- **Client** ✅ مكتمل — Vue 3 + Tauri، عميل POS خفيف

---

## المكدس التقني

| الطبقة | التقنية |
|----------|----------|
| الواجهة الأمامية (السطح المكتب) | Tauri 2 + React 19 + TypeScript |
| الواجهة الخلفية (Rust) | Diesel ORM + SQLite |
| الواجهة الخلفية (Pro/Cloud) | Django 4.2+ + Channels |
| الواجهة الأمامية (Client) | Vue 3 + Tauri |
| التزامن | الخلفية + SQLite (محلي) / Django (سحابي) |

---

## الأدلة

- [البنية المعمارية](/docs/ar/pos/ARCHITECTURE) — مخطط النظام، حدود الإصدارات
- [الإصدارات](/docs/ar/pos/editions) — مصفوفة ميزات Community/Standard/Pro/Cloud/Client
- [الواجهة الخلفية (Rust)](/docs/ar/pos/backend) — auth، database، operations، seed
- [الواجهة الأمامية (React)](/docs/ar/pos/frontend) — TypeScript، components، contexts، hooks
- [Sidecar (Django)](/docs/ar/pos/sidecar) — django-bolt، ORM، network، websocket
- [البنية التحتية](/docs/ar/pos/infrastructure) — النشر، Docker، CI/CD
- [حالات الاستخدام](/docs/ar/pos/use-cases) — سيناريوهات المطاعم، التخصيص

---

## البدء السريع

```bash
cd projects/formints/formint-community
pnpm dev          # Terminal 1: Vite
pnpm tauri dev    # Terminal 2: Tauri dev
```

---

## ذات الصلة

- [البنية المعمارية](/docs/ar/pos/ARCHITECTURE)
- [الإصدارات](/docs/ar/pos/editions)
- [الواجهة الخلفية](/docs/ar/pos/backend)
- [الواجهة الأمامية](/docs/ar/pos/frontend)

<!-- AI-generated: review needed -->
