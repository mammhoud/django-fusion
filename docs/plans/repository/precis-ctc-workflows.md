# Precis CTC Research — Cross-Module Workflow Plan

> **Status:** Proposed
> **Date:** 2026-08-18
> **Canonical product:** `projects/precis/precis-ctc/`
> **Execution boundary:** Dramatiq actors through the shared task backend

<!-- AI-generated: review needed -->

## Context

CTC Research crosses content publishing, the medical-learning catalog,
notifications, events, analytics, and attribution. Direct synchronous calls
between these modules make publication slow and make retries, audit history,
and failure handling inconsistent.

The intended message replacement is:

```text
HTTP/admin/scheduled trigger
  → validate command and write workflow record
  → enqueue one Dramatiq message
  → actor loads current database state
  → actor performs one idempotent boundary operation
  → actor emits status/analytics/attribution events
```

Dramatiq is the single execution boundary for publishing, refresh, analytics,
and attribution. A module may validate synchronously, but it must not call a
second queue system or silently perform a cross-module side effect inline.

## Workflow definitions

| # | Workflow | Trigger | Primary actor boundary | Queue |
|---:|---|---|---|---|
| 1 | Publish page | Wagtail publish action | Validate page, publish revision, invalidate page cache | `content` |
| 2 | Unpublish/archive page | Wagtail unpublish action | Mark page unavailable and invalidate public cache | `content` |
| 3 | Publish course | Course release action | Validate course, modules, lessons, prerequisites, and disclaimer | `courses` |
| 4 | Refresh course catalog | Schedule/admin refresh | Rebuild published catalog projection and search metadata | `courses` |
| 5 | Rebuild media renditions | Image upload/replacement | Generate approved renditions and update gallery references | `content` |
| 6 | Refresh navigation/search | Page or course publication | Rebuild navigation/search projection for the active locale | `content` |
| 7 | Send enrollment confirmation | Successful enrollment | Render localized enrollment email and send through email actor | `email` |
| 8 | Send course completion/certificate | Lesson/course completion | Validate completion, create certificate, notify learner | `courses` then `email` |
| 9 | Send event reminder | Scheduled event window | Resolve timezone and send reminder to eligible attendees | `email` |
| 10 | Process contact submission | Contact form fragment | Validate, persist ticket/event, notify approved mailbox | `email` |
| 11 | Refresh learning analytics | Nightly schedule | Aggregate enrollments, progress, completion, and certificate metrics | `analytics` |
| 12 | Refresh content analytics | Nightly schedule | Aggregate page, article, gallery, and CTA engagement | `analytics` |
| 13 | Record publication attribution | Publish/CTA event | Associate campaign, locale, referrer, and content version | `attribution` |
| 14 | Record enrollment attribution | Enrollment event | Associate first/last touch and course/product source | `attribution` |
| 15 | Refresh campaign attribution | Daily schedule | Reconcile event stream with campaign/source dimensions | `attribution` |
| 16 | Send translation-review task | Locale content change | Create reviewer task and notify the locale owner | `content` / `email` |

## Actor contract

Every cross-module actor should:

- accept a stable `website` value (`precis-ctc`) and a correlation/workflow ID;
- be idempotent for the same entity/version/event key;
- load current state inside the actor instead of trusting stale request payloads;
- persist start/success/failure status through the shared task backend;
- use bounded retries for transient database, Redis, and SMTP failures;
- avoid logging secrets, full message bodies, patient data, or access tokens;
- emit a structured result suitable for analytics and audit history.

Existing shared boundaries include:

- `plugins.workers.shared_content` for content/account actors;
- `plugins.workers.shared_email` for single, bulk, and raw email actors;
- `django_fusion.tasks` for task registration and queue execution;
- Compose `worker` and `scheduler` services for execution.

Proposed actor names should follow the existing `actor_name` convention, for
example:

```python
@task(queue="content", actor_name="ctc.content.publish_page")
def publish_page(workflow_id: str, page_id: int, website: str = "precis-ctc") -> dict:
    ...
```

## Message replacement rules

| Existing risk | Replacement |
|---|---|
| View calls email service directly | View validates and sends `shared.email.send` with a workflow ID |
| Publish action rebuilds every projection inline | Publish actor writes an event and enqueues projection refresh |
| Analytics query runs in a request | Scheduled analytics actor computes and stores an aggregate |
| Attribution is inferred independently by each module | Attribution actors consume a common event envelope |
| Locale change is silently published | Locale review actor creates an explicit review task |

## Rollout order

1. Add workflow/event persistence and correlation IDs.
2. Wrap existing email sends with the shared email actors; preserve response behavior.
3. Move page/course publish side effects behind actors.
4. Add idempotent analytics and attribution projections.
5. Add dashboards, retry/dead-letter inspection, and operational alerts.
6. Remove direct cross-module calls only after actor parity is verified.

## Verification

- Unit-test actor idempotency and retry classification.
- Test each producer with a fake/in-memory broker or task backend.
- Verify queue names and actor registration during Django startup.
- Run a staging publish → catalog refresh → analytics → attribution chain.
- Confirm failed email and content tasks are visible without exposing payload secrets.
- Confirm the CTC `make redeploy` recreates worker and scheduler services.

## Remarks & Notes

- This is a plan, not an assertion that all 16 actors already exist. Existing shared email/content actors are the starting boundary; the remaining domain actors require implementation and review.
- Do not introduce Celery, RQ, a second Dramatiq broker, or ad-hoc background threads for these workflows without an accepted architecture decision.
- Medical analytics must be aggregate and privacy-reviewed; patient-level or identifiable data is outside this public-site workflow plan.
