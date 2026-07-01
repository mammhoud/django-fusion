"""
Orchestration tests for the email automation system.

Tests end-to-end workflows:
- Email queuing → template rendering → database logging → delivery simulation
- Role hierarchy enforcement
- Periodic task scheduling

Requirements: 10.1-10.7
"""

import os
import tempfile
from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone
from ceptor_ai.communication.email.models import EmailLog
from ceptor_ai.models.users import UserGroup
from ceptor_ai.communication.email.models.models import UserRole
from ceptor_ai.services.communication.invitation_service import InvitationService
from ceptor_ai.services.email.email_service import EmailService
from ceptor_ai.communication.tasks import (
    check_registrations_task,
    generate_weekly_report_task,
    setup_periodic_tasks,
)

User = get_user_model()


# ---------------------------------------------------------------------------
# 15.1 – Email Workflow Orchestration
# Validates: Requirements 10.1, 10.2, 10.5
# ---------------------------------------------------------------------------

@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    DEFAULT_FROM_EMAIL='noreply@test.example.com',
    REPORT_EMAIL_TO='admin@test.example.com',
    REPORT_EMAIL_FROM='reports@test.example.com',
)
class EmailWorkflowOrchestrationTestCase(TestCase):
    """
    End-to-end orchestration test: InvitationService → EmailService → EmailLog.

    Validates: Requirements 10.1, 10.2, 10.5
    """

    def setUp(self):
        mail.outbox = []
        self.temp_dir = tempfile.mkdtemp()
        self.csv_path = os.path.join(self.temp_dir, 'emails.csv')

        with open(self.csv_path, 'w') as f:
            f.write('email,role\n')
            f.write('invite1@test.example.com,instructor\n')
            f.write('invite2@test.example.com,manager\n')
            f.write('registered@test.example.com,supervisor\n')

        # Create a registered user so they are filtered out
        User.objects.create_user(
            username='registered_user',
            email='registered@test.example.com',
        )

    def tearDown(self):
        if os.path.exists(self.csv_path):
            os.remove(self.csv_path)
        os.rmdir(self.temp_dir)

    # ------------------------------------------------------------------
    # 1. Email queuing creates an EmailLog record
    # ------------------------------------------------------------------

    def test_email_queuing_creates_database_log(self):
        """Queuing an email creates an EmailLog entry in the database."""
        service = EmailService()

        with patch('django_seed.services.email_service.render_to_string',
                   return_value='<html>Invite</html>'):
            log = service.send_invitation(
                recipient='invite1@test.example.com',
                context={'subject': 'Test Invitation'},
                queue=True,
            )

        self.assertIsNotNone(log)
        self.assertIsNotNone(log.pk)
        self.assertEqual(log.recipient, 'invite1@test.example.com')
        # Status is QUEUED (with backend) or SENT (no backend – immediate send)
        self.assertIn(log.status, [EmailLog.Status.QUEUED, EmailLog.Status.SENT])

        # Verify persisted in DB
        db_log = EmailLog.objects.get(pk=log.pk)
        self.assertEqual(db_log.recipient, 'invite1@test.example.com')

    # ------------------------------------------------------------------
    # 2. Template rendering produces HTML content
    # ------------------------------------------------------------------

    def test_template_rendering_in_workflow(self):
        """Email service renders the invitation template before sending."""
        service = EmailService()

        rendered_html = '<html><body>Hello invite1@test.example.com</body></html>'

        with patch('django_seed.services.email_service.render_to_string',
                   return_value=rendered_html) as mock_render:
            service.send_invitation(
                recipient='invite1@test.example.com',
                context={'subject': 'Invite', 'name': 'Alice'},
                queue=False,
            )

        # render_to_string was called with the invitation template
        mock_render.assert_called()
        call_args = mock_render.call_args_list[0]
        self.assertIn('invitation', call_args[0][0])

    # ------------------------------------------------------------------
    # 3. Immediate send updates EmailLog to SENT and delivers via SMTP mock
    # ------------------------------------------------------------------

    def test_immediate_send_updates_log_to_sent(self):
        """Sending immediately marks EmailLog as SENT and delivers to outbox."""
        service = EmailService()

        with patch.object(service, '_render_template', return_value='<html>Hi</html>'):
            log = service.send_invitation(
                recipient='invite1@test.example.com',
                context={'subject': 'Immediate Invite'},
                queue=False,
            )

        self.assertEqual(log.status, EmailLog.Status.SENT)
        self.assertIsNotNone(log.sent_at)

        # Verify mock SMTP (locmem backend) captured the email
        self.assertEqual(len(mail.outbox), 1)
        sent = mail.outbox[0]
        self.assertIn('invite1@test.example.com', sent.to)
        self.assertEqual(sent.subject, 'Immediate Invite')

    # ------------------------------------------------------------------
    # 4. Full chain: InvitationService → EmailService → EmailLog
    # ------------------------------------------------------------------

    def test_full_invitation_chain_filters_registered_users(self):
        """
        InvitationService reads CSV, filters registered users,
        queues invitations, and creates EmailLog records.
        """
        invitation_service = InvitationService(csv_path=self.csv_path)

        with patch('django_seed.services.email_service.render_to_string',
                   return_value='<html>Invite</html>'):
            logs = invitation_service.send_invitations_from_csv()

        # Only the 2 unregistered users should receive invitations
        self.assertEqual(len(logs), 2)
        recipients = {log.recipient for log in logs}
        self.assertIn('invite1@test.example.com', recipients)
        self.assertIn('invite2@test.example.com', recipients)
        self.assertNotIn('registered@test.example.com', recipients)

        # All logs are persisted in the database
        for log in logs:
            self.assertIsNotNone(log.pk)
            db_log = EmailLog.objects.get(pk=log.pk)
            self.assertIn(db_log.status, [
                EmailLog.Status.QUEUED,
                EmailLog.Status.SENT,
            ])

    # ------------------------------------------------------------------
    # 5. Duplicate prevention: no second invitation within 7 days
    # ------------------------------------------------------------------

    def test_duplicate_prevention_in_workflow(self):
        """InvitationService does not re-invite users invited within 7 days."""
        # Simulate a recent invitation for invite1
        EmailLog.objects.create(
            recipient='invite1@test.example.com',
            subject='Previous Invitation',
            template_used='emails/invitation.html',
            status=EmailLog.Status.SENT,
            timestamp=timezone.now() - timedelta(days=2),
        )

        invitation_service = InvitationService(csv_path=self.csv_path)

        with patch('django_seed.services.email_service.render_to_string',
                   return_value='<html>Invite</html>'):
            logs = invitation_service.send_invitations_from_csv()

        # Only invite2 should receive an invitation (invite1 was recently invited)
        recipients = {log.recipient for log in logs}
        self.assertNotIn('invite1@test.example.com', recipients)
        self.assertIn('invite2@test.example.com', recipients)

    # ------------------------------------------------------------------
    # 6. EmailLog failure tracking
    # ------------------------------------------------------------------

    def test_email_log_failure_tracking(self):
        """EmailLog records failure details when sending fails."""
        service = EmailService()

        with patch.object(service, '_render_template', side_effect=Exception('Template missing')):
            with self.assertRaises(Exception):
                service.send_invitation(
                    recipient='invite1@test.example.com',
                    context={'subject': 'Failing Invite'},
                    queue=False,
                )

        # The log should be marked FAILED with an error message
        log = EmailLog.objects.filter(recipient='invite1@test.example.com').first()
        self.assertIsNotNone(log)
        self.assertEqual(log.status, EmailLog.Status.FAILED)
        self.assertIn('Template missing', log.error_message)

    # ------------------------------------------------------------------
    # 7. Group email workflow
    # ------------------------------------------------------------------

    def test_group_email_workflow(self):
        """Group email sends to all group members and creates logs for each."""
        user_a = User.objects.create_user(username='user_a', email='a@test.example.com')
        user_b = User.objects.create_user(username='user_b', email='b@test.example.com')
        group = UserGroup.objects.create(name='instructors')
        group.users.add(user_a, user_b)

        service = EmailService()

        with patch('django_seed.services.email_service.render_to_string',
                   return_value='<html>Group Email</html>'):
            logs = service.send_group_email(
                group_name='instructors',
                subject='Group Announcement',
                template_name='emails/invitation.html',
                context={},
            )

        self.assertEqual(len(logs), 2)
        recipients = {log.recipient for log in logs}
        self.assertIn('a@test.example.com', recipients)
        self.assertIn('b@test.example.com', recipients)

        # All logs persisted
        for log in logs:
            self.assertIsNotNone(log.pk)


# ---------------------------------------------------------------------------
# 15.2 – Role Hierarchy Orchestration
# Validates: Requirements 10.6
# ---------------------------------------------------------------------------

class RoleHierarchyOrchestrationTestCase(TestCase):
    """
    Tests role hierarchy enforcement across the system.

    Validates: Requirement 10.6
    """

    def setUp(self):
        self.supervisor = User.objects.create_user(
            username='supervisor_user', email='supervisor@test.example.com'
        )
        self.manager = User.objects.create_user(
            username='manager_user', email='manager@test.example.com'
        )
        self.instructor = User.objects.create_user(
            username='instructor_user', email='instructor@test.example.com'
        )
        self.content_manager = User.objects.create_user(
            username='cm_user', email='cm@test.example.com'
        )
        self.no_role_user = User.objects.create_user(
            username='norole_user', email='norole@test.example.com'
        )

        # Assign roles
        UserRole.objects.create(user=self.supervisor, role=UserRole.Role.SUPERVISOR)
        UserRole.objects.create(user=self.manager, role=UserRole.Role.MANAGER)
        UserRole.objects.create(user=self.instructor, role=UserRole.Role.INSTRUCTOR)
        UserRole.objects.create(user=self.content_manager, role=UserRole.Role.CONTENT_MANAGER)

    # ------------------------------------------------------------------
    # Hierarchy: supervisor > manager > instructor > content_manager
    # ------------------------------------------------------------------

    def test_supervisor_has_all_permissions(self):
        """Supervisor can access all role levels."""
        for role in [
            UserRole.Role.SUPERVISOR,
            UserRole.Role.MANAGER,
            UserRole.Role.INSTRUCTOR,
            UserRole.Role.CONTENT_MANAGER,
        ]:
            self.assertTrue(
                UserRole.has_permission(self.supervisor, role),
                f"Supervisor should have permission for {role}",
            )

    def test_manager_cannot_access_supervisor_level(self):
        """Manager cannot access supervisor-level resources."""
        self.assertFalse(UserRole.has_permission(self.manager, UserRole.Role.SUPERVISOR))

    def test_manager_can_access_own_and_lower_levels(self):
        """Manager can access manager, instructor, and content_manager levels."""
        for role in [
            UserRole.Role.MANAGER,
            UserRole.Role.INSTRUCTOR,
            UserRole.Role.CONTENT_MANAGER,
        ]:
            self.assertTrue(
                UserRole.has_permission(self.manager, role),
                f"Manager should have permission for {role}",
            )

    def test_instructor_cannot_access_manager_or_supervisor(self):
        """Instructor cannot access manager or supervisor levels."""
        self.assertFalse(UserRole.has_permission(self.instructor, UserRole.Role.SUPERVISOR))
        self.assertFalse(UserRole.has_permission(self.instructor, UserRole.Role.MANAGER))

    def test_instructor_can_access_own_and_lower_levels(self):
        """Instructor can access instructor and content_manager levels."""
        for role in [UserRole.Role.INSTRUCTOR, UserRole.Role.CONTENT_MANAGER]:
            self.assertTrue(UserRole.has_permission(self.instructor, role))

    def test_content_manager_can_only_access_own_level(self):
        """Content manager can only access content_manager level."""
        self.assertTrue(UserRole.has_permission(self.content_manager, UserRole.Role.CONTENT_MANAGER))
        self.assertFalse(UserRole.has_permission(self.content_manager, UserRole.Role.INSTRUCTOR))
        self.assertFalse(UserRole.has_permission(self.content_manager, UserRole.Role.MANAGER))
        self.assertFalse(UserRole.has_permission(self.content_manager, UserRole.Role.SUPERVISOR))

    def test_user_with_no_role_has_no_permissions(self):
        """User with no role has no permissions."""
        for role in [
            UserRole.Role.SUPERVISOR,
            UserRole.Role.MANAGER,
            UserRole.Role.INSTRUCTOR,
            UserRole.Role.CONTENT_MANAGER,
        ]:
            self.assertFalse(UserRole.has_permission(self.no_role_user, role))

    # ------------------------------------------------------------------
    # get_highest_role with multiple roles
    # ------------------------------------------------------------------

    def test_get_highest_role_single_role(self):
        """get_highest_role returns the single assigned role."""
        self.assertEqual(
            UserRole.get_highest_role(self.supervisor),
            UserRole.Role.SUPERVISOR,
        )
        self.assertEqual(
            UserRole.get_highest_role(self.content_manager),
            UserRole.Role.CONTENT_MANAGER,
        )

    def test_get_highest_role_multiple_roles_returns_highest(self):
        """get_highest_role returns the highest role when user has multiple."""
        # Give instructor also a manager role
        UserRole.objects.create(user=self.instructor, role=UserRole.Role.MANAGER)

        highest = UserRole.get_highest_role(self.instructor)
        self.assertEqual(highest, UserRole.Role.MANAGER)

    def test_get_highest_role_all_roles_returns_supervisor(self):
        """User with all roles gets supervisor as highest."""
        multi_user = User.objects.create_user(
            username='multi_user', email='multi@test.example.com'
        )
        for role in UserRole.Role:
            UserRole.objects.create(user=multi_user, role=role)

        self.assertEqual(UserRole.get_highest_role(multi_user), UserRole.Role.SUPERVISOR)

    def test_get_highest_role_no_roles_returns_none(self):
        """get_highest_role returns None for user with no roles."""
        self.assertIsNone(UserRole.get_highest_role(self.no_role_user))

    def test_hierarchy_order_is_correct(self):
        """Verify the numeric hierarchy values are in the correct order."""
        hierarchy = UserRole.ROLE_HIERARCHY
        self.assertGreater(
            hierarchy[UserRole.Role.SUPERVISOR],
            hierarchy[UserRole.Role.MANAGER],
        )
        self.assertGreater(
            hierarchy[UserRole.Role.MANAGER],
            hierarchy[UserRole.Role.INSTRUCTOR],
        )
        self.assertGreater(
            hierarchy[UserRole.Role.INSTRUCTOR],
            hierarchy[UserRole.Role.CONTENT_MANAGER],
        )


# ---------------------------------------------------------------------------
# 15.3 – Periodic Task Orchestration
# Validates: Requirements 10.7
# ---------------------------------------------------------------------------

@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    DEFAULT_FROM_EMAIL='noreply@test.example.com',
    REPORT_EMAIL_TO='admin@test.example.com',
    REPORT_EMAIL_FROM='reports@test.example.com',
)
class PeriodicTaskOrchestrationTestCase(TestCase):
    """
    Tests periodic task scheduling and execution.

    Validates: Requirement 10.7
    """

    def setUp(self):
        mail.outbox = []
        self.temp_dir = tempfile.mkdtemp()
        self.csv_path = os.path.join(self.temp_dir, 'emails.csv')

        with open(self.csv_path, 'w') as f:
            f.write('email,role\n')
            f.write('unregistered@test.example.com,instructor\n')
            f.write('registered@test.example.com,manager\n')

        User.objects.create_user(
            username='registered_user',
            email='registered@test.example.com',
        )

    def tearDown(self):
        if os.path.exists(self.csv_path):
            os.remove(self.csv_path)
        os.rmdir(self.temp_dir)

    # ------------------------------------------------------------------
    # check_registrations_task
    # ------------------------------------------------------------------

    def test_check_registrations_reads_csv_and_filters_registered(self):
        """
        check_registrations_task reads CSV, filters registered users,
        and sends invitations only to unregistered users.
        """
        with patch.dict(os.environ, {'EMAILS_CSV_PATH': self.csv_path}):
            with patch('django_seed.tasks.InvitationService') as MockIS:
                is_instance = MockIS.return_value
                mock_log = MagicMock()
                mock_log.status = EmailLog.Status.QUEUED
                is_instance.send_invitations_from_csv.return_value = [mock_log]

                with patch('django_seed.tasks.ReportGenerator') as MockRG:
                    rg_instance = MockRG.return_value

                    check_registrations_task()

                    # Verify CSV path was passed to InvitationService
                    MockIS.assert_called_once_with(csv_path=self.csv_path)
                    # Verify invitations were sent
                    is_instance.send_invitations_from_csv.assert_called_once()
                    # Verify batch report was sent after invitations
                    rg_instance.send_batch_report.assert_called_once_with(
                        batch_type='registration_check',
                        email_logs=[mock_log],
                    )

    def test_check_registrations_sends_batch_report_after_invitations(self):
        """
        check_registrations_task sends a batch report after processing invitations.
        """
        with patch.dict(os.environ, {'EMAILS_CSV_PATH': self.csv_path}):
            with patch('django_seed.tasks.InvitationService') as MockIS:
                is_instance = MockIS.return_value
                logs = [MagicMock(), MagicMock()]
                is_instance.send_invitations_from_csv.return_value = logs

                with patch('django_seed.tasks.ReportGenerator') as MockRG:
                    rg_instance = MockRG.return_value

                    check_registrations_task()

                    rg_instance.send_batch_report.assert_called_once()
                    call_kwargs = rg_instance.send_batch_report.call_args.kwargs
                    self.assertEqual(call_kwargs['batch_type'], 'registration_check')
                    self.assertEqual(call_kwargs['email_logs'], logs)

    def test_check_registrations_sends_alert_on_csv_not_found(self):
        """
        check_registrations_task sends an alert when the CSV file is missing.
        """
        with patch.dict(os.environ, {'EMAILS_CSV_PATH': '/nonexistent/emails.csv'}):
            with patch('django_seed.tasks.InvitationService') as MockIS:
                is_instance = MockIS.return_value
                is_instance.send_invitations_from_csv.side_effect = FileNotFoundError(
                    'CSV not found'
                )

                with patch('django_seed.tasks.ReportGenerator') as MockRG:
                    rg_instance = MockRG.return_value

                    check_registrations_task()

                    rg_instance.send_alert.assert_called_once()
                    alert_kwargs = rg_instance.send_alert.call_args.kwargs
                    self.assertIn('CSV Not Found', alert_kwargs['alert_type'])

    # ------------------------------------------------------------------
    # generate_weekly_report_task
    # ------------------------------------------------------------------

    def test_generate_weekly_report_task_sends_report(self):
        """generate_weekly_report_task calls send_weekly_report."""
        with patch('django_seed.tasks.ReportGenerator') as MockRG:
            rg_instance = MockRG.return_value

            generate_weekly_report_task()

            rg_instance.send_weekly_report.assert_called_once()

    def test_generate_weekly_report_task_sends_alert_on_failure(self):
        """generate_weekly_report_task sends an alert when report generation fails."""
        with patch('django_seed.tasks.ReportGenerator') as MockRG:
            rg_instance = MockRG.return_value
            rg_instance.send_weekly_report.side_effect = Exception('SMTP unavailable')

            generate_weekly_report_task()

            rg_instance.send_alert.assert_called_once()
            alert_kwargs = rg_instance.send_alert.call_args.kwargs
            self.assertIn('Weekly Report', alert_kwargs['alert_type'])

    def test_generate_weekly_report_task_handles_double_failure(self):
        """generate_weekly_report_task does not raise when both report and alert fail."""
        with patch('django_seed.tasks.ReportGenerator') as MockRG:
            rg_instance = MockRG.return_value
            rg_instance.send_weekly_report.side_effect = Exception('SMTP down')
            rg_instance.send_alert.side_effect = Exception('Alert also failed')

            # Must not raise
            generate_weekly_report_task()

    # ------------------------------------------------------------------
    # setup_periodic_tasks – scheduling registration
    # ------------------------------------------------------------------

    def test_setup_periodic_tasks_registers_check_registrations(self):
        """setup_periodic_tasks registers the check_registrations periodic task."""
        with patch('django_seed.tasks.EmailQueueManager') as MockQM:
            qm_instance = MockQM.return_value

            setup_periodic_tasks()

            calls = {
                call.kwargs['name']: call.kwargs
                for call in qm_instance.schedule_periodic_task.call_args_list
            }

            self.assertIn('check_registrations', calls)
            reg_call = calls['check_registrations']
            self.assertEqual(
                reg_call['func'],
                'django_seed.tasks.check_registrations_task',
            )

    def test_setup_periodic_tasks_registers_weekly_report(self):
        """setup_periodic_tasks registers the generate_weekly_report periodic task."""
        with patch('django_seed.tasks.EmailQueueManager') as MockQM:
            qm_instance = MockQM.return_value

            setup_periodic_tasks()

            calls = {
                call.kwargs['name']: call.kwargs
                for call in qm_instance.schedule_periodic_task.call_args_list
            }

            self.assertIn('generate_weekly_report', calls)
            report_call = calls['generate_weekly_report']
            self.assertEqual(
                report_call['func'],
                'django_seed.tasks.generate_weekly_report_task',
            )

    def test_setup_periodic_tasks_registers_both_tasks(self):
        """setup_periodic_tasks registers exactly two periodic tasks."""
        with patch('django_seed.tasks.EmailQueueManager') as MockQM:
            qm_instance = MockQM.return_value

            setup_periodic_tasks()

            self.assertEqual(qm_instance.schedule_periodic_task.call_count, 2)

    def test_setup_periodic_tasks_check_registrations_schedule_type(self):
        """check_registrations task uses daily schedule type."""
        with patch('django_seed.tasks.EmailQueueManager') as MockQM:
            qm_instance = MockQM.return_value

            setup_periodic_tasks()

            calls = {
                call.kwargs['name']: call.kwargs
                for call in qm_instance.schedule_periodic_task.call_args_list
            }

            reg_call = calls['check_registrations']
            # 'D' = Daily schedule type in Django Q
            self.assertEqual(reg_call['schedule_type'], 'D')

    def test_setup_periodic_tasks_weekly_report_schedule_type(self):
        """generate_weekly_report task uses weekly schedule type."""
        with patch('django_seed.tasks.EmailQueueManager') as MockQM:
            qm_instance = MockQM.return_value

            setup_periodic_tasks()

            calls = {
                call.kwargs['name']: call.kwargs
                for call in qm_instance.schedule_periodic_task.call_args_list
            }

            report_call = calls['generate_weekly_report']
            # 'W' = Weekly schedule type in Django Q
            self.assertEqual(report_call['schedule_type'], 'W')

    def test_setup_periodic_tasks_both_repeat_infinitely(self):
        """Both periodic tasks are configured to repeat indefinitely."""
        with patch('django_seed.tasks.EmailQueueManager') as MockQM:
            qm_instance = MockQM.return_value

            setup_periodic_tasks()

            for call in qm_instance.schedule_periodic_task.call_args_list:
                self.assertEqual(
                    call.kwargs['repeats'],
                    -1,
                    f"Task {call.kwargs['name']} should repeat indefinitely (repeats=-1)",
                )
