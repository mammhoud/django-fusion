# Cross-Domain Leakage Report

## 1. structa.cloud/apps/content/apps.py
**Primary Domain:** content

**Leaked Domains:** accounts

**Sample Symbols:**
- import apps.content.signals.user

## 2. structa.cloud/apps/lms/wagtail_hooks.py
**Primary Domain:** lms

**Leaked Domains:** content, alliance, accounts

**Sample Symbols:**
- import SnippetViewSetGroup
- class ClassesSnippetViewSetGroup
- class TracksSnippetViewSetGroup
- class EnrollmentSnippetGroup
- from wagtail.snippets.models import

## 3. structa.cloud/apps/lms/urls.py
**Primary Domain:** lms

**Leaked Domains:** cart, alliance

**Sample Symbols:**
- import Course
- from crafts_ai.pipelines.site.payments import

## 4. structa.cloud/apps/accounts/email_templates.py
**Primary Domain:** accounts

**Leaked Domains:** messaging

**Sample Symbols:**
- import EmailTemplateRegistry, Email

## 5. structa.cloud/apps/accounts/signals.py
**Primary Domain:** accounts

**Leaked Domains:** content, lms, messaging

**Sample Symbols:**
- import post
- from apps.lms.models import
- import Email

## 6. structa.cloud/apps/accounts/wagtail_hooks.py
**Primary Domain:** accounts

**Leaked Domains:** content, messaging

**Sample Symbols:**
- from wagtail.snippets.models import
- from wagtail.snippets.views.snippets import
- import AuthEmail
- class AuthEmailTemplateViewSet
- class AuthEmailSnippetGroup

## 7. structa.cloud/apps/accounts/blocks.py
**Primary Domain:** accounts

**Leaked Domains:** content

**Sample Symbols:**
- from wagtail.snippets.blocks import

## 8. structa.cloud/apps/content/signals/user.py
**Primary Domain:** content

**Leaked Domains:** accounts, messaging

**Sample Symbols:**
- import get_user
- import send_user
- def create_user_related_records
- from django.contrib.auth import
- import Person

## 9. structa.cloud/apps/content/signals/profile.py
**Primary Domain:** content

**Leaked Domains:** accounts

**Sample Symbols:**
- def sync_profile_to_user

## 10. structa.cloud/apps/content/signals/default.py
**Primary Domain:** content

**Leaked Domains:** accounts

**Sample Symbols:**
- from django.contrib.auth.models import
- from django.contrib.auth.models import
- import Permission
- def assign_default_permissions
- import Group  # ✅ Use Django's built-in Group

## 11. structa.cloud/apps/content/models/contact.py
**Primary Domain:** content

**Leaked Domains:** forms, messaging

**Sample Symbols:**
- def get_email
- class ContactSubmission
- import FieldPanel, MultiField
- def get_field_value

## 12. structa.cloud/apps/content/models/pages/about.py
**Primary Domain:** content

**Leaked Domains:** forms

**Sample Symbols:**
- from wagtail.fields import
- import Field
- import StreamField

## 13. structa.cloud/apps/content/models/pages/home.py
**Primary Domain:** content

**Leaked Domains:** forms

**Sample Symbols:**
- import BaseForm
- from wagtail.fields import
- import FieldPanel, MultiField
- import StreamField

## 14. structa.cloud/apps/content/models/pages/team.py
**Primary Domain:** content

**Leaked Domains:** forms

**Sample Symbols:**
- from wagtail.fields import
- import FieldPanel, MultiField
- import StreamField

## 15. structa.cloud/apps/content/models/pages/contact.py
**Primary Domain:** content

**Leaked Domains:** forms

**Sample Symbols:**
- import BaseForm
- from wagtail.fields import
- import FieldPanel, MultiField
- import StreamField

## 16. structa.cloud/apps/content/models/pages/base.py
**Primary Domain:** content

**Leaked Domains:** forms, messaging

**Sample Symbols:**
- import Email
- def send_submission_email
- from ..blocks.form import
- import MinimalContactForm
- class BaseFormPage

## 17. structa.cloud/apps/content/models/blocks/form.py
**Primary Domain:** content

**Leaked Domains:** forms

**Sample Symbols:**
- class SimpleFormFieldBlock
- class MinimalContactFormBlock
- class SimpleFormFieldBlock

## 18. structa.cloud/apps/lms/snippets/track.py
**Primary Domain:** lms

**Leaked Domains:** alliance

**Sample Symbols:**
- import Course
- class CourseSnippet

## 19. structa.cloud/apps/lms/snippets/__init__.py
**Primary Domain:** lms

**Leaked Domains:** alliance

**Sample Symbols:**
- from .enrollment import

## 20. structa.cloud/apps/lms/snippets/specialization.py
**Primary Domain:** lms

**Leaked Domains:** content, alliance, messaging

**Sample Symbols:**
- from wagtail.admin.filters import
- import Wagtail
- def courses_count
- def update_courses_count_action
- import message

## 21. structa.cloud/apps/lms/snippets/enrollment.py
**Primary Domain:** lms

**Leaked Domains:** content, alliance

**Sample Symbols:**
- from wagtail.snippets.views.snippets import
- import Enrollment
- class EnrollmentViewSet

## 22. structa.cloud/apps/lms/snippets/reviews.py
**Primary Domain:** lms

**Leaked Domains:** alliance

**Sample Symbols:**
- def course_display

## 23. structa.cloud/apps/lms/templatetags/lms_tags.py
**Primary Domain:** lms

**Leaked Domains:** alliance

**Sample Symbols:**
- import Enrollment

## 24. structa.cloud/apps/lms/managers/progress.py
**Primary Domain:** lms

**Leaked Domains:** alliance, accounts

**Sample Symbols:**
- import get_user
- from django.contrib.auth import
- def _get_enrollment_for_course
- def _update_course_progress_from_lesson
- def _update_course_progress_from_module

## 25. structa.cloud/apps/lms/managers/__init__.py
**Primary Domain:** lms

**Leaked Domains:** alliance

**Sample Symbols:**
- from .course import
- from .enrollments import
- from .progress import

## 26. structa.cloud/apps/lms/managers/module.py
**Primary Domain:** lms

**Leaked Domains:** cart, alliance, accounts

**Sample Symbols:**
- import get_user
- from django.contrib.auth import
- import Lesson
- import LessonProgress
- def reorder_modules

## 27. structa.cloud/apps/lms/managers/course.py
**Primary Domain:** lms

**Leaked Domains:** alliance, accounts

**Sample Symbols:**
- import get_user
- def get_user_enrolled_courses
- def _get_user_interests
- def get_user_learning_path
- def _assess_user_skills

## 28. structa.cloud/apps/lms/managers/enrollments.py
**Primary Domain:** lms

**Leaked Domains:** alliance, accounts

**Sample Symbols:**
- import get_user
- def get_user_enrollments
- from django.contrib.auth import
- from apps.lms.models.courses import
- import Course

## 29. structa.cloud/apps/lms/views/__init__.py
**Primary Domain:** lms

**Leaked Domains:** cart, alliance

**Sample Symbols:**
- from .courses import
- from .lessons import
- from .cart import

## 30. structa.cloud/apps/lms/views/cart.py
**Primary Domain:** lms

**Leaked Domains:** content, cart, alliance, messaging

**Sample Symbols:**
- import Page
- def post
- def post
- def post
- def post

## 31. structa.cloud/apps/lms/views/courses.py
**Primary Domain:** lms

**Leaked Domains:** content, alliance

**Sample Symbols:**
- import Page
- import Course
- import CourseSearchView, CourseSearchAPIView, FrontCourse
- class FrontCourseDetail
- class FrontCourseDetailFragment

## 32. structa.cloud/apps/lms/views/lessons.py
**Primary Domain:** lms

**Leaked Domains:** content, alliance, accounts, messaging

**Sample Symbols:**
- import User
- def get_user_progress
- from django.contrib.auth.mixins import
- import Login
- import Page

## 33. structa.cloud/apps/lms/blocks/form.py
**Primary Domain:** lms

**Leaked Domains:** content, forms

**Sample Symbols:**
- from wagtail import
- class SimpleFormFieldBlock
- class MinimalContactFormBlock
- class SimpleFormFieldBlock

## 34. structa.cloud/apps/lms/services/__init__.py
**Primary Domain:** lms

**Leaked Domains:** alliance

**Sample Symbols:**
- from .courses import
- from .lesson import
- from .lessons import
- from .enrollment import
- from .enrollments import

## 35. structa.cloud/apps/lms/services/courses.py
**Primary Domain:** lms

**Leaked Domains:** alliance, accounts

**Sample Symbols:**
- import get_user
- def enroll_user
- def get_user_course_dashboard
- def get_user_recommended_courses
- def _get_user_interests

## 36. structa.cloud/apps/lms/services/lessons.py
**Primary Domain:** lms

**Leaked Domains:** alliance, accounts

**Sample Symbols:**
- import get_user
- from django.contrib.auth import
- def get_course_modules
- def get_course_lessons
- def _check_course_completion

## 37. structa.cloud/apps/lms/services/enrollments.py
**Primary Domain:** lms

**Leaked Domains:** alliance, accounts

**Sample Symbols:**
- import get_user
- def get_user_learning_dashboard
- def enroll_user_in_multiple_courses
- from django.contrib.auth import
- from ..managers.course import

## 38. structa.cloud/apps/lms/services/certificates.py
**Primary Domain:** lms

**Leaked Domains:** content, alliance, accounts

**Sample Symbols:**
- def _get_user_display_name
- def get_user_certificates
- from reportlab.lib.pagesizes import
- import Content
- def _draw_certificate_content

## 39. structa.cloud/apps/lms/services/legacy.py
**Primary Domain:** lms

**Leaked Domains:** alliance, accounts

**Sample Symbols:**
- import get_user
- def get_user_learning_dashboard
- def enroll_user_in_multiple_courses
- from django.contrib.auth import
- import Person

## 40. structa.cloud/apps/lms/models/classes.py
**Primary Domain:** lms

**Leaked Domains:** content, forms

**Sample Symbols:**
- from wagtail.admin.panels import
- from wagtail.fields import
- from wagtail.search import
- import Content
- class MeetingPlatform

## 41. structa.cloud/apps/lms/models/__init__.py
**Primary Domain:** lms

**Leaked Domains:** alliance

**Sample Symbols:**
- from .courses import
- from .enrollment import
- from .certificate import
- import Certificate

## 42. structa.cloud/apps/lms/models/certificate.py
**Primary Domain:** lms

**Leaked Domains:** alliance

**Sample Symbols:**
- from apps.lms.services.certificates import
- import Certificate
- class Certificate
- def generate_certificate_id

## 43. structa.cloud/apps/lms/models/enrollment.py
**Primary Domain:** lms

**Leaked Domains:** alliance

**Sample Symbols:**
- def get_active_courses
- import Enrollment
- class Enrollment

## 44. structa.cloud/apps/lms/models/review.py
**Primary Domain:** lms

**Leaked Domains:** alliance

**Sample Symbols:**
- from .courses import
- import Course

## 45. structa.cloud/apps/lms/models/wishlist.py
**Primary Domain:** lms

**Leaked Domains:** accounts

**Sample Symbols:**
- def get_user_wishlist

## 46. structa.cloud/apps/lms/admin/__init__.py
**Primary Domain:** lms

**Leaked Domains:** alliance, forms

**Sample Symbols:**
- from ..models.courses import
- from ..models.courses.specification import
- from ..models.courses.specification import
- from ..models.courses.specification import
- import Course

## 47. structa.cloud/apps/lms/models/courses/detail.py
**Primary Domain:** lms

**Leaked Domains:** content, cart, alliance, forms

**Sample Symbols:**
- from wagtail.admin.panels import
- from wagtail.models import
- import Course
- def course_count
- def lessons_count

## 48. structa.cloud/apps/lms/models/courses/progress.py
**Primary Domain:** lms

**Leaked Domains:** alliance

**Sample Symbols:**
- from apps.lms.models.courses.specification import
- from ..models.lesson_progress import
- import Lesson
- import Lesson
- class LessonProgress

## 49. structa.cloud/apps/lms/models/courses/__init__.py
**Primary Domain:** lms

**Leaked Domains:** alliance

**Sample Symbols:**
- from .progress import

## 50. structa.cloud/apps/lms/models/courses/specification.py
**Primary Domain:** lms

**Leaked Domains:** content, cart, alliance, forms

**Sample Symbols:**
- from wagtail.embeds.blocks import
- from wagtail.images.blocks import
- from wagtail import
- from wagtail.admin.panels import
- from wagtail.fields import

## 51. structa.cloud/apps/lms/models/courses/info.py
**Primary Domain:** lms

**Leaked Domains:** content, alliance, forms

**Sample Symbols:**
- from wagtail.admin.panels import
- from wagtail.embeds.blocks import
- from wagtail.fields import
- from wagtail.search import
- from apps.lms.services.courses import

## 52. structa.cloud/apps/lms/models/courses/index.py
**Primary Domain:** lms

**Leaked Domains:** content, alliance, forms

**Sample Symbols:**
- from apps.content.models.pages.base import
- import BaseIndexPage
- class CoursesPage
- from wagtail import
- from wagtail.admin.panels import

## 53. structa.cloud/apps/lms/models/blocks/cart.py
**Primary Domain:** lms

**Leaked Domains:** content, cart, alliance, forms

**Sample Symbols:**
- from django.contrib.contenttypes.fields import
- from django.contrib.contenttypes.models import
- import Content
- class CourseCartItem
- from core.CI.models.cart import

## 54. structa.cloud/apps/lms/models/blocks/assignment.py
**Primary Domain:** lms

**Leaked Domains:** content

**Sample Symbols:**
- from wagtail import

## 55. structa.cloud/apps/lms/models/schemas/content.py
**Primary Domain:** lms

**Leaked Domains:** alliance, accounts

**Sample Symbols:**
- import _CourseReference, _ModuleReference, _User
- import _Course

## 56. structa.cloud/apps/lms/models/schemas/__init__.py
**Primary Domain:** lms

**Leaked Domains:** content, alliance

**Sample Symbols:**
- from .content import
- from .course import
- import CourseCreateSchema, CourseSchema, Course
- from .enrollment import
- import Enrollment

## 57. structa.cloud/apps/lms/models/schemas/course.py
**Primary Domain:** lms

**Leaked Domains:** alliance, accounts

**Sample Symbols:**
- import _CategoryReference, _User
- class CourseTranslationSchema
- class CourseCreateSchema
- class CourseUpdateSchema
- class CourseSchema

## 58. structa.cloud/apps/lms/models/schemas/enrollment.py
**Primary Domain:** lms

**Leaked Domains:** alliance, accounts

**Sample Symbols:**
- import _CourseReference, _User
- import _Course
- class EnrollmentSchema

## 59. structa.cloud/apps/lms/models/schemas/review.py
**Primary Domain:** lms

**Leaked Domains:** alliance, accounts

**Sample Symbols:**
- import _CourseReference, _User
- import _Course

## 60. structa.cloud/apps/lms/models/schemas/references.py
**Primary Domain:** lms

**Leaked Domains:** alliance, accounts

**Sample Symbols:**
- class _UserReference
- class _CourseReference

## 61. structa.cloud/apps/accounts/snippets/tags.py
**Primary Domain:** accounts

**Leaked Domains:** content, forms, messaging

**Sample Symbols:**
- from wagtail.admin.views.pages.bulk_actions.delete import
- def published_posts_display
- from wagtail import
- from wagtail.admin.views.pages.bulk_actions.delete import
- import Blog

## 62. structa.cloud/apps/accounts/snippets/base.py
**Primary Domain:** accounts

**Leaked Domains:** content, forms, messaging

**Sample Symbols:**
- from wagtail.snippets.views.snippets import
- import message
- import form

## 63. structa.cloud/apps/accounts/processors/company.py
**Primary Domain:** accounts

**Leaked Domains:** messaging

**Sample Symbols:**
- import Contact, ContactEmail

## 64. structa.cloud/apps/accounts/processors/contacts.py
**Primary Domain:** accounts

**Leaked Domains:** messaging

**Sample Symbols:**
- import Contact, ContactEmail

## 65. structa.cloud/apps/accounts/filters/revision.py
**Primary Domain:** accounts

**Leaked Domains:** content

**Sample Symbols:**
- from wagtail.admin.filters import

## 66. structa.cloud/apps/accounts/managers/__init__.py
**Primary Domain:** accounts

**Leaked Domains:** lms, alliance

**Sample Symbols:**
- from .enrollments import
- from .enrollments import

## 67. structa.cloud/apps/accounts/managers/notes.py
**Primary Domain:** accounts

**Leaked Domains:** content

**Sample Symbols:**
- from django.contrib.contenttypes.models import
- import Content

## 68. structa.cloud/apps/accounts/managers/peoples.py
**Primary Domain:** accounts

**Leaked Domains:** messaging

**Sample Symbols:**
- def filter_by_notification_preferences
- def bulk_update_notification_preferences
- def get_by_email
- def verify_email
- def bulk_verify_emails

## 69. structa.cloud/apps/accounts/managers/messages.py
**Primary Domain:** accounts

**Leaked Domains:** content, messaging

**Sample Symbols:**
- from django.contrib.contenttypes.models import
- import Content
- class MessageManager
- def get_user_messages
- def send_system_message

## 70. structa.cloud/apps/accounts/managers/certificates.py
**Primary Domain:** accounts

**Leaked Domains:** content, alliance, lms

**Sample Symbols:**
- from django.contrib.contenttypes.models import
- import Content
- class CertificateManager
- def get_valid_certificates
- def verify_certificate

## 71. structa.cloud/apps/accounts/site/settings.py
**Primary Domain:** accounts

**Leaked Domains:** content, forms, messaging

**Sample Symbols:**
- import NotificationMixin, Page
- import require_GET, require_POST
- def post
- def _handle_settings_post
- import Notification

## 72. structa.cloud/apps/accounts/site/dashboard.py
**Primary Domain:** accounts

**Leaked Domains:** content, messaging

**Sample Symbols:**
- import NotificationMixin, Page
- import require_GET, require_POST
- import Notification

## 73. structa.cloud/apps/accounts/site/tags.py
**Primary Domain:** accounts

**Leaked Domains:** content, messaging

**Sample Symbols:**
- import NotificationMixin, Page
- import require_GET, require_POST
- import Notification

## 74. structa.cloud/apps/accounts/site/__init__.py
**Primary Domain:** accounts

**Leaked Domains:** cart, messaging

**Sample Symbols:**
- from .messages import
- from .cart import

## 75. structa.cloud/apps/accounts/site/auth.py
**Primary Domain:** accounts

**Leaked Domains:** content, forms, messaging

**Sample Symbols:**
- import Page
- def post
- def post
- import trigger_notification
- def email_activation_sent

## 76. structa.cloud/apps/accounts/site/notes.py
**Primary Domain:** accounts

**Leaked Domains:** content, messaging, lms, alliance, forms

**Sample Symbols:**
- import NotificationMixin, Page
- import require_GET, require_POST
- from django.contrib.contenttypes.fields import
- from django.contrib.contenttypes.models import
- import Content

## 77. structa.cloud/apps/accounts/site/cart.py
**Primary Domain:** accounts

**Leaked Domains:** content, cart

**Sample Symbols:**
- import Page
- def post
- def post
- def post
- from core.CI.services.cart_service import

## 78. structa.cloud/apps/accounts/site/messages.py
**Primary Domain:** accounts

**Leaked Domains:** content, messaging, lms, alliance, forms

**Sample Symbols:**
- import NotificationMixin, Page
- import require_GET, require_POST
- from django.contrib.contenttypes.fields import
- from django.contrib.contenttypes.models import
- import Content

## 79. structa.cloud/apps/accounts/site/profile.py
**Primary Domain:** accounts

**Leaked Domains:** content

**Sample Symbols:**
- import Page
- import require_GET, require_POST
- def post
- def post
- def post

## 80. structa.cloud/apps/accounts/views/tags.py
**Primary Domain:** accounts

**Leaked Domains:** content

**Sample Symbols:**
- import Article
- class ArticlesByTagView
- from django.contrib.contenttypes.models import
- import Content

## 81. structa.cloud/apps/accounts/registration/adapter.py
**Primary Domain:** accounts

**Leaked Domains:** messaging

**Sample Symbols:**
- from .emails import
- import send_registration_email

## 82. structa.cloud/apps/accounts/registration/emails.py
**Primary Domain:** accounts

**Leaked Domains:** messaging

**Sample Symbols:**
- from email.mime.multipart import
- from email.mime.text import
- import Email
- import AuthEmail
- def send_registration_email

## 83. structa.cloud/apps/accounts/registration/signals.py
**Primary Domain:** accounts

**Leaked Domains:** messaging

**Sample Symbols:**
- from .emails import
- import send_signin_success_email

## 84. structa.cloud/apps/accounts/registration/forms.py
**Primary Domain:** accounts

**Leaked Domains:** forms, messaging

**Sample Symbols:**
- def clean_email
- import form
- class RegistrationForm
- class PasswordCreationForm
- from django.contrib.auth.password_validation import

## 85. structa.cloud/apps/accounts/registration/wagtail_hooks.py
**Primary Domain:** accounts

**Leaked Domains:** content, messaging

**Sample Symbols:**
- from wagtail.snippets.models import
- from wagtail.snippets.views.snippets import
- import AuthEmail
- class AuthEmailTemplateViewSet
- class AuthEmailSnippetGroup

## 86. structa.cloud/apps/accounts/registration/models.py
**Primary Domain:** accounts

**Leaked Domains:** content, forms, messaging

**Sample Symbols:**
- from wagtail.fields import
- class AuthEmailTemplate
- from wagtail.fields import
- import RichTextField

## 87. structa.cloud/apps/accounts/registration/allauth_views.py
**Primary Domain:** accounts

**Leaked Domains:** content, forms, messaging

**Sample Symbols:**
- import Page
- import trigger_notification
- def form_valid
- def form_invalid
- def form_valid

## 88. structa.cloud/apps/accounts/registration/views.py
**Primary Domain:** accounts

**Leaked Domains:** content, forms, messaging

**Sample Symbols:**
- import Page
- def post
- def post
- def trigger_notification
- from .emails import

## 89. structa.cloud/apps/accounts/services/person.py
**Primary Domain:** accounts

**Leaked Domains:** content, forms, messaging

**Sample Symbols:**
- from wagtail.users.models import
- import UserProfile as Wagtail
- def update_notification_preferences
- def get_user_profile_information

## 90. structa.cloud/apps/accounts/services/__init__.py
**Primary Domain:** accounts

**Leaked Domains:** lms, alliance, messaging

**Sample Symbols:**
- from .certificates import
- from .certificates import
- from .messages import
- from .notifications import
- import trigger_notification

## 91. structa.cloud/apps/accounts/services/messages.py
**Primary Domain:** accounts

**Leaked Domains:** content, messaging

**Sample Symbols:**
- import EmptyPage, Page
- from django.contrib.contenttypes.models import
- import Content
- import Message
- import Message

## 92. structa.cloud/apps/accounts/services/form_submission.py
**Primary Domain:** accounts

**Leaked Domains:** content, forms, messaging

**Sample Symbols:**
- import Page
- from wagtail.models import
- import EmailMessage
- def send_notification_email
- import Email

## 93. structa.cloud/apps/accounts/services/certificates.py
**Primary Domain:** accounts

**Leaked Domains:** content, alliance, lms

**Sample Symbols:**
- from django.contrib.contenttypes.models import
- import Content
- import Certificate
- import Certificate
- import Certificate

## 94. structa.cloud/apps/accounts/services/notifications.py
**Primary Domain:** accounts

**Leaked Domains:** messaging

**Sample Symbols:**
- def trigger_notification

## 95. structa.cloud/apps/accounts/models/tags.py
**Primary Domain:** accounts

**Leaked Domains:** content, forms

**Sample Symbols:**
- from django.contrib.contenttypes.fields import
- from django.contrib.contenttypes.models import
- import Content
- from django.contrib.contenttypes.fields import

## 96. structa.cloud/apps/accounts/models/__init__.py
**Primary Domain:** accounts

**Leaked Domains:** content, forms

**Sample Symbols:**
- import Article
- from .forms import

## 97. structa.cloud/apps/accounts/models/example_tagged_model.py
**Primary Domain:** accounts

**Leaked Domains:** content

**Sample Symbols:**
- class ArticleManager
- class Article
- from django.contrib.contenttypes.models import
- import Content

## 98. structa.cloud/apps/accounts/models/snippets.py
**Primary Domain:** accounts

**Leaked Domains:** content, forms, messaging

**Sample Symbols:**
- from wagtail.fields import
- class AuthEmailTemplate
- from wagtail.fields import
- import RichTextField

## 99. structa.cloud/apps/accounts/forms/preferences.py
**Primary Domain:** accounts

**Leaked Domains:** forms

**Sample Symbols:**
- import form
- class PreferencesSettingsForm
- from django.contrib.auth.password_validation import
- import Validation

## 100. structa.cloud/apps/accounts/forms/billing.py
**Primary Domain:** accounts

**Leaked Domains:** forms

**Sample Symbols:**
- import form
- class BillingSettingsForm
- from django.contrib.auth.password_validation import
- import Validation

## 101. structa.cloud/apps/accounts/forms/account.py
**Primary Domain:** accounts

**Leaked Domains:** forms, messaging

**Sample Symbols:**
- def clean_email
- import form
- class AccountSettingsForm
- from django.contrib.auth.password_validation import
- import Validation

## 102. structa.cloud/apps/accounts/forms/__init__.py
**Primary Domain:** accounts

**Leaked Domains:** messaging

**Sample Symbols:**
- from .notification import

## 103. structa.cloud/apps/accounts/forms/security.py
**Primary Domain:** accounts

**Leaked Domains:** forms

**Sample Symbols:**
- import form
- class SecuritySettingsForm
- from django.contrib.auth.password_validation import
- import Validation

## 104. structa.cloud/apps/accounts/forms/privacy.py
**Primary Domain:** accounts

**Leaked Domains:** forms

**Sample Symbols:**
- import form
- class PrivacySettingsForm
- from django.contrib.auth.password_validation import
- import Validation

## 105. structa.cloud/apps/accounts/forms/notification.py
**Primary Domain:** accounts

**Leaked Domains:** forms, messaging

**Sample Symbols:**
- class NotificationSettingsForm
- import form
- class NotificationSettingsForm
- from django.contrib.auth.password_validation import
- import Validation

## 106. structa.cloud/apps/accounts/snippets/newsletter/content.py
**Primary Domain:** accounts

**Leaked Domains:** content, messaging

**Sample Symbols:**
- from wagtail.admin.filters import
- import Wagtail
- import message
- def send_test_email_action

## 107. structa.cloud/apps/accounts/snippets/newsletter/__init__.py
**Primary Domain:** accounts

**Leaked Domains:** content

**Sample Symbols:**
- from .content import

## 108. structa.cloud/apps/accounts/snippets/newsletter/template.py
**Primary Domain:** accounts

**Leaked Domains:** content, messaging

**Sample Symbols:**
- from wagtail.admin.filters import
- import Wagtail
- import message
- import Email
- class EmailTemplateFilterSet

## 109. structa.cloud/apps/accounts/snippets/manage/team.py
**Primary Domain:** accounts

**Leaked Domains:** forms, messaging

**Sample Symbols:**
- import message
- import form

## 110. structa.cloud/apps/accounts/snippets/manage/peoples.py
**Primary Domain:** accounts

**Leaked Domains:** content, forms, messaging

**Sample Symbols:**
- from wagtail.admin.panels import
- from wagtail.admin.filters import
- from wagtail.snippets.views.snippets import
- import Wagtail
- class ContactEmailFilterSet

## 111. structa.cloud/apps/accounts/snippets/manage/services.py
**Primary Domain:** accounts

**Leaked Domains:** content

**Sample Symbols:**
- from wagtail.admin.ui.tables import

## 112. structa.cloud/apps/accounts/services/email/__init__.py
**Primary Domain:** accounts

**Leaked Domains:** messaging

**Sample Symbols:**
- import Email

## 113. structa.cloud/apps/accounts/services/email/service.py
**Primary Domain:** accounts

**Leaked Domains:** lms, alliance, messaging

**Sample Symbols:**
- def send_course_completion
- def send_enrollment_confirmation
- def send_course_completion
- def send_enrollment_confirmation
- import EmailMessage

## 114. structa.cloud/apps/accounts/services/email/tasks.py
**Primary Domain:** accounts

**Leaked Domains:** messaging

**Sample Symbols:**
- from apps.accounts.services.email.service import
- from apps.accounts.services.email.service import
- import Email
- import Email
- import Email

## 115. structa.cloud/apps/accounts/models/manage/company.py
**Primary Domain:** accounts

**Leaked Domains:** content, forms

**Sample Symbols:**
- from wagtail.admin.panels import
- from wagtail.models import
- from wagtail.search import
- from wagtail.snippets.models import
- import Validation

## 116. structa.cloud/apps/accounts/models/manage/service.py
**Primary Domain:** accounts

**Leaked Domains:** content, forms

**Sample Symbols:**
- from wagtail import
- from wagtail.admin.panels import
- from wagtail.fields import
- def formatted_price
- from wagtail.fields import

## 117. structa.cloud/apps/accounts/models/manage/event.py
**Primary Domain:** accounts

**Leaked Domains:** content, forms

**Sample Symbols:**
- from wagtail.admin.panels import
- from wagtail.fields import
- from wagtail.fields import
- import FieldPanel, MultiField
- import StreamField

## 118. structa.cloud/apps/accounts/models/blog/tags.py
**Primary Domain:** accounts

**Leaked Domains:** content, cart, forms

**Sample Symbols:**
- class BlogPageTag
- from wagtail.admin.panels import
- from wagtail.models import
- from wagtail.search import
- class BlogTagCategory

## 119. structa.cloud/apps/accounts/models/blog/post.py
**Primary Domain:** accounts

**Leaked Domains:** content, cart, forms

**Sample Symbols:**
- import DraftStateMixin, Orderable, Page
- import BlogPage
- import BlogPage
- class BlogPage
- def increment_page_views

## 120. structa.cloud/apps/accounts/models/blog/__init__.py
**Primary Domain:** accounts

**Leaked Domains:** content

**Sample Symbols:**
- from .post import

## 121. structa.cloud/apps/accounts/models/blog/index.py
**Primary Domain:** accounts

**Leaked Domains:** content, forms, messaging

**Sample Symbols:**
- from wagtail.contrib.routable_page.models import
- import RoutablePage
- import Page
- import BlogPage
- class BlogIndexPage

## 122. structa.cloud/apps/accounts/models/profiles/__init__.py
**Primary Domain:** accounts

**Leaked Domains:** lms, alliance, messaging

**Sample Symbols:**
- from .certificate import
- from .certificate import
- from .message import

## 123. structa.cloud/apps/accounts/models/profiles/message.py
**Primary Domain:** accounts

**Leaked Domains:** content, forms, messaging

**Sample Symbols:**
- from django.contrib.contenttypes.fields import
- from django.contrib.contenttypes.models import
- import Content
- class Message
- class MessageTypeChoices

## 124. structa.cloud/apps/accounts/models/profiles/certificate.py
**Primary Domain:** accounts

**Leaked Domains:** content, alliance, forms, lms

**Sample Symbols:**
- from django.contrib.contenttypes.fields import
- from django.contrib.contenttypes.models import
- import Content
- class Certificate
- class Certificate

## 125. structa.cloud/apps/accounts/models/profiles/note.py
**Primary Domain:** accounts

**Leaked Domains:** content, forms

**Sample Symbols:**
- from django.contrib.contenttypes.fields import
- from django.contrib.contenttypes.models import
- import Content
- from django.contrib.contenttypes.fields import
- import Validation

## 126. structa.cloud/apps/accounts/models/forms/submission.py
**Primary Domain:** accounts

**Leaked Domains:** content, forms, messaging

**Sample Symbols:**
- import Page
- from wagtail.models import
- def get_email
- def mark_email_sent
- class FormSubmission

## 127. structa.cloud/apps/accounts/models/forms/__init__.py
**Primary Domain:** accounts

**Leaked Domains:** forms

**Sample Symbols:**
- import Form
- from .submission import
- import FormSubmission

