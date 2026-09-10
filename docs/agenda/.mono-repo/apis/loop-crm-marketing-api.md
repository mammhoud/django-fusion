---
Object type: API
Tags: api, rest-api, marketing, email, oauth
Status: Active
Related Features: marketing-publishing, email-sync
Related Integrations: social-publishing, email-oauth-sync
Related Products: loop-crm
---

# Loop-CRM Marketing & Email APIs — `/apis/marketing/`, OAuth

> **Description:** Social channel connect + publishing surface and the email OAuth sync road.

## Endpoints

| Road | Purpose |
|---|---|
| `/apis/marketing/` | Social channels, campaigns, posts, analytics |
| `apps/marketing/oauth_urls.py` | OAuth channel-connect flow |
| `apps/core/email_oauth_urls.py` | Mailbox OAuth consent + token storage |
| `apps/core/email_sync.py` | Periodic message sync into `EmailAccount`/`EmailMessage` |

## Contract notes

- Channel connect requires OAuth consent per platform; refresh tokens stored per workspace
- Publishing targets real platform publishers for all 12 catalog platforms
- Email sync runs per connected mailbox; consent + revocation per tenant

## Related

- → `loop-crm-core-api.md` — Core road
- → `../integrations/social-publishing.md` — Social connector
- → `../integrations/email-oauth-sync.md` — Email connector
- → `../objects/api.md` — API object type