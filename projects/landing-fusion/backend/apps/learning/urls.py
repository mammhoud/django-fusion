from django.urls import path

from . import views

app_name = "learning"

urlpatterns = [
    path("", views.catalog, name="catalog"),
    path("course/<slug:slug>/", views.course_detail, name="course"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile_dashboard, name="profile"),
    path("course/<slug:slug>/enroll/", views.enroll, name="enroll"),
    path("course/<slug:slug>/wishlist/", views.toggle_wishlist, name="wishlist"),
    path("lesson/<int:lesson_id>/complete/", views.complete_lesson, name="complete_lesson"),
]
