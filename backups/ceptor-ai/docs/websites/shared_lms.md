# Shared LMS Domain

> **Related Code**
> * **Domain:** Cross-site LMS application surface
> * **Paths:**
>   * `applications/ctc-research/plugins/lms/views/courses.py`
>   * `applications/lms-demo/plugins/lms/views/courses.py`
>   * `applications/libs/django-fusion/src/django_fusion/comp/routes/sites.py` (the `Application` class)
> * **Sites using this surface:** [ctc-research](ctc-research/index.md), [lms-demo](lms-demo/index.md)
> * **Variants:** `layout/landing/skeleton.html` (course landing) + `layout/learning/skeleton.html` (lesson viewer)

## What this is

CTC Research and LMS Demo share an almost-identical LMS Application surface: a `LMSApp` `Application` subclass that mounts `CourseListComponent`, `LessonPlayerComponent`, and `EnrollmentComponent`. Only the wrapper Page models and brand assets differ — the routing, viewsets, and templates are reused verbatim.

The `Application` class that wires these viewsets together lives in `applications/libs/django-fusion/src/django_fusion/comp/routes/sites.py` and is documented in [`../architecture/routable_applications.md`](../reference/architecture/routable_applications.md).

## Application tree (shared)

```text
LMSApp (Application, autodiscovered from plugins/lms/apps.py)
├── CourseListComponent (FragmentComponent)    -- /courses/
├── LessonPlayerComponent (RoutableComponent)  -- /courses/<slug>/<int:lesson>/
└── EnrollmentComponent (FragmentComponent)    -- /courses/<slug>/enroll/
```

## Why it's shared

Per-site copy-paste of the LMS Application would drift over time. The shared surface is a deliberate `django-fusion` choice: install the `plugins/lms` reusable package-style app into both sites, and the `VResumeSite`-style Site class auto-discovers the Application via class import.

## Per-site overrides

* **CTC Research** overrides `CourseListComponent` to add a "Peer-reviewed" badge column (`applications/ctc-research/plugins/lms/views/courses.py`).
* **LMS Demo** keeps the defaults, only customising copy.

## See also

* [`ctc-research/index.md`](ctc-research/index.md) — site-specific notes.
* [`lms-demo/index.md`](lms-demo/index.md) — site-specific notes.
* [`../architecture/routable_applications.md`](../reference/architecture/routable_applications.md) — full Application class docs.
* [`../architecture/routable_site.md`](../reference/architecture/routable_site.md) — Site registration patterns (autodiscovery vs explicit register).
