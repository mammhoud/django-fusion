from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from ceptor_ai.pipelines.models import Person


class NotificationSettingsForm(forms.Form):
    # Email Notifications
    course_updates = forms.BooleanField(
        label=_("Course updates and announcements"),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'role': 'switch'
        })
    )
    
    instructor_messages = forms.BooleanField(
        label=_("New messages from instructors"),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'role': 'switch'
        })
    )
    
    marketing_emails = forms.BooleanField(
        label=_("Marketing and promotional emails"),
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'role': 'switch'
        })
    )
    
    weekly_reports = forms.BooleanField(
        label=_("Weekly progress reports"),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'role': 'switch'
        })
    )
    
    # Push Notifications
    assignment_notifications = forms.BooleanField(
        label=_("New course assignments"),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'role': 'switch'
        })
    )
    
    forum_activity = forms.BooleanField(
        label=_("Forum activity"),
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'role': 'switch'
        })
    )
    
    deadline_reminders = forms.BooleanField(
        label=_("Deadline reminders"),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'role': 'switch'
        })
    )
    
    # SMS Notifications
    sms_notifications = forms.BooleanField(
        label=_("Enable SMS notifications for urgent updates"),
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'role': 'switch'
        }),
        help_text=_("Standard carrier rates may apply")
    )
    
    # Notification Frequency
    NOTIFICATION_FREQUENCY_CHOICES = [
        ('realtime', _('Real-time')),
        ('daily', _('Daily digest')),
        ('weekly', _('Weekly summary')),
    ]
    
    notification_frequency = forms.ChoiceField(
        label=_("Notification Frequency"),
        choices=NOTIFICATION_FREQUENCY_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        initial='realtime'
    )
