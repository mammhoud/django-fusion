# Profile Plugin

## Overview
This plugin contains all profile-related functionality, separated from the core handlers app.

## Structure

```
plugins/profile/
├── views/          # Profile page views (dashboard, profile, settings, etc.)
├── forms/          # Profile-related forms (account, billing, security, etc.)
├── models/         # Profile-related models (Certificate, Message, Note, etc.)
├── services/       # Business logic services (CertificateService, MessageService, etc.)
├── filters/        # Django filters for profile querysets
├── managers/       # Custom model managers (PersonManager)
├── templates/      # Profile templates
├── urls.py         # URL routing (included at /profile/)
└── apps.py         # App configuration
```

## Views Available

| URL | View | Description |
|-----|------|-------------|
| `/profile/dashboard/` | DashboardView | User learning dashboard |
| `/profile/profile/` | ProfileView | View/update profile |
| `/profile/edit/` | ProfileEditView | Edit profile details |
| `/profile/courses/` | CoursesView | User's enrolled courses |
| `/profile/certifications/` | CertificationsView | User's certifications |
| `/profile/notes/` | NotesView | User's notes |
| `/profile/settings/` | SettingsView | Account settings |
| `/profile/messages/` | MessagesView | User messages |
| `/profile/blog/` | BlogPostsView | User's blog posts |

## Forms

- `AccountSettingsForm` - Basic account info (name, email, phone, bio)
- `BillingSettingsForm` - Subscription and billing settings
- `NotificationSettingsForm` - Notification preferences
- `PreferencesSettingsForm` - Display preferences (language, timezone, theme)
- `PrivacySettingsForm` - Privacy settings (visibility, indexing)
- `SecuritySettingsForm` - Security settings (2FA, session timeout)

## Models

- `Certificate` - User certifications
- `Message` - User-to-user messages
- `Note` / `SharedNote` - User notes with sharing
- `PrivacyPolicy` / `PrivacyConsent` - Privacy consent tracking
- `TermsOfService` / `TermsConsent` - Terms consent tracking

## Services

- `CertificateService` - Certificate issuance, validation, reporting
- `MessageService` - Message sending, threading, analytics
- `PersonService` - Profile creation, sync, notification preferences
