"""Course enrollment forms."""

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from plugins.lms.models import CourseEnrollmentLead


class CourseEnrollmentForm(forms.ModelForm):
    """Form for capturing course enrollment leads."""

    agree_terms = forms.BooleanField(
        required=True,
        label=_("I agree to the terms and conditions"),
        help_text=_("You must agree to the terms to proceed"),
    )

    class Meta:
        model = CourseEnrollmentLead
        fields = ['full_name', 'email', 'phone', 'notes']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Your full name'),
                'required': 'required',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('your@email.com'),
                'required': 'required',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('+1 (555) 000-0000'),
                'type': 'tel',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': _('Any additional information (optional)'),
                'rows': 4,
            }),
        }
        labels = {
            'full_name': _('Full Name'),
            'email': _('Email Address'),
            'phone': _('Phone Number'),
            'notes': _('Additional Notes'),
        }
        help_texts = {
            'full_name': _('Your full name'),
            'email': _('We\'ll use this to confirm your enrollment'),
            'phone': _('Optional - helps us contact you'),
            'notes': _('Any questions or additional information'),
        }

    def clean_email(self):
        """Validate email is not already enrolled for this course."""
        email = self.cleaned_data.get('email')
        course = self.instance.course

        if email and course:
            existing = CourseEnrollmentLead.objects.filter(
                email=email,
                course=course,
                status__in=['confirmed', 'enrolled']
            ).exists()

            if existing:
                raise ValidationError(
                    _('This email is already enrolled in this course'),
                    code='already_enrolled'
                )

        return email

    def clean_full_name(self):
        """Validate full name is not empty."""
        full_name = self.cleaned_data.get('full_name')

        if full_name and len(full_name.strip()) < 2:
            raise ValidationError(
                _('Please enter a valid full name'),
                code='invalid_name'
            )

        return full_name

    def clean_phone(self):
        """Validate phone if provided."""
        phone = self.cleaned_data.get('phone')

        if phone and len(phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')) < 10:
            raise ValidationError(
                _('Please enter a valid phone number'),
                code='invalid_phone'
            )

        return phone


class CourseEnrollmentBulkForm(forms.Form):
    """Form for bulk enrollment lead imports."""

    csv_file = forms.FileField(
        label=_('CSV File'),
        help_text=_('Upload a CSV file with columns: full_name, email, phone'),
        required=True,
    )

    def clean_csv_file(self):
        """Validate CSV file format."""
        file = self.cleaned_data['csv_file']

        if not file.name.endswith('.csv'):
            raise ValidationError(
                _('Please upload a valid CSV file'),
                code='invalid_file_type'
            )

        if file.size > 5 * 1024 * 1024:  # 5MB limit
            raise ValidationError(
                _('File size must not exceed 5MB'),
                code='file_too_large'
            )

        return file


class EnrollmentLeadFilterForm(forms.Form):
    """Form for filtering enrollment leads."""

    COURSE_CHOICES = [('', '-- All Courses --')]
    STATUS_CHOICES = [('', '-- All Statuses --')] + list(CourseEnrollmentLead.Status.choices)
    SORT_CHOICES = [
        ('-created_at', _('Newest First')),
        ('created_at', _('Oldest First')),
        ('email', _('Email A-Z')),
        ('-updated_at', _('Recently Updated')),
    ]

    course = forms.CharField(
        required=False,
        label=_('Course'),
        widget=forms.Select(choices=COURSE_CHOICES, attrs={
            'class': 'form-select',
        })
    )

    status = forms.ChoiceField(
        required=False,
        label=_('Status'),
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
        })
    )

    search = forms.CharField(
        required=False,
        label=_('Search'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Search by name or email...'),
        })
    )

    sort = forms.ChoiceField(
        required=False,
        label=_('Sort By'),
        choices=SORT_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate course choices dynamically
        from plugins.lms.models import Course
        courses = Course.objects.filter(is_active=True).values_list('id', 'title').order_by('title')
        self.fields['course'].widget.choices = self.COURSE_CHOICES + list(courses)
