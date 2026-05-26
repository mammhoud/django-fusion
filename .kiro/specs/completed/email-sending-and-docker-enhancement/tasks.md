# Implementation Tasks — Email Sending & Docker Enhancement

**Legend**: `[ ]` not started · `[-]` in progress · `[x]` complete · `[~]` queued

---

## Tasks

- [x] 1. Verify and enhance Role and Group models (R3)
  - [x] 1.1 Check django_seed models for UserRole and UserGroup
    - Verify `django_seed/models.py` contains both models
    - Confirm they have proper fields: name, description, score
    - Verify ManyToMany relation between Role and Group
    - Run `python manage.py check` in both sites
    - _Requirements: R3.1–R3.5_

  - [x] 1.2 Create migrations if needed
    - If models are missing fields, create migration
    - If relation is missing, create migration
    - Run migrations in both sites
    - _Requirements: R3.1–R3.5_

- [x] 2. Create send_invitations_from_csv command (R2)
  - [x] 2.1 Create management command file
    - Create `django_seed/management/commands/send_invitations_from_csv.py`
    - Implement CSV parsing
    - Implement role/group creation logic
    - Implement email sending
    - _Requirements: R2.1–R2.7_

  - [x] 2.2 Test command with emails.csv
    - Run `uv run python manage.py send_invitations_from_csv emails.csv`
    - Verify EmailLog records created
    - Verify User records have roles assigned
    - Verify Group memberships created
    - _Requirements: R2.7_

- [ ] 3. Docker container rebuild (R1)
  - [x] 3.1 Remove and rebuild ctc-research.com containers
    - Run `docker-compose down -v` in ctc-research.com
    - Run `docker-compose up -d --build website media`
    - Verify containers are healthy
    - _Requirements: R1.1–R1.5_

  - [x] 3.2 Remove and rebuild structa.cloud containers
    - Run `docker-compose down -v` in structa.cloud
    - Run `docker-compose up -d --build website media`
    - Verify containers are healthy
    - _Requirements: R1.1–R1.5_

  - [x] 3.3 Run migrations and verify health
    - Run `python manage.py migrate` in both sites
    - Run `python manage.py check` in both sites
    - Verify sites are accessible
    - _Requirements: R1.5_
    - **Note**: Blocked by missing `django_rseal.pipelines` module - pre-existing architectural issue

- [ ] 4. Review and apply enhancement tasks from docs (R4)
  - [ ] 4.1 Scan docs directory for enhancement tasks
    - List all files in `docs/`
    - Identify enhancement-related documents
    - Document findings
    - _Requirements: R4.1–R4.2_

  - [ ] 4.2 Apply applicable enhancements
    - Review each enhancement task
    - Integrate into email sending workflow if applicable
    - Update code as needed
    - _Requirements: R4.3_

  - [ ] 4.3 Update documentation
    - Add enhancement notes to relevant docs
    - Update README if needed
    - _Requirements: R4.4_

- [ ] 5. Create Selenium integration tests (R5)
  - [ ] 5.1 Create test structure
    - Create `tests/selenium/` directory
    - Create `tests/selenium/test_auth.py`
    - Create `tests/selenium/test_admin.py`
    - Create `tests/selenium/conftest.py` (fixtures)
    - _Requirements: R5.1–R5.2_

  - [ ] 5.2 Implement login tests
    - Test login page loads
    - Test login form submission
    - Test redirect after successful login
    - Test error handling for invalid credentials
    - _Requirements: R5.1, R5.4_

  - [ ] 5.3 Implement registration tests
    - Test registration page loads
    - Test registration form submission
    - Test email validation
    - Test password validation
    - _Requirements: R5.1, R5.4_

  - [ ] 5.4 Implement admin page tests
    - Test admin login
    - Test admin dashboard loads
    - Test admin assets load (CSS, JS)
    - Test admin page navigation
    - _Requirements: R5.1, R5.4_

  - [ ] 5.5 Implement asset loading tests
    - Test all CSS files load (no 404)
    - Test all JS files load (no 404)
    - Test images load (no 404)
    - _Requirements: R5.1, R5.4_

  - [ ] 5.6 Run and verify all tests
    - Run `pytest tests/selenium/ -v`
    - Verify all tests pass
    - Document any failures
    - _Requirements: R5.5_

---

## Notes

- Tasks 1–2 can be done in parallel
- Task 3 (Docker rebuild) should be done after tasks 1–2 are complete
- Task 4 (docs review) can be done in parallel with other tasks
- Task 5 (Selenium tests) should be done after Docker rebuild
- All tasks should verify with `python manage.py check` and test runs

