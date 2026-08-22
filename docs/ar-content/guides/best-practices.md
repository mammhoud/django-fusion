---
title: أفضل الممارسات — اصطلاحات الكود
description: اصطلاحات خاصة باللغات ومعايير توثيق لمستودع Structa Cloud.
navigation:
  title: أفضل الممارسات
  icon: i-lucide-badge-check
---

# 📐 أفضل الممارسات — اصطلاحات الكود

> اصطلاحات خاصة باللغات ومعايير توثيق لمستودع Structa Cloud.

---

## Python (Django)

```python
# PEP 8, طول سطر Black 88 حرفاً
from django_fusion.comp.routes import Viewset  # مسارات استيراد معيارية

class MyViewset(ModelViewset):  # طرق عرض قائمة على الفئات
    """سلسلة توثيق من سطر واحد."""
    model = MyModel
```

- استخدم تلميحات النوع للدوال الجديدة
- لا تلف الاستيرادات بـ `try/except`
- منطق الأعمال في الخدمات، وليس في طرق العرض
- `fragment_name` لمعرّفات شظايا HTMX

## Rust (خلفية POS)

```rust
/// ملخص من سطر واحد.
pub fn get_products(db_path: &str) -> Result<Vec<Product>, String> {
    let mut conn = establish_connection(db_path);
    // استعلامات Diesel ORM
}
```

- كل أوامر Tauri ترجع `Result<T, String>`
- وحدات العمليات تتبع: CRUD + نمط الحذف الناعم

## TypeScript (واجهة POS)

```typescript
/** وصف موجز. */
function MyComponent({ data }: Props): JSX.Element {
  const { t } = useTranslation();
  return <div>{t('common.save')}</div>;
}
```

- React 19 + TypeScript 5.8
- مكونات دالة مع خطافات
- JSDoc للدوال المُصدَّرة

## معايير التوثيق

| العنصر | الاصطلاح |
|--------|----------|
| العناوين | `# H1` عنوان الصفحة، `## H2` الأقسام، `### H3` الأقسام الفرعية |
| الكود | Backticks للمسارات/الأوامر، كتل مسوّرة مع اللغة |
| الروابط | مسارات نسبية من ملف المصدر |
| الإيموجي | ثابت: 🏠 تنقل، 🟢 قابل للتخصيص، ⚠️ تحذير، 💡 نصيحة |

## وسوم التخصيص

| الوسم | المعنى |
|-------|--------|
| 🟢 `customizable` | آمن للتعديل والتوسيع والتجاوز |
| 🔴 `not-customizable` | إطار أساسي — التعديل على مسؤوليتك |
| 🟡 `delegate` | توسعة عبر الخطافات/التفويض |
| 🔵 `template` | مستوى القالب فقط |
| ⚪ `config` | إعداد عبر متغيرات البيئة/الإعدادات |

## Remarks & Notes

- النسخة الإنجليزية الكاملة: [`/docs/en/guides/07-best-practices`](/docs/en/guides/07-best-practices).
- راجع [`/docs/en/guides/05-customize`](/docs/en/guides/05-customize) لنظام الوسوم التفصيلي.
