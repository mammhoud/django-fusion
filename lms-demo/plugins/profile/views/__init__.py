# Profile views - migrated from accounts plugin

try:
    from .blog import BlogPostCreateView, BlogPostDeleteView, BlogPostEditView, BlogPostsView
    _blog_views_available = True
except (ImportError, RuntimeError, Exception):
    _blog_views_available = False
    BlogPostsView = BlogPostCreateView = BlogPostEditView = BlogPostDeleteView = None

from .certifications import CertificationsView
from .courses import CoursesView
from .dashboard import DashboardView
from .messages import MessagesView
from .notes import ContentDashboardView, NotesView
from .profile import ProfileEditView, ProfileImageRemoveView, ProfileImageUploadView, ProfileView
from .settings import SettingsView

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
    # Courses
    "CoursesView",
    # Certifications
    "CertificationsView",
    # Notes
    "NotesView",
    "ContentDashboardView",
    # Blog
    "BlogPostsView",
    "BlogPostCreateView",
    "BlogPostEditView",
    "BlogPostDeleteView",
]
