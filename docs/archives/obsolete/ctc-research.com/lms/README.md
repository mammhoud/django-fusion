# LMS - Learning Management System

> ![Coming Soon](https://img.shields.io/badge/Status-Coming%20Soon-yellow?style=for-the-badge)

## Overview

The LMS (Learning Management System) is a planned application that will provide comprehensive learning management capabilities integrated with the Wagtail CMS backend.

This application is currently in development and not yet available.

## Planned Features

### Course Management
- Create and manage courses with structured content
- Organize lessons, modules, and learning paths
- Track course progress and completion rates
- Manage course access and enrollment

### Student Management
- Student enrollment and onboarding
- Individual progress tracking
- Performance analytics and reporting
- Certificate generation upon completion

### Content Management
- Rich lesson creation with Wagtail page editor
- Quiz and assessment builder
- Resource and attachment management
- Content versioning and revision history

### Analytics & Reporting
- Student progress dashboards
- Performance and engagement metrics
- Completion and dropout reports
- Instructor analytics

### Certification
- Automated certificate generation
- Badge and achievement system
- Completion tracking and verification

## Planned Integration

The LMS will be built as a Wagtail CMS application, leveraging:

- **Wagtail Pages** — for course and lesson content management
- **Django REST Framework** — for API endpoints
- **django-unfold** — for the admin interface
- **PostgreSQL** — for data persistence

## Expected Availability

The LMS application is planned for a future release. Current infrastructure includes:

- Maintenance mode placeholder at `lms.structa.cloud`
- Reserved database schema
- Docker service configuration

## Current Status

| Component | Status |
|-----------|--------|
| Infrastructure | ✅ Configured (maintenance mode) |
| Database schema | 🔲 Planned |
| Backend models | 🔲 Planned |
| API endpoints | 🔲 Planned |
| Frontend UI | 🔲 Planned |
| Wagtail integration | 🔲 Planned |

## Related

- [Blog System](../blog/README.md) — Also coming soon
- [LMS Feature Roadmap](./01-lms-feature-roadmap.md) — Detailed feature planning
- [Architecture Overview](../deployment/architecture.md)
