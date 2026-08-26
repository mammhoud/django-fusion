---
title: أوامر Structa Cloud
description: كتالوج الأوامر الموحد، سلسلة التفويض، وتسلسل النشر.
navigation:
  title: الأوامر
  icon: i-lucide-terminal
---

# 🛠️ أوامر Structa Cloud — مرجع موحد

> كتالوج كامل للأوامر، تسمية الأفعال الموحدة، سلسلة التفويض، وتسلسل النشر المتتالي.

---

## التسلسل الهرمي للأوامر

```
جذر Justfile (واجهة المستخدم)
  ├── just install          # مزامنة المساحة الكاملة (Python + JS + Formints + Docs)
  ├── just check            # nx run-many check --all
  ├── just test             # nx run-many test --all
  ├── just deploy           # نشر كامل (postgres-first)
  ├── just nx <target>      # تفويض لأي هدف Nx
  └── just deploy-*         # نشر الخدمات الفردية

Makefile الجذر (التنفيذ الأساسي)
  ├── make deploy           # النشر الكامل (postgres-first)
  ├── make deploy-databases # PostgreSQL + Redis
  ├── make deploy-proxy     # Traefik
  ├── make deploy-tools     # أدوات الخدمة الذاتية (Blinko، Docus، Affine، Mailpit، Monitoring، Ollama)
  ├── make deploy-app       # تطبيقات المنتجات (Precis، CTC، Syntara، Loop-CRM)
  ├── make cleanup          # تنظيف الحاويات المتوقفة + الصور المعلقة + ذاكرة البناء المؤقتة
  ├── make prune            # الحاويات + الأحجام + الصور
  ├── make status           # حالة النشر
  └── make help             # كتالوج الأوامر الكامل

Makefile المشاريع (موزع موقع الويب)
  ├── make check WEBSITE=precis-main
  ├── make test WEBSITE=precis-main
  ├── make run-dev WEBSITE=precis-landing
  ├── make docker-build WEBSITE=precis-main
  └── make migrate WEBSITE=precis-main
```

---

## تسمية الأفعال الموحدة

| فعل | نطاق |
|-----|-------|
| `install` | مزامنة التبعيات (Python + JS + Rust) |
| `check` | فحوصات اللينت، التايب، Django check |
| `test` | تشغيل مجموعات الاختبار |
| `build` | بناء الإنتاج (الحزم، static، Docker) |
| `deploy` | النشر مع التسلسل |
| `migrate` | هجرات قاعدة البيانات |
| `seed` | بيانات الاختبار/التطوير |
| `dev` | خوادم التطوير (إعادة تحميل ساخنة) |
| `cleanup` | إزالة المتوقف + المعلقة + ذاكرة البناء المؤقتة |
| `prune` | إزالة عنيفة (الحاويات + الأحجام + الصور) |
| `status` | حالة الحاويات/الخدمات |
| `logs` | تتبع السجلات |
| `probe-health` | فحوصات نقطة نهاية الصحة |

---

## تسلسل النشر (postgres-first)

```bash
1. make deploy-databases      # PostgreSQL + Redis
2. make deploy-tools          # Blinko، Docus، Affine، Mailpit، Monitoring، Ollama
3. make deploy-app            # Precis، CTC، Syntara، Loop-CRM
4. make deploy-proxy          # Traefik (إعادة تحميل التوجيه)
5. make probe-health          # التحقق من نقاط نهاية الصحة
```

---

## تفويض Justfile → Makefile

```bash
just deploy           → make deploy
just deploy-docs      → nx run docs:deploy
just check            → nx run-many check --all
just nx run docs:build → node_modules/.bin/nx run docs:build
```

---

## اختصارات مفيدة

```bash
make probe-health
make cleanup
make status
make deploy
```

## ملاحظات وإرشادات

- `make deploy` يشغل `deploy-preflight` + `preflight-network` تلقائيًا كحراس رخيصين.
- تجاوز الترتيب: `make deploy DEPLOY_ORDER=legacy` (للأنظمة القديمة فقط).
- `make cleanup` يزيل الحاويات المتوقفة + الصور المعلقة + ذاكرة البناء المؤقتة (يحتفظ بالأحجام).
- `make prune` = `prune-containers` + `prune-volumes` + `prune-images` — تدميري.
- لا تشغل `docker compose down --volumes` أو `docker system prune` ضد بيئة مشتركة دون موافقة صريحة.

<!-- AI-generated: review needed -->
