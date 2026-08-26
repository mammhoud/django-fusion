---
title: خريطة مرجعية للتوثيق
description: فهرس كامل لشجرة docs/ — كل مجلد ومجلد فرعي ومشروعه المالك وما يشير إليه كل ملف.
navigation:
  title: الخريطة المرجعية
  icon: i-lucide-map
---

# 🗺️ خريطة مرجعية للتوثيق

> فهرس واحد لشجرة `docs/` بأكملها: كل مجلد، و**المشروع المالك**، وما يشير إليه
> كل **ملف**. استخدمه للعثور على مكان موضوع ما قبل إنشاء صفحة جديدة
> (اربط، لا تكرر).

<!-- AI-generated: review needed -->

## المستندات الجذرية

| الملف | المشروع المالك | يشير إلى |
|-------|----------------|----------|
| [`README.md`](/docs/en/) | workspace | مركز التوثيق، جدول المنتجات، روابط سريعة |
| [`ARCHITECTURE.md`](/docs/en/architecture) | workspace | بنية المستودع، دورة حياة الطلب، خط أنابيب الهيكل |
| [`project-structure.md`](/docs/en/project-structure) | workspace | خريطة الدليل، قواعد الملكية والموضع |
| [`overview.md`](/docs/en/overview) | workspace | نظرة عامة عالية المستوى |
| [`recommendations.md`](/docs/en/recommendations) | workspace | الأولويات والتسلسل الموصى به |
| [`guides/02-setup.md`](/docs/en/guides/02-setup) | workspace | فهارس الإعداد/البناء لكل مشروع + سير عمل CI |
| [`recent-changes.md`](/docs/en/recent-changes) | workspace | سجل التغييرات الأخيرة |
| [`REFERENCE.md`](/docs/en/reference) | workspace | هذه الخريطة المرجعية |
| [`COMMANDS.md`](/docs/en/commands) | workspace | تسمية الأفعال الموحدة، سلسلة التفويض، تسلسل النشر |

## وثائق المنتجات

| المجلد | المشروع المالك | الملفات ← ما تشير إليه |
|--------|----------------|------------------------|
| [`precis/`](/docs/en/precis) | `precis-main` | README (فهرس) · ARCHITECTURE (بنية LMS + Landing) · configuration · courses · deployment |
| [`precis/precis-landing/`](/docs/en/precis) | `precis-landing` (قديم) | backend-api · deployment · frontend |
| [`precis/client/ctc-research/`](/docs/en/precis/client/ctc-research) | `precis-ctc` | README (فهرس) · content-strategy · publishing-and-production · client-production |
| [`syntara/`](/docs/en/syntara) | `syntara` | README (فهرس) · configuration · features · infrastructure · use-cases |
| [`pos/`](/docs/en/pos) | `formints` | README (فهرس) · editions (مؤشر → `plans/editions/`) · cloud-edition — الوثائق المعيارية في `projects/formints/docs/` |
| [`loop-crm/`](/docs/en/loop-crm) | `loop-crm` | README (فهرس) · design-system · setup-and-build |

## وثائق مشتركة وإطار العمل

| المجلد | المشروع المالك | الملفات ← ما تشير إليه |
|--------|----------------|------------------------|
| [`libs/`](/docs/en/libs) | `django-fusion` | README (فهرس) · django-fusion · auth-customization · configuration · js-structure · templates-architecture |
| [`shared/`](/docs/en/shared) | workspace | README (فهرس) · configuration · shared-methods · use-cases |

## أدلة وتطوير وميزات وذكاء اصطناعي ونشر

| المجلد | المشروع المالك | الملفات ← ما تشير إليه |
|--------|----------------|------------------------|
| [`guides/`](/docs/en/guides) | workspace | README (فهرس) · 01-quickstart → 10-fusion-assets-health · auth/webauthn-passkeys · fixture-loading |
| [`dev/`](/docs/en/dev) | workspace | README (فهرس) — مواضيع التطوير |
| [`dev/infrastructure/`](/docs/en/dev/infrastructure) | infrastructure | README · deployment · proxy · routing-proxy · shared-worker · worker-stack |
| [`features/`](/docs/en/features) | workspace | README · data-token-sync-tagging · feature-roadmap |
| [`ai/`](/docs/en/ai) | workspace/agents | README · agents · mcp-integration · prompts · skills-catalog |
| [`publish/`](/docs/en/publish) | workspace | README · ci-cd · docker-deploy · pos-release |
| [`tests/`](/docs/en/tests) | workspace | README · e2e-test-report · testing-strategies |

## الخطط (قرارات بنمط ADR)

| المجلد | المشروع المالك | الملفات ← ما تشير إليه |
|--------|----------------|------------------------|
| [`plans/`](/docs/en/plans) | workspace | README (السجل) · deletion-manifest · document-lifecycle · precis-landing · marketing-claims |
| [`plans/editions/`](/docs/en/plans) | `formints` | README (فهرس) · comparison · 01-community → 09-completion-plan |
| [`plans/repository/`](/docs/en/plans) | workspace | توحيد المستودع، إغلاق المشاريع، نشر CTC، خطط التحسين |

## استراتيجية الشركة الناشئة (خاصة) 🔒

| المجلد | المشروع المالك | الملفات ← ما تشير إليه |
|--------|----------------|------------------------|
| [`startup/`](/docs/en/startup) | workspace | README (فهرس) · STRATEGY · comparison · PLAN · PRICING · SALES · company-profile · product-profiles · revenue-model · presentation |

## الترجمات العربية (المصدر المؤلف)

| المجلد | المشروع المالك | الملفات ← ما تشير إليه |
|--------|----------------|------------------------|
| [`ar-content/`](/docs/ar/) | workspace | index (الرئيسية) · overview · architecture · project-structure · guides (quickstart, deploy, config-cascade, setup, auth, dev, customize, clone-site, best-practices, docus) · libs/django-fusion · startup · precis/client/ctc-research · المنتجات (precis, pos, syntara, loop-crm, libs, shared) |

## Remarks & Notes

- تُولَّد هذه الخريطة يدوياً من شجرة `docs/` الحية؛ حافظ على مزامنتها عند إضافة
  أو إعادة تسمية أو حذف مجلد.
- مجلدات `content/` و`scripts/` و`public/` و`assets/` هي نواتج بناء أو أدوات،
  وليست توثيقاً مؤلفاً — حُذفت عمداً.
- النسخة الإنجليزية الكاملة: [`/docs/en/reference`](/docs/en/reference).
