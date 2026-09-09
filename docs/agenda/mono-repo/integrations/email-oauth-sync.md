---
Object type: Integration
Tags: integration, email-service, oauth, sync
Status: Active
Category: Email
Provider: IMAP/SMTP providers via OAuth
Related Products: loop-crm
Related Features: email-sync
Related Plans: product-development
Related APIs: email-apis
---

# Email OAuth Sync — Mailbox Connection & Sync

> **Description:** Connect a mailbox via OAuth (`apps/core/email_oauth.py` + `email_oauth_urls.py`) and sync messages into `EmailAccount`/`EmailMessage` models.

## Method

- OAuth consent flow (Google/Microsoft-style) → refresh token stored per workspace
- Periodic sync imports messages into `EmailMessage`
- Consent + token revocation handled per tenant

## Use case

Salesperson connects their inbox; emails appear in the Loop-CRM workspace linked to contacts/deals.

## Auth type

- OAuth 2.0 (authorization code + refresh)

## Evidence

- `email_oauth_urls.py` + `email_sync.py` present; tests green

## Related

- → `../apis/loop-crm-marketing-api.md` — Marketing + email API road
- → `../objects/integration.md` — Integration object type