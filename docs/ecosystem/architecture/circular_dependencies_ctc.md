# Circular Dependency Cycles

## Cycle 1
Path: ctc-research.com.apps.lms.services.certificates → ctc-research.com.apps.lms.models.certificate
Suggestion: Break bidirectional dependency between ctc-research.com.apps.lms.services.certificates and ctc-research.com.apps.lms.models.certificate. Consider extracting shared interface or using dependency injection.

## Cycle 2
Path: ctc-research.com.apps.accounts.services.email.service → ctc-research.com.apps.accounts.services.email.tasks
Suggestion: Break bidirectional dependency between ctc-research.com.apps.accounts.services.email.service and ctc-research.com.apps.accounts.services.email.tasks. Consider extracting shared interface or using dependency injection.

## Cycle 3
Path: ctc-research.com.apps.handlers.managers.enrollments → ctc-research.com.apps.lms.models.courses.detail → ctc-research.com.apps.lms.models.courses.info → ctc-research.com.apps.lms.services.courses → ctc-research.com.apps.accounts.services.person → ctc-research.com.apps.accounts.managers.__init__
Suggestion: Break cycle by extracting shared functionality from ctc-research.com.apps.handlers.managers.enrollments to a new module, or refactor to use event-based communication.

## Cycle 4
Path: ctc-research.com.apps.lms.services.courses → ctc-research.com.apps.lms.models.courses.detail → ctc-research.com.apps.lms.models.courses.info
Suggestion: Break cycle by extracting shared functionality from ctc-research.com.apps.lms.services.courses to a new module, or refactor to use event-based communication.

