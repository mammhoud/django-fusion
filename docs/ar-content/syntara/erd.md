---
title: Syntara — مخطط الكيانات والعلاقات (ERD)
description: توليد مخططات الكيانات والعلاقات لنماذج Django في Syntara (دردشة Cypercloud بالذكاء الاصطناعي).
navigation:
  title: ERD
  icon: i-lucide-database
---

# Syntara — مخطط الكيانات والعلاقات (ERD)

مخططات الكيانات والعلاقات لنماذج Django في Syntara (دردشة Cypercloud بالذكاء الاصطناعي).

## التوليد

```bash
cd projects/syntara
make erd        # combined diagram → docs/erd/syntara_erd.png
make erd-all    # one PNG per app  → docs/erd/
```

المخرجات: `projects/syntara/docs/erd/syntara_erd.png`

التطبيقات المغطّاة: `chat`

## المتطلبات

- `graphviz` — حزمة نظام، مثبَّتة مسبقاً في صورة Syntara Docker
- `django-extensions` — في `requirements.txt`
- `pydot` — في `requirements.txt`
- `django_extensions` في `INSTALLED_APPS` داخل `settings.py`

## ملاحظات

ملفات PNG الناتجة مُتجاهَلة في git (`*.png` في `.gitignore` الجذري).
مجلد `docs/erd/` مُتتبَّع عبر `.gitkeep`.
أعِد التوليد بعد أي هجرة نماذج في `chat/`.

<!-- AI-generated: review needed -->
