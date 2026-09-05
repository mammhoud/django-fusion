---
Object type: Data Pipeline
Tags: data-pipeline, email, oauth, sync
Status: Active
Type: Scheduled
Source: Connected mailboxes (IMAP via OAuth)
Destination: EmailAccount / EmailMessage models
Schedule: Periodic per mailbox
Related Reports: product-metrics
---

# Email OAuth Sync

> **Description:** Connected mailboxes are periodically synced into Loop-CRM message models for CRM-linked email context.

## Flow

1. User connects mailbox via OAuth consent (`email_oauth_urls.py`)
2. Refresh token stored per workspace
3. `email_sync.py` pulls new messages on schedule
4. Messages link to contacts/deals where matched

## Failure handling

- Token revocation → consent re-request
- Partial syncs are idempotent (message UID tracking)

## Related

- → `../integrations/email-oauth-sync.md` — Integration object
- → `../objects/data-pipeline.md` — Data Pipeline object type