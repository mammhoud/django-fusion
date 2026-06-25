# Cross-Domain Leakage Elimination Plan

## Overview

This document outlines the strategy for eliminating cross-domain leakage detected in task 6.7.

**Detection Results:**
- structa.cloud: 127 modules with cross-domain leakage
- ctc-research.com: 139 modules with cross-domain leakage

## Key Findings

### Primary Leakage Patterns

1. **accounts ↔ messaging**: Accounts domain imports messaging (email, notifications)
   - **Root Cause**: Email templates and notification services are in accounts but should be in messaging
   - **Solution**: Extract email/notification logic to messaging domain

2. **lms ↔ alliance**: LMS domain references alliance (same domain, different project)
   - **Root Cause**: Code uses "alliance" keyword for structa.cloud's LMS
   - **Solution**: Consolidate LMS/alliance into single domain with project-specific subclasses

3. **content ↔ forms**: Content domain imports form-related code
   - **Root Cause**: Contact forms and form submissions are in content but belong to forms domain
   - **Solution**: Extract form-related models/services to forms domain

4. **accounts ↔ content**: Accounts imports content (pages, blog)
   - **Root Cause**: User profiles, blog posts, and content management are mixed
   - **Solution**: Separate user management (accounts) from content management (content)

5. **lms ↔ accounts**: LMS imports user/account logic
   - **Root Cause**: Course enrollment, progress tracking need user data
   - **Solution**: Use dependency injection to pass user data without direct imports

6. **lms ↔ content**: LMS imports content (pages, blocks)
   - **Root Cause**: Course pages and content blocks are shared
   - **Solution**: Create shared interfaces in crafts_ai for page/block abstractions

## Elimination Strategy

### Phase 1: Low-Risk Splits (No Data Migration)

These modules can be split without database changes:

1. **accounts/email_templates.py** → messaging/email_templates.py
2. **accounts/registration/emails.py** → messaging/registration_emails.py
3. **accounts/services/email/** → messaging/services/email/
4. **accounts/services/notifications.py** → messaging/services/notifications.py
5. **accounts/forms/notification.py** → messaging/forms/notification.py
6. **accounts/snippets/newsletter/** → messaging/snippets/newsletter/
7. **accounts/managers/peoples.py** (notification methods) → messaging/managers/peoples.py

### Phase 2: Medium-Risk Splits (Require Import Updates)

These modules need careful import refactoring:

1. **content/models/contact.py** → forms/models/contact.py
2. **content/models/pages/base.py** (form-related) → forms/models/pages/base.py
3. **content/models/blocks/form.py** → forms/models/blocks/form.py
4. **lms/blocks/form.py** → forms/models/blocks/form.py
5. **accounts/models/forms/** → forms/models/
6. **accounts/services/form_submission.py** → forms/services/form_submission.py

### Phase 3: High-Risk Splits (Require Careful Refactoring)

These modules have complex interdependencies:

1. **accounts/site/** (dashboard, courses, certifications) → Split by domain
   - accounts/site/dashboard.py → accounts/site/dashboard.py (keep user-specific)
   - accounts/site/courses.py → lms/site/courses.py (move to LMS)
   - accounts/site/certifications.py → lms/site/certifications.py (move to LMS)

2. **lms/managers/** → Refactor to use dependency injection
   - Remove direct user imports
   - Pass user objects as parameters

3. **accounts/managers/enrollments.py** → lms/managers/enrollments.py
   - Move enrollment logic to LMS domain

## Implementation Approach

### For Each Module Split:

1. **Analyze Dependencies**
   - Identify all imports from other domains
   - Determine if they're necessary or can be refactored

2. **Create Target Module**
   - Create new file in target domain
   - Copy relevant code

3. **Update Imports**
   - Update all references across both projects
   - Use find-and-replace with verification

4. **Run Tests**
   - Verify no import errors
   - Run test suite to ensure functionality

5. **Delete Original**
   - Remove original file after verification
   - Commit changes

## Priority Order

### High Priority (Start Here)
1. accounts/email_templates.py → messaging
2. accounts/registration/emails.py → messaging
3. accounts/services/email/ → messaging
4. accounts/services/notifications.py → messaging

### Medium Priority
1. content/models/contact.py → forms
2. accounts/models/forms/ → forms
3. accounts/services/form_submission.py → forms

### Lower Priority (Requires More Refactoring)
1. accounts/site/ splits
2. lms/managers/ refactoring
3. accounts/managers/enrollments.py → lms

## Notes

- The "alliance" vs "lms" leakage is expected (same domain, different project names)
- Some leakage is architectural (e.g., content pages importing forms) and may require package-level refactoring
- Focus on eliminating unnecessary cross-domain imports while preserving functionality
- Use dependency injection pattern to reduce tight coupling

