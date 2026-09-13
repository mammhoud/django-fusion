---
title: سير العمل وCI
description: سير عمل GitHub Actions وتفويض Makefile في المستودع.
navigation:
  title: سير العمل وCI
  icon: i-lucide-workflow
---

# سير العمل وCI

## GitHub Actions

### `deploy-ci.yml`

الموقع: `.github/workflows/deploy-ci.yml`.

يُشغَّل عند تغيير:
- `Makefile` و`Makefile.*`
- `.github/workflows/deploy-ci.yml`
- `.github/actions/deploy-preflight/**`
- `**/docker-compose*.yml` و`*.yaml`
- `libs/**/*.md`
- `application/scripts/staging/check_markdown_links.py`

الوظائف:

1. **preflight** — يشغّل الإجراء المركّب المحلي `.github/actions/deploy-preflight`
   للتحقق من Docker daemon و`make deploy-ci`.
2. **markdown-links** — يشغّل `application/scripts/staging/check_markdown_links.py`
   للتحقق من الروابط المتقاطعة في Markdown.

### `check-extras.yml`

الموقع: `.github/workflows/check-extras.yml`.

يتحقق من أن أي سطر `uv add "pkg[extras]"` / `pip install "pkg[extras]"`
في `libs/**/docs/` يطابق الإضافات المعلنة في `pyproject.toml` المقابل.

## تفويض Makefile

`Makefile` الجذري نقطة دخول رفيعة تفوّض عمل الموقع إلى `projects/Makefile`.

```bash
# شغّل هدفاً لموقع محدد
cd projects
make check WEBSITE=precis-ctc
make docker-up WEBSITE=lms
make test WEBSITE=vresume
```

الأهداف الشائعة:

| الهدف | الغرض |
|---|---|
| `check` | فحوصات نظام Django |
| `docker-up` | بناء وتشغيل حاوية موقع |
| `docker-down` | إيقاف حاويات الموقع |
| `docker-health-check` | فحص صحة الحاويات قيد التشغيل |
| `tests-unit` | اختبارات الوحدة |
| `tests-integration` | اختبارات التكامل |

## تحسينات موصى بها

1. أضف سير عمل `docs.yml` يشغّل `npm --prefix docs run build` للتحقق من مسارات
   Docus واللغات في كل طلب سحب للوثائق.
2. ثبّت `actions/checkout` و`actions/setup-python` على تجزئات محددة لأمن سلسلة التوريد.
3. أبقِ `make -C docs serve` كأمر معاينة Docus المحلي المعياري.

## Remarks & Notes

- النسخة الإنجليزية الكاملة: [`/docs/en/guides/01-setup`](/docs/en/guides/01-setup).
- راجع [`/docs/en/commands`](/docs/en/commands) لمرجع الأوامر الكامل.
