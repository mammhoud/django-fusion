# 📊 Locale / Translation Files Usage Analysis

**Path:** `projects/assets/locale/`
**Status:** ✅ Active — used by all projects via `LOCALE_PATHS`

---

## Overview

Django internationalization (i18n) translation files. Configured in `projects/configs/base/assets.py` via `LOCALE_PATHS = [str(LOCALE_DIRS)]`.

---

## Language Support

| Language | Code | Files | Status |
|----------|------|-------|--------|
| Arabic | `ar` | `django.po`, `django.mo` | ✅ Active |
| German | `de` | `django.po`, `django.mo` | ✅ Active |
| Spanish | `es` | `.po` (compiled) | ✅ Active |
| French | `fr` | `django.po`, `django.mo` | ✅ Active |

---

## Usage by Project

| Project | Uses Locale? | Notes |
|---------|-------------|-------|
| **lms** | ✅ Yes | All translations available |
| **cms-fusion** | ✅ Yes | All translations available |
| **lms-fusion** | ✅ Yes | All translations available |
| **portfolio** | ✅ Yes | All translations available |
| **cypercloud** | ✅ Yes | All translations available |
| **ctc-research** | ✅ Yes | All translations available |

---

## Key Files

| File | Description |
|------|-------------|
| `ar/LC_MESSAGES/django.po` | Arabic translation source |
| `ar/LC_MESSAGES/django.mo` | Arabic compiled translation |
| `de/LC_MESSAGES/django.po` | German translation source |
| `de/LC_MESSAGES/django.mo` | German compiled translation |
| `fr/LC_MESSAGES/django.po` | French translation source |
| `fr/LC_MESSAGES/django.mo` | French compiled translation |
| `es.po` | Spanish translation source |
| `ar.po` | Arabic translation source (flat) |
| `de.po` | German translation source (flat) |
| `fr.po` | French translation source (flat) |
