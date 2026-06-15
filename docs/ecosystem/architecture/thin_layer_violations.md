# Thin Layer Violations Report
## Summary
**Total violations**: 1214
- **ctc-research.com**: 811 violations
- **structa.cloud**: 403 violations

---

## Project: ctc-research.com
**Violations**: 811

### `apps/accounts/management/commands/create_groups_from_csv.py`
- **Line 60** `get_all_permissions_for_role` (business_logic_function): 12 lines — standalone function with business logic
- **Line 74** `create_or_update_group` (business_logic_function): 23 lines — standalone function with business logic
- **Line 103** `add_arguments` (business_logic_function): 16 lines — standalone function with business logic
- **Line 121** `handle` (business_logic_function): 50 lines — standalone function with business logic
- **Line 173** `_extract_roles_from_csv` (business_logic_function): 13 lines — standalone function with business logic
- **Line 188** `_assign_users_to_groups` (business_logic_function): 48 lines — standalone function with business logic

### `apps/accounts/management/commands/create_privacy_policies.py`
- **Line 19** `handle` (business_logic_function): 86 lines — standalone function with business logic

### `apps/accounts/management/commands/populate_content.py`
- **Line 48** `_extract_field_trans` (business_logic_function): 58 lines — standalone function with business logic
- **Line 109** `_get_trans` (business_logic_function): 12 lines — standalone function with business logic
- **Line 136** `_populate_home` (business_logic_function): 71 lines — standalone function with business logic
- **Line 210** `_populate_about` (business_logic_function): 48 lines — standalone function with business logic
- **Line 261** `_populate_contact` (business_logic_function): 23 lines — standalone function with business logic
- **Line 287** `_populate_team` (business_logic_function): 53 lines — standalone function with business logic
- **Line 351** `_populate_event_or_services` (business_logic_function): 27 lines — standalone function with business logic
- **Line 400** `handle` (business_logic_function): 170 lines — standalone function with business logic

### `apps/accounts/management/commands/run_campaign_worker.py`
- **Line 31** `handle` (business_logic_function): 17 lines — standalone function with business logic

### `apps/accounts/management/commands/send_bulk_emails.py`
- **Line 26** `BulkEmailSender` (business_logic_class): 8 methods — no package delegation detected
- **Line 29** `__init__` (business_logic_function): 21 lines — standalone function with business logic
- **Line 62** `parse_csv` (business_logic_function): 27 lines — standalone function with business logic
- **Line 91** `load_template` (business_logic_function): 28 lines — standalone function with business logic
- **Line 131** `send_email` (business_logic_function): 42 lines — standalone function with business logic
- **Line 175** `process_batch` (business_logic_function): 22 lines — standalone function with business logic
- **Line 199** `send_bulk_emails` (business_logic_function): 49 lines — standalone function with business logic
- **Line 254** `add_arguments` (business_logic_function): 15 lines — standalone function with business logic
- **Line 271** `handle` (business_logic_function): 76 lines — standalone function with business logic

### `apps/accounts/management/commands/send_error_report.py`
- **Line 31** `add_arguments` (business_logic_function): 12 lines — standalone function with business logic
- **Line 45** `handle` (business_logic_function): 17 lines — standalone function with business logic
- **Line 66** `_collect_errors` (business_logic_function): 53 lines — standalone function with business logic
- **Line 121** `_scan_log_files` (business_logic_function): 47 lines — standalone function with business logic
- **Line 172** `_build_email` (business_logic_function): 65 lines — standalone function with business logic

### `apps/accounts/management/commands/send_invites.py`
- **Line 20** `add_arguments` (business_logic_function): 12 lines — standalone function with business logic
- **Line 34** `handle` (business_logic_function): 120 lines — standalone function with business logic

### `apps/accounts/management/commands/send_test_email.py`
- **Line 25** `handle` (business_logic_function): 59 lines — standalone function with business logic

### `apps/accounts/management/commands/setup_wagtail_home.py`
- **Line 18** `handle` (business_logic_function): 46 lines — standalone function with business logic

### `apps/accounts/management/commands/test_email_csv.py`
- **Line 32** `EmailCSVTester` (business_logic_class): 9 methods — no package delegation detected
- **Line 56** `read_csv` (business_logic_function): 18 lines — standalone function with business logic
- **Line 87** `get_template_path` (business_logic_function): 16 lines — standalone function with business logic
- **Line 105** `render_email` (business_logic_function): 26 lines — standalone function with business logic
- **Line 133** `send_email` (business_logic_function): 38 lines — standalone function with business logic
- **Line 173** `process_csv` (business_logic_function): 65 lines — standalone function with business logic
- **Line 255** `add_arguments` (business_logic_function): 27 lines — standalone function with business logic
- **Line 284** `handle` (business_logic_function): 39 lines — standalone function with business logic

### `apps/accounts/management/commands/update_site_settings.py`
- **Line 125** `_resolve_social_json` (business_logic_function): 30 lines — standalone function with business logic
- **Line 40** `handle` (business_logic_function): 78 lines — standalone function with business logic

### `apps/accounts/management/commands/validate_config.py`
- **Line 69** `_load_env_file` (business_logic_function): 17 lines — standalone function with business logic
- **Line 89** `_collect_yaml_keys` (business_logic_function): 42 lines — standalone function with business logic
- **Line 134** `_check_secret_key` (business_logic_function): 22 lines — standalone function with business logic
- **Line 175** `handle` (business_logic_function): 130 lines — standalone function with business logic

### `apps/accounts/management/commands/verify_content.py`
- **Line 40** `_write_page_report` (business_logic_function): 44 lines — standalone function with business logic
- **Line 101** `handle` (business_logic_function): 72 lines — standalone function with business logic

### `apps/accounts/management/commands/verify_deployment.py`
- **Line 69** `_run` (business_logic_function): 13 lines — standalone function with business logic
- **Line 116** `_check_container_status` (business_logic_function): 19 lines — standalone function with business logic
- **Line 138** `_check_network` (business_logic_function): 18 lines — standalone function with business logic
- **Line 172** `_check_env_vars` (business_logic_function): 38 lines — standalone function with business logic
- **Line 213** `_check_traefik_config` (business_logic_function): 33 lines — standalone function with business logic
- **Line 249** `_check_dependencies` (business_logic_function): 14 lines — standalone function with business logic
- **Line 266** `_check_health` (business_logic_function): 18 lines — standalone function with business logic
- **Line 287** `_check_asset_health` (business_logic_function): 66 lines — standalone function with business logic
- **Line 376** `handle` (business_logic_function): 171 lines — standalone function with business logic

### `apps/accounts/managers/certificates.py`
- **Line 15** `get_valid_certificates` (business_logic_function): 19 lines — standalone function with business logic
- **Line 36** `get_expiring_soon` (business_logic_function): 20 lines — standalone function with business logic
- **Line 58** `verify_certificate` (business_logic_function): 20 lines — standalone function with business logic
- **Line 81** `get_certificate_stats` (business_logic_function): 25 lines — standalone function with business logic
- **Line 108** `get_certificates_by_issuer` (business_logic_function): 23 lines — standalone function with business logic
- **Line 133** `bulk_verify_certificates` (business_logic_function): 34 lines — standalone function with business logic

### `apps/accounts/managers/enrollments.py`
- **Line 21** `EnrollmentManager` (business_logic_class): 18 methods — consider extracting to package
- **Line 40** `get_user_enrollments_detailed` (business_logic_function): 87 lines — standalone function with business logic
- **Line 129** `_get_enrollment_dashboard_data` (business_logic_function): 40 lines — standalone function with business logic
- **Line 171** `_get_next_lesson_for_enrollment` (business_logic_function): 42 lines — standalone function with business logic
- **Line 215** `_get_module_progress` (business_logic_function): 38 lines — standalone function with business logic
- **Line 255** `_get_user_enrollment_stats` (business_logic_function): 32 lines — standalone function with business logic
- **Line 289** `_calculate_learning_streak` (business_logic_function): 19 lines — standalone function with business logic
- **Line 310** `_get_weekly_learning_time` (business_logic_function): 11 lines — standalone function with business logic
- **Line 327** `get_course_enrollments_detailed` (business_logic_function): 91 lines — standalone function with business logic
- **Line 420** `_get_course_enrollment_analytics` (business_logic_function): 59 lines — standalone function with business logic
- **Line 481** `_get_top_performers` (business_logic_function): 13 lines — standalone function with business logic
- **Line 496** `_get_recent_activity` (business_logic_function): 24 lines — standalone function with business logic
- **Line 526** `bulk_enroll_students` (business_logic_function): 77 lines — standalone function with business logic
- **Line 605** `bulk_update_enrollment_progress` (business_logic_function): 56 lines — standalone function with business logic
- **Line 667** `get_enrollment_summary` (business_logic_function): 71 lines — standalone function with business logic
- **Line 740** `_get_upcoming_deadlines` (business_logic_function): 30 lines — standalone function with business logic

### `apps/accounts/managers/messages.py`
- **Line 16** `get_user_messages` (business_logic_function): 26 lines — standalone function with business logic
- **Line 44** `get_conversation` (business_logic_function): 33 lines — standalone function with business logic
- **Line 79** `send_system_message` (business_logic_function): 31 lines — standalone function with business logic
- **Line 112** `send_bulk_messages` (business_logic_function): 31 lines — standalone function with business logic
- **Line 146** `get_message_statistics` (business_logic_function): 25 lines — standalone function with business logic
- **Line 173** `_get_top_senders` (business_logic_function): 17 lines — standalone function with business logic
- **Line 192** `_get_recent_message_activity` (business_logic_function): 15 lines — standalone function with business logic
- **Line 209** `cleanup_old_messages` (business_logic_function): 22 lines — standalone function with business logic
- **Line 233** `mark_conversation_as_read` (business_logic_function): 17 lines — standalone function with business logic

### `apps/accounts/managers/notes.py`
- **Line 16** `get_user_notes` (business_logic_function): 29 lines — standalone function with business logic
- **Line 48** `search_notes` (business_logic_function): 45 lines — standalone function with business logic
- **Line 95** `get_pinned_notes` (business_logic_function): 14 lines — standalone function with business logic
- **Line 111** `get_recent_notes` (business_logic_function): 13 lines — standalone function with business logic
- **Line 127** `get_note_statistics` (business_logic_function): 29 lines — standalone function with business logic
- **Line 169** `bulk_update_notes` (business_logic_function): 19 lines — standalone function with business logic
- **Line 190** `get_notes_by_tag` (business_logic_function): 13 lines — standalone function with business logic
- **Line 205** `get_notes_by_date_range` (business_logic_function): 14 lines — standalone function with business logic

### `apps/accounts/managers/peoples.py`
- **Line 27** `PersonManager` (business_logic_class): 33 methods — consider extracting to package
- **Line 68** `get_complete_profiles` (business_logic_function): 12 lines — standalone function with business logic
- **Line 127** `get_or_create_for_user` (business_logic_function): 24 lines — standalone function with business logic
- **Line 156** `search` (business_logic_function): 15 lines — standalone function with business logic
- **Line 173** `filter_by_demographics` (business_logic_function): 38 lines — standalone function with business logic
- **Line 213** `filter_by_notification_preferences` (business_logic_function): 21 lines — standalone function with business logic
- **Line 239** `update_last_active` (business_logic_function): 11 lines — standalone function with business logic
- **Line 252** `verify_email` (business_logic_function): 15 lines — standalone function with business logic
- **Line 280** `activate_person` (business_logic_function): 16 lines — standalone function with business logic
- **Line 298** `deactivate_person` (business_logic_function): 16 lines — standalone function with business logic
- **Line 316** `get_profile_statistics` (business_logic_function): 47 lines — standalone function with business logic
- **Line 397** `bulk_update_last_active` (business_logic_function): 11 lines — standalone function with business logic
- **Line 410** `bulk_verify_emails` (business_logic_function): 16 lines — standalone function with business logic
- **Line 428** `bulk_activate` (business_logic_function): 19 lines — standalone function with business logic
- **Line 449** `bulk_update_notification_preferences` (business_logic_function): 19 lines — standalone function with business logic
- **Line 473** `get_statistics` (business_logic_function): 37 lines — standalone function with business logic
- **Line 515** `get_or_create_user_profile` (business_logic_function): 28 lines — standalone function with business logic
- **Line 548** `invalidate_object_cache` (business_logic_function): 27 lines — standalone function with business logic

### `apps/accounts/middleware/privacy_consent.py`
- **Line 34** `__call__` (business_logic_function): 30 lines — standalone function with business logic

### `apps/accounts/models/blog/index.py`
- **Line 77** `get_posts` (business_logic_function): 14 lines — standalone function with business logic
- **Line 122** `get_context` (business_logic_function): 22 lines — standalone function with business logic
- **Line 158** `tag_archive` (business_logic_function): 13 lines — standalone function with business logic
- **Line 174** `author_archive` (business_logic_function): 13 lines — standalone function with business logic

### `apps/accounts/models/blog/post.py`
- **Line 331** `add_author` (business_logic_function): 22 lines — standalone function with business logic
- **Line 355** `add_tag_with_metadata` (business_logic_function): 22 lines — standalone function with business logic
- **Line 379** `set_primary_tag` (business_logic_function): 16 lines — standalone function with business logic
- **Line 397** `get_related_posts` (business_logic_function): 29 lines — standalone function with business logic
- **Line 443** `save` (business_logic_function): 22 lines — standalone function with business logic

### `apps/accounts/models/example_tagged_model.py`
- **Line 11** `Article` (business_logic_class): 4 methods — no package delegation detected
- **Line 67** `Product` (business_logic_class): 4 methods — no package delegation detected
- **Line 41** `add_tag` (business_logic_function): 13 lines — standalone function with business logic
- **Line 96** `add_tag` (business_logic_function): 13 lines — standalone function with business logic

### `apps/accounts/models/manage/company.py`
- **Line 492** `clean` (business_logic_function): 25 lines — standalone function with business logic
- **Line 519** `save` (business_logic_function): 12 lines — standalone function with business logic
- **Line 881** `clean` (business_logic_function): 24 lines — standalone function with business logic
- **Line 907** `save` (business_logic_function): 14 lines — standalone function with business logic

### `apps/accounts/models/profiles/message.py`
- **Line 113** `reply` (business_logic_function): 13 lines — standalone function with business logic

### `apps/accounts/models/profiles/note.py`
- **Line 65** `save` (business_logic_function): 12 lines — standalone function with business logic

### `apps/accounts/models/profiles/privacy_consent.py`
- **Line 70** `record_consent` (business_logic_function): 19 lines — standalone function with business logic
- **Line 148** `record_consent` (business_logic_function): 19 lines — standalone function with business logic

### `apps/accounts/models/tags.py`
- **Line 89** `TagManager` (business_logic_class): 5 methods — no package delegation detected
- **Line 115** `filter_by_tags` (business_logic_function): 28 lines — standalone function with business logic
- **Line 145** `search_by_tags` (business_logic_function): 14 lines — standalone function with business logic

### `apps/accounts/processors/auth_utils.py`
- **Line 41** `decode_jwt_token` (business_logic_function): 12 lines — standalone function with business logic

### `apps/accounts/processors/basic_auth.py`
- **Line 50** `decode_jwt_token` (business_logic_function): 12 lines — standalone function with business logic
- **Line 106** `authenticate` (business_logic_function): 31 lines — standalone function with business logic

### `apps/accounts/processors/company.py`
- **Line 9** `contacts_list` (business_logic_function): 45 lines — standalone function with business logic
- **Line 57** `contact_details` (business_logic_function): 28 lines — standalone function with business logic
- **Line 88** `contact_company` (business_logic_function): 16 lines — standalone function with business logic
- **Line 107** `company_contacts` (business_logic_function): 16 lines — standalone function with business logic
- **Line 126** `company_contacts_details` (business_logic_function): 19 lines — standalone function with business logic

### `apps/accounts/processors/contacts.py`
- **Line 15** `contacts_list` (business_logic_function): 45 lines — standalone function with business logic
- **Line 63** `contact_details` (business_logic_function): 28 lines — standalone function with business logic
- **Line 94** `contact_company` (business_logic_function): 16 lines — standalone function with business logic
- **Line 113** `company_contacts` (business_logic_function): 16 lines — standalone function with business logic
- **Line 132** `company_contacts_details` (business_logic_function): 19 lines — standalone function with business logic

### `apps/accounts/processors/selectors.py`
- **Line 8** `get_filtered_branches` (business_logic_function): 12 lines — standalone function with business logic
- **Line 23** `get_filtered_corporates` (business_logic_function): 11 lines — standalone function with business logic

### `apps/accounts/registration/adapter.py`
- **Line 12** `RegistrationAdapter` (business_logic_class): 4 methods — no package delegation detected
- **Line 21** `send_confirmation_mail` (business_logic_function): 19 lines — standalone function with business logic

### `apps/accounts/registration/allauth_views.py`
- **Line 83** `form_valid` (business_logic_function): 11 lines — standalone function with business logic

### `apps/accounts/registration/emails.py`
- **Line 22** `_get_sender_accounts` (business_logic_function): 41 lines — standalone function with business logic
- **Line 66** `_get_fallback_html` (business_logic_function): 37 lines — standalone function with business logic
- **Line 106** `send_registration_email` (business_logic_function): 82 lines — standalone function with business logic
- **Line 191** `_send_via_smtp` (business_logic_function): 34 lines — standalone function with business logic
- **Line 228** `_send_with_django_backend` (business_logic_function): 18 lines — standalone function with business logic
- **Line 249** `_resolve_template` (business_logic_function): 26 lines — standalone function with business logic
- **Line 278** `send_signin_success_email` (business_logic_function): 69 lines — standalone function with business logic

### `apps/accounts/registration/forms.py`
- **Line 100** `clean_password` (business_logic_function): 24 lines — standalone function with business logic

### `apps/accounts/registration/management/commands/send_registration_email.py`
- **Line 36** `handle` (business_logic_function): 51 lines — standalone function with business logic

### `apps/accounts/registration/models.py`
- **Line 41** `CSVEmailTest` (business_logic_class): 4 methods — no package delegation detected

### `apps/accounts/registration/signals.py`
- **Line 13** `on_user_logged_in` (business_logic_function): 20 lines — standalone function with business logic

### `apps/accounts/registration/tokens.py`
- **Line 21** `RegistrationTokenGenerator` (business_logic_class): 5 methods — no package delegation detected
- **Line 34** `make_token` (business_logic_function): 16 lines — standalone function with business logic
- **Line 52** `validate_token` (business_logic_function): 21 lines — standalone function with business logic
- **Line 75** `check_token` (business_logic_function): 20 lines — standalone function with business logic
- **Line 97** `make_allauth_compatible_token` (business_logic_function): 28 lines — standalone function with business logic

### `apps/accounts/registration/views.py`
- **Line 47** `rate_limit_check` (business_logic_function): 16 lines — standalone function with business logic
- **Line 79** `ensure_groups_exist` (business_logic_function): 12 lines — standalone function with business logic
- **Line 115** `trigger_notification` (business_logic_function): 25 lines — standalone function with business logic
- **Line 474** `_ensure_profile_exists` (business_logic_function): 22 lines — standalone function with business logic
- **Line 170** `post` (business_logic_function): 118 lines — standalone function with business logic
- **Line 309** `_get_user_from_token` (business_logic_function): 21 lines — standalone function with business logic
- **Line 332** `get` (business_logic_function): 46 lines — standalone function with business logic
- **Line 380** `post` (business_logic_function): 82 lines — standalone function with business logic

### `apps/accounts/services/certificates.py`
- **Line 14** `CertificateService` (business_logic_class): 4 methods — no package delegation detected
- **Line 20** `issue_certificate` (business_logic_function): 48 lines — standalone function with business logic
- **Line 71** `validate_certificate` (business_logic_function): 62 lines — standalone function with business logic
- **Line 136** `get_certificate_profile` (business_logic_function): 61 lines — standalone function with business logic
- **Line 200** `generate_certificate_report` (business_logic_function): 82 lines — standalone function with business logic

### `apps/accounts/services/email/service.py`
- **Line 14** `EmailService` (business_logic_class): 8 methods — consider extracting to package
- **Line 22** `send` (business_logic_function): 61 lines — standalone function with business logic
- **Line 85** `send_simple` (business_logic_function): 47 lines — standalone function with business logic
- **Line 134** `queue` (business_logic_function): 34 lines — standalone function with business logic
- **Line 190** `send_enrollment_confirmation` (business_logic_function): 17 lines — standalone function with business logic
- **Line 209** `send_course_completion` (business_logic_function): 17 lines — standalone function with business logic

### `apps/accounts/services/email/tasks.py`
- **Line 9** `send_email_task` (business_logic_function): 27 lines — standalone function with business logic
- **Line 38** `send_bulk_email_task` (business_logic_function): 33 lines — standalone function with business logic
- **Line 73** `send_email_raw` (business_logic_function): 30 lines — standalone function with business logic

### `apps/accounts/services/form_submission.py`
- **Line 28** `save_submission` (business_logic_function): 28 lines — standalone function with business logic
- **Line 59** `send_notification_email` (business_logic_function): 61 lines — standalone function with business logic
- **Line 123** `_build_plain_email` (business_logic_function): 20 lines — standalone function with business logic
- **Line 146** `get_submissions_for_form` (business_logic_function): 24 lines — standalone function with business logic
- **Line 173** `get_submission_stats` (business_logic_function): 28 lines — standalone function with business logic

### `apps/accounts/services/messages.py`
- **Line 16** `MessageService` (business_logic_class): 5 methods — no package delegation detected
- **Line 22** `send_message` (business_logic_function): 58 lines — standalone function with business logic
- **Line 83** `send_bulk_notification` (business_logic_function): 57 lines — standalone function with business logic
- **Line 143** `get_conversation_thread` (business_logic_function): 65 lines — standalone function with business logic
- **Line 211** `get_message_analytics` (business_logic_function): 118 lines — standalone function with business logic
- **Line 332** `_calculate_message_trends` (business_logic_function): 32 lines — standalone function with business logic

### `apps/accounts/services/notes_service.py`
- **Line 18** `NotesService` (business_logic_class): 15 methods — no package delegation detected
- **Line 22** `create_note` (business_logic_function): 30 lines — standalone function with business logic
- **Line 74** `get_user_notes` (business_logic_function): 12 lines — standalone function with business logic
- **Line 127** `share_note` (business_logic_function): 17 lines — standalone function with business logic
- **Line 153** `get_note_permissions` (business_logic_function): 37 lines — standalone function with business logic
- **Line 193** `search_notes` (business_logic_function): 11 lines — standalone function with business logic

### `apps/accounts/services/person.py`
- **Line 19** `PersonService` (business_logic_class): 9 methods — consider extracting to package
- **Line 26** `create_person_with_profile` (business_logic_function): 34 lines — standalone function with business logic
- **Line 63** `_create_or_link_profile` (business_logic_function): 30 lines — standalone function with business logic
- **Line 96** `_link_alternative_profile` (business_logic_function): 24 lines — standalone function with business logic
- **Line 123** `get_user_profile_information` (business_logic_function): 62 lines — standalone function with business logic
- **Line 195** `_calculate_profile_stats` (business_logic_function): 38 lines — standalone function with business logic
- **Line 236** `sync_person_with_user` (business_logic_function): 41 lines — standalone function with business logic
- **Line 280** `update_notification_preferences` (business_logic_function): 45 lines — standalone function with business logic
- **Line 328** `invite_person_to_register` (business_logic_function): 73 lines — standalone function with business logic

### `apps/accounts/signals.py`
- **Line 20** `handle_file_uploads` (business_logic_function): 27 lines — standalone function with business logic

### `apps/accounts/site/asset_health.py`
- **Line 8** `asset_health_check` (business_logic_function): 118 lines — standalone function with business logic

### `apps/accounts/site/blog.py`
- **Line 29** `get_context_data` (business_logic_function): 32 lines — standalone function with business logic
- **Line 88** `post` (business_logic_function): 57 lines — standalone function with business logic
- **Line 160** `get` (business_logic_function): 12 lines — standalone function with business logic
- **Line 174** `post` (business_logic_function): 57 lines — standalone function with business logic
- **Line 240** `post` (business_logic_function): 23 lines — standalone function with business logic

### `apps/accounts/site/cart.py`
- **Line 30** `_get_cart_items` (business_logic_function): 46 lines — standalone function with business logic
- **Line 97** `get` (business_logic_function): 13 lines — standalone function with business logic
- **Line 118** `post` (business_logic_function): 32 lines — standalone function with business logic
- **Line 158** `delete` (business_logic_function): 17 lines — standalone function with business logic
- **Line 183** `post` (business_logic_function): 34 lines — standalone function with business logic
- **Line 228** `get_context_data` (business_logic_function): 21 lines — standalone function with business logic

### `apps/accounts/site/certifications.py`
- **Line 28** `get_context_data` (business_logic_function): 39 lines — standalone function with business logic
- **Line 83** `upload_certificate` (business_logic_function): 54 lines — standalone function with business logic

### `apps/accounts/site/courses.py`
- **Line 24** `get_context_data` (business_logic_function): 40 lines — standalone function with business logic
- **Line 81** `enroll_course` (business_logic_function): 56 lines — standalone function with business logic

### `apps/accounts/site/dashboard.py`
- **Line 26** `get_context_data` (business_logic_function): 67 lines — standalone function with business logic
- **Line 95** `_get_tag_analytics` (business_logic_function): 15 lines — standalone function with business logic
- **Line 112** `_get_recent_activity` (business_logic_function): 42 lines — standalone function with business logic
- **Line 156** `_get_learning_statistics` (business_logic_function): 23 lines — standalone function with business logic
- **Line 181** `_calculate_learning_streak` (business_logic_function): 24 lines — standalone function with business logic
- **Line 207** `_get_quick_actions` (business_logic_function): 61 lines — standalone function with business logic

### `apps/accounts/site/media_health.py`
- **Line 8** `media_health_check` (business_logic_function): 82 lines — standalone function with business logic

### `apps/accounts/site/messages.py`
- **Line 28** `get_context_data` (business_logic_function): 43 lines — standalone function with business logic
- **Line 76** `send_message` (business_logic_function): 60 lines — standalone function with business logic

### `apps/accounts/site/notes.py`
- **Line 28** `get_context_data` (business_logic_function): 40 lines — standalone function with business logic
- **Line 76** `_get_note_filters` (business_logic_function): 19 lines — standalone function with business logic
- **Line 100** `create_note` (business_logic_function): 52 lines — standalone function with business logic
- **Line 164** `get_context_data` (business_logic_function): 45 lines — standalone function with business logic
- **Line 211** `_get_recent_activity` (business_logic_function): 60 lines — standalone function with business logic
- **Line 273** `_get_quick_actions` (business_logic_function): 66 lines — standalone function with business logic
- **Line 341** `_calculate_overall_stats` (business_logic_function): 19 lines — standalone function with business logic
- **Line 369** `_calculate_activity_score` (business_logic_function): 19 lines — standalone function with business logic

### `apps/accounts/site/profile.py`
- **Line 28** `get_context_data` (business_logic_function): 52 lines — standalone function with business logic
- **Line 109** `get_context_data` (business_logic_function): 35 lines — standalone function with business logic
- **Line 152** `post` (business_logic_function): 46 lines — standalone function with business logic
- **Line 206** `post` (business_logic_function): 28 lines — standalone function with business logic

### `apps/accounts/site/tags.py`
- **Line 27** `get_context_data` (business_logic_function): 46 lines — standalone function with business logic
- **Line 75** `_get_tag_analytics` (business_logic_function): 28 lines — standalone function with business logic
- **Line 105** `_generate_tag_cloud` (business_logic_function): 33 lines — standalone function with business logic
- **Line 142** `search_tags_api` (business_logic_function): 46 lines — standalone function with business logic
- **Line 193** `merge_tags_api` (business_logic_function): 70 lines — standalone function with business logic

### `apps/accounts/snippets/base.py`
- **Line 34** `BaseSnippetViewSet` (business_logic_class): 8 methods — no package delegation detected
- **Line 50** `duplicate` (business_logic_function): 12 lines — standalone function with business logic
- **Line 67** `export_csv` (business_logic_function): 17 lines — standalone function with business logic

### `apps/accounts/snippets/manage/team.py`
- **Line 87** `status_display` (business_logic_function): 14 lines — standalone function with business logic

### `apps/accounts/snippets/newsletter/content.py`
- **Line 84** `send_test_email_action` (business_logic_function): 12 lines — standalone function with business logic
- **Line 101** `duplicate_newsletter_action` (business_logic_function): 13 lines — standalone function with business logic

### `apps/accounts/snippets/newsletter/template.py`
- **Line 56** `set_default_template` (business_logic_function): 16 lines — standalone function with business logic

### `apps/accounts/snippets/tags.py`
- **Line 96** `display_tag` (business_logic_function): 12 lines — standalone function with business logic
- **Line 141** `usage_count_display` (business_logic_function): 13 lines — standalone function with business logic
- **Line 175** `get_extra_actions` (business_logic_function): 25 lines — standalone function with business logic
- **Line 284** `display_category` (business_logic_function): 12 lines — standalone function with business logic
- **Line 417** `display_tag` (business_logic_function): 12 lines — standalone function with business logic
- **Line 462** `usage_count_display` (business_logic_function): 13 lines — standalone function with business logic
- **Line 558** `display_category` (business_logic_function): 12 lines — standalone function with business logic

### `apps/accounts/views/notes.py`
- **Line 20** `notes_section` (business_logic_function): 12 lines — standalone function with business logic
- **Line 37** `notes_list` (business_logic_function): 11 lines — standalone function with business logic
- **Line 79** `create_note` (business_logic_function): 21 lines — standalone function with business logic
- **Line 105** `update_note` (business_logic_function): 25 lines — standalone function with business logic
- **Line 150** `pin_note` (business_logic_function): 16 lines — standalone function with business logic
- **Line 171** `unpin_note` (business_logic_function): 16 lines — standalone function with business logic
- **Line 192** `archive_note` (business_logic_function): 16 lines — standalone function with business logic
- **Line 213** `search_notes` (business_logic_function): 21 lines — standalone function with business logic

### `apps/accounts/views/privacy.py`
- **Line 21** `privacy_policy_modal` (business_logic_function): 14 lines — standalone function with business logic
- **Line 39** `terms_modal` (business_logic_function): 14 lines — standalone function with business logic
- **Line 58** `accept_privacy_policy` (business_logic_function): 22 lines — standalone function with business logic
- **Line 85** `accept_terms` (business_logic_function): 22 lines — standalone function with business logic
- **Line 111** `check_consent_status` (business_logic_function): 27 lines — standalone function with business logic

### `apps/accounts/views/tags.py`
- **Line 138** `search_tags` (business_logic_function): 14 lines — standalone function with business logic
- **Line 156** `filter_by_tags` (business_logic_function): 47 lines — standalone function with business logic
- **Line 30** `get_context_data` (business_logic_function): 12 lines — standalone function with business logic
- **Line 53** `get_context_data` (business_logic_function): 23 lines — standalone function with business logic
- **Line 87** `get_queryset` (business_logic_function): 11 lines — standalone function with business logic
- **Line 116** `get_queryset` (business_logic_function): 11 lines — standalone function with business logic

### `apps/blog/api.py`
- **Line 13** `search_tags` (business_logic_function): 11 lines — standalone function with business logic
- **Line 28** `tag_autocomplete` (business_logic_function): 18 lines — standalone function with business logic
- **Line 50** `tag_cloud` (business_logic_function): 16 lines — standalone function with business logic
- **Line 70** `related_tags` (business_logic_function): 23 lines — standalone function with business logic

### `apps/blog/feeds.py`
- **Line 11** `LatestBlogPostsFeed` (business_logic_class): 5 methods — no package delegation detected
- **Line 41** `BlogTagFeed` (business_logic_class): 9 methods — no package delegation detected
- **Line 74** `BlogCategoryFeed` (business_logic_class): 9 methods — no package delegation detected

### `apps/blog/forms.py`
- **Line 61** `filter_queryset` (business_logic_function): 16 lines — standalone function with business logic
- **Line 180** `clean` (business_logic_function): 16 lines — standalone function with business logic

### `apps/blog/management/commands/manage_tags.py`
- **Line 22** `add_arguments` (business_logic_function): 27 lines — standalone function with business logic
- **Line 51** `handle` (business_logic_function): 13 lines — standalone function with business logic
- **Line 66** `list_tags` (business_logic_function): 16 lines — standalone function with business logic
- **Line 84** `create_tag` (business_logic_function): 17 lines — standalone function with business logic
- **Line 103** `delete_tag` (business_logic_function): 21 lines — standalone function with business logic
- **Line 126** `merge_tags` (business_logic_function): 33 lines — standalone function with business logic
- **Line 161** `list_unused_tags` (business_logic_function): 20 lines — standalone function with business logic

### `apps/blog/models/pages.py`
- **Line 95** `get_posts` (business_logic_function): 15 lines — standalone function with business logic
- **Line 137** `get_context` (business_logic_function): 40 lines — standalone function with business logic
- **Line 183** `tag_archive` (business_logic_function): 30 lines — standalone function with business logic
- **Line 216** `category_archive` (business_logic_function): 27 lines — standalone function with business logic
- **Line 246** `search_view` (business_logic_function): 25 lines — standalone function with business logic

### `apps/blog/models/post.py`
- **Line 15** `BlogPost` (business_logic_class): 7 methods — no package delegation detected
- **Line 149** `get_related_posts` (business_logic_function): 24 lines — standalone function with business logic

### `apps/blog/views/comments.py`
- **Line 21** `post` (business_logic_function): 33 lines — standalone function with business logic

### `apps/blog/views/likes.py`
- **Line 20** `post` (business_logic_function): 17 lines — standalone function with business logic

### `apps/blog/views/post.py`
- **Line 43** `get_queryset` (business_logic_function): 21 lines — standalone function with business logic
- **Line 66** `get_context_data` (business_logic_function): 36 lines — standalone function with business logic
- **Line 122** `get_context_data` (business_logic_function): 17 lines — standalone function with business logic
- **Line 163** `get_queryset` (business_logic_function): 12 lines — standalone function with business logic

### `apps/content/models/contact.py`
- **Line 166** `get_name` (business_logic_function): 14 lines — standalone function with business logic
- **Line 204** `export_as_dict` (business_logic_function): 20 lines — standalone function with business logic
- **Line 226** `export_as_csv_row` (business_logic_function): 13 lines — standalone function with business logic

### `apps/content/models/pages/base.py`
- **Line 74** `serve` (business_logic_function): 28 lines — standalone function with business logic
- **Line 105** `get_context` (business_logic_function): 60 lines — standalone function with business logic
- **Line 168** `get_listed_data` (business_logic_function): 21 lines — standalone function with business logic
- **Line 312** `serve` (business_logic_function): 41 lines — standalone function with business logic
- **Line 355** `send_submission_email` (business_logic_function): 52 lines — standalone function with business logic
- **Line 547** `get_context` (business_logic_function): 29 lines — standalone function with business logic

### `apps/content/search/views.py`
- **Line 13** `search` (business_logic_function): 32 lines — standalone function with business logic

### `apps/content/signals/default.py`
- **Line 10** `create_default_groups` (business_logic_function): 77 lines — standalone function with business logic
- **Line 92** `assign_default_permissions` (business_logic_function): 35 lines — standalone function with business logic

### `apps/content/signals/profile.py`
- **Line 13** `sync_profile_to_user` (business_logic_function): 26 lines — standalone function with business logic

### `apps/content/signals/user.py`
- **Line 28** `create_user_related_records` (business_logic_function): 84 lines — standalone function with business logic

### `apps/handlers/management/commands/create_groups_from_csv.py`
- **Line 60** `get_all_permissions_for_role` (business_logic_function): 12 lines — standalone function with business logic
- **Line 74** `create_or_update_group` (business_logic_function): 23 lines — standalone function with business logic
- **Line 103** `add_arguments` (business_logic_function): 16 lines — standalone function with business logic
- **Line 121** `handle` (business_logic_function): 50 lines — standalone function with business logic
- **Line 173** `_extract_roles_from_csv` (business_logic_function): 13 lines — standalone function with business logic
- **Line 188** `_assign_users_to_groups` (business_logic_function): 48 lines — standalone function with business logic

### `apps/handlers/management/commands/create_privacy_policies.py`
- **Line 19** `handle` (business_logic_function): 86 lines — standalone function with business logic

### `apps/handlers/management/commands/populate_content.py`
- **Line 48** `_extract_field_trans` (business_logic_function): 58 lines — standalone function with business logic
- **Line 109** `_get_trans` (business_logic_function): 12 lines — standalone function with business logic
- **Line 136** `_populate_home` (business_logic_function): 71 lines — standalone function with business logic
- **Line 210** `_populate_about` (business_logic_function): 48 lines — standalone function with business logic
- **Line 261** `_populate_contact` (business_logic_function): 23 lines — standalone function with business logic
- **Line 287** `_populate_team` (business_logic_function): 53 lines — standalone function with business logic
- **Line 351** `_populate_event_or_services` (business_logic_function): 27 lines — standalone function with business logic
- **Line 400** `handle` (business_logic_function): 170 lines — standalone function with business logic

### `apps/handlers/management/commands/run_campaign_worker.py`
- **Line 31** `handle` (business_logic_function): 17 lines — standalone function with business logic

### `apps/handlers/management/commands/send_bulk_emails.py`
- **Line 26** `BulkEmailSender` (business_logic_class): 8 methods — no package delegation detected
- **Line 29** `__init__` (business_logic_function): 21 lines — standalone function with business logic
- **Line 62** `parse_csv` (business_logic_function): 27 lines — standalone function with business logic
- **Line 91** `load_template` (business_logic_function): 28 lines — standalone function with business logic
- **Line 131** `send_email` (business_logic_function): 42 lines — standalone function with business logic
- **Line 175** `process_batch` (business_logic_function): 22 lines — standalone function with business logic
- **Line 199** `send_bulk_emails` (business_logic_function): 49 lines — standalone function with business logic
- **Line 254** `add_arguments` (business_logic_function): 15 lines — standalone function with business logic
- **Line 271** `handle` (business_logic_function): 76 lines — standalone function with business logic

### `apps/handlers/management/commands/send_error_report.py`
- **Line 31** `add_arguments` (business_logic_function): 12 lines — standalone function with business logic
- **Line 45** `handle` (business_logic_function): 17 lines — standalone function with business logic
- **Line 66** `_collect_errors` (business_logic_function): 53 lines — standalone function with business logic
- **Line 121** `_scan_log_files` (business_logic_function): 47 lines — standalone function with business logic
- **Line 172** `_build_email` (business_logic_function): 65 lines — standalone function with business logic

### `apps/handlers/management/commands/send_invites.py`
- **Line 20** `add_arguments` (business_logic_function): 12 lines — standalone function with business logic
- **Line 34** `handle` (business_logic_function): 120 lines — standalone function with business logic

### `apps/handlers/management/commands/send_test_email.py`
- **Line 25** `handle` (business_logic_function): 59 lines — standalone function with business logic

### `apps/handlers/management/commands/setup_wagtail_home.py`
- **Line 18** `handle` (business_logic_function): 46 lines — standalone function with business logic

### `apps/handlers/management/commands/test_email_csv.py`
- **Line 32** `EmailCSVTester` (business_logic_class): 9 methods — no package delegation detected
- **Line 56** `read_csv` (business_logic_function): 18 lines — standalone function with business logic
- **Line 87** `get_template_path` (business_logic_function): 16 lines — standalone function with business logic
- **Line 105** `render_email` (business_logic_function): 26 lines — standalone function with business logic
- **Line 133** `send_email` (business_logic_function): 38 lines — standalone function with business logic
- **Line 173** `process_csv` (business_logic_function): 65 lines — standalone function with business logic
- **Line 255** `add_arguments` (business_logic_function): 27 lines — standalone function with business logic
- **Line 284** `handle` (business_logic_function): 39 lines — standalone function with business logic

### `apps/handlers/management/commands/update_site_settings.py`
- **Line 125** `_resolve_social_json` (business_logic_function): 30 lines — standalone function with business logic
- **Line 40** `handle` (business_logic_function): 78 lines — standalone function with business logic

### `apps/handlers/management/commands/validate_config.py`
- **Line 69** `_load_env_file` (business_logic_function): 17 lines — standalone function with business logic
- **Line 89** `_collect_yaml_keys` (business_logic_function): 42 lines — standalone function with business logic
- **Line 134** `_check_secret_key` (business_logic_function): 22 lines — standalone function with business logic
- **Line 175** `handle` (business_logic_function): 130 lines — standalone function with business logic

### `apps/handlers/management/commands/verify_content.py`
- **Line 40** `_write_page_report` (business_logic_function): 44 lines — standalone function with business logic
- **Line 101** `handle` (business_logic_function): 72 lines — standalone function with business logic

### `apps/handlers/management/commands/verify_deployment.py`
- **Line 69** `_run` (business_logic_function): 13 lines — standalone function with business logic
- **Line 116** `_check_container_status` (business_logic_function): 19 lines — standalone function with business logic
- **Line 138** `_check_network` (business_logic_function): 18 lines — standalone function with business logic
- **Line 172** `_check_env_vars` (business_logic_function): 38 lines — standalone function with business logic
- **Line 213** `_check_traefik_config` (business_logic_function): 33 lines — standalone function with business logic
- **Line 249** `_check_dependencies` (business_logic_function): 14 lines — standalone function with business logic
- **Line 266** `_check_health` (business_logic_function): 18 lines — standalone function with business logic
- **Line 287** `_check_asset_health` (business_logic_function): 66 lines — standalone function with business logic
- **Line 376** `handle` (business_logic_function): 171 lines — standalone function with business logic

### `apps/handlers/managers/certificates.py`
- **Line 15** `get_valid_certificates` (business_logic_function): 19 lines — standalone function with business logic
- **Line 36** `get_expiring_soon` (business_logic_function): 20 lines — standalone function with business logic
- **Line 58** `verify_certificate` (business_logic_function): 20 lines — standalone function with business logic
- **Line 81** `get_certificate_stats` (business_logic_function): 25 lines — standalone function with business logic
- **Line 108** `get_certificates_by_issuer` (business_logic_function): 23 lines — standalone function with business logic
- **Line 133** `bulk_verify_certificates` (business_logic_function): 34 lines — standalone function with business logic

### `apps/handlers/managers/enrollments.py`
- **Line 21** `EnrollmentManager` (business_logic_class): 18 methods — consider extracting to package
- **Line 40** `get_user_enrollments_detailed` (business_logic_function): 87 lines — standalone function with business logic
- **Line 129** `_get_enrollment_dashboard_data` (business_logic_function): 40 lines — standalone function with business logic
- **Line 171** `_get_next_lesson_for_enrollment` (business_logic_function): 42 lines — standalone function with business logic
- **Line 215** `_get_module_progress` (business_logic_function): 38 lines — standalone function with business logic
- **Line 255** `_get_user_enrollment_stats` (business_logic_function): 32 lines — standalone function with business logic
- **Line 289** `_calculate_learning_streak` (business_logic_function): 19 lines — standalone function with business logic
- **Line 310** `_get_weekly_learning_time` (business_logic_function): 11 lines — standalone function with business logic
- **Line 327** `get_course_enrollments_detailed` (business_logic_function): 91 lines — standalone function with business logic
- **Line 420** `_get_course_enrollment_analytics` (business_logic_function): 59 lines — standalone function with business logic
- **Line 481** `_get_top_performers` (business_logic_function): 13 lines — standalone function with business logic
- **Line 496** `_get_recent_activity` (business_logic_function): 24 lines — standalone function with business logic
- **Line 526** `bulk_enroll_students` (business_logic_function): 77 lines — standalone function with business logic
- **Line 605** `bulk_update_enrollment_progress` (business_logic_function): 56 lines — standalone function with business logic
- **Line 667** `get_enrollment_summary` (business_logic_function): 71 lines — standalone function with business logic
- **Line 740** `_get_upcoming_deadlines` (business_logic_function): 30 lines — standalone function with business logic

### `apps/handlers/managers/messages.py`
- **Line 16** `get_user_messages` (business_logic_function): 26 lines — standalone function with business logic
- **Line 44** `get_conversation` (business_logic_function): 33 lines — standalone function with business logic
- **Line 79** `send_system_message` (business_logic_function): 31 lines — standalone function with business logic
- **Line 112** `send_bulk_messages` (business_logic_function): 31 lines — standalone function with business logic
- **Line 146** `get_message_statistics` (business_logic_function): 25 lines — standalone function with business logic
- **Line 173** `_get_top_senders` (business_logic_function): 17 lines — standalone function with business logic
- **Line 192** `_get_recent_message_activity` (business_logic_function): 15 lines — standalone function with business logic
- **Line 209** `cleanup_old_messages` (business_logic_function): 22 lines — standalone function with business logic
- **Line 233** `mark_conversation_as_read` (business_logic_function): 17 lines — standalone function with business logic

### `apps/handlers/managers/notes.py`
- **Line 16** `get_user_notes` (business_logic_function): 29 lines — standalone function with business logic
- **Line 48** `search_notes` (business_logic_function): 45 lines — standalone function with business logic
- **Line 95** `get_pinned_notes` (business_logic_function): 14 lines — standalone function with business logic
- **Line 111** `get_recent_notes` (business_logic_function): 13 lines — standalone function with business logic
- **Line 127** `get_note_statistics` (business_logic_function): 29 lines — standalone function with business logic
- **Line 169** `bulk_update_notes` (business_logic_function): 19 lines — standalone function with business logic
- **Line 190** `get_notes_by_tag` (business_logic_function): 13 lines — standalone function with business logic
- **Line 205** `get_notes_by_date_range` (business_logic_function): 14 lines — standalone function with business logic

### `apps/handlers/managers/peoples.py`
- **Line 27** `PersonManager` (business_logic_class): 33 methods — consider extracting to package
- **Line 68** `get_complete_profiles` (business_logic_function): 12 lines — standalone function with business logic
- **Line 127** `get_or_create_for_user` (business_logic_function): 24 lines — standalone function with business logic
- **Line 156** `search` (business_logic_function): 15 lines — standalone function with business logic
- **Line 173** `filter_by_demographics` (business_logic_function): 38 lines — standalone function with business logic
- **Line 213** `filter_by_notification_preferences` (business_logic_function): 21 lines — standalone function with business logic
- **Line 239** `update_last_active` (business_logic_function): 11 lines — standalone function with business logic
- **Line 252** `verify_email` (business_logic_function): 15 lines — standalone function with business logic
- **Line 280** `activate_person` (business_logic_function): 16 lines — standalone function with business logic
- **Line 298** `deactivate_person` (business_logic_function): 16 lines — standalone function with business logic
- **Line 316** `get_profile_statistics` (business_logic_function): 47 lines — standalone function with business logic
- **Line 397** `bulk_update_last_active` (business_logic_function): 11 lines — standalone function with business logic
- **Line 410** `bulk_verify_emails` (business_logic_function): 16 lines — standalone function with business logic
- **Line 428** `bulk_activate` (business_logic_function): 19 lines — standalone function with business logic
- **Line 449** `bulk_update_notification_preferences` (business_logic_function): 19 lines — standalone function with business logic
- **Line 473** `get_statistics` (business_logic_function): 37 lines — standalone function with business logic
- **Line 515** `get_or_create_user_profile` (business_logic_function): 28 lines — standalone function with business logic
- **Line 548** `invalidate_object_cache` (business_logic_function): 27 lines — standalone function with business logic

### `apps/handlers/middleware/privacy_consent.py`
- **Line 34** `__call__` (business_logic_function): 30 lines — standalone function with business logic

### `apps/handlers/models/blog/index.py`
- **Line 77** `get_posts` (business_logic_function): 14 lines — standalone function with business logic
- **Line 122** `get_context` (business_logic_function): 22 lines — standalone function with business logic
- **Line 158** `tag_archive` (business_logic_function): 13 lines — standalone function with business logic
- **Line 174** `author_archive` (business_logic_function): 13 lines — standalone function with business logic

### `apps/handlers/models/blog/post.py`
- **Line 331** `add_author` (business_logic_function): 22 lines — standalone function with business logic
- **Line 355** `add_tag_with_metadata` (business_logic_function): 22 lines — standalone function with business logic
- **Line 379** `set_primary_tag` (business_logic_function): 16 lines — standalone function with business logic
- **Line 397** `get_related_posts` (business_logic_function): 29 lines — standalone function with business logic
- **Line 443** `save` (business_logic_function): 22 lines — standalone function with business logic

### `apps/handlers/models/example_tagged_model.py`
- **Line 11** `Article` (business_logic_class): 4 methods — no package delegation detected
- **Line 67** `Product` (business_logic_class): 4 methods — no package delegation detected
- **Line 41** `add_tag` (business_logic_function): 13 lines — standalone function with business logic
- **Line 96** `add_tag` (business_logic_function): 13 lines — standalone function with business logic

### `apps/handlers/models/manage/company.py`
- **Line 492** `clean` (business_logic_function): 25 lines — standalone function with business logic
- **Line 519** `save` (business_logic_function): 12 lines — standalone function with business logic
- **Line 881** `clean` (business_logic_function): 24 lines — standalone function with business logic
- **Line 907** `save` (business_logic_function): 14 lines — standalone function with business logic

### `apps/handlers/models/profiles/message.py`
- **Line 113** `reply` (business_logic_function): 13 lines — standalone function with business logic

### `apps/handlers/models/profiles/note.py`
- **Line 65** `save` (business_logic_function): 12 lines — standalone function with business logic

### `apps/handlers/models/profiles/privacy_consent.py`
- **Line 70** `record_consent` (business_logic_function): 19 lines — standalone function with business logic
- **Line 148** `record_consent` (business_logic_function): 19 lines — standalone function with business logic

### `apps/handlers/models/tags.py`
- **Line 89** `TagManager` (business_logic_class): 5 methods — no package delegation detected
- **Line 115** `filter_by_tags` (business_logic_function): 28 lines — standalone function with business logic
- **Line 145** `search_by_tags` (business_logic_function): 14 lines — standalone function with business logic

### `apps/handlers/processors/auth_utils.py`
- **Line 41** `decode_jwt_token` (business_logic_function): 12 lines — standalone function with business logic

### `apps/handlers/processors/basic_auth.py`
- **Line 50** `decode_jwt_token` (business_logic_function): 12 lines — standalone function with business logic
- **Line 106** `authenticate` (business_logic_function): 31 lines — standalone function with business logic

### `apps/handlers/processors/company.py`
- **Line 9** `contacts_list` (business_logic_function): 45 lines — standalone function with business logic
- **Line 57** `contact_details` (business_logic_function): 28 lines — standalone function with business logic
- **Line 88** `contact_company` (business_logic_function): 16 lines — standalone function with business logic
- **Line 107** `company_contacts` (business_logic_function): 16 lines — standalone function with business logic
- **Line 126** `company_contacts_details` (business_logic_function): 19 lines — standalone function with business logic

### `apps/handlers/processors/contacts.py`
- **Line 15** `contacts_list` (business_logic_function): 45 lines — standalone function with business logic
- **Line 63** `contact_details` (business_logic_function): 28 lines — standalone function with business logic
- **Line 94** `contact_company` (business_logic_function): 16 lines — standalone function with business logic
- **Line 113** `company_contacts` (business_logic_function): 16 lines — standalone function with business logic
- **Line 132** `company_contacts_details` (business_logic_function): 19 lines — standalone function with business logic

### `apps/handlers/processors/selectors.py`
- **Line 8** `get_filtered_branches` (business_logic_function): 12 lines — standalone function with business logic
- **Line 23** `get_filtered_corporates` (business_logic_function): 11 lines — standalone function with business logic

### `apps/handlers/registration/adapter.py`
- **Line 12** `RegistrationAdapter` (business_logic_class): 4 methods — no package delegation detected
- **Line 21** `send_confirmation_mail` (business_logic_function): 19 lines — standalone function with business logic

### `apps/handlers/registration/allauth_views.py`
- **Line 83** `form_valid` (business_logic_function): 11 lines — standalone function with business logic

### `apps/handlers/registration/emails.py`
- **Line 22** `_get_sender_accounts` (business_logic_function): 41 lines — standalone function with business logic
- **Line 66** `_get_fallback_html` (business_logic_function): 37 lines — standalone function with business logic
- **Line 106** `send_registration_email` (business_logic_function): 82 lines — standalone function with business logic
- **Line 191** `_send_via_smtp` (business_logic_function): 34 lines — standalone function with business logic
- **Line 228** `_send_with_django_backend` (business_logic_function): 18 lines — standalone function with business logic
- **Line 249** `_resolve_template` (business_logic_function): 26 lines — standalone function with business logic
- **Line 278** `send_signin_success_email` (business_logic_function): 69 lines — standalone function with business logic

### `apps/handlers/registration/forms.py`
- **Line 100** `clean_password` (business_logic_function): 24 lines — standalone function with business logic

### `apps/handlers/registration/management/commands/send_registration_email.py`
- **Line 36** `handle` (business_logic_function): 51 lines — standalone function with business logic

### `apps/handlers/registration/models.py`
- **Line 41** `CSVEmailTest` (business_logic_class): 4 methods — no package delegation detected

### `apps/handlers/registration/signals.py`
- **Line 13** `on_user_logged_in` (business_logic_function): 20 lines — standalone function with business logic

### `apps/handlers/registration/tokens.py`
- **Line 21** `RegistrationTokenGenerator` (business_logic_class): 5 methods — no package delegation detected
- **Line 34** `make_token` (business_logic_function): 16 lines — standalone function with business logic
- **Line 52** `validate_token` (business_logic_function): 21 lines — standalone function with business logic
- **Line 75** `check_token` (business_logic_function): 20 lines — standalone function with business logic
- **Line 97** `make_allauth_compatible_token` (business_logic_function): 28 lines — standalone function with business logic

### `apps/handlers/registration/views.py`
- **Line 47** `rate_limit_check` (business_logic_function): 16 lines — standalone function with business logic
- **Line 79** `ensure_groups_exist` (business_logic_function): 12 lines — standalone function with business logic
- **Line 115** `trigger_notification` (business_logic_function): 25 lines — standalone function with business logic
- **Line 474** `_ensure_profile_exists` (business_logic_function): 22 lines — standalone function with business logic
- **Line 170** `post` (business_logic_function): 118 lines — standalone function with business logic
- **Line 309** `_get_user_from_token` (business_logic_function): 21 lines — standalone function with business logic
- **Line 332** `get` (business_logic_function): 46 lines — standalone function with business logic
- **Line 380** `post` (business_logic_function): 82 lines — standalone function with business logic

### `apps/handlers/services/certificates.py`
- **Line 14** `CertificateService` (business_logic_class): 4 methods — no package delegation detected
- **Line 20** `issue_certificate` (business_logic_function): 48 lines — standalone function with business logic
- **Line 71** `validate_certificate` (business_logic_function): 62 lines — standalone function with business logic
- **Line 136** `get_certificate_profile` (business_logic_function): 61 lines — standalone function with business logic
- **Line 200** `generate_certificate_report` (business_logic_function): 82 lines — standalone function with business logic

### `apps/handlers/services/email/service.py`
- **Line 14** `EmailService` (business_logic_class): 8 methods — consider extracting to package
- **Line 22** `send` (business_logic_function): 61 lines — standalone function with business logic
- **Line 85** `send_simple` (business_logic_function): 47 lines — standalone function with business logic
- **Line 134** `queue` (business_logic_function): 31 lines — standalone function with business logic
- **Line 187** `send_enrollment_confirmation` (business_logic_function): 17 lines — standalone function with business logic
- **Line 206** `send_course_completion` (business_logic_function): 17 lines — standalone function with business logic

### `apps/handlers/services/email/tasks.py`
- **Line 9** `send_email_task` (business_logic_function): 27 lines — standalone function with business logic
- **Line 38** `send_bulk_email_task` (business_logic_function): 33 lines — standalone function with business logic
- **Line 73** `send_email_raw` (business_logic_function): 30 lines — standalone function with business logic

### `apps/handlers/services/form_submission.py`
- **Line 28** `save_submission` (business_logic_function): 28 lines — standalone function with business logic
- **Line 59** `send_notification_email` (business_logic_function): 61 lines — standalone function with business logic
- **Line 123** `_build_plain_email` (business_logic_function): 20 lines — standalone function with business logic
- **Line 146** `get_submissions_for_form` (business_logic_function): 24 lines — standalone function with business logic
- **Line 173** `get_submission_stats` (business_logic_function): 28 lines — standalone function with business logic

### `apps/handlers/services/messages.py`
- **Line 16** `MessageService` (business_logic_class): 5 methods — no package delegation detected
- **Line 22** `send_message` (business_logic_function): 58 lines — standalone function with business logic
- **Line 83** `send_bulk_notification` (business_logic_function): 57 lines — standalone function with business logic
- **Line 143** `get_conversation_thread` (business_logic_function): 65 lines — standalone function with business logic
- **Line 211** `get_message_analytics` (business_logic_function): 118 lines — standalone function with business logic
- **Line 332** `_calculate_message_trends` (business_logic_function): 32 lines — standalone function with business logic

### `apps/handlers/services/notes_service.py`
- **Line 18** `NotesService` (business_logic_class): 15 methods — no package delegation detected
- **Line 22** `create_note` (business_logic_function): 30 lines — standalone function with business logic
- **Line 74** `get_user_notes` (business_logic_function): 12 lines — standalone function with business logic
- **Line 127** `share_note` (business_logic_function): 17 lines — standalone function with business logic
- **Line 153** `get_note_permissions` (business_logic_function): 37 lines — standalone function with business logic
- **Line 193** `search_notes` (business_logic_function): 11 lines — standalone function with business logic

### `apps/handlers/services/person.py`
- **Line 19** `PersonService` (business_logic_class): 9 methods — consider extracting to package
- **Line 26** `create_person_with_profile` (business_logic_function): 34 lines — standalone function with business logic
- **Line 63** `_create_or_link_profile` (business_logic_function): 30 lines — standalone function with business logic
- **Line 96** `_link_alternative_profile` (business_logic_function): 24 lines — standalone function with business logic
- **Line 123** `get_user_profile_information` (business_logic_function): 62 lines — standalone function with business logic
- **Line 195** `_calculate_profile_stats` (business_logic_function): 38 lines — standalone function with business logic
- **Line 236** `sync_person_with_user` (business_logic_function): 41 lines — standalone function with business logic
- **Line 280** `update_notification_preferences` (business_logic_function): 45 lines — standalone function with business logic
- **Line 328** `invite_person_to_register` (business_logic_function): 73 lines — standalone function with business logic

### `apps/handlers/signals.py`
- **Line 15** `handle_file_uploads` (business_logic_function): 27 lines — standalone function with business logic
- **Line 49** `create_user_profiles` (business_logic_function): 37 lines — standalone function with business logic

### `apps/handlers/site/asset_health.py`
- **Line 8** `asset_health_check` (business_logic_function): 118 lines — standalone function with business logic

### `apps/handlers/site/blog.py`
- **Line 29** `get_context_data` (business_logic_function): 32 lines — standalone function with business logic
- **Line 88** `post` (business_logic_function): 57 lines — standalone function with business logic
- **Line 160** `get` (business_logic_function): 12 lines — standalone function with business logic
- **Line 174** `post` (business_logic_function): 57 lines — standalone function with business logic
- **Line 240** `post` (business_logic_function): 23 lines — standalone function with business logic

### `apps/handlers/site/cart.py`
- **Line 30** `_get_cart_items` (business_logic_function): 46 lines — standalone function with business logic
- **Line 97** `get` (business_logic_function): 13 lines — standalone function with business logic
- **Line 118** `post` (business_logic_function): 32 lines — standalone function with business logic
- **Line 158** `delete` (business_logic_function): 17 lines — standalone function with business logic
- **Line 183** `post` (business_logic_function): 34 lines — standalone function with business logic
- **Line 228** `get_context_data` (business_logic_function): 21 lines — standalone function with business logic

### `apps/handlers/site/certifications.py`
- **Line 28** `get_context_data` (business_logic_function): 39 lines — standalone function with business logic
- **Line 83** `upload_certificate` (business_logic_function): 54 lines — standalone function with business logic

### `apps/handlers/site/courses.py`
- **Line 24** `get_context_data` (business_logic_function): 40 lines — standalone function with business logic
- **Line 81** `enroll_course` (business_logic_function): 56 lines — standalone function with business logic

### `apps/handlers/site/dashboard.py`
- **Line 26** `get_context_data` (business_logic_function): 67 lines — standalone function with business logic
- **Line 95** `_get_tag_analytics` (business_logic_function): 15 lines — standalone function with business logic
- **Line 112** `_get_recent_activity` (business_logic_function): 42 lines — standalone function with business logic
- **Line 156** `_get_learning_statistics` (business_logic_function): 23 lines — standalone function with business logic
- **Line 181** `_calculate_learning_streak` (business_logic_function): 24 lines — standalone function with business logic
- **Line 207** `_get_quick_actions` (business_logic_function): 61 lines — standalone function with business logic

### `apps/handlers/site/media_health.py`
- **Line 8** `media_health_check` (business_logic_function): 82 lines — standalone function with business logic

### `apps/handlers/site/messages.py`
- **Line 28** `get_context_data` (business_logic_function): 43 lines — standalone function with business logic
- **Line 76** `send_message` (business_logic_function): 60 lines — standalone function with business logic

### `apps/handlers/site/notes.py`
- **Line 28** `get_context_data` (business_logic_function): 40 lines — standalone function with business logic
- **Line 76** `_get_note_filters` (business_logic_function): 19 lines — standalone function with business logic
- **Line 100** `create_note` (business_logic_function): 52 lines — standalone function with business logic
- **Line 164** `get_context_data` (business_logic_function): 45 lines — standalone function with business logic
- **Line 211** `_get_recent_activity` (business_logic_function): 60 lines — standalone function with business logic
- **Line 273** `_get_quick_actions` (business_logic_function): 66 lines — standalone function with business logic
- **Line 341** `_calculate_overall_stats` (business_logic_function): 19 lines — standalone function with business logic
- **Line 369** `_calculate_activity_score` (business_logic_function): 19 lines — standalone function with business logic

### `apps/handlers/site/profile.py`
- **Line 28** `get_context_data` (business_logic_function): 52 lines — standalone function with business logic
- **Line 109** `get_context_data` (business_logic_function): 35 lines — standalone function with business logic
- **Line 152** `post` (business_logic_function): 46 lines — standalone function with business logic
- **Line 206** `post` (business_logic_function): 28 lines — standalone function with business logic

### `apps/handlers/site/tags.py`
- **Line 27** `get_context_data` (business_logic_function): 46 lines — standalone function with business logic
- **Line 75** `_get_tag_analytics` (business_logic_function): 28 lines — standalone function with business logic
- **Line 105** `_generate_tag_cloud` (business_logic_function): 33 lines — standalone function with business logic
- **Line 142** `search_tags_api` (business_logic_function): 46 lines — standalone function with business logic
- **Line 193** `merge_tags_api` (business_logic_function): 70 lines — standalone function with business logic

### `apps/handlers/snippets/base.py`
- **Line 34** `BaseSnippetViewSet` (business_logic_class): 8 methods — no package delegation detected
- **Line 50** `duplicate` (business_logic_function): 12 lines — standalone function with business logic
- **Line 67** `export_csv` (business_logic_function): 17 lines — standalone function with business logic

### `apps/handlers/snippets/manage/team.py`
- **Line 87** `status_display` (business_logic_function): 14 lines — standalone function with business logic

### `apps/handlers/snippets/newsletter/content.py`
- **Line 84** `send_test_email_action` (business_logic_function): 12 lines — standalone function with business logic
- **Line 101** `duplicate_newsletter_action` (business_logic_function): 13 lines — standalone function with business logic

### `apps/handlers/snippets/newsletter/template.py`
- **Line 56** `set_default_template` (business_logic_function): 16 lines — standalone function with business logic

### `apps/handlers/snippets/tags.py`
- **Line 96** `display_tag` (business_logic_function): 12 lines — standalone function with business logic
- **Line 141** `usage_count_display` (business_logic_function): 13 lines — standalone function with business logic
- **Line 175** `get_extra_actions` (business_logic_function): 25 lines — standalone function with business logic
- **Line 284** `display_category` (business_logic_function): 12 lines — standalone function with business logic
- **Line 417** `display_tag` (business_logic_function): 12 lines — standalone function with business logic
- **Line 462** `usage_count_display` (business_logic_function): 13 lines — standalone function with business logic
- **Line 558** `display_category` (business_logic_function): 12 lines — standalone function with business logic

### `apps/handlers/views/notes.py`
- **Line 20** `notes_section` (business_logic_function): 12 lines — standalone function with business logic
- **Line 37** `notes_list` (business_logic_function): 11 lines — standalone function with business logic
- **Line 79** `create_note` (business_logic_function): 21 lines — standalone function with business logic
- **Line 105** `update_note` (business_logic_function): 25 lines — standalone function with business logic
- **Line 150** `pin_note` (business_logic_function): 16 lines — standalone function with business logic
- **Line 171** `unpin_note` (business_logic_function): 16 lines — standalone function with business logic
- **Line 192** `archive_note` (business_logic_function): 16 lines — standalone function with business logic
- **Line 213** `search_notes` (business_logic_function): 21 lines — standalone function with business logic

### `apps/handlers/views/privacy.py`
- **Line 21** `privacy_policy_modal` (business_logic_function): 14 lines — standalone function with business logic
- **Line 39** `terms_modal` (business_logic_function): 14 lines — standalone function with business logic
- **Line 58** `accept_privacy_policy` (business_logic_function): 22 lines — standalone function with business logic
- **Line 85** `accept_terms` (business_logic_function): 22 lines — standalone function with business logic
- **Line 111** `check_consent_status` (business_logic_function): 27 lines — standalone function with business logic

### `apps/handlers/views/tags.py`
- **Line 138** `search_tags` (business_logic_function): 14 lines — standalone function with business logic
- **Line 156** `filter_by_tags` (business_logic_function): 47 lines — standalone function with business logic
- **Line 30** `get_context_data` (business_logic_function): 12 lines — standalone function with business logic
- **Line 53** `get_context_data` (business_logic_function): 23 lines — standalone function with business logic
- **Line 87** `get_queryset` (business_logic_function): 11 lines — standalone function with business logic
- **Line 116** `get_queryset` (business_logic_function): 11 lines — standalone function with business logic

### `apps/lms/managers/course.py`
- **Line 21** `CourseManager` (business_logic_class): 7 methods — consider extracting to package
- **Line 35** `get_user_enrolled_courses` (business_logic_function): 80 lines — standalone function with business logic
- **Line 118** `_get_user_interests` (business_logic_function): 44 lines — standalone function with business logic
- **Line 165** `get_user_learning_path` (business_logic_function): 58 lines — standalone function with business logic
- **Line 226** `_assess_user_skills` (business_logic_function): 56 lines — standalone function with business logic
- **Line 289** `get_user_course_completion_analytics` (business_logic_function): 94 lines — standalone function with business logic
- **Line 390** `_apply_filters` (business_logic_function): 63 lines — standalone function with business logic

### `apps/lms/managers/enrollments.py`
- **Line 17** `get_user_enrollments` (business_logic_function): 26 lines — standalone function with business logic
- **Line 45** `get_enrollment_analytics` (business_logic_function): 46 lines — standalone function with business logic
- **Line 93** `get_course_enrollments` (business_logic_function): 22 lines — standalone function with business logic
- **Line 117** `get_learning_path` (business_logic_function): 60 lines — standalone function with business logic
- **Line 179** `bulk_update_progress` (business_logic_function): 20 lines — standalone function with business logic
- **Line 201** `cleanup_inactive_enrollments` (business_logic_function): 26 lines — standalone function with business logic

### `apps/lms/managers/module.py`
- **Line 18** `get_module_completion_stats` (business_logic_function): 54 lines — standalone function with business logic
- **Line 74** `reorder_modules` (business_logic_function): 36 lines — standalone function with business logic

### `apps/lms/managers/progress.py`
- **Line 34** `update_lesson_progress` (business_logic_function): 74 lines — standalone function with business logic
- **Line 110** `update_module_progress` (business_logic_function): 63 lines — standalone function with business logic
- **Line 175** `_get_enrollment_for_course` (business_logic_function): 11 lines — standalone function with business logic
- **Line 188** `_update_or_create_lesson_progress` (business_logic_function): 59 lines — standalone function with business logic
- **Line 249** `_update_or_create_module_progress` (business_logic_function): 21 lines — standalone function with business logic
- **Line 272** `_update_module_progress_from_lesson` (business_logic_function): 25 lines — standalone function with business logic
- **Line 299** `_mark_lessons_completed` (business_logic_function): 25 lines — standalone function with business logic
- **Line 326** `_update_course_progress_from_lesson` (business_logic_function): 27 lines — standalone function with business logic
- **Line 355** `_update_course_progress_from_module` (business_logic_function): 33 lines — standalone function with business logic
- **Line 400** `_check_course_completion` (business_logic_function): 14 lines — standalone function with business logic
- **Line 416** `_get_next_lesson` (business_logic_function): 52 lines — standalone function with business logic
- **Line 482** `get_progress_overview` (business_logic_function): 58 lines — standalone function with business logic
- **Line 542** `_get_recent_progress_activity` (business_logic_function): 23 lines — standalone function with business logic
- **Line 567** `bulk_update_progress` (business_logic_function): 87 lines — standalone function with business logic

### `apps/lms/models/certificate.py`
- **Line 11** `Certificate` (business_logic_class): 4 methods — no package delegation detected

### `apps/lms/models/classes.py`
- **Line 310** `next_occurrence` (business_logic_function): 18 lines — standalone function with business logic
- **Line 347** `clean` (business_logic_function): 18 lines — standalone function with business logic
- **Line 367** `generate_occurrences` (business_logic_function): 15 lines — standalone function with business logic
- **Line 406** `get_ongoing_sessions` (business_logic_function): 12 lines — standalone function with business logic
- **Line 731** `clean` (business_logic_function): 17 lines — standalone function with business logic
- **Line 750** `save` (business_logic_function): 14 lines — standalone function with business logic

### `apps/lms/models/courses/index.py`
- **Line 107** `get_published_courses` (business_logic_function): 17 lines — standalone function with business logic
- **Line 127** `get_listed_items` (business_logic_function): 33 lines — standalone function with business logic
- **Line 181** `get_context` (business_logic_function): 57 lines — standalone function with business logic

### `apps/lms/models/courses/info.py`
- **Line 439** `_compute_final_price` (business_logic_function): 17 lines — standalone function with business logic
- **Line 458** `save` (business_logic_function): 25 lines — standalone function with business logic
- **Line 495** `get_course_details` (business_logic_function): 28 lines — standalone function with business logic
- **Line 546** `get_cached_search_results` (business_logic_function): 18 lines — standalone function with business logic

### `apps/lms/models/courses/progress.py`
- **Line 73** `update_progress` (business_logic_function): 14 lines — standalone function with business logic
- **Line 89** `get_lesson_progress_stats` (business_logic_function): 18 lines — standalone function with business logic
- **Line 166** `complete` (business_logic_function): 39 lines — standalone function with business logic
- **Line 207** `update_progress` (business_logic_function): 12 lines — standalone function with business logic

### `apps/lms/models/courses/specification.py`
- **Line 21** `Lesson` (business_logic_class): 7 methods — no package delegation detected
- **Line 190** `save` (business_logic_function): 12 lines — standalone function with business logic

### `apps/lms/models/quiz.py`
- **Line 295** `complete` (business_logic_function): 17 lines — standalone function with business logic
- **Line 371** `evaluate` (business_logic_function): 29 lines — standalone function with business logic

### `apps/lms/models/wishlist.py`
- **Line 10** `Wishlist` (business_logic_class): 5 methods — no package delegation detected

### `apps/lms/services/certificates.py`
- **Line 14** `CertificateService` (business_logic_class): 6 methods — no package delegation detected
- **Line 20** `create_certificate` (business_logic_function): 37 lines — standalone function with business logic
- **Line 60** `_get_user_display_name` (business_logic_function): 11 lines — standalone function with business logic
- **Line 74** `generate_pdf` (business_logic_function): 39 lines — standalone function with business logic
- **Line 116** `_draw_certificate_content` (business_logic_function): 48 lines — standalone function with business logic
- **Line 167** `verify_certificate` (business_logic_function): 25 lines — standalone function with business logic

### `apps/lms/services/courses.py`
- **Line 25** `CourseService` (business_logic_class): 13 methods — consider extracting to package
- **Line 39** `execute` (business_logic_function): 17 lines — standalone function with business logic
- **Line 58** `enroll_user` (business_logic_function): 66 lines — standalone function with business logic
- **Line 126** `update_course_progress` (business_logic_function): 48 lines — standalone function with business logic
- **Line 176** `get_user_course_dashboard` (business_logic_function): 77 lines — standalone function with business logic
- **Line 255** `generate_course_completion_report` (business_logic_function): 113 lines — standalone function with business logic
- **Line 378** `_apply_filters` (business_logic_function): 26 lines — standalone function with business logic
- **Line 406** `get_user_recommended_courses` (business_logic_function): 66 lines — standalone function with business logic
- **Line 474** `get_published_courses_cached` (business_logic_function): 73 lines — standalone function with business logic
- **Line 549** `get_course_by_slug_cached` (business_logic_function): 77 lines — standalone function with business logic
- **Line 629** `_get_user_interests` (business_logic_function): 19 lines — standalone function with business logic
- **Line 650** `_get_path_courses` (business_logic_function): 72 lines — standalone function with business logic

### `apps/lms/services/enrollments.py`
- **Line 55** `get_user_learning_dashboard` (business_logic_function): 62 lines — standalone function with business logic
- **Line 120** `_get_learning_analytics` (business_logic_function): 67 lines — standalone function with business logic
- **Line 190** `_get_active_courses_with_progress` (business_logic_function): 46 lines — standalone function with business logic
- **Line 239** `_get_next_lesson_for_enrollment` (business_logic_function): 39 lines — standalone function with business logic
- **Line 281** `_estimate_completion_date` (business_logic_function): 18 lines — standalone function with business logic
- **Line 302** `_is_behind_schedule` (business_logic_function): 15 lines — standalone function with business logic
- **Line 320** `_calculate_course_priority` (business_logic_function): 34 lines — standalone function with business logic
- **Line 357** `_get_completion_timeline` (business_logic_function): 22 lines — standalone function with business logic
- **Line 382** `_get_learning_habits` (business_logic_function): 41 lines — standalone function with business logic
- **Line 426** `_get_course_recommendations` (business_logic_function): 44 lines — standalone function with business logic
- **Line 473** `_calculate_relevance_score` (business_logic_function): 28 lines — standalone function with business logic
- **Line 508** `update_course_progress` (business_logic_function): 106 lines — standalone function with business logic
- **Line 617** `_update_module_progress` (business_logic_function): 24 lines — standalone function with business logic
- **Line 644** `_update_course_overall_progress` (business_logic_function): 16 lines — standalone function with business logic
- **Line 676** `enroll_user_in_multiple_courses` (business_logic_function): 84 lines — standalone function with business logic
- **Line 763** `sync_enrollment_progress_from_external` (business_logic_function): 75 lines — standalone function with business logic
- **Line 845** `get_enrollment_certificate_info` (business_logic_function): 66 lines — standalone function with business logic
- **Line 914** `validate_enrollment_for_access` (business_logic_function): 81 lines — standalone function with business logic
- **Line 998** `_check_lesson_availability` (business_logic_function): 22 lines — standalone function with business logic
- **Line 1023** `_invalidate_enrollment_caches` (business_logic_function): 15 lines — standalone function with business logic

### `apps/lms/services/legacy.py`
- **Line 53** `get_user_learning_dashboard` (business_logic_function): 62 lines — standalone function with business logic
- **Line 118** `_get_learning_analytics` (business_logic_function): 68 lines — standalone function with business logic
- **Line 189** `_get_active_courses_with_progress` (business_logic_function): 46 lines — standalone function with business logic
- **Line 238** `_get_next_lesson_for_enrollment` (business_logic_function): 33 lines — standalone function with business logic
- **Line 274** `_estimate_completion_date` (business_logic_function): 18 lines — standalone function with business logic
- **Line 295** `_is_behind_schedule` (business_logic_function): 15 lines — standalone function with business logic
- **Line 313** `_calculate_course_priority` (business_logic_function): 34 lines — standalone function with business logic
- **Line 350** `_get_completion_timeline` (business_logic_function): 26 lines — standalone function with business logic
- **Line 379** `_get_learning_habits` (business_logic_function): 44 lines — standalone function with business logic
- **Line 426** `_get_course_recommendations` (business_logic_function): 44 lines — standalone function with business logic
- **Line 473** `_calculate_relevance_score` (business_logic_function): 29 lines — standalone function with business logic
- **Line 509** `update_course_progress` (business_logic_function): 108 lines — standalone function with business logic
- **Line 620** `_update_module_progress` (business_logic_function): 26 lines — standalone function with business logic
- **Line 649** `_update_course_overall_progress` (business_logic_function): 17 lines — standalone function with business logic
- **Line 682** `enroll_user_in_multiple_courses` (business_logic_function): 87 lines — standalone function with business logic
- **Line 772** `sync_enrollment_progress_from_external` (business_logic_function): 81 lines — standalone function with business logic
- **Line 860** `get_enrollment_certificate_info` (business_logic_function): 68 lines — standalone function with business logic
- **Line 931** `validate_enrollment_for_access` (business_logic_function): 82 lines — standalone function with business logic
- **Line 1016** `_check_lesson_availability` (business_logic_function): 23 lines — standalone function with business logic
- **Line 1042** `_invalidate_enrollment_caches` (business_logic_function): 15 lines — standalone function with business logic

### `apps/lms/services/lessons.py`
- **Line 27** `get_course_modules` (business_logic_function): 21 lines — standalone function with business logic
- **Line 68** `get_course_lessons` (business_logic_function): 35 lines — standalone function with business logic
- **Line 106** `get_module_lessons` (business_logic_function): 26 lines — standalone function with business logic
- **Line 135** `get_lesson_with_context` (business_logic_function): 44 lines — standalone function with business logic
- **Line 182** `_check_lesson_access` (business_logic_function): 23 lines — standalone function with business logic
- **Line 208** `mark_lesson_as_completed` (business_logic_function): 57 lines — standalone function with business logic
- **Line 268** `_check_course_completion` (business_logic_function): 22 lines — standalone function with business logic
- **Line 293** `get_lesson_progress` (business_logic_function): 31 lines — standalone function with business logic
- **Line 327** `update_lesson` (business_logic_function): 91 lines — standalone function with business logic
- **Line 421** `_invalidate_lesson_caches` (business_logic_function): 11 lines — standalone function with business logic

### `apps/lms/services/notes.py`
- **Line 11** `NoteService` (business_logic_class): 6 methods — no package delegation detected
- **Line 17** `create_note` (business_logic_function): 64 lines — standalone function with business logic
- **Line 84** `update_note` (business_logic_function): 42 lines — standalone function with business logic
- **Line 129** `share_note` (business_logic_function): 62 lines — standalone function with business logic
- **Line 194** `search_notes` (business_logic_function): 45 lines — standalone function with business logic
- **Line 242** `get_note_analytics` (business_logic_function): 69 lines — standalone function with business logic
- **Line 314** `_calculate_note_trends` (business_logic_function): 26 lines — standalone function with business logic

### `apps/lms/signals.py`
- **Line 24** `create_lms_profiles` (business_logic_function): 39 lines — standalone function with business logic

### `apps/lms/snippets/specialization.py`
- **Line 69** `update_courses_count_action` (business_logic_function): 18 lines — standalone function with business logic

### `apps/lms/views/cart.py`
- **Line 49** `get_context_data` (business_logic_function): 14 lines — standalone function with business logic
- **Line 65** `post` (business_logic_function): 85 lines — standalone function with business logic
- **Line 163** `clear_enrollment_cache` (business_logic_function): 13 lines — standalone function with business logic
- **Line 188** `get_context_data` (business_logic_function): 11 lines — standalone function with business logic
- **Line 307** `get_context_data` (business_logic_function): 19 lines — standalone function with business logic

### `apps/lms/views/courses.py`
- **Line 37** `dispatch` (business_logic_function): 12 lines — standalone function with business logic
- **Line 51** `get_course_context` (business_logic_function): 32 lines — standalone function with business logic
- **Line 85** `get_context_data` (business_logic_function): 39 lines — standalone function with business logic
- **Line 126** `get` (business_logic_function): 30 lines — standalone function with business logic
- **Line 166** `get_context_data` (business_logic_function): 21 lines — standalone function with business logic
- **Line 189** `get_course_header_fragment` (business_logic_function): 17 lines — standalone function with business logic
- **Line 212** `get_sidebar_fragment` (business_logic_function): 17 lines — standalone function with business logic
- **Line 254** `get_queryset` (business_logic_function): 16 lines — standalone function with business logic
- **Line 272** `_build_filters` (business_logic_function): 36 lines — standalone function with business logic
- **Line 310** `get_context_data` (business_logic_function): 33 lines — standalone function with business logic
- **Line 345** `_get_filter_options` (business_logic_function): 86 lines — standalone function with business logic
- **Line 433** `render_to_response` (business_logic_function): 11 lines — standalone function with business logic
- **Line 458** `get` (business_logic_function): 50 lines — standalone function with business logic
- **Line 510** `_build_filters` (business_logic_function): 20 lines — standalone function with business logic

### `apps/lms/views/lessons.py`
- **Line 21** `get` (business_logic_function): 39 lines — standalone function with business logic
- **Line 63** `get_user_progress` (business_logic_function): 21 lines — standalone function with business logic
- **Line 86** `get_completed_lessons` (business_logic_function): 13 lines — standalone function with business logic
- **Line 108** `post` (business_logic_function): 15 lines — standalone function with business logic
- **Line 125** `mark_lesson_complete` (business_logic_function): 14 lines — standalone function with business logic
- **Line 156** `get` (business_logic_function): 22 lines — standalone function with business logic
- **Line 180** `get_last_watched_lesson` (business_logic_function): 28 lines — standalone function with business logic

### `apps/pages/models/contact.py`
- **Line 166** `get_name` (business_logic_function): 14 lines — standalone function with business logic
- **Line 204** `export_as_dict` (business_logic_function): 20 lines — standalone function with business logic
- **Line 226** `export_as_csv_row` (business_logic_function): 13 lines — standalone function with business logic

### `apps/pages/models/pages/base.py`
- **Line 74** `serve` (business_logic_function): 28 lines — standalone function with business logic
- **Line 105** `get_context` (business_logic_function): 60 lines — standalone function with business logic
- **Line 168** `get_listed_data` (business_logic_function): 21 lines — standalone function with business logic
- **Line 312** `serve` (business_logic_function): 41 lines — standalone function with business logic
- **Line 355** `send_submission_email` (business_logic_function): 52 lines — standalone function with business logic
- **Line 547** `get_context` (business_logic_function): 29 lines — standalone function with business logic

### `apps/pages/search/views.py`
- **Line 13** `search` (business_logic_function): 32 lines — standalone function with business logic

### `apps/pages/signals/default.py`
- **Line 10** `create_default_groups` (business_logic_function): 77 lines — standalone function with business logic
- **Line 92** `assign_default_permissions` (business_logic_function): 35 lines — standalone function with business logic

### `apps/pages/signals/profile.py`
- **Line 13** `sync_profile_to_user` (business_logic_function): 26 lines — standalone function with business logic

### `apps/pages/signals/user.py`
- **Line 28** `create_user_related_records` (business_logic_function): 84 lines — standalone function with business logic


## Project: structa.cloud
**Violations**: 403

### `apps/accounts/management/commands/sync_xellent.py`
- **Line 9** `handle` (business_logic_function): 31 lines — standalone function with business logic

### `apps/accounts/management/commands/validate_config.py`
- **Line 70** `_load_env_file` (business_logic_function): 17 lines — standalone function with business logic
- **Line 90** `_collect_yaml_keys` (business_logic_function): 42 lines — standalone function with business logic
- **Line 135** `_check_secret_key` (business_logic_function): 22 lines — standalone function with business logic
- **Line 176** `handle` (business_logic_function): 130 lines — standalone function with business logic

### `apps/accounts/management/commands/verify_deployment.py`
- **Line 67** `_run` (business_logic_function): 13 lines — standalone function with business logic
- **Line 114** `_check_container_status` (business_logic_function): 19 lines — standalone function with business logic
- **Line 136** `_check_network` (business_logic_function): 18 lines — standalone function with business logic
- **Line 170** `_check_env_vars` (business_logic_function): 38 lines — standalone function with business logic
- **Line 211** `_check_traefik_config` (business_logic_function): 33 lines — standalone function with business logic
- **Line 247** `_check_dependencies` (business_logic_function): 14 lines — standalone function with business logic
- **Line 264** `_check_health` (business_logic_function): 18 lines — standalone function with business logic
- **Line 305** `handle` (business_logic_function): 151 lines — standalone function with business logic

### `apps/accounts/managers/certificates.py`
- **Line 18** `get_valid_certificates` (business_logic_function): 19 lines — standalone function with business logic
- **Line 39** `get_expiring_soon` (business_logic_function): 20 lines — standalone function with business logic
- **Line 61** `verify_certificate` (business_logic_function): 20 lines — standalone function with business logic
- **Line 84** `get_certificate_stats` (business_logic_function): 25 lines — standalone function with business logic
- **Line 111** `get_certificates_by_issuer` (business_logic_function): 23 lines — standalone function with business logic
- **Line 136** `bulk_verify_certificates` (business_logic_function): 34 lines — standalone function with business logic

### `apps/accounts/managers/messages.py`
- **Line 18** `get_user_messages` (business_logic_function): 26 lines — standalone function with business logic
- **Line 46** `get_conversation` (business_logic_function): 33 lines — standalone function with business logic
- **Line 81** `send_system_message` (business_logic_function): 31 lines — standalone function with business logic
- **Line 114** `send_bulk_messages` (business_logic_function): 31 lines — standalone function with business logic
- **Line 148** `get_message_statistics` (business_logic_function): 25 lines — standalone function with business logic
- **Line 175** `_get_top_senders` (business_logic_function): 17 lines — standalone function with business logic
- **Line 194** `_get_recent_message_activity` (business_logic_function): 15 lines — standalone function with business logic
- **Line 211** `cleanup_old_messages` (business_logic_function): 22 lines — standalone function with business logic
- **Line 235** `mark_conversation_as_read` (business_logic_function): 17 lines — standalone function with business logic

### `apps/accounts/managers/notes.py`
- **Line 18** `get_user_notes` (business_logic_function): 30 lines — standalone function with business logic
- **Line 51** `search_notes` (business_logic_function): 45 lines — standalone function with business logic
- **Line 98** `get_pinned_notes` (business_logic_function): 14 lines — standalone function with business logic
- **Line 114** `get_recent_notes` (business_logic_function): 13 lines — standalone function with business logic
- **Line 130** `get_note_statistics` (business_logic_function): 29 lines — standalone function with business logic
- **Line 172** `bulk_update_notes` (business_logic_function): 19 lines — standalone function with business logic
- **Line 193** `get_notes_by_tag` (business_logic_function): 13 lines — standalone function with business logic
- **Line 208** `get_notes_by_date_range` (business_logic_function): 14 lines — standalone function with business logic

### `apps/accounts/managers/peoples.py`
- **Line 27** `PersonManager` (business_logic_class): 33 methods — consider extracting to package
- **Line 68** `get_complete_profiles` (business_logic_function): 12 lines — standalone function with business logic
- **Line 127** `get_or_create_for_user` (business_logic_function): 24 lines — standalone function with business logic
- **Line 156** `search` (business_logic_function): 15 lines — standalone function with business logic
- **Line 173** `filter_by_demographics` (business_logic_function): 38 lines — standalone function with business logic
- **Line 213** `filter_by_notification_preferences` (business_logic_function): 21 lines — standalone function with business logic
- **Line 239** `update_last_active` (business_logic_function): 11 lines — standalone function with business logic
- **Line 252** `verify_email` (business_logic_function): 15 lines — standalone function with business logic
- **Line 280** `activate_person` (business_logic_function): 16 lines — standalone function with business logic
- **Line 298** `deactivate_person` (business_logic_function): 16 lines — standalone function with business logic
- **Line 316** `get_profile_statistics` (business_logic_function): 47 lines — standalone function with business logic
- **Line 397** `bulk_update_last_active` (business_logic_function): 11 lines — standalone function with business logic
- **Line 410** `bulk_verify_emails` (business_logic_function): 16 lines — standalone function with business logic
- **Line 428** `bulk_activate` (business_logic_function): 19 lines — standalone function with business logic
- **Line 449** `bulk_update_notification_preferences` (business_logic_function): 19 lines — standalone function with business logic
- **Line 473** `get_statistics` (business_logic_function): 37 lines — standalone function with business logic
- **Line 515** `get_or_create_user_profile` (business_logic_function): 28 lines — standalone function with business logic
- **Line 548** `invalidate_object_cache` (business_logic_function): 27 lines — standalone function with business logic

### `apps/accounts/middleware/privacy_consent.py`
- **Line 34** `__call__` (business_logic_function): 30 lines — standalone function with business logic

### `apps/accounts/models/blog/index.py`
- **Line 77** `get_posts` (business_logic_function): 14 lines — standalone function with business logic
- **Line 122** `get_context` (business_logic_function): 22 lines — standalone function with business logic
- **Line 158** `tag_archive` (business_logic_function): 13 lines — standalone function with business logic
- **Line 174** `author_archive` (business_logic_function): 13 lines — standalone function with business logic

### `apps/accounts/models/blog/post.py`
- **Line 332** `add_author` (business_logic_function): 22 lines — standalone function with business logic
- **Line 356** `add_tag_with_metadata` (business_logic_function): 22 lines — standalone function with business logic
- **Line 380** `set_primary_tag` (business_logic_function): 16 lines — standalone function with business logic
- **Line 398** `get_related_posts` (business_logic_function): 28 lines — standalone function with business logic
- **Line 443** `save` (business_logic_function): 22 lines — standalone function with business logic

### `apps/accounts/models/example_tagged_model.py`
- **Line 17** `add_tag` (business_logic_function): 12 lines — standalone function with business logic

### `apps/accounts/models/forms/submission.py`
- **Line 9** `FormSubmission` (business_logic_class): 5 methods — no package delegation detected

### `apps/accounts/models/manage/company.py`
- **Line 494** `clean` (business_logic_function): 25 lines — standalone function with business logic
- **Line 521** `save` (business_logic_function): 12 lines — standalone function with business logic
- **Line 883** `clean` (business_logic_function): 24 lines — standalone function with business logic
- **Line 909** `save` (business_logic_function): 14 lines — standalone function with business logic

### `apps/accounts/models/profiles/message.py`
- **Line 116** `reply` (business_logic_function): 13 lines — standalone function with business logic

### `apps/accounts/models/profiles/note.py`
- **Line 68** `save` (business_logic_function): 12 lines — standalone function with business logic

### `apps/accounts/models/profiles/privacy_consent.py`
- **Line 70** `record_consent` (business_logic_function): 19 lines — standalone function with business logic
- **Line 148** `record_consent` (business_logic_function): 19 lines — standalone function with business logic

### `apps/accounts/models/tags.py`
- **Line 13** `TagManager` (business_logic_class): 5 methods — no package delegation detected
- **Line 32** `filter_by_tags` (business_logic_function): 22 lines — standalone function with business logic

### `apps/accounts/processors/auth_utils.py`
- **Line 21** `AuthUtils` (business_logic_class): 6 methods — no package delegation detected
- **Line 34** `decode_jwt_token` (business_logic_function): 12 lines — standalone function with business logic

### `apps/accounts/processors/basic_auth.py`
- **Line 24** `AuthUtils` (business_logic_class): 6 methods — no package delegation detected
- **Line 37** `decode_jwt_token` (business_logic_function): 12 lines — standalone function with business logic
- **Line 93** `authenticate` (business_logic_function): 31 lines — standalone function with business logic

### `apps/accounts/processors/company.py`
- **Line 9** `contacts_list` (business_logic_function): 45 lines — standalone function with business logic
- **Line 57** `contact_details` (business_logic_function): 28 lines — standalone function with business logic
- **Line 88** `contact_company` (business_logic_function): 16 lines — standalone function with business logic
- **Line 107** `company_contacts` (business_logic_function): 16 lines — standalone function with business logic
- **Line 126** `company_contacts_details` (business_logic_function): 19 lines — standalone function with business logic

### `apps/accounts/processors/contacts.py`
- **Line 6** `contacts_list` (business_logic_function): 45 lines — standalone function with business logic
- **Line 54** `contact_details` (business_logic_function): 28 lines — standalone function with business logic
- **Line 85** `contact_company` (business_logic_function): 16 lines — standalone function with business logic
- **Line 104** `company_contacts` (business_logic_function): 16 lines — standalone function with business logic
- **Line 123** `company_contacts_details` (business_logic_function): 19 lines — standalone function with business logic

### `apps/accounts/processors/selectors.py`
- **Line 8** `get_filtered_branches` (business_logic_function): 11 lines — standalone function with business logic

### `apps/accounts/registration/adapter.py`
- **Line 21** `send_confirmation_mail` (business_logic_function): 22 lines — standalone function with business logic

### `apps/accounts/registration/allauth_views.py`
- **Line 83** `form_valid` (business_logic_function): 11 lines — standalone function with business logic

### `apps/accounts/registration/emails.py`
- **Line 25** `_get_sender_accounts` (business_logic_function): 18 lines — standalone function with business logic
- **Line 46** `_resolve_template` (business_logic_function): 26 lines — standalone function with business logic
- **Line 75** `send_registration_email` (business_logic_function): 60 lines — standalone function with business logic
- **Line 138** `send_signin_success_email` (business_logic_function): 58 lines — standalone function with business logic
- **Line 199** `_get_fallback_html` (business_logic_function): 11 lines — standalone function with business logic
- **Line 213** `_send_via_smtp` (business_logic_function): 34 lines — standalone function with business logic
- **Line 250** `_send_with_django_backend` (business_logic_function): 18 lines — standalone function with business logic

### `apps/accounts/registration/forms.py`
- **Line 100** `clean_password` (business_logic_function): 24 lines — standalone function with business logic

### `apps/accounts/registration/signals.py`
- **Line 11** `on_user_logged_in` (business_logic_function): 20 lines — standalone function with business logic

### `apps/accounts/registration/tokens.py`
- **Line 21** `RegistrationTokenGenerator` (business_logic_class): 5 methods — no package delegation detected
- **Line 44** `validate_token` (business_logic_function): 21 lines — standalone function with business logic
- **Line 67** `check_token` (business_logic_function): 15 lines — standalone function with business logic
- **Line 84** `make_allauth_compatible_token` (business_logic_function): 25 lines — standalone function with business logic

### `apps/accounts/registration/views.py`
- **Line 46** `rate_limit_check` (business_logic_function): 16 lines — standalone function with business logic
- **Line 78** `ensure_groups_exist` (business_logic_function): 12 lines — standalone function with business logic
- **Line 114** `trigger_notification` (business_logic_function): 25 lines — standalone function with business logic
- **Line 473** `_ensure_profile_exists` (business_logic_function): 22 lines — standalone function with business logic
- **Line 169** `post` (business_logic_function): 118 lines — standalone function with business logic
- **Line 308** `_get_user_from_token` (business_logic_function): 21 lines — standalone function with business logic
- **Line 331** `get` (business_logic_function): 46 lines — standalone function with business logic
- **Line 379** `post` (business_logic_function): 82 lines — standalone function with business logic

### `apps/accounts/services/certificates.py`
- **Line 16** `CertificateService` (business_logic_class): 4 methods — no package delegation detected
- **Line 22** `issue_certificate` (business_logic_function): 48 lines — standalone function with business logic
- **Line 73** `validate_certificate` (business_logic_function): 62 lines — standalone function with business logic
- **Line 138** `get_certificate_profile` (business_logic_function): 61 lines — standalone function with business logic
- **Line 202** `generate_certificate_report` (business_logic_function): 82 lines — standalone function with business logic

### `apps/accounts/services/email/service.py`
- **Line 20** `EmailService` (business_logic_class): 9 methods — consider extracting to package
- **Line 28** `send` (business_logic_function): 61 lines — standalone function with business logic
- **Line 91** `send_simple` (business_logic_function): 47 lines — standalone function with business logic
- **Line 140** `queue` (business_logic_function): 36 lines — standalone function with business logic
- **Line 206** `send_enrollment_confirmation` (business_logic_function): 17 lines — standalone function with business logic
- **Line 225** `send_course_completion` (business_logic_function): 17 lines — standalone function with business logic

### `apps/accounts/services/email/tasks.py`
- **Line 9** `send_email_task` (business_logic_function): 27 lines — standalone function with business logic
- **Line 38** `send_bulk_email_task` (business_logic_function): 33 lines — standalone function with business logic
- **Line 73** `send_email_raw` (business_logic_function): 30 lines — standalone function with business logic

### `apps/accounts/services/form_submission.py`
- **Line 18** `FormSubmissionService` (business_logic_class): 5 methods — no package delegation detected
- **Line 24** `save_submission` (business_logic_function): 28 lines — standalone function with business logic
- **Line 55** `send_notification_email` (business_logic_function): 61 lines — standalone function with business logic
- **Line 119** `_build_plain_email` (business_logic_function): 20 lines — standalone function with business logic
- **Line 142** `get_submissions_for_form` (business_logic_function): 24 lines — standalone function with business logic
- **Line 169** `get_submission_stats` (business_logic_function): 28 lines — standalone function with business logic

### `apps/accounts/services/messages.py`
- **Line 27** `send_message` (business_logic_function): 46 lines — standalone function with business logic
- **Line 76** `get_message_analytics` (business_logic_function): 118 lines — standalone function with business logic
- **Line 197** `_calculate_message_trends` (business_logic_function): 32 lines — standalone function with business logic

### `apps/accounts/services/notifications.py`
- **Line 13** `trigger_notification` (business_logic_function): 29 lines — standalone function with business logic

### `apps/accounts/services/person.py`
- **Line 28** `_create_or_link_profile` (business_logic_function): 30 lines — standalone function with business logic
- **Line 61** `_link_alternative_profile` (business_logic_function): 24 lines — standalone function with business logic
- **Line 88** `get_user_profile_information` (business_logic_function): 62 lines — standalone function with business logic
- **Line 160** `_calculate_profile_stats` (business_logic_function): 38 lines — standalone function with business logic
- **Line 202** `update_notification_preferences` (business_logic_function): 45 lines — standalone function with business logic

### `apps/accounts/signals.py`
- **Line 20** `handle_file_uploads` (business_logic_function): 27 lines — standalone function with business logic

### `apps/accounts/site/asset_health.py`
- **Line 8** `asset_health_check` (business_logic_function): 118 lines — standalone function with business logic

### `apps/accounts/site/auth.py`
- **Line 33** `post` (business_logic_function): 46 lines — standalone function with business logic

### `apps/accounts/site/cart.py`
- **Line 26** `_get_cart_items` (business_logic_function): 38 lines — standalone function with business logic
- **Line 85** `get` (business_logic_function): 13 lines — standalone function with business logic
- **Line 106** `post` (business_logic_function): 32 lines — standalone function with business logic
- **Line 146** `delete` (business_logic_function): 17 lines — standalone function with business logic
- **Line 175** `post` (business_logic_function): 35 lines — standalone function with business logic
- **Line 221** `get_context_data` (business_logic_function): 21 lines — standalone function with business logic

### `apps/accounts/site/dashboard.py`
- **Line 29** `get_context_data` (business_logic_function): 24 lines — standalone function with business logic
- **Line 55** `_get_tag_analytics` (business_logic_function): 12 lines — standalone function with business logic
- **Line 74** `_get_quick_actions` (business_logic_function): 19 lines — standalone function with business logic

### `apps/accounts/site/messages.py`
- **Line 36** `get_context_data` (business_logic_function): 43 lines — standalone function with business logic
- **Line 84** `send_message` (business_logic_function): 60 lines — standalone function with business logic

### `apps/accounts/site/notes.py`
- **Line 35** `get_context_data` (business_logic_function): 40 lines — standalone function with business logic
- **Line 83** `_get_note_filters` (business_logic_function): 19 lines — standalone function with business logic
- **Line 107** `create_note` (business_logic_function): 52 lines — standalone function with business logic
- **Line 171** `get_context_data` (business_logic_function): 45 lines — standalone function with business logic
- **Line 218** `_get_recent_activity` (business_logic_function): 60 lines — standalone function with business logic
- **Line 280** `_get_quick_actions` (business_logic_function): 66 lines — standalone function with business logic
- **Line 348** `_calculate_overall_stats` (business_logic_function): 19 lines — standalone function with business logic
- **Line 376** `_calculate_activity_score` (business_logic_function): 19 lines — standalone function with business logic

### `apps/accounts/site/profile.py`
- **Line 30** `get_context_data` (business_logic_function): 52 lines — standalone function with business logic
- **Line 111** `get_context_data` (business_logic_function): 35 lines — standalone function with business logic
- **Line 154** `post` (business_logic_function): 48 lines — standalone function with business logic
- **Line 210** `post` (business_logic_function): 28 lines — standalone function with business logic

### `apps/accounts/site/tags.py`
- **Line 30** `get_context_data` (business_logic_function): 46 lines — standalone function with business logic
- **Line 78** `_get_tag_analytics` (business_logic_function): 28 lines — standalone function with business logic
- **Line 108** `_generate_tag_cloud` (business_logic_function): 33 lines — standalone function with business logic
- **Line 145** `search_tags_api` (business_logic_function): 46 lines — standalone function with business logic
- **Line 196** `merge_tags_api` (business_logic_function): 70 lines — standalone function with business logic

### `apps/accounts/snippets/base.py`
- **Line 34** `BaseSnippetViewSet` (business_logic_class): 8 methods — no package delegation detected
- **Line 50** `duplicate` (business_logic_function): 12 lines — standalone function with business logic
- **Line 67** `export_csv` (business_logic_function): 17 lines — standalone function with business logic

### `apps/accounts/snippets/manage/team.py`
- **Line 87** `status_display` (business_logic_function): 14 lines — standalone function with business logic

### `apps/accounts/snippets/newsletter/content.py`
- **Line 84** `send_test_email_action` (business_logic_function): 12 lines — standalone function with business logic
- **Line 101** `duplicate_newsletter_action` (business_logic_function): 13 lines — standalone function with business logic

### `apps/accounts/snippets/newsletter/template.py`
- **Line 56** `set_default_template` (business_logic_function): 16 lines — standalone function with business logic

### `apps/accounts/snippets/tags.py`
- **Line 96** `display_tag` (business_logic_function): 12 lines — standalone function with business logic
- **Line 141** `usage_count_display` (business_logic_function): 13 lines — standalone function with business logic
- **Line 175** `get_extra_actions` (business_logic_function): 25 lines — standalone function with business logic
- **Line 284** `display_category` (business_logic_function): 12 lines — standalone function with business logic
- **Line 417** `display_tag` (business_logic_function): 12 lines — standalone function with business logic
- **Line 462** `usage_count_display` (business_logic_function): 13 lines — standalone function with business logic
- **Line 558** `display_category` (business_logic_function): 12 lines — standalone function with business logic

### `apps/accounts/startup.py`
- **Line 48** `_check_secret_key` (business_logic_function): 27 lines — standalone function with business logic
- **Line 78** `_check_duplicate_settings` (business_logic_function): 50 lines — standalone function with business logic
- **Line 131** `_check_url_routing` (business_logic_function): 13 lines — standalone function with business logic
- **Line 147** `_check_middleware_compatibility` (business_logic_function): 40 lines — standalone function with business logic
- **Line 190** `run_startup_checks` (business_logic_function): 30 lines — standalone function with business logic

### `apps/blog/api.py`
- **Line 13** `search_tags` (business_logic_function): 11 lines — standalone function with business logic
- **Line 28** `tag_autocomplete` (business_logic_function): 18 lines — standalone function with business logic
- **Line 50** `tag_cloud` (business_logic_function): 16 lines — standalone function with business logic
- **Line 70** `related_tags` (business_logic_function): 23 lines — standalone function with business logic

### `apps/blog/feeds.py`
- **Line 11** `LatestBlogPostsFeed` (business_logic_class): 5 methods — no package delegation detected
- **Line 41** `BlogTagFeed` (business_logic_class): 9 methods — no package delegation detected
- **Line 74** `BlogCategoryFeed` (business_logic_class): 9 methods — no package delegation detected

### `apps/blog/forms.py`
- **Line 61** `filter_queryset` (business_logic_function): 16 lines — standalone function with business logic
- **Line 180** `clean` (business_logic_function): 16 lines — standalone function with business logic

### `apps/blog/management/commands/manage_tags.py`
- **Line 16** `add_arguments` (business_logic_function): 11 lines — standalone function with business logic
- **Line 29** `handle` (business_logic_function): 12 lines — standalone function with business logic
- **Line 50** `create_tag` (business_logic_function): 12 lines — standalone function with business logic
- **Line 76** `merge_tags` (business_logic_function): 11 lines — standalone function with business logic

### `apps/blog/models/pages.py`
- **Line 95** `get_posts` (business_logic_function): 15 lines — standalone function with business logic
- **Line 137** `get_context` (business_logic_function): 40 lines — standalone function with business logic
- **Line 183** `tag_archive` (business_logic_function): 30 lines — standalone function with business logic
- **Line 216** `category_archive` (business_logic_function): 27 lines — standalone function with business logic
- **Line 246** `search_view` (business_logic_function): 25 lines — standalone function with business logic

### `apps/blog/models/post.py`
- **Line 15** `BlogPost` (business_logic_class): 7 methods — no package delegation detected
- **Line 149** `get_related_posts` (business_logic_function): 24 lines — standalone function with business logic

### `apps/blog/views/comments.py`
- **Line 21** `post` (business_logic_function): 33 lines — standalone function with business logic

### `apps/blog/views/likes.py`
- **Line 20** `post` (business_logic_function): 17 lines — standalone function with business logic

### `apps/blog/views/post.py`
- **Line 43** `get_queryset` (business_logic_function): 21 lines — standalone function with business logic
- **Line 66** `get_context_data` (business_logic_function): 36 lines — standalone function with business logic
- **Line 122** `get_context_data` (business_logic_function): 17 lines — standalone function with business logic
- **Line 163** `get_queryset` (business_logic_function): 12 lines — standalone function with business logic

### `apps/content/models/contact.py`
- **Line 167** `get_name` (business_logic_function): 14 lines — standalone function with business logic
- **Line 205** `export_as_dict` (business_logic_function): 20 lines — standalone function with business logic
- **Line 227** `export_as_csv_row` (business_logic_function): 15 lines — standalone function with business logic

### `apps/content/models/pages/base.py`
- **Line 77** `serve` (business_logic_function): 28 lines — standalone function with business logic
- **Line 108** `get_context` (business_logic_function): 56 lines — standalone function with business logic
- **Line 167** `get_listed_data` (business_logic_function): 21 lines — standalone function with business logic
- **Line 311** `serve` (business_logic_function): 41 lines — standalone function with business logic
- **Line 354** `send_submission_email` (business_logic_function): 52 lines — standalone function with business logic
- **Line 546** `get_context` (business_logic_function): 29 lines — standalone function with business logic

### `apps/content/search/views.py`
- **Line 13** `search` (business_logic_function): 32 lines — standalone function with business logic

### `apps/content/signals/default.py`
- **Line 10** `create_default_groups` (business_logic_function): 77 lines — standalone function with business logic
- **Line 92** `assign_default_permissions` (business_logic_function): 35 lines — standalone function with business logic

### `apps/content/signals/profile.py`
- **Line 13** `sync_profile_to_user` (business_logic_function): 26 lines — standalone function with business logic

### `apps/content/signals/user.py`
- **Line 28** `create_user_related_records` (business_logic_function): 84 lines — standalone function with business logic

### `apps/lms/managers/course.py`
- **Line 21** `CourseManager` (business_logic_class): 7 methods — consider extracting to package
- **Line 35** `get_user_enrolled_courses` (business_logic_function): 80 lines — standalone function with business logic
- **Line 118** `_get_user_interests` (business_logic_function): 44 lines — standalone function with business logic
- **Line 165** `get_user_learning_path` (business_logic_function): 58 lines — standalone function with business logic
- **Line 226** `_assess_user_skills` (business_logic_function): 56 lines — standalone function with business logic
- **Line 289** `get_user_course_completion_analytics` (business_logic_function): 94 lines — standalone function with business logic
- **Line 390** `_apply_filters` (business_logic_function): 63 lines — standalone function with business logic

### `apps/lms/managers/enrollments.py`
- **Line 17** `get_user_enrollments` (business_logic_function): 26 lines — standalone function with business logic
- **Line 45** `get_enrollment_analytics` (business_logic_function): 46 lines — standalone function with business logic
- **Line 93** `get_course_enrollments` (business_logic_function): 22 lines — standalone function with business logic
- **Line 117** `get_learning_path` (business_logic_function): 60 lines — standalone function with business logic
- **Line 179** `bulk_update_progress` (business_logic_function): 20 lines — standalone function with business logic
- **Line 201** `cleanup_inactive_enrollments` (business_logic_function): 26 lines — standalone function with business logic

### `apps/lms/managers/module.py`
- **Line 18** `get_module_completion_stats` (business_logic_function): 54 lines — standalone function with business logic
- **Line 74** `reorder_modules` (business_logic_function): 36 lines — standalone function with business logic

### `apps/lms/managers/progress.py`
- **Line 34** `update_lesson_progress` (business_logic_function): 74 lines — standalone function with business logic
- **Line 110** `update_module_progress` (business_logic_function): 63 lines — standalone function with business logic
- **Line 175** `_get_enrollment_for_course` (business_logic_function): 11 lines — standalone function with business logic
- **Line 188** `_update_or_create_lesson_progress` (business_logic_function): 59 lines — standalone function with business logic
- **Line 249** `_update_or_create_module_progress` (business_logic_function): 21 lines — standalone function with business logic
- **Line 272** `_update_module_progress_from_lesson` (business_logic_function): 25 lines — standalone function with business logic
- **Line 299** `_mark_lessons_completed` (business_logic_function): 25 lines — standalone function with business logic
- **Line 326** `_update_course_progress_from_lesson` (business_logic_function): 27 lines — standalone function with business logic
- **Line 355** `_update_course_progress_from_module` (business_logic_function): 33 lines — standalone function with business logic
- **Line 400** `_check_course_completion` (business_logic_function): 14 lines — standalone function with business logic
- **Line 416** `_get_next_lesson` (business_logic_function): 52 lines — standalone function with business logic
- **Line 482** `get_progress_overview` (business_logic_function): 58 lines — standalone function with business logic
- **Line 542** `_get_recent_progress_activity` (business_logic_function): 23 lines — standalone function with business logic
- **Line 567** `bulk_update_progress` (business_logic_function): 87 lines — standalone function with business logic

### `apps/lms/models/certificate.py`
- **Line 11** `Certificate` (business_logic_class): 4 methods — no package delegation detected

### `apps/lms/models/classes.py`
- **Line 312** `next_occurrence` (business_logic_function): 18 lines — standalone function with business logic
- **Line 349** `clean` (business_logic_function): 18 lines — standalone function with business logic
- **Line 369** `generate_occurrences` (business_logic_function): 15 lines — standalone function with business logic
- **Line 408** `get_ongoing_sessions` (business_logic_function): 12 lines — standalone function with business logic
- **Line 759** `clean` (business_logic_function): 17 lines — standalone function with business logic
- **Line 778** `save` (business_logic_function): 14 lines — standalone function with business logic

### `apps/lms/models/courses/index.py`
- **Line 107** `get_published_courses` (business_logic_function): 17 lines — standalone function with business logic
- **Line 127** `get_listed_items` (business_logic_function): 33 lines — standalone function with business logic
- **Line 181** `get_context` (business_logic_function): 57 lines — standalone function with business logic

### `apps/lms/models/courses/info.py`
- **Line 439** `_compute_final_price` (business_logic_function): 17 lines — standalone function with business logic
- **Line 458** `save` (business_logic_function): 25 lines — standalone function with business logic
- **Line 495** `get_course_details` (business_logic_function): 28 lines — standalone function with business logic
- **Line 546** `get_cached_search_results` (business_logic_function): 18 lines — standalone function with business logic

### `apps/lms/models/courses/progress.py`
- **Line 73** `update_progress` (business_logic_function): 14 lines — standalone function with business logic
- **Line 89** `get_lesson_progress_stats` (business_logic_function): 18 lines — standalone function with business logic
- **Line 166** `complete` (business_logic_function): 39 lines — standalone function with business logic
- **Line 207** `update_progress` (business_logic_function): 12 lines — standalone function with business logic

### `apps/lms/models/courses/specification.py`
- **Line 21** `Lesson` (business_logic_class): 7 methods — no package delegation detected
- **Line 190** `save` (business_logic_function): 12 lines — standalone function with business logic

### `apps/lms/models/quiz.py`
- **Line 295** `complete` (business_logic_function): 17 lines — standalone function with business logic
- **Line 371** `evaluate` (business_logic_function): 29 lines — standalone function with business logic

### `apps/lms/models/wishlist.py`
- **Line 10** `Wishlist` (business_logic_class): 5 methods — no package delegation detected

### `apps/lms/services/certificates.py`
- **Line 14** `CertificateService` (business_logic_class): 6 methods — no package delegation detected
- **Line 20** `create_certificate` (business_logic_function): 37 lines — standalone function with business logic
- **Line 60** `_get_user_display_name` (business_logic_function): 11 lines — standalone function with business logic
- **Line 74** `generate_pdf` (business_logic_function): 39 lines — standalone function with business logic
- **Line 116** `_draw_certificate_content` (business_logic_function): 48 lines — standalone function with business logic
- **Line 167** `verify_certificate` (business_logic_function): 25 lines — standalone function with business logic

### `apps/lms/services/courses.py`
- **Line 25** `CourseService` (business_logic_class): 13 methods — consider extracting to package
- **Line 39** `execute` (business_logic_function): 17 lines — standalone function with business logic
- **Line 58** `enroll_user` (business_logic_function): 66 lines — standalone function with business logic
- **Line 126** `update_course_progress` (business_logic_function): 48 lines — standalone function with business logic
- **Line 176** `get_user_course_dashboard` (business_logic_function): 77 lines — standalone function with business logic
- **Line 255** `generate_course_completion_report` (business_logic_function): 113 lines — standalone function with business logic
- **Line 378** `_apply_filters` (business_logic_function): 26 lines — standalone function with business logic
- **Line 406** `get_user_recommended_courses` (business_logic_function): 66 lines — standalone function with business logic
- **Line 474** `get_published_courses_cached` (business_logic_function): 73 lines — standalone function with business logic
- **Line 549** `get_course_by_slug_cached` (business_logic_function): 77 lines — standalone function with business logic
- **Line 629** `_get_user_interests` (business_logic_function): 19 lines — standalone function with business logic
- **Line 650** `_get_path_courses` (business_logic_function): 72 lines — standalone function with business logic

### `apps/lms/services/enrollments.py`
- **Line 55** `get_user_learning_dashboard` (business_logic_function): 62 lines — standalone function with business logic
- **Line 120** `_get_learning_analytics` (business_logic_function): 67 lines — standalone function with business logic
- **Line 190** `_get_active_courses_with_progress` (business_logic_function): 46 lines — standalone function with business logic
- **Line 239** `_get_next_lesson_for_enrollment` (business_logic_function): 39 lines — standalone function with business logic
- **Line 281** `_estimate_completion_date` (business_logic_function): 18 lines — standalone function with business logic
- **Line 302** `_is_behind_schedule` (business_logic_function): 15 lines — standalone function with business logic
- **Line 320** `_calculate_course_priority` (business_logic_function): 34 lines — standalone function with business logic
- **Line 357** `_get_completion_timeline` (business_logic_function): 22 lines — standalone function with business logic
- **Line 382** `_get_learning_habits` (business_logic_function): 41 lines — standalone function with business logic
- **Line 426** `_get_course_recommendations` (business_logic_function): 44 lines — standalone function with business logic
- **Line 473** `_calculate_relevance_score` (business_logic_function): 28 lines — standalone function with business logic
- **Line 508** `update_course_progress` (business_logic_function): 106 lines — standalone function with business logic
- **Line 617** `_update_module_progress` (business_logic_function): 24 lines — standalone function with business logic
- **Line 644** `_update_course_overall_progress` (business_logic_function): 16 lines — standalone function with business logic
- **Line 676** `enroll_user_in_multiple_courses` (business_logic_function): 84 lines — standalone function with business logic
- **Line 763** `sync_enrollment_progress_from_external` (business_logic_function): 75 lines — standalone function with business logic
- **Line 845** `get_enrollment_certificate_info` (business_logic_function): 66 lines — standalone function with business logic
- **Line 914** `validate_enrollment_for_access` (business_logic_function): 81 lines — standalone function with business logic
- **Line 998** `_check_lesson_availability` (business_logic_function): 22 lines — standalone function with business logic
- **Line 1023** `_invalidate_enrollment_caches` (business_logic_function): 15 lines — standalone function with business logic

### `apps/lms/services/legacy.py`
- **Line 53** `get_user_learning_dashboard` (business_logic_function): 62 lines — standalone function with business logic
- **Line 118** `_get_learning_analytics` (business_logic_function): 68 lines — standalone function with business logic
- **Line 189** `_get_active_courses_with_progress` (business_logic_function): 46 lines — standalone function with business logic
- **Line 238** `_get_next_lesson_for_enrollment` (business_logic_function): 33 lines — standalone function with business logic
- **Line 274** `_estimate_completion_date` (business_logic_function): 18 lines — standalone function with business logic
- **Line 295** `_is_behind_schedule` (business_logic_function): 15 lines — standalone function with business logic
- **Line 313** `_calculate_course_priority` (business_logic_function): 34 lines — standalone function with business logic
- **Line 350** `_get_completion_timeline` (business_logic_function): 26 lines — standalone function with business logic
- **Line 379** `_get_learning_habits` (business_logic_function): 44 lines — standalone function with business logic
- **Line 426** `_get_course_recommendations` (business_logic_function): 44 lines — standalone function with business logic
- **Line 473** `_calculate_relevance_score` (business_logic_function): 29 lines — standalone function with business logic
- **Line 509** `update_course_progress` (business_logic_function): 108 lines — standalone function with business logic
- **Line 620** `_update_module_progress` (business_logic_function): 26 lines — standalone function with business logic
- **Line 649** `_update_course_overall_progress` (business_logic_function): 17 lines — standalone function with business logic
- **Line 682** `enroll_user_in_multiple_courses` (business_logic_function): 87 lines — standalone function with business logic
- **Line 772** `sync_enrollment_progress_from_external` (business_logic_function): 81 lines — standalone function with business logic
- **Line 860** `get_enrollment_certificate_info` (business_logic_function): 68 lines — standalone function with business logic
- **Line 931** `validate_enrollment_for_access` (business_logic_function): 82 lines — standalone function with business logic
- **Line 1016** `_check_lesson_availability` (business_logic_function): 23 lines — standalone function with business logic
- **Line 1042** `_invalidate_enrollment_caches` (business_logic_function): 15 lines — standalone function with business logic

### `apps/lms/services/lessons.py`
- **Line 27** `get_course_modules` (business_logic_function): 21 lines — standalone function with business logic
- **Line 68** `get_course_lessons` (business_logic_function): 35 lines — standalone function with business logic
- **Line 106** `get_module_lessons` (business_logic_function): 26 lines — standalone function with business logic
- **Line 135** `get_lesson_with_context` (business_logic_function): 44 lines — standalone function with business logic
- **Line 182** `_check_lesson_access` (business_logic_function): 23 lines — standalone function with business logic
- **Line 208** `mark_lesson_as_completed` (business_logic_function): 57 lines — standalone function with business logic
- **Line 268** `_check_course_completion` (business_logic_function): 22 lines — standalone function with business logic
- **Line 293** `get_lesson_progress` (business_logic_function): 31 lines — standalone function with business logic
- **Line 327** `update_lesson` (business_logic_function): 91 lines — standalone function with business logic
- **Line 421** `_invalidate_lesson_caches` (business_logic_function): 11 lines — standalone function with business logic

### `apps/lms/services/notes.py`
- **Line 11** `NoteService` (business_logic_class): 6 methods — no package delegation detected
- **Line 17** `create_note` (business_logic_function): 64 lines — standalone function with business logic
- **Line 84** `update_note` (business_logic_function): 42 lines — standalone function with business logic
- **Line 129** `share_note` (business_logic_function): 62 lines — standalone function with business logic
- **Line 194** `search_notes` (business_logic_function): 45 lines — standalone function with business logic
- **Line 242** `get_note_analytics` (business_logic_function): 69 lines — standalone function with business logic
- **Line 314** `_calculate_note_trends` (business_logic_function): 26 lines — standalone function with business logic

### `apps/lms/signals.py`
- **Line 25** `create_lms_profiles` (business_logic_function): 29 lines — standalone function with business logic

### `apps/lms/snippets/specialization.py`
- **Line 69** `update_courses_count_action` (business_logic_function): 18 lines — standalone function with business logic

### `apps/lms/views/cart.py`
- **Line 49** `get_context_data` (business_logic_function): 14 lines — standalone function with business logic
- **Line 65** `post` (business_logic_function): 85 lines — standalone function with business logic
- **Line 163** `clear_enrollment_cache` (business_logic_function): 13 lines — standalone function with business logic
- **Line 188** `get_context_data` (business_logic_function): 11 lines — standalone function with business logic
- **Line 307** `get_context_data` (business_logic_function): 19 lines — standalone function with business logic

### `apps/lms/views/courses.py`
- **Line 37** `dispatch` (business_logic_function): 12 lines — standalone function with business logic
- **Line 51** `get_course_context` (business_logic_function): 32 lines — standalone function with business logic
- **Line 85** `get_context_data` (business_logic_function): 39 lines — standalone function with business logic
- **Line 126** `get` (business_logic_function): 30 lines — standalone function with business logic
- **Line 166** `get_context_data` (business_logic_function): 21 lines — standalone function with business logic
- **Line 189** `get_course_header_fragment` (business_logic_function): 17 lines — standalone function with business logic
- **Line 212** `get_sidebar_fragment` (business_logic_function): 17 lines — standalone function with business logic
- **Line 254** `get_queryset` (business_logic_function): 16 lines — standalone function with business logic
- **Line 272** `_build_filters` (business_logic_function): 36 lines — standalone function with business logic
- **Line 310** `get_context_data` (business_logic_function): 33 lines — standalone function with business logic
- **Line 345** `_get_filter_options` (business_logic_function): 86 lines — standalone function with business logic
- **Line 433** `render_to_response` (business_logic_function): 11 lines — standalone function with business logic
- **Line 458** `get` (business_logic_function): 50 lines — standalone function with business logic
- **Line 510** `_build_filters` (business_logic_function): 20 lines — standalone function with business logic

### `apps/lms/views/lessons.py`
- **Line 21** `get` (business_logic_function): 39 lines — standalone function with business logic
- **Line 63** `get_user_progress` (business_logic_function): 21 lines — standalone function with business logic
- **Line 86** `get_completed_lessons` (business_logic_function): 13 lines — standalone function with business logic
- **Line 108** `post` (business_logic_function): 15 lines — standalone function with business logic
- **Line 125** `mark_lesson_complete` (business_logic_function): 14 lines — standalone function with business logic
- **Line 156** `get` (business_logic_function): 22 lines — standalone function with business logic
- **Line 180** `get_last_watched_lesson` (business_logic_function): 28 lines — standalone function with business logic

### `apps/pages/models/contact.py`
- **Line 167** `get_name` (business_logic_function): 14 lines — standalone function with business logic
- **Line 205** `export_as_dict` (business_logic_function): 20 lines — standalone function with business logic
- **Line 227** `export_as_csv_row` (business_logic_function): 15 lines — standalone function with business logic

### `apps/pages/models/pages/base.py`
- **Line 77** `serve` (business_logic_function): 28 lines — standalone function with business logic
- **Line 108** `get_context` (business_logic_function): 56 lines — standalone function with business logic
- **Line 167** `get_listed_data` (business_logic_function): 21 lines — standalone function with business logic
- **Line 311** `serve` (business_logic_function): 41 lines — standalone function with business logic
- **Line 354** `send_submission_email` (business_logic_function): 52 lines — standalone function with business logic
- **Line 546** `get_context` (business_logic_function): 29 lines — standalone function with business logic

### `apps/pages/search/views.py`
- **Line 13** `search` (business_logic_function): 32 lines — standalone function with business logic

### `apps/pages/signals/default.py`
- **Line 10** `create_default_groups` (business_logic_function): 77 lines — standalone function with business logic
- **Line 92** `assign_default_permissions` (business_logic_function): 35 lines — standalone function with business logic

### `apps/pages/signals/profile.py`
- **Line 13** `sync_profile_to_user` (business_logic_function): 26 lines — standalone function with business logic

### `apps/pages/signals/user.py`
- **Line 28** `create_user_related_records` (business_logic_function): 84 lines — standalone function with business logic

