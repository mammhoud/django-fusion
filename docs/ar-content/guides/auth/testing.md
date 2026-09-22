---
title: اختبار نظام المصادقة
description: اختبارات الوحدة والتكامل والاختبارات القائمة على الخصائص لنظام المصادقة.
---

# اختبار نظام المصادقة

## ملفات الاختبار

| الملف | النوع | الغرض |
|------|------|---------|
| `websites/tests/unit/test_auth_fragments.py` | قائم على الخصائص | بنية القالب، سلوك HTMX |
| `websites/tests/unit/test_auth_notifications.py` | وحدة | المحوّل، رسالة تسجيل الخروج، القوالب المحذوفة |
| `websites/tests/unit/test_app_structure.py` | وحدة | موقع التطبيق، الهوية البصرية، نطاقات URL |
| `websites/tests/integration/test_auth_flows.py` | تكامل | تدفقات مصادقة من طرف إلى طرف على الحاويات |

## تشغيل الاختبارات

```bash
# Unit tests (no running server needed)
pytest websites/tests/unit/test_auth_fragments.py -v
pytest websites/tests/unit/test_auth_notifications.py -v
pytest websites/tests/unit/test_app_structure.py -v

# Integration tests (requires running containers)
CTC_BASE_URL=http://localhost:5070 STRUCTA_BASE_URL=http://localhost:5080 \
    pytest websites/tests/integration/test_auth_flows.py -v

# All auth tests
pytest websites/tests/unit/test_auth_fragments.py \
       websites/tests/unit/test_auth_notifications.py \
       websites/tests/unit/test_app_structure.py \
       websites/tests/integration/test_auth_flows.py -v
```

## الاختبارات القائمة على الخصائص

تستخدم [Hypothesis](https://hypothesis.readthedocs.io/) للتحقق من خصائص عامة عبر كل قوالب المصادقة.

### الخصائص

| # | الخاصية | ما تتحقق منه |
|---|----------|-----------|
| 1 | كل قوالب auth/ شظايا خالصة | بلا `{% extends %}`، والعنصر الخارجي = `fragment--form` |
| 2 | لا تبقى مراجع `pipelines:` | اكتمال ترحيل نطاق URL |
| 3 | كل النماذج تحتوي مُدخلَي `strategy` و`supports_sse` | حقول سياق HTMX موجودة |
| 4 | الأزرار الاجتماعية تستخدم `<a>` لا `hx-post` | توافق إعادة توجيه OAuth |
| 5 | طلبات HTMX تُعيد شظايا مجرّدة | `HX-Request: true` ← بلا هيكل |
| 6 | الطلبات غير HTMX تُعيد الهيكل | صفحة كاملة ← `auth-container` + `fragment--form` |
| 7 | ذهاب وإياب لحقل strategy | بقاء قيمة `strategy` عبر إرسال النموذج |
| 8 | إرسالات HTMX غير الصحيحة تُعيد شظايا 2xx | بلا إعادات توجيه عند أخطاء نموذج HTMX |
| 9 | المزوّدون المُهيَّؤون يعرضون أزراراً | `SOCIALACCOUNT_PROVIDERS` ← الأزرار ظاهرة |

### الإعداد

```python
from hypothesis import settings
settings.register_profile("ci", max_examples=100)
settings.load_profile("ci")
```

### مثال

```python
from hypothesis import given, settings as h_settings, strategies as st

@given(template_path=st.sampled_from(AUTH_TEMPLATE_PATHS))
@h_settings(max_examples=100)
def test_no_pipelines_references(template_path):
    content = Path(template_path).read_text(encoding="utf-8")
    assert "pipelines:" not in content
```

## اختبارات التكامل

اختبارات من طرف إلى طرف تستخدم `requests` مقابل حاويات قيد التشغيل. تُتخطّى الاختبارات تلقائياً إذا كان الموقع غير قابل للوصول.

```python
@pytest.mark.parametrize("site", SITE_CONFIGS, ids=lambda s: s["name"])
def test_htmx_fragment_response(site):
    resp = requests.get(
        f"{site['base_url']}/auth/login/",
        headers={"HX-Request": "true"},
    )
    assert "fragment--form" in resp.text
    assert "auth-container" not in resp.text
```

<!-- AI-generated: review needed -->
