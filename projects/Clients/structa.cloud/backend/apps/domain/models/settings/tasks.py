import logging

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel
from wagtail.models import Task, TaskState

logger = logging.getLogger(__name__)


class UserApprovalTaskState(TaskState):
    """
    Custom task state for UserApprovalTask.
    Tracks per-instance state during workflow approval.
    """



class UserApprovalTask(Task):
    """
    A custom Wagtail workflow task that restricts approval to a specific user.
    Useful for cases where only one designated editor or admin should approve
    a specific page or workflow step.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        verbose_name=_("Assigned Approver"),
        help_text=_("Only this user can approve or reject this task."),
    )

    # ------------------------------------------------------------------
    # CONFIGURATION
    # ------------------------------------------------------------------
    admin_form_fields = Task.admin_form_fields + ["user"]
    task_state_class = UserApprovalTaskState

    # Prevent editing the assigned approver after creation
    admin_form_readonly_on_edit_fields = Task.admin_form_readonly_on_edit_fields + ["user"]

    panels = [
        FieldPanel("user"),
    ]

    # ------------------------------------------------------------------
    # ACCESS CONTROL
    # ------------------------------------------------------------------
    def user_can_access_editor(self, page, user):
        """
        Only the assigned approver can edit the page when this task is active.
        """
        can_access = user == self.user
        logger.debug(
            f"User {user} attempted editor access for page '{page.title}'. Allowed: {can_access}"
        )
        return can_access

    def page_locked_for_user(self, page, user):
        """
        Lock the page for everyone except the assigned approver.
        """
        locked = user != self.user
        logger.debug(f"Page '{page.title}' locked for {user}: {locked}")
        return locked

    # ------------------------------------------------------------------
    # TASK ACTIONS
    # ------------------------------------------------------------------
    def get_actions(self, page, user):
        """
        Return available workflow actions for this user.
        Only the assigned approver can take action.
        """
        if user == self.user:
            return [
                ("approve", _("Approve"), False),
                ("reject", _("Reject"), False),
                ("cancel", _("Cancel"), False),
            ]
        return []

    def on_action(self, task_state, user, action_name, **kwargs):
        """
        Handle user actions (approve, reject, cancel).
        """
        if not self.user:
            logger.warning(f"UserApprovalTask '{self.name}' has no assigned user.")
            return super().on_action(task_state, user, action_name, **kwargs)

        if action_name == "cancel":
            logger.info(f"User {user} canceled task {self.name}.")
            return task_state.workflow_state.cancel(user=user)
        elif action_name in ["approve", "reject"]:
            logger.info(f"User {user} performed '{action_name}' on task {self.name}.")
            return super().on_action(task_state, user, action_name, **kwargs)

        logger.warning(f"Unknown action '{action_name}' by {user} on task {self.name}.")
        return super().on_action(task_state, user, action_name, **kwargs)

    # ------------------------------------------------------------------
    # MODERATION
    # ------------------------------------------------------------------
    def get_task_states_user_can_moderate(self, user, **kwargs):
        """
        Limit moderation access to task states assigned to this user.
        """
        if user == self.user:
            return TaskState.objects.filter(
                status=TaskState.STATUS_IN_PROGRESS,
                task=self.task_ptr,
            )
        return TaskState.objects.none()

    # ------------------------------------------------------------------
    # DESCRIPTION
    # ------------------------------------------------------------------
    @classmethod
    def get_description(cls):
        """
        Description for admin/workflow interfaces.
        """
        return _("Only the assigned user can approve or reject this task.")

    def __str__(self):
        approver = self.user.get_full_name() if self.user else _("(Unassigned)")
        return f"{self.name} — {approver}"
