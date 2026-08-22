---
title: نظرة عامة على المستودع
description: خريطة واسعة لمنتجات Structa Cloud والبنية التحتية والأوامر وتدفق البيانات.
navigation:
  title: نظرة عامة
  icon: i-lucide-map
---

# 🏠 نظرة عامة على المستودع — Structa Cloud Monorepo

> نظرة واسعة على بيئة المستودع الكاملة: ما هو، وكيف تترابط أجزاؤه، وكيف تبني وتنشر وتطلق مشاريع جديدة.

<!-- AI-generated: review needed -->

> **التوجيه المعياري:** [`guides/00-project-awareness.md`](/docs/en/guides/00-project-awareness) يشرح مخطط الكائنات وقواعد مصدر الحقيقة والأوامر ونموذج بيانات Docus.

---

## ماذا يحتوي هذا المستودع

مستودع Structa Cloud هو **منصة متعددة المشاريع مبنية على Django + Rust + TypeScript + Astro** تبني وتنشر وتطلق تطبيقات ويب مستقلة وتطبيقات سطح مكتب وخدمات ذكاء اصطناعي من قاعدة كود واحدة.

| الطبقة | التقنية | المشاريع المستخدمة |
|--------|---------|--------------------|
| **الخلفية** | Python 3.11 + Django 5.2 + Wagtail 7.4 | Precis LMS, Precis Landing, Syntara, Formint Cloud |
| **سطح المكتب** | Rust + Tauri 2.x | Formint Community, Formint Professional, Formint Client |
| **الواجهة** | Astro 5 + TypeScript + Vue 3 + React 19 | Precis Landing, إصدارات Formint, Syntara Chat |
| **الذكاء الاصطناعي** | Ollama + متوافق مع OpenAI + MCP | Syntara (CeptorAI) |
| **البنية التحتية** | Docker + Traefik + Nginx + Coder | جميع المشاريع |
| **قاعدة البيانات** | PostgreSQL 16 (إنتاج) / SQLite (تطوير) | جميع مشاريع Django |

---

## مرجع أوامر سريع

### موزّع المشاريع

```bash
cd projects
make check WEBSITE=precis-main         # فحص Precis LMS
make test WEBSITE=precis-main          # اختبار Precis LMS
make run-dev WEBSITE=precis-landing    # خادم Precis Landing للتطوير
make check WEBSITE=precis-ctc          # فحوصات CTC Research
make check WEBSITE=precis-landing
make test WEBSITE=precis-landing
```

### أوامر كل منتج

```bash
# Precis LMS
cd projects/precis/precis-main/backend
make check && make test && make migrate

# Precis Landing
cd projects/precis/precis-landing
just install && make check && make build
make backend-migrate && make backend-check && make backend-test

# Formint Professional
cd projects/formints/formint-pro
just install && make check && make test

# Formint Cloud
cd projects/formints/formint-cloud
just install && make check && make test

# Formint Community
cd projects/formints/formint-community
pnpm install && pnpm tauri dev

# CTC Research
cd projects/precis/precis-ctc
make check && make test

# وثائق Docus
cd docs
make check && make build

# مكتبة django-fusion
cd libs/django-fusion
uv run pytest
```

### نشر Docker

```bash
make deploy            # نشر كامل (قواعد البيانات ← الوسائط ← التطبيقات ← الوكيل)
make deploy-databases  # Postgres + Redis فقط
make deploy-app        # تطبيقات Django فقط
make deploy-proxy      # الوكيل العكسي Traefik
make status            # عرض حالة جميع الحاويات
make logs              # تتبع سجلات جميع الخدمات
```

---

## خريطة المشاريع

| المشروع | المجلد | النوع | المنفذ | التقنية |
|---------|--------|-------|--------|---------|
| **Precis (نظام تعلم + تسويق موحّد)** | `projects/precis/precis-main/` | Astro + Django | الخلفية 8074 · الواجهة 3000 (Docker) | Wagtail + Astro 5 + django-fusion |
| **Precis Landing** | `projects/precis/precis-landing/` | نسخة توافق قديمة | — | مصدر تاريخي؛ وقت التشغيل يُوجّه إلى Precis Main |
| **CTC Research** | `projects/precis/precis-ctc/` | موقع Django | — | Wagtail + django-fusion |
| **Syntara** | `projects/syntara/` | موقع Django | 5073 | محادثة ذكاء اصطناعي + CeptorAI + Ollama |
| **Loop-CRM** | `projects/loop-crm/` | Django + Astro | 8000 | django-fusion + جزر React |
| **Formint Community** | `projects/formints/formint-community/` | Tauri Desktop | — | Rust + React 19 + SQLite |
| **Formint Standard** | `projects/formints/formint-standard/` | Tauri + Astro | — | Tauri + FlyonUI |
| **Formint Professional** | `projects/formints/formint-pro/` | Tauri + Django | — | Astro + Django + Unfold |
| **Formint Cloud** | `projects/formints/formint-cloud/` | خادم Django | 8767 | Django + Channels + Unfold |
| **Formint Client** | `projects/formints/formint-client/` | Tauri Desktop | — | Tauri + Vue 3 + TypeScript |
| **django-fusion** | `libs/django-fusion/` | حزمة Python | — | مكونات مشتركة (submodule) |

### مقارنة إصدارات Formint

| الإصدار | البنية | المزامنة | الإدارة |
|---------|--------|----------|---------|
| **Community** | Rust/Diesel + React 19 + SQLite | لا شيء (offline-first) | لا شيء |
| **Professional** | Django Ninja + Astro + Alpine/HTMX + Tauri | مزامنة sidecar | Unfold |
| **Cloud** | Django كامل + Channels + WebSocket + Unfold | SaaS متعدد الأطراف | Unfold + Bolt |
| **Client** | Vue 3 + Tauri + Pinia | عبر Cloud API | لا شيء |

---

## بنية البنية التحتية

```text
                  ┌──────────────────────────────────┐
                  │         Traefik Proxy :443        │
                  │   (Let's Encrypt SSL, auto-cert)  │
                  └────┬──────┬──────┬──────┬────────┘
                       │      │      │      │
           ┌───────────┼──────┼──────┼──────┼───────────┐
           │           │      │      │      │           │
        Precis    Landing   Syntara   Formint    shared-proxy
        LMS       Fusion    Chat      Cloud        :80
           │           │      │      │      │           │
           └───────────┴──────┴──────┴──────┴───────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
              PostgreSQL 16        Redis (broker)
              (per-site DBs)     (shared-worker queue)
```

### شبكات Docker

| الشبكة | الغرض |
|--------|-------|
| `common` | اتصالات بين الحاويات لتطبيقات Django + العمال |
| `traefik-net` | توجيه الوكيل ↔ الخلفية |
| `internal` | قناة خاصة بين قاعدة البيانات والتطبيق |
| `utilities-net` | مجموعة المراقبة |
| `warehouse-net` | خدمات مزامنة POS |
| `ollama-net` | استدلال نماذج الذكاء الاصطناعي |

---

## فلسفة تعدد المشاريع

صُمم هذا المستودع لـ **بناء ونشر وإطلاق منتجات مستقلة متعددة** من بنية تحتية مشتركة:

1. **سلسلة أدوات واحدة** — `uv` للبايثون، `pnpm` للواجهة، `Cargo` لـ Rust
2. **إعدادات مشتركة** — `projects/precis/configs/` توفر إعدادات Django أساسية تُعاد عبر مواقع Precis
3. **أصول مشتركة** — `projects/assets/` تحتوي قوالب وملفات ثابتة ولغة مشتركة بين المواقع
4. **إطار مشترك** — `libs/django-fusion/` يوفر المكونات والتوجيه والشظايا
5. **بنية تحتية مشتركة** — وكيل Traefik واحد، وخادم Nginx وسائط واحد، ومجموعة Postgres واحدة
6. **عزل لكل موقع** — لكل موقع حاويته ومنفذه وقاعدة بياناته ونطاقه

---

## دليل الأسماء المهاجرة

| الاسم القديم | الاسم الحالي | المسار الحالي |
|---|---|---|
| `precis-ctc` / `ctc` | **CTC Research** | `projects/precis/precis-ctc/` |
| `precis-lms` / `lms` | **Precis LMS** (اسم بديل) | `projects/precis/precis-main/` |
| `precis-landing` | **Precis Landing** | `projects/precis/precis-landing/` |
| `cms-fusion` | دُمج في Precis + Precis Landing | — |
| `cypercloud` | **Syntara** (اسم التشغيل محفوظ) | `projects/syntara/` |
| `portfolio` / `VResume` | دُمج في Precis | `projects/precis/precis-main/` |
| `pos-mini` / `forge-pos` / `formintA` / `formint-community` | **Formint Community** | `projects/formints/formint-community/` |
| `pos-solo` / `pos-full` / `formint` / `formint-pro` | **Formint Professional** (مدمج) | `projects/formints/formint-pro/` |
| `pos-cloud` / `formintB` / `formint-cloud` | **Formint Cloud** | `projects/formints/formint-cloud/` |
| `pos-client` / `formintC` / `formint-client` | **Formint Client** | `projects/formints/formint-client/` |
| `core/` | `projects/` | `projects/` |
| `core/libs/` | `libs/` | `libs/` |
| `core/configs/` | إعدادات Django المشتركة | `projects/precis/configs/` |

> ⚠️ **استخدم الأسماء الحالية في الكود الجديد.** قد تظهر الأسماء القديمة في وثائق الهجرة أو بيانات التوافق لكن لا ينبغي استخدامها لمسارات مصادر جديدة.

## Remarks & Notes

- استخدم `docs/guides/00-project-awareness.md` كفهرس تشغيلي؛ تبقى هذه النظرة واسعة عمداً.
- تعامل مع `projects/Makefile` و`AGENTS.md` الخاصة بالمنتجات وملفات Makefiles الخاصة بها كمصادر حقيقة قابلة للتنفيذ للمسارات والأوامر.
- النسخة الإنجليزية الكاملة: [`/docs/en/overview`](/docs/en/overview).
