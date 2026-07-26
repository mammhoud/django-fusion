"""
Test notification API endpoints using Django TestCase.
Run with: python manage.py test tests.test_notifications -v 2
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
import json

from plugins.lms.models import Notification, NotificationPreference


class NotificationAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testnotif', password='testpass123'
        )
        self.client.login(username='testnotif', password='testpass123')

        # Create 3 test notifications
        for i in range(3):
            Notification.objects.create(
                user=self.user,
                notification_type='system',
                title=f'Test Notification {i+1}',
                message=f'This is test notification number {i+1}',
            )

        # Ensure NotificationPreference exists
        NotificationPreference.objects.get_or_create(user=self.user)

    def test_01_notification_list(self):
        """GET /apis/notifications/ — list notifications"""
        response = self.client.get('/apis/notifications/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        results = data.get('results', [])
        self.assertEqual(len(results), 3)
        for n in results:
            self.assertIn('id', n)
            self.assertIn('type', n)
            self.assertIn('title', n)

    def test_02_unread_count(self):
        """GET /apis/notifications/unread-count/"""
        response = self.client.get('/apis/notifications/unread-count/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['data']['unread_count'], 3)

    def test_03_mark_all_read(self):
        """POST /apis/notifications/mark-all-read/"""
        response = self.client.post('/apis/notifications/mark-all-read/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['data']['marked_read'], 3)

        # Verify unread count is now 0
        response = self.client.get('/apis/notifications/unread-count/')
        data = json.loads(response.content)
        self.assertEqual(data['data']['unread_count'], 0)

    def test_04_mark_single_read(self):
        """PATCH /apis/notifications/<pk>/read/"""
        n = Notification.objects.create(
            user=self.user,
            notification_type='quiz',
            title='Single Read Test',
        )
        response = self.client.patch(f'/apis/notifications/{n.id}/read/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['data']['is_read'])

    def test_05_dismiss(self):
        """DELETE /apis/notifications/<pk>/"""
        n = Notification.objects.create(
            user=self.user,
            notification_type='system',
            title='Dismiss Test',
        )
        response = self.client.delete(f'/apis/notifications/{n.id}/')
        self.assertEqual(response.status_code, 200)
        n.refresh_from_db()
        self.assertTrue(n.is_dismissed)

    def test_06_preferences_get(self):
        """GET /apis/notifications/preferences/"""
        response = self.client.get('/apis/notifications/preferences/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        prefs = data['data']
        self.assertTrue(prefs['in_app_notifications'])
        self.assertTrue(prefs['email_notifications'])
        self.assertEqual(prefs['digest_frequency'], 'immediate')

    def test_07_preferences_update(self):
        """PATCH /apis/notifications/preferences/update/"""
        response = self.client.patch(
            '/apis/notifications/preferences/update/',
            json.dumps({'quiz_notifications': False, 'digest_frequency': 'daily'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        prefs = data['data']
        self.assertFalse(prefs['quiz_notifications'])
        self.assertEqual(prefs['digest_frequency'], 'daily')

    def test_08_create_notification_trigger(self):
        """Test create_notification helper function"""
        from www.api.notifications import create_notification

        result = create_notification(
            user=self.user,
            notification_type='enrollment',
            title='Trigger Test',
            message='Created via trigger',
            link='/dashboard/',
        )
        self.assertIsNotNone(result)
        self.assertEqual(result['type'], 'enrollment')
        self.assertEqual(result['title'], 'Trigger Test')

        # Verify it was saved to DB
        self.assertEqual(
            Notification.objects.filter(user=self.user).count(), 4
        )

    def test_09_notification_preferences_block(self):
        """Test create_notification respects disabled prefs"""
        from www.api.notifications import create_notification

        pref = NotificationPreference.objects.get(user=self.user)
        pref.quiz_notifications = False
        pref.save()

        result = create_notification(
            user=self.user,
            notification_type='quiz',
            title='Should be blocked',
            message='This should not appear',
        )
        self.assertIsNone(result)
