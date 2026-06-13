# Circular Dependency Cycles

## Cycle 1
Path: structa.cloud.apps.accounts.services.email.tasks → structa.cloud.apps.accounts.services.email.service
Suggestion: Break bidirectional dependency between structa.cloud.apps.accounts.services.email.tasks and structa.cloud.apps.accounts.services.email.service. Consider extracting shared interface or using dependency injection.

## Cycle 2
Path: structa.cloud.apps.lms.services.certificates → structa.cloud.apps.lms.models.certificate
Suggestion: Break bidirectional dependency between structa.cloud.apps.lms.services.certificates and structa.cloud.apps.lms.models.certificate. Consider extracting shared interface or using dependency injection.

## Cycle 3
Path: structa.cloud.apps.lms.models.courses.detail → structa.cloud.apps.lms.models.courses.info → structa.cloud.apps.lms.services.courses
Suggestion: Break cycle by extracting shared functionality from structa.cloud.apps.lms.models.courses.detail to a new module, or refactor to use event-based communication.

## Cycle 4
Path: structa.cloud.apps.lms.models.courses.detail → structa.cloud.apps.lms.models.courses.info → structa.cloud.apps.lms.services.courses → structa.cloud.apps.accounts.services.person → structa.cloud.apps.accounts.managers.__init__ → structa.cloud.apps.lms.managers.enrollments
Suggestion: Break cycle by extracting shared functionality from structa.cloud.apps.lms.models.courses.detail to a new module, or refactor to use event-based communication.

