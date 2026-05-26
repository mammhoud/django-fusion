# Requirements — Email Sending & Docker Enhancement

## Overview

This spec covers the next phase of project enhancement:
- Docker container cleanup and rebuild (ctc-research.com and structa.cloud)
- Email sending from CSV with role/group management
- Role and Group model verification and enhancement
- Selenium integration tests for authentication flows
- Documentation review and enhancement task integration

## Requirements

### R1 — Docker Container Cleanup & Rebuild

**User Story**: As a developer, I want to remove and rebuild the website and media containers so the environment is clean and up-to-date.

#### Acceptance Criteria

**R1.1** THE ctc-research.com website container SHALL be removed and rebuilt:
```bash
docker-compose -f ctc-research.com/docker-compose.yml down -v
docker-compose -f ctc-research.com/docker-compose.yml up -d --build website
```

**R1.2** THE ctc-research.com media container SHALL be removed and rebuilt.

**R1.3** THE structa.cloud website container SHALL be removed and rebuilt.

**R1.4** THE structa.cloud media container SHALL be removed and rebuilt.

**R1.5** AFTER rebuild, BOTH sites SHALL be accessible and healthy (health checks pass).

---

### R2 — Email Sending from CSV with Role/Group Management

**User Story**: As an admin, I want to send invitation emails from the CSV file and automatically create/assign roles and groups.

#### Acceptance Criteria

**R2.1** THE CSV file at `emails.csv` SHALL be read with structure: `email,role`

**R2.2** FOR each email in the CSV:
- IF role does not exist as a Group, CREATE it
- ASSIGN the first role to the email/user
- ADD all roles to the user's group membership

**R2.3** THE Role model SHALL have:
- `name` (CharField, unique)
- `description` (TextField, optional)
- Relation to Group model

**R2.4** THE Group model SHALL have:
- `name` (CharField, unique)
- `description` (TextField, optional)
- `score` (IntegerField, default=0)
- Relation to Role model

**R2.5** WHEN sending emails, THE system SHALL:
1. Create Group if not exists (with name from role)
2. Create Role if not exists
3. Assign first role to user
4. Add user to all role groups
5. Send invitation email

**R2.6** THE email sending command SHALL be:
```bash
cd ctc-research.com && uv run python manage.py send_invitations_from_csv emails.csv
```

**R2.7** AFTER sending, THE database SHALL contain:
- EmailLog records for each recipient
- User records with assigned roles
- Group memberships for all roles

---

### R3 — Role and Group Model Verification

**User Story**: As a developer, I want to verify that Role and Group models are properly initialized with correct relations.

#### Acceptance Criteria

**R3.1** THE Role model SHALL be located at `django_seed.models.UserRole` or equivalent.

**R3.2** THE Group model SHALL be located at `django_seed.models.UserGroup` or equivalent.

**R3.3** BOTH models SHALL have proper database migrations.

**R3.4** THE relation between Role and Group SHALL be:
- ManyToMany or ForeignKey (as appropriate)
- Properly indexed
- Tested with `python manage.py check`

**R3.5** AFTER verification, `python manage.py check` SHALL exit 0 in both sites.

---

### R4 — Enhancement Tasks from Documentation

**User Story**: As a developer, I want to review enhancement tasks in the docs directory and apply them to the project.

#### Acceptance Criteria

**R4.1** THE `docs/` directory SHALL be scanned for enhancement tasks.

**R4.2** ENHANCEMENT tasks SHALL be identified and documented.

**R4.3** APPLICABLE enhancements SHALL be integrated into the email sending workflow.

**R4.4** DOCUMENTATION SHALL be updated to reflect new enhancements.

---

### R5 — Selenium Integration Tests

**User Story**: As a QA engineer, I want automated Selenium tests for authentication flows and admin pages.

#### Acceptance Criteria

**R5.1** SELENIUM tests SHALL cover:
- User login flow
- User registration flow
- Admin login and page access
- Asset loading (CSS, JS, images)

**R5.2** TESTS SHALL be located at `tests/selenium/` in both sites.

**R5.3** TESTS SHALL use Chrome/Chromium driver.

**R5.4** TESTS SHALL verify:
- Page loads successfully
- Forms are interactive
- Assets load without 404 errors
- Admin dashboard is accessible

**R5.5** TESTS SHALL be runnable via:
```bash
pytest tests/selenium/ -v
```

---

## Success Metrics

| Requirement | Verification |
|-------------|--------------|
| R1 — Docker rebuild | `docker ps` shows healthy containers |
| R2 — Email sending | `EmailLog.objects.count()` > 0 after command |
| R3 — Model verification | `python manage.py check` exits 0 |
| R4 — Enhancements | Docs reviewed and tasks applied |
| R5 — Selenium tests | All tests pass with `pytest tests/selenium/ -v` |

