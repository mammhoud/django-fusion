"""
Temporal Workflows for Django RSeal.

Workflows are the orchestration layer for Temporal. They coordinate activities
and handle the business logic flow.

Best Practices:
- Workflows must be deterministic
- Use workflow.execute_activity() to call activities
- Don't make direct external calls from workflows
- Use workflow.sleep() instead of asyncio.sleep()
- Use single dataclass argument pattern for backwards compatibility
"""

from dataclasses import dataclass
from datetime import timedelta

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class OnboardingWorkflowInput:
    """Input for user onboarding workflow."""

    user_id: int
    email: str
    name: str


@dataclass
class BatchProcessingWorkflowInput:
    """Input for batch processing workflow."""

    batch_id: str
    user_ids: list[int]


def create_user_onboarding_workflow():
    """
    Factory function to create UserOnboardingWorkflow class.

    This approach avoids direct temporalio imports at module level,
    making the module more testable and avoiding import errors
    when temporalio is not installed.
    """
    from temporalio import workflow
    from temporalio.common import RetryPolicy

    # Import activities using with_imports_passed_through if needed
    with workflow.unsafe.imports_passed_through():
        from ceptor_ai.workflows.temporal.activities import (
            EmailPayload,
            UserProcessingPayload,
            process_user_activity,
            send_email_activity,
        )

    @workflow.defn(name="user_onboarding")
    class UserOnboardingWorkflow:
        """
        User onboarding workflow.

        This workflow demonstrates:
        - Multi-step orchestration
        - Activity execution with retries
        - Error handling
        - Workflow sleep/delays
        """

        @workflow.run
        async def run(self, input: OnboardingWorkflowInput) -> dict:
            """Execute the user onboarding workflow."""
            workflow.logger.info(
                "Starting user onboarding",
                user_id=input.user_id,
                email=input.email,
            )

            # Step 1: Process user
            process_result = await workflow.execute_activity(
                process_user_activity,
                UserProcessingPayload(user_id=input.user_id, action="onboard"),
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    maximum_interval=timedelta(seconds=10),
                    maximum_attempts=3,
                ),
            )

            workflow.logger.info("User processed", result=process_result)

            # Step 2: Send welcome email
            email_result = await workflow.execute_activity(
                send_email_activity,
                EmailPayload(
                    to=input.email,
                    subject=f"Welcome, {input.name}!",
                    body=f"Hello {input.name},\n\nWelcome! We're excited to have you on board.",
                ),
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    maximum_interval=timedelta(seconds=10),
                    maximum_attempts=3,
                ),
            )

            workflow.logger.info("Welcome email sent", result=email_result)

            # Step 3: Wait for 24 hours before sending follow-up
            workflow.logger.info("Waiting 24 hours before follow-up")
            await workflow.sleep(timedelta(hours=24))

            # Step 4: Send follow-up email
            followup_result = await workflow.execute_activity(
                send_email_activity,
                EmailPayload(
                    to=input.email,
                    subject="How are you liking our service?",
                    body=f"Hi {input.name},\n\nJust checking in to see how you're finding our service. Let us know if you have any questions!",
                ),
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    maximum_interval=timedelta(seconds=10),
                    maximum_attempts=3,
                ),
            )

            workflow.logger.info("Follow-up email sent", result=followup_result)

            return {
                "status": "completed",
                "user_id": input.user_id,
                "steps_completed": ["process_user", "welcome_email", "followup_email"],
            }

    return UserOnboardingWorkflow


def create_batch_processing_workflow():
    """
    Factory function to create BatchProcessingWorkflow class.

    This approach avoids direct temporalio imports at module level,
    making the module more testable and avoiding import errors
    when temporalio is not installed.
    """
    from temporalio import workflow
    from temporalio.common import RetryPolicy

    # Import activities using with_imports_passed_through if needed
    with workflow.unsafe.imports_passed_through():
        from ceptor_ai.workflows.temporal.activities import (
            UserProcessingPayload,
            process_user_activity,
        )

    @workflow.defn(name="batch_processing")
    class BatchProcessingWorkflow:
        """
        Batch processing workflow.

        Demonstrates parallel activity execution.
        """

        @workflow.run
        async def run(self, input: BatchProcessingWorkflowInput) -> dict:
            """Execute batch processing workflow."""
            workflow.logger.info(
                "Starting batch processing",
                batch_id=input.batch_id,
                count=len(input.user_ids),
            )

            # Process all users in parallel
            tasks = []
            for user_id in input.user_ids:
                task = workflow.execute_activity(
                    process_user_activity,
                    UserProcessingPayload(user_id=user_id, action="batch_process"),
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=RetryPolicy(
                        initial_interval=timedelta(seconds=1),
                        maximum_interval=timedelta(seconds=10),
                        maximum_attempts=3,
                    ),
                )
                tasks.append(task)

            # Wait for all tasks to complete
            results = await workflow.asyncio.gather(*tasks, return_exceptions=True)

            # Count successes and failures
            successes = sum(1 for r in results if not isinstance(r, Exception))
            failures = len(results) - successes

            workflow.logger.info(
                "Batch processing completed",
                batch_id=input.batch_id,
                successes=successes,
                failures=failures,
            )

            return {
                "status": "completed",
                "batch_id":input.batch_id,
                "total": len(input.user_ids),
                "successes": successes,
                "failures": failures,
            }

    return BatchProcessingWorkflow


# Lazy-loaded workflow classes
# These are created on first access to avoid temporalio import at module level
class _LazyWorkflowLoader:
    """Lazy loader for workflow classes."""

    _UserOnboardingWorkflow = None
    _BatchProcessingWorkflow = None

    @property
    def UserOnboardingWorkflow(self):
        if self._UserOnboardingWorkflow is None:
            self._UserOnboardingWorkflow = create_user_onboarding_workflow()
        return self._UserOnboardingWorkflow

    @property
    def BatchProcessingWorkflow(self):
        if self._BatchProcessingWorkflow is None:
            self._BatchProcessingWorkflow = create_batch_processing_workflow()
        return self._BatchProcessingWorkflow


_workflow_loader = _LazyWorkflowLoader()

# Export workflow classes via property accessors
# This allows importing without requiring temporalio at import time
UserOnboardingWorkflow = _workflow_loader.UserOnboardingWorkflow
BatchProcessingWorkflow = _workflow_loader.BatchProcessingWorkflow
