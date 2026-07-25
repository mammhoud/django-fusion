---
# yaml-language-server: $schema=schemas/feature.schema.json
Object type:
    - Feature
Tags:
    - lms
    - quizzes
    - assessment
    - education
Status: Planned
Links:
    - LMS
---

# Quizzes — LMS Assessment System

> **Type:** Feature ✨
> **Description:** Quiz and assessment engine for the LMS Demo platform — multiple question types, scoring, feedback, and progress tracking.

---

## Overview

The Quiz system powers formative and summative assessment across all courses:

| Question Type | Description | Scoring |
|---------------|-------------|---------|
| **Multiple Choice** | Single or multi-select answers | Auto-graded |
| **True / False** | Binary choice | Auto-graded |
| **Fill in the Blank** | Text input against expected answer | Auto-graded |
| **Short Answer** | Free text response | Instructor-graded |
| **Essay** | Long-form response | Instructor-graded |
| **Matching** | Pair items from two columns | Auto-graded |
| **Ordering** | Arrange items in correct sequence | Auto-graded |

---

## Project Context

| Aspect | Description |
|--------|-------------|
| **Site** | LMS Demo + CTC Research |
| **Color** | Amber (#f59e0b) / Yellow (#eab308) — representing assessment, challenge, and achievement |
| **Progress Impact** | Quiz scores contribute to course completion percentage |
| **Tech** | Wagtail Page models, django-fusion components |

---

## Color Palette: Quiz Amber

| Token | Hex | Usage |
|-------|-----|-------|
| Primary | `#f59e0b` (Amber-500) | Quiz headers, question markers |
| Surface | `#fffbeb` / `#451a03` | Quiz panels (light/dark) |
| Correct | `#22c55e` (Green-500) | Correct answer indicator |
| Incorrect | `#ef4444` (Red-500) | Incorrect answer indicator |
| Partial | `#eab308` (Yellow-500) | Partial credit indicator |

---

## Related Docs

- → `learning-curve.md` — Learning progression
- → `../../guides/development.md` — Adding quiz components
- → `../../README.md` — Master index
