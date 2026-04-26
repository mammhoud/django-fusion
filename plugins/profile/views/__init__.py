# Profile views
try:
    from .blog import (
        BlogPostCreateView,
        BlogPostDeleteView,
        BlogPostEditView,
        BlogPostsView,
    )
    _blog_views_available = True
except (ImportError, RuntimeError):
    _blog_views_available = False
    BlogPostsView = BlogPostCreateView = BlogPostEditView = BlogPostDeleteView = None

from .certifications import CertificationsView
from .courses import CoursesView
from .dashboard import DashboardView
from .messages import MessagesView
from .notes import ContentDashboardView, NotesView
from .profile import (
    ProfileEditView,
    ProfileImageRemoveView,
    ProfileImageUploadView,
    ProfileView,
)
from .settings import SettingsView
from .tags import EnhancedTagsView

__all__ = [
    # Dashboard
    "DashboardView",
    # Profile
    "ProfileView",
    "ProfileEditView",
    "ProfileImageUploadView",
    "ProfileImageRemoveView",
    # Settings
    "SettingsView",
    # Messages
    "MessagesView",
    # Notes
    "NotesView",
    "ContentDashboardView",
    # Courses
    "CoursesView",
    # Certifications
    "CertificationsView",
    # Blog
    "BlogPostsView",
    "BlogPostCreateView",
    "BlogPostEditView",
    "BlogPostDeleteView",
    # Tags
    "EnhancedTagsView",
]
