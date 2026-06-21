"""
Django RSeal Temporal Integration.

Provides Temporal.io workflow and activity support for Django applications.
This module enables async workflow orchestration using Temporal.

Usage:
    from django_rseal.workflows.temporal import (
        TemporalWorker,
        send_email_activity,
        process_user_activity,
        UserOnboardingWorkflow,
        BatchProcessingWorkflow,
    )

Note: temporalio package must be installed to use workflows.
Activities can be used without temporalio.
"""

import warnings


def __getattr__(name):
    """Lazy import for workflow classes to avoid requiring temporalio at import time."""
    if name in ("UserOnboardingWorkflow", "BatchProcessingWorkflow"):
        warnings.warn(
            f"Importing '{name}' requires temporalio to be installed. "
            "Install with: pip install temporalio",
            DeprecationWarning,
            stacklevel=2,
        )
        from django_rseal.workflows.temporal import workflows

        return getattr(workflows, name)
    if name in ("OnboardingWorkflowInput", "BatchProcessingWorkflowInput"):
        from django_rseal.workflows.temporal import workflows

        return getattr(workflows, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# Activities can be imported directly - they don't require temporalio
from django_rseal.workflows.temporal.activities import (
    EmailPayload,
    UserProcessingPayload,
    process_user_activity,
    send_email_activity,
)

__all__ = [
    # Activities
    "EmailPayload",
    "UserProcessingPayload",
    "send_email_activity",
    "process_user_activity",
    # Workflows (lazy-loaded, require temporalio)
    "OnboardingWorkflowInput",
    "BatchProcessingWorkflowInput",
    "UserOnboardingWorkflow",
    "BatchProcessingWorkflow",
]
