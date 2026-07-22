"""
LMS REST API — pure Django JSON views (no DRF dependency).

All views follow the patterns established by the existing django-bolt
and PageHandler architecture.  They return JSON responses compatible
with the Next.js RTK Query slices at projects/lms/lms/src/store/api/.

Endpoints:
  /api/auth/*          – Login, register, profile, password reset
  /api/courses/*       – Course CRUD, featured, categories
  /api/students/*      – Student dashboard, enrollments, progress
  /api/instructors/*   – Instructor CRUD, dashboard, reviews
  /api/blog/*          – Blog posts, categories, featured
  /api/shop/*          – Shop products, cart, orders
  /api/events/*        – Event listing & details
  /api/contact/        – Contact form submission
"""

API_VERSION = "1.0.0"
