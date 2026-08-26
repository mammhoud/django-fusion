---
title: الخريطة المرجعية للتوثيق
description: فهرس كامل لشجرة docs/ — كل مجلد ومجلد فرعي ومشروعه المالك وما يشير إليه كل ملف.
navigation:
  title: الخريطة المرجعية
  icon: i-lucide-map
---

# 🗺️ الخريطة المرجعية للتوثيق

> فهرس واحد لشجرة `docs/` بأكملها: كل مجلد، و**المشروع المالك**، وما يشير إليه كل **ملف**. استخدمه للعثور على مكان موضوع ما قبل إنشاء صفحة جديدة (اربط، لا تكرر).

---

## المستندات الجذرية

| الملف | المشروع المالك | يشير إلى |
|-------|----------------|----------|
| `README.md` | workspace | مركز التوثيق، جدول المنتجات، روابط سريعة |
| `ARCHITECTURE.md` | workspace | بنية المستودع، دورة حياة الطلب، خط أنابيب الهيكل |
| `project-structure.md` | workspace | خريطة الدليل، قواعد الملكية والموضع |
| `overview.md` | workspace | نظرة عامة عالية المستوى |
| `recommendations.md` | workspace | الأولويات والتسلسل الموصى به |
| `recent-changes.md` | workspace | سجل التغييرات الأخيرة |
| `REFERENCE.md` | workspace | هذه الخريطة المرجعية |
| `COMMANDS.md` | workspace | تسمية الأفعال الموحدة، سلسلة التفويض، تسلسل النشر |

## وثائق المنتجات

| المجلد | المشروع المالك | الملفات ← ما تشير إليه |
|--------|----------------|------------------------|
| `precis/` | `precis-main` | README (فهرس) · ARCHITECTURE (بنية LMS + Landing) · configuration · courses · deployment |
| `precis/precis-landing/` | `precis-landing` (قديم) | backend-api · deployment · frontend |
| `precis/client/ctc-research/` | `precis-ctc` | README (فهرس) · content-strategy · publishing-and-production · client-production |
| `syntara/` | `syntara` | README (فهرس) · configuration · features · infrastructure · use-cases |
| `pos/` | `formints` | README (فهرس) · editions (مؤشر → `plans/editions/`) · cloud-edition — الوثائق المعيارية في `projects/formints/docs/` |
| `loop-crm/` | `loop-crm` | README (فهرس) · design-system · setup-and-build |

## وثائق مشتركة وإطار العمل

| المجلد | المشروع المالك | الملفات ← ما تشير إليه |
|--------|----------------|------------------------|
| `libs/` | `django-fusion` | README (فهرس) · django-fusion · auth-customization · configuration · js-structure · templates-architecture |
| `shared/` | workspace | README (فهرس) · configuration · shared-methods · use-cases |

## أدلة وتطوير وميزات وذكاء اصطناعي ونشر

| المجلد | المشروع المالك | الملفات ← ما تشير إليه |
|--------|----------------|------------------------|
| `guides/` | workspace | README (فهرس) · 01-quickstart → 10-fusion-assets-health · auth/webauthn-passkeys · fixture-loading |
| `dev/` | workspace | README (فهرس) — مواضيع التطوير |
| `dev/infrastructure/` | infrastructure | README · deployment · proxy · routing-proxy · shared-worker · worker-stack |
| `features/` | workspace | README · data-token-sync-tagging · feature-roadmap |
| `ai/` | workspace/agents | README · agents · mcp-integration · prompts · skills-catalog |
| `publish/` | workspace | README · ci-cd · docker-deploy · pos-release |
| `tests/` | workspace | README · e2e-test-report · testing-strategies |
| `changelogs/` | workspace | README (فهرس) · libs · pos · repo · session notes |

## الخطط (قرارات بنمط ADR)

| المجلد | المشروع المالك | الملفات ← ما تشير إليه |
|--------|----------------|------------------------|
| `plans/` | workspace | README (السجل) · deletion-manifest · document-lifecycle · precis-landing · marketing-claims |
| `plans/editions/` | `formints` | README (فهرس) · comparison · 01-community → 09-completion-plan |
| `plans/loop-crm/` | `loop-crm` | demo-state-gap-fixing · formint-integration-finance · merge-plan · twenty-postiz-comparison · wagtail-landing-plan |
| `plans/repository/` | workspace | توحيد المستودع، إغلاق المشاريع، نشر CTC، خطط التحسين |

## استراتيجية الشركة الناشئة (خاصة) 🔒

| المجلد | المشروع المالك | الملفات ← ما تشير إليه |
|--------|----------------|------------------------|
| `startup/` | workspace | README (فهرس) · STRATEGY · comparison · PLAN · PRICING · SALES · company-profile · product-profiles · revenue-model · presentation |

## الترجمات العربية (المصدر المؤلف)

| المجلد | المشروع المالك | الملفات ← ما تشير إليه |
|--------|----------------|------------------------|
| `ar-content/` | workspace | index (الرئيسية) · overview · architecture · project-structure · guides (quickstart, deployment, config-cascade, setup, auth, dev, customize, clone-site, best-practices, docus) · libs/django-fusion · startup · precis/client/ctc-research · المنتجات (precis, pos, syntara, loop-crm, libs, shared) |

## ملاحظات وإرشادات

- تُولَّد هذه الخريطة يدوياً من شجرة `docs/` الحية؛ حافظ على مزامنتها عند إضافة أو إعادة تسمية أو حذف مجلد.
- كل منتج له `README.md` فهرس — اتبع نفس النمط للمنتجات الجديدة.
- مجلدات `content/` و`scripts/` و`public/` و`assets/` هي نواتج بناء أو أدوات، ليست توثيقاً مؤلفاً — حُذفت عمداً.
- النسخة الإنجليزية الكاملة: [`/docs/en/reference`](/docs/en/reference).

<!-- AI-generated: review needed -->
