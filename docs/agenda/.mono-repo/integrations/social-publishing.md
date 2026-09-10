---
Object type: Integration
Tags: integration, social, publishing, marketing
Status: Active
Category: Social
Provider: Social platforms (12 catalog platforms)
Related Products: loop-crm
Related Features: marketing-publishing
Related Plans: marketing-strategy
Related APIs: marketing-apis
---

# Social Publishing — Multi-Platform Posting

> **Description:** Publish posts across the 12 social catalog platforms from Loop-CRM (`apps/marketing`) with real publishers, OAuth channel connect, scheduling, and analytics.

## Method

- SocialChannel (workspace-scoped) + Campaign + Post + Media + PostAnalytics models
- Channel connect via OAuth (see `apps/marketing/oauth.py` + `oauth_urls.py`)
- Real publishers for all catalog platforms (shipped with the finance integration milestone)

## Use case

Marketing team connects channels, schedules campaign posts, and reads PostAnalytics back in the Loop-CRM workspace.

## Auth type

- OAuth 2.0 per platform + refresh token handling

## Evidence

- Channel connect forms + OAuth tests green (`test_oauth.py`, `test_channel_connect.py`)
- Research: Twenty/Postiz DNA comparison ✅ (merged-product validation)

## Related

- → `stripe-billing.md` — Billing surface
- → `../apis/loop-crm-marketing-api.md` — Marketing API road
- → `../objects/integration.md` — Integration object type