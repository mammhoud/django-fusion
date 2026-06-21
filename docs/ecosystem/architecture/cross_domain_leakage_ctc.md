# Cross-Domain Leakage Report

## 1. ctc-research.com/apps/content/apps.py
**Primary Domain:** content

**Leaked Domains:** accounts

**Sample Symbols:**
- import apps.content.signals.user

## 2. ctc-research.com/apps/content/wagtail_hooks.py
**Primary Domain:** content

**Leaked Domains:** forms, accounts

**Sample Symbols:**
- import SnippetViewSetGroup
- class ManagementsSnippetGroup
- import Form
- from crafts_ai.pipelines.snippets.manage.submissions import
- import FormSubmission

## 3. ctc-research.com/apps/lms/wagtail_hooks.py
**Primary Domain:** lms

**Leaked Domains:** alliance, content, accounts

**Sample Symbols:**
- import SnippetViewSetGroup
- class ClassesSnippetViewSetGroup
- class TracksSnippetViewSetGroup
- class EnrollmentSnippetGroup
- from wagtail.snippets.models import

## 4. ctc-research.com/apps/lms/urls.py
**Primary Domain:** lms

**Leaked Domains:** cart, alliance

**Sample Symbols:**
- import Course
- from crafts_ai.pipelines.site.payments import

## 5. ctc-research.com/apps/accounts/apps.py
**Primary Domain:** accounts

**Leaked Domains:** content

**Sample Symbols:**
- import post
- def _on_post_migrate

## 6. ctc-research.com/apps/accounts/email_templates.py
**Primary Domain:** accounts

**Leaked Domains:** messaging

**Sample Symbols:**
- import EmailTemplateRegistry, Email

## 7. ctc-research.com/apps/accounts/signals.py
**Primary Domain:** accounts

**Leaked Domains:** messaging, content

**Sample Symbols:**
- import post
- import Email

## 8. ctc-research.com/apps/accounts/blocks.py
**Primary Domain:** accounts

**Leaked Domains:** content

**Sample Symbols:**
- from wagtail.snippets.blocks import

## 9. ctc-research.com/apps/handlers/forms/account.py
**Primary Domain:** forms

**Leaked Domains:** messaging, accounts

**Sample Symbols:**
- import User
- from django.contrib.auth.models import
- def clean_email

## 10. ctc-research.com/apps/handlers/forms/__init__.py
**Primary Domain:** forms

**Leaked Domains:** messaging

**Sample Symbols:**
- from .notification import

## 11. ctc-research.com/apps/handlers/forms/notification.py
**Primary Domain:** forms

**Leaked Domains:** messaging

**Sample Symbols:**
- class NotificationSettingsForm

## 12. ctc-research.com/apps/content/signals/user.py
**Primary Domain:** content

**Leaked Domains:** messaging, accounts

**Sample Symbols:**
- import get_user
- import send_user
- def create_user_related_records
- from django.contrib.auth import
- import Person

## 13. ctc-research.com/apps/content/signals/profile.py
**Primary Domain:** content

**Leaked Domains:** accounts

**Sample Symbols:**
- def sync_profile_to_user

## 14. ctc-research.com/apps/content/signals/default.py
**Primary Domain:** content

**Leaked Domains:** accounts

**Sample Symbols:**
- from django.contrib.auth.models import
- from django.contrib.auth.models import
- import Permission
- def assign_default_permissions
- import Group  # ✅ Use Django's built-in Group

## 15. ctc-research.com/apps/content/models/contact.py
**Primary Domain:** content

**Leaked Domains:** forms, messaging

**Sample Symbols:**
- def get_email
- class ContactSubmission
- import FieldPanel, MultiField
- def get_field_value

## 16. ctc-research.com/apps/content/admin/__init__.py
**Primary Domain:** content

**Leaked Domains:** forms, messaging

**Sample Symbols:**
- def get_email_display
- import ContactSubmission
- class ContactSubmissionAdmin

## 17. ctc-research.com/apps/content/models/pages/about.py
**Primary Domain:** content

**Leaked Domains:** forms

**Sample Symbols:**
- from wagtail.fields import
- import Field
- import StreamField

## 18. ctc-research.com/apps/content/models/pages/home.py
**Primary Domain:** content

**Leaked Domains:** forms

**Sample Symbols:**
- import BaseForm
- from wagtail.fields import
- import FieldPanel, MultiField
- import StreamField

## 19. ctc-research.com/apps/content/models/pages/team.py
**Primary Domain:** content

**Leaked Domains:** forms

**Sample Symbols:**
- from wagtail.fields import
- import FieldPanel, MultiField
- import StreamField

## 20. ctc-research.com/apps/content/models/pages/contact.py
**Primary Domain:** content

**Leaked Domains:** forms

**Sample Symbols:**
- import BaseForm
- from wagtail.fields import
- import FieldPanel, MultiField
- import StreamField

## 21. ctc-research.com/apps/content/models/pages/base.py
**Primary Domain:** content

**Leaked Domains:** lms, forms, messaging

**Sample Symbols:**
- from apps.lms.blocks.form import
- import Email
- def send_submission_email
- from apps.lms.blocks.form import
- import MinimalContactForm

## 22. ctc-research.com/apps/lms/snippets/track.py
**Primary Domain:** lms

**Leaked Domains:** alliance

**Sample Symbols:**
- import Course
- class CourseSnippet

## 23. ctc-research.com/apps/lms/snippets/__init__.py
**Primary Domain:** lms

**Leaked Domains:** alliance

**Sample Symbols:**
- from .enrollment import

## 24. ctc-research.com/apps/lms/snippets/specialization.py
**Primary Domain:** lms

**Leaked Domains:** messaging, alliance, content

**Sample Symbols:**
- from wagtail.admin.filters import
- import Wagtail
- def courses_count
- def update_courses_count_action
- import message

## 25. ctc-research.com/apps/lms/snippets/enrollment.py
**Primary Domain:** lms

**Leaked Domains:** alliance, content

**Sample Symbols:**
- from wagtail.snippets.views.snippets import
- import Enrollment
- class EnrollmentViewSet

## 26. ctc-research.com/apps/lms/snippets/reviews.py
**Primary Domain:** lms

**Leaked Domains:** alliance

**Sample Symbols:**
- def course_display

## 27. ctc-research.com/apps/lms/templatetags/lms_tags.py
**Primary Domain:** lms

**Leaked Domains:** alliance

**Sample Symbols:**
- import Enrollment

## 28. ctc-research.com/apps/lms/managers/progress.py
**Primary Domain:** lms

**Leaked Domains:** alliance, accounts

**Sample Symbols:**
- import get_user
- from django.contrib.auth import
- def _get_enrollment_for_course
- def _update_course_progress_from_lesson
- def _update_course_progress_from_module

## 29. ctc-research.com/apps/lms/managers/__init__.py
**Primary Domain:** lms

**Leaked Domains:** alliance

**Sample Symbols:**
- from .course import
- from .enrollments import
- from .progress import

## 30. ctc-research.com/apps/lms/managers/module.py
**Primary Domain:** lms

**Leaked Domains:** cart, alliance, accounts

**Sample Symbols:**
- import get_user
- from django.contrib.auth import
- import Lesson
- import LessonProgress
- def reorder_modules

## 31. ctc-research.com/apps/lms/managers/course.py
**Primary Domain:** lms

**Leaked Domains:** alliance, accounts

**Sample Symbols:**
- import get_user
- def get_user_enrolled_courses
- def _get_user_interests
- def get_user_learning_path
- def _assess_user_skills

## 32. ctc-research.com/apps/lms/managers/enrollments.py
**Primary Domain:** lms

**Leaked Domains:** alliance, accounts

**Sample Symbols:**
- import get_user
- def get_user_enrollments
- from django.contrib.auth import
- from apps.lms.models.courses import
- import Course

## 33. ctc-research.com/apps/lms/views/__init__.py
**Primary Domain:** lms

**Leaked Domains:** cart, alliance

**Sample Symbols:**
- from .courses import
- from .lessons import
- from .cart import

## 34. ctc-research.com/apps/lms/views/cart.py
**Primary Domain:** lms

**Leaked Domains:** cart, messaging, alliance, content

**Sample Symbols:**
- import Page
- def post
- def post
- def post
- def post

## 35. ctc-research.com/apps/lms/views/courses.py
**Primary Domain:** lms

**Leaked Domains:** alliance, content

**Sample Symbols:**
- import Page
- import Course
- import CourseSearchView, CourseSearchAPIView, FrontCourse
- class FrontCourseDetail
- class FrontCourseDetailFragment

## 36. ctc-research.com/apps/lms/views/lessons.py
**Primary Domain:** lms

**Leaked Domains:** alliance, messaging, content, accounts

**Sample Symbols:**
- import User
- def get_user_progress
- from django.contrib.auth.mixins import
- import Login
- import Page

## 37. ctc-research.com/apps/lms/blocks/form.py
**Primary Domain:** lms

**Leaked Domains:** forms, content

**Sample Symbols:**
- from wagtail import
- class SimpleFormFieldBlock
- class MinimalContactFormBlock
- class SimpleFormFieldBlock

## 38. ctc-research.com/apps/lms/services/__init__.py
**Primary Domain:** lms

**Leaked Domains:** alliance

**Sample Symbols:**
- from .courses import
- from .lesson import
- from .lessons import
- from .enrollment import
- from .enrollments import

## 39. ctc-research.com/apps/lms/services/courses.py
**Primary Domain:** lms

**Leaked Domains:** alliance, accounts

**Sample Symbols:**
- import get_user
- def enroll_user
- def get_user_course_dashboard
- def get_user_recommended_courses
- def _get_user_interests

## 40. ctc-research.com/apps/lms/services/lessons.py
**Primary Domain:** lms

**Leaked Domains:** alliance, accounts

**Sample Symbols:**
- import get_user
- from django.contrib.auth import
- def get_course_modules
- def get_course_lessons
- def _check_course_completion

## 41. ctc-research.com/apps/lms/services/enrollments.py
**Primary Domain:** lms

**Leaked Domains:** alliance, accounts

**Sample Symbols:**
- import get_user
- def get_user_learning_dashboard
- def enroll_user_in_multiple_courses
- from django.contrib.auth import
- from ..managers.course import

## 42. ctc-research.com/apps/lms/services/certificates.py
**Primary Domain:** lms

**Leaked Domains:** alliance, content, accounts

**Sample Symbols:**
- def _get_user_display_name
- def get_user_certificates
- from reportlab.lib.pagesizes import
- import Content
- def _draw_certificate_content

## 43. ctc-research.com/apps/lms/services/legacy.py
**Primary Domain:** lms

**Leaked Domains:** alliance, accounts

**Sample Symbols:**
- import get_user
- def get_user_learning_dashboard
- def enroll_user_in_multiple_courses
- from django.contrib.auth import
- import Person

## 44. ctc-research.com/apps/lms/models/classes.py
**Primary Domain:** lms

**Leaked Domains:** forms, content

**Sample Symbols:**
- from wagtail.admin.panels import
- from wagtail.fields import
- from wagtail.search import
- import Content
- class MeetingPlatform

## 45. ctc-research.com/apps/lms/models/__init__.py
**Primary Domain:** lms

**Leaked Domains:** alliance

**Sample Symbols:**
- from .courses import
- from .enrollment import
- from .certificate import
- import Certificate

## 46. ctc-research.com/apps/lms/models/certificate.py
**Primary Domain:** lms

**Leaked Domains:** alliance

**Sample Symbols:**
- from apps.lms.services.certificates import
- import Certificate
- class Certificate
- def generate_certificate_id

## 47. ctc-research.com/apps/lms/models/enrollment.py
**Primary Domain:** lms

**Leaked Domains:** alliance

**Sample Symbols:**
- def get_active_courses
- import Enrollment
- class Enrollment

## 48. ctc-research.com/apps/lms/models/review.py
**Primary Domain:** lms

**Leaked Domains:** alliance

**Sample Symbols:**
- from .courses import
- import Course

## 49. ctc-research.com/apps/lms/models/wishlist.py
**Primary Domain:** lms

**Leaked Domains:** accounts

**Sample Symbols:**
- def get_user_wishlist

## 50. ctc-research.com/apps/lms/admin/__init__.py
**Primary Domain:** lms

**Leaked Domains:** forms, alliance

**Sample Symbols:**
- from ..models.courses import
- from ..models.courses.specification import
- from ..models.courses.specification import
- from ..models.courses.specification import
- import Course

## 51. ctc-research.com/apps/lms/models/courses/detail.py
**Primary Domain:** lms

**Leaked Domains:** forms, cart, alliance, content

**Sample Symbols:**
- from wagtail.admin.panels import
- from wagtail.models import
- import Course
- def course_count
- def lessons_count

## 52. ctc-research.com/apps/lms/models/courses/progress.py
**Primary Domain:** lms

**Leaked Domains:** alliance

**Sample Symbols:**
- from apps.lms.models.courses.specification import
- from ..models.lesson_progress import
- import Lesson
- import Lesson
- class LessonProgress

## 53. ctc-research.com/apps/lms/models/courses/__init__.py
**Primary Domain:** lms

**Leaked Domains:** alliance

**Sample Symbols:**
- from .progress import

## 54. ctc-research.com/apps/lms/models/courses/specification.py
**Primary Domain:** lms

**Leaked Domains:** forms, cart, alliance, content

**Sample Symbols:**
- from wagtail.embeds.blocks import
- from wagtail.images.blocks import
- from wagtail import
- from wagtail.admin.panels import
- from wagtail.fields import

## 55. ctc-research.com/apps/lms/models/courses/info.py
**Primary Domain:** lms

**Leaked Domains:** forms, alliance, content

**Sample Symbols:**
- from wagtail.admin.panels import
- from wagtail.embeds.blocks import
- from wagtail.fields import
- from wagtail.search import
- from apps.lms.services.courses import

## 56. ctc-research.com/apps/lms/models/courses/index.py
**Primary Domain:** lms

**Leaked Domains:** forms, alliance, content

**Sample Symbols:**
- from apps.content.models.pages.base import
- import BaseIndexPage
- class CoursesPage
- from wagtail import
- from wagtail.admin.panels import

## 57. ctc-research.com/apps/lms/models/blocks/cart.py
**Primary Domain:** lms

**Leaked Domains:** forms, cart, alliance, content

**Sample Symbols:**
- from django.contrib.contenttypes.fields import
- from django.contrib.contenttypes.models import
- import Content
- class CourseCartItem
- from core.CI.models.cart import

## 58. ctc-research.com/apps/lms/models/blocks/assignment.py
**Primary Domain:** lms

**Leaked Domains:** content

**Sample Symbols:**
- from wagtail import

## 59. ctc-research.com/apps/lms/models/schemas/content.py
**Primary Domain:** lms

**Leaked Domains:** alliance, accounts

**Sample Symbols:**
- import _CourseReference, _ModuleReference, _User
- import _Course

## 60. ctc-research.com/apps/lms/models/schemas/__init__.py
**Primary Domain:** lms

**Leaked Domains:** alliance, content

**Sample Symbols:**
- from .content import
- from .course import
- import CourseCreateSchema, CourseSchema, Course
- from .enrollment import
- import Enrollment

## 61. ctc-research.com/apps/lms/models/schemas/course.py
**Primary Domain:** lms

**Leaked Domains:** alliance, accounts

**Sample Symbols:**
- import _CategoryReference, _User
- class CourseTranslationSchema
- class CourseCreateSchema
- class CourseUpdateSchema
- class CourseSchema

## 62. ctc-research.com/apps/lms/models/schemas/enrollment.py
**Primary Domain:** lms

**Leaked Domains:** alliance, accounts

**Sample Symbols:**
- import _CourseReference, _User
- import _Course
- class EnrollmentSchema

## 63. ctc-research.com/apps/lms/models/schemas/review.py
**Primary Domain:** lms

**Leaked Domains:** alliance, accounts

**Sample Symbols:**
- import _CourseReference, _User
- import _Course

## 64. ctc-research.com/apps/lms/models/schemas/references.py
**Primary Domain:** lms

**Leaked Domains:** alliance, accounts

**Sample Symbols:**
- class _UserReference
- class _CourseReference

## 65. ctc-research.com/apps/accounts/snippets/tags.py
**Primary Domain:** accounts

**Leaked Domains:** forms, messaging, content

**Sample Symbols:**
- from wagtail.admin.views.pages.bulk_actions.delete import
- def published_posts_display
- from wagtail import
- from wagtail.admin.views.pages.bulk_actions.delete import
- import Blog

## 66. ctc-research.com/apps/accounts/snippets/base.py
**Primary Domain:** accounts

**Leaked Domains:** forms, messaging, content

**Sample Symbols:**
- from wagtail.snippets.views.snippets import
- import message
- import form

## 67. ctc-research.com/apps/accounts/processors/company.py
**Primary Domain:** accounts

**Leaked Domains:** messaging

**Sample Symbols:**
- import Contact, ContactEmail

## 68. ctc-research.com/apps/accounts/processors/contacts.py
**Primary Domain:** accounts

**Leaked Domains:** messaging

**Sample Symbols:**
- import Contact, ContactEmail
- import Contact, ContactEmail

## 69. ctc-research.com/apps/accounts/filters/revision.py
**Primary Domain:** accounts

**Leaked Domains:** content

**Sample Symbols:**
- from wagtail.admin.filters import

## 70. ctc-research.com/apps/accounts/managers/__init__.py
**Primary Domain:** accounts

**Leaked Domains:** lms, alliance

**Sample Symbols:**
- from .enrollments import
- from .enrollments import

## 71. ctc-research.com/apps/accounts/managers/peoples.py
**Primary Domain:** accounts

**Leaked Domains:** messaging

**Sample Symbols:**
- def filter_by_notification_preferences
- def bulk_update_notification_preferences
- def get_by_email
- def verify_email
- def bulk_verify_emails

## 72. ctc-research.com/apps/accounts/managers/messages.py
**Primary Domain:** accounts

**Leaked Domains:** messaging, content

**Sample Symbols:**
- from django.contrib.contenttypes.models import
- import Content
- class MessageManager
- def get_user_messages
- def send_system_message

## 73. ctc-research.com/apps/accounts/managers/enrollments.py
**Primary Domain:** accounts

**Leaked Domains:** lms, forms, alliance

**Sample Symbols:**
- from ..models.courses.detail import
- from ..models.courses.detail import
- from ..models.courses.detail import
- import Course
- def get_course_enrollments_detailed

## 74. ctc-research.com/apps/accounts/managers/certificates.py
**Primary Domain:** accounts

**Leaked Domains:** lms, alliance

**Sample Symbols:**
- class CertificateManager
- def get_valid_certificates
- def verify_certificate
- def get_certificate_stats
- def get_certificates_by_issuer

## 75. ctc-research.com/apps/accounts/site/settings.py
**Primary Domain:** accounts

**Leaked Domains:** forms, messaging, content

**Sample Symbols:**
- import NotificationMixin, Page
- def post
- def _handle_settings_post
- import Notification
- def _handle_test_notification

## 76. ctc-research.com/apps/accounts/site/dashboard.py
**Primary Domain:** accounts

**Leaked Domains:** lms, alliance, content

**Sample Symbols:**
- import Page
- from apps.lms.models.courses.progress import
- import Course
- import Lesson
- import Lesson

## 77. ctc-research.com/apps/accounts/site/tags.py
**Primary Domain:** accounts

**Leaked Domains:** messaging, content

**Sample Symbols:**
- import NotificationMixin, Page
- import require_GET, require_POST
- import Notification

## 78. ctc-research.com/apps/accounts/site/__init__.py
**Primary Domain:** accounts

**Leaked Domains:** messaging, alliance, content, lms, cart

**Sample Symbols:**
- from .blog import
- from .courses import
- from .courses import
- from .messages import
- from .cart import

## 79. ctc-research.com/apps/accounts/site/notes.py
**Primary Domain:** accounts

**Leaked Domains:** lms, messaging, alliance, content

**Sample Symbols:**
- import NotificationMixin, Page
- import require_POST
- class ContentDashboardView
- import Course
- import Enrollment

## 80. ctc-research.com/apps/accounts/site/cart.py
**Primary Domain:** accounts

**Leaked Domains:** lms, cart, alliance, content

**Sample Symbols:**
- import Page
- def post
- def post
- from apps.lms.models.courses.info import
- import Course

## 81. ctc-research.com/apps/accounts/site/courses.py
**Primary Domain:** accounts

**Leaked Domains:** lms, messaging, alliance, content

**Sample Symbols:**
- import NotificationMixin, Page
- import require_POST
- from apps.lms.services.courses import
- import Course
- import Course

## 82. ctc-research.com/apps/accounts/site/messages.py
**Primary Domain:** accounts

**Leaked Domains:** messaging, content

**Sample Symbols:**
- import NotificationMixin, Page
- import require_POST
- import Message
- import Message
- class MessagesView

## 83. ctc-research.com/apps/accounts/site/profile.py
**Primary Domain:** accounts

**Leaked Domains:** content

**Sample Symbols:**
- import Page
- def post
- def post
- def post

## 84. ctc-research.com/apps/accounts/site/blog.py
**Primary Domain:** accounts

**Leaked Domains:** forms, messaging, content

**Sample Symbols:**
- import NotificationMixin, Page
- import BlogPostFilterForm, BlogPost
- import BlogCategory, BlogPost
- import Post
- class BlogPostsView

## 85. ctc-research.com/apps/accounts/site/certifications.py
**Primary Domain:** accounts

**Leaked Domains:** lms, messaging, alliance, content

**Sample Symbols:**
- import NotificationMixin, Page
- import require_POST
- import Certificate
- import Certificate
- import Certificate

## 86. ctc-research.com/apps/accounts/views/tags.py
**Primary Domain:** accounts

**Leaked Domains:** content

**Sample Symbols:**
- import Article
- class ArticlesByTagView
- from django.contrib.contenttypes.models import
- import Content

## 87. ctc-research.com/apps/accounts/registration/admin.py
**Primary Domain:** accounts

**Leaked Domains:** messaging

**Sample Symbols:**
- import AuthEmailTemplate, CSVEmailTest, CSVEmail
- class CSVEmailTestAdmin
- class CSVEmailTestBatchAdmin
- class AuthEmailTemplateAdmin

## 88. ctc-research.com/apps/accounts/registration/adapter.py
**Primary Domain:** accounts

**Leaked Domains:** messaging

**Sample Symbols:**
- from .emails import
- import send_registration_email

## 89. ctc-research.com/apps/accounts/registration/emails.py
**Primary Domain:** accounts

**Leaked Domains:** messaging

**Sample Symbols:**
- from email.mime.multipart import
- from email.mime.text import
- import Email
- import AuthEmail
- def send_registration_email

## 90. ctc-research.com/apps/accounts/registration/signals.py
**Primary Domain:** accounts

**Leaked Domains:** messaging

**Sample Symbols:**
- from .emails import
- import send_signin_success_email

## 91. ctc-research.com/apps/accounts/registration/forms.py
**Primary Domain:** accounts

**Leaked Domains:** forms, messaging

**Sample Symbols:**
- def clean_email
- import form
- class RegistrationForm
- class PasswordCreationForm
- from django.contrib.auth.password_validation import

## 92. ctc-research.com/apps/accounts/registration/wagtail_hooks.py
**Primary Domain:** accounts

**Leaked Domains:** messaging, content

**Sample Symbols:**
- from wagtail.snippets.models import
- from wagtail.snippets.views.snippets import
- import AuthEmail
- class AuthEmailTemplateViewSet
- class AuthEmailSnippetGroup

## 93. ctc-research.com/apps/accounts/registration/models.py
**Primary Domain:** accounts

**Leaked Domains:** forms, messaging, content

**Sample Symbols:**
- from wagtail.fields import
- class AuthEmailTemplate
- class CSVEmailTest
- class CSVEmailTestBatch
- from wagtail.fields import

## 94. ctc-research.com/apps/accounts/registration/allauth_views.py
**Primary Domain:** accounts

**Leaked Domains:** forms, messaging, content

**Sample Symbols:**
- import Page
- import trigger_notification
- def form_valid
- def form_invalid
- def form_valid

## 95. ctc-research.com/apps/accounts/registration/views.py
**Primary Domain:** accounts

**Leaked Domains:** forms, messaging, content

**Sample Symbols:**
- import Page
- def post
- def post
- def trigger_notification
- from .emails import

## 96. ctc-research.com/apps/accounts/services/person.py
**Primary Domain:** accounts

**Leaked Domains:** forms, messaging, content

**Sample Symbols:**
- from wagtail.users.models import
- import UserProfile as Wagtail
- def update_notification_preferences
- def get_user_profile_information

## 97. ctc-research.com/apps/accounts/services/__init__.py
**Primary Domain:** accounts

**Leaked Domains:** lms, forms, messaging, alliance

**Sample Symbols:**
- from .certificates import
- from .certificates import
- from .messages import
- from .form_submission import
- import FormSubmissionService as Form

## 98. ctc-research.com/apps/accounts/services/messages.py
**Primary Domain:** accounts

**Leaked Domains:** messaging, content

**Sample Symbols:**
- from django.contrib.contenttypes.models import
- import Content
- import Message
- import Message
- import Message

## 99. ctc-research.com/apps/accounts/services/form_submission.py
**Primary Domain:** accounts

**Leaked Domains:** forms, messaging, content

**Sample Symbols:**
- import Page
- from wagtail.models import
- import EmailMessage
- def send_notification_email
- import Email

## 100. ctc-research.com/apps/accounts/services/certificates.py
**Primary Domain:** accounts

**Leaked Domains:** lms, alliance

**Sample Symbols:**
- import Certificate
- import Certificate
- import Certificate
- import Certificate
- class CertificateService

## 101. ctc-research.com/apps/accounts/services/notes_service.py
**Primary Domain:** accounts

**Leaked Domains:** content

**Sample Symbols:**
- from django.contrib.contenttypes.models import
- import Content

## 102. ctc-research.com/apps/accounts/models/tags.py
**Primary Domain:** accounts

**Leaked Domains:** forms, content

**Sample Symbols:**
- from django.contrib.contenttypes.fields import
- from django.contrib.contenttypes.models import
- from django.contrib.contenttypes.models import
- from django.contrib.contenttypes.models import
- from django.contrib.contenttypes.models import

## 103. ctc-research.com/apps/accounts/models/__init__.py
**Primary Domain:** accounts

**Leaked Domains:** forms, content

**Sample Symbols:**
- import Article as Article
- from .forms import

## 104. ctc-research.com/apps/accounts/models/example_tagged_model.py
**Primary Domain:** accounts

**Leaked Domains:** content

**Sample Symbols:**
- class Article
- from django.contrib.contenttypes.models import
- import Content

## 105. ctc-research.com/apps/accounts/forms/preferences.py
**Primary Domain:** accounts

**Leaked Domains:** forms

**Sample Symbols:**
- import form
- class PreferencesSettingsForm

## 106. ctc-research.com/apps/accounts/forms/billing.py
**Primary Domain:** accounts

**Leaked Domains:** forms

**Sample Symbols:**
- import form
- class BillingSettingsForm

## 107. ctc-research.com/apps/accounts/forms/account.py
**Primary Domain:** accounts

**Leaked Domains:** forms, messaging

**Sample Symbols:**
- def clean_email
- import form
- class AccountSettingsForm
- import Validation

## 108. ctc-research.com/apps/accounts/forms/__init__.py
**Primary Domain:** accounts

**Leaked Domains:** messaging

**Sample Symbols:**
- from .notification import

## 109. ctc-research.com/apps/accounts/forms/security.py
**Primary Domain:** accounts

**Leaked Domains:** forms

**Sample Symbols:**
- import form
- class SecuritySettingsForm

## 110. ctc-research.com/apps/accounts/forms/privacy.py
**Primary Domain:** accounts

**Leaked Domains:** forms

**Sample Symbols:**
- import form
- class PrivacySettingsForm

## 111. ctc-research.com/apps/accounts/forms/notification.py
**Primary Domain:** accounts

**Leaked Domains:** forms, messaging

**Sample Symbols:**
- class NotificationSettingsForm
- import form
- class NotificationSettingsForm

## 112. ctc-research.com/apps/accounts/snippets/newsletter/content.py
**Primary Domain:** accounts

**Leaked Domains:** messaging, content

**Sample Symbols:**
- from wagtail.admin.filters import
- import Wagtail
- import message
- def send_test_email_action

## 113. ctc-research.com/apps/accounts/snippets/newsletter/__init__.py
**Primary Domain:** accounts

**Leaked Domains:** content

**Sample Symbols:**
- from .content import

## 114. ctc-research.com/apps/accounts/snippets/newsletter/template.py
**Primary Domain:** accounts

**Leaked Domains:** messaging, content

**Sample Symbols:**
- from wagtail.admin.filters import
- import Wagtail
- import message
- import Email
- class EmailTemplateFilterSet

## 115. ctc-research.com/apps/accounts/snippets/manage/team.py
**Primary Domain:** accounts

**Leaked Domains:** forms, messaging

**Sample Symbols:**
- import message
- import form

## 116. ctc-research.com/apps/accounts/snippets/manage/peoples.py
**Primary Domain:** accounts

**Leaked Domains:** forms, messaging, content

**Sample Symbols:**
- from wagtail.admin.panels import
- from wagtail.admin.filters import
- from wagtail.snippets.views.snippets import
- import Wagtail
- class ContactEmailFilterSet

## 117. ctc-research.com/apps/accounts/snippets/manage/services.py
**Primary Domain:** accounts

**Leaked Domains:** content

**Sample Symbols:**
- from wagtail.admin.ui.tables import

## 118. ctc-research.com/apps/accounts/registration/management/commands/send_registration_email.py
**Primary Domain:** accounts

**Leaked Domains:** messaging

**Sample Symbols:**
- from apps.accounts.registration.emails import
- import send_registration_email

## 119. ctc-research.com/apps/accounts/services/email/__init__.py
**Primary Domain:** accounts

**Leaked Domains:** messaging

**Sample Symbols:**
- import Email

## 120. ctc-research.com/apps/accounts/services/email/service.py
**Primary Domain:** accounts

**Leaked Domains:** lms, messaging, alliance

**Sample Symbols:**
- def send_course_completion
- def send_enrollment_confirmation
- def send_course_completion
- def send_enrollment_confirmation
- import EmailMessage

## 121. ctc-research.com/apps/accounts/services/email/tasks.py
**Primary Domain:** accounts

**Leaked Domains:** messaging

**Sample Symbols:**
- from apps.accounts.services.email.service import
- from apps.accounts.services.email.service import
- import Email
- import Email
- import Email

## 122. ctc-research.com/apps/accounts/models/manage/company.py
**Primary Domain:** accounts

**Leaked Domains:** forms, content

**Sample Symbols:**
- from wagtail.admin.panels import
- from wagtail.search import
- import Validation

## 123. ctc-research.com/apps/accounts/models/manage/service.py
**Primary Domain:** accounts

**Leaked Domains:** forms, content

**Sample Symbols:**
- from wagtail import
- from wagtail.admin.panels import
- from wagtail.fields import
- def formatted_price
- from wagtail.fields import

## 124. ctc-research.com/apps/accounts/models/manage/event.py
**Primary Domain:** accounts

**Leaked Domains:** forms, content

**Sample Symbols:**
- from wagtail.admin.panels import
- from wagtail.fields import
- from wagtail.fields import
- import FieldPanel, MultiField
- import StreamField

## 125. ctc-research.com/apps/accounts/models/blog/tags.py
**Primary Domain:** accounts

**Leaked Domains:** forms, cart, content

**Sample Symbols:**
- class BlogPageTag
- from wagtail.admin.panels import
- from wagtail.models import
- from wagtail.search import
- class BlogTagCategory

## 126. ctc-research.com/apps/accounts/models/blog/post.py
**Primary Domain:** accounts

**Leaked Domains:** forms, cart, content

**Sample Symbols:**
- import DraftStateMixin, Orderable, Page
- import BlogPage
- import BlogPage
- class BlogPage
- def increment_page_views

## 127. ctc-research.com/apps/accounts/models/blog/__init__.py
**Primary Domain:** accounts

**Leaked Domains:** content

**Sample Symbols:**
- from .post import

## 128. ctc-research.com/apps/accounts/models/blog/index.py
**Primary Domain:** accounts

**Leaked Domains:** forms, messaging, content

**Sample Symbols:**
- from wagtail.contrib.routable_page.models import
- import RoutablePage
- import Page
- import BlogPage
- class BlogIndexPage

## 129. ctc-research.com/apps/accounts/models/profiles/__init__.py
**Primary Domain:** accounts

**Leaked Domains:** lms, messaging, alliance

**Sample Symbols:**
- from .certificate import
- from .certificate import
- from .message import

## 130. ctc-research.com/apps/accounts/models/profiles/message.py
**Primary Domain:** accounts

**Leaked Domains:** forms, messaging, content

**Sample Symbols:**
- from django.contrib.contenttypes.fields import
- from django.contrib.contenttypes.models import
- import Content
- class Message
- class MessageTypeChoices

## 131. ctc-research.com/apps/accounts/models/profiles/certificate.py
**Primary Domain:** accounts

**Leaked Domains:** lms, forms, alliance, content

**Sample Symbols:**
- from django.contrib.contenttypes.fields import
- from django.contrib.contenttypes.models import
- import Content
- class Certificate
- class Certificate

## 132. ctc-research.com/apps/accounts/models/profiles/note.py
**Primary Domain:** accounts

**Leaked Domains:** forms, content

**Sample Symbols:**
- from django.contrib.contenttypes.fields import
- from django.contrib.contenttypes.models import
- import Content
- from django.contrib.contenttypes.fields import

## 133. ctc-research.com/apps/accounts/models/forms/__init__.py
**Primary Domain:** accounts

**Leaked Domains:** forms

**Sample Symbols:**
- from crafts_ai.handlers.models.forms.submission import
- import Form
- from crafts_ai.handlers.models.forms.submission import
- import FormSubmission

## 134. ctc-research.com/apps/accounts/management/commands/setup_wagtail_home.py
**Primary Domain:** accounts

**Leaked Domains:** content

**Sample Symbols:**
- from apps.content.models.pages.home import
- import Page
- import HomePage
- from wagtail.models import
- from apps.content.models.pages.home import

## 135. ctc-research.com/apps/accounts/management/commands/populate_content.py
**Primary Domain:** accounts

**Leaked Domains:** lms, forms, alliance, content

**Sample Symbols:**
- from apps.content.models.pages.about import
- from apps.content.models.pages.contact import
- from apps.content.models.pages.events import
- from apps.content.models.pages.home import
- from apps.content.models.pages.services import

## 136. ctc-research.com/apps/accounts/management/commands/send_error_report.py
**Primary Domain:** accounts

**Leaked Domains:** messaging, content

**Sample Symbols:**
- import Page
- from wagtail.log_actions import
- from wagtail.models import
- import Email
- def _build_email

## 137. ctc-research.com/apps/accounts/management/commands/update_site_settings.py
**Primary Domain:** accounts

**Leaked Domains:** content

**Sample Symbols:**
- from wagtail.images.models import

## 138. ctc-research.com/apps/accounts/management/commands/send_bulk_emails.py
**Primary Domain:** accounts

**Leaked Domains:** messaging

**Sample Symbols:**
- import Email
- import CSVEmail
- class BulkEmailSender
- def send_email
- def send_bulk_emails

## 139. ctc-research.com/apps/accounts/management/commands/verify_content.py
**Primary Domain:** accounts

**Leaked Domains:** forms, content

**Sample Symbols:**
- import Locale, Page
- def _write_page_report
- from wagtail.fields import
- from wagtail.models import
- from wagtail.fields import

