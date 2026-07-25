# Integrations — Third-Party Connectors

> **Type:** Integration 🔗
> **Description:** Third-party service integrations — payment gateways, email/SMS providers, CRM connectors, auth providers, cloud storage, and analytics services.

---

## Integration Categories

| Category | Providers | Status |
|----------|-----------|--------|
| **Payment** | Stripe, Square, PayPal | 📋 Planned |
| **Email** | SendGrid, Mailgun, SES | 📋 Planned |
| **SMS** | Twilio, Vonage | 📋 Planned |
| **CRM** | HubSpot, Salesforce | 📋 Planned |
| **Auth** | Google, GitHub, Okta | ✅ Complete |
| **Storage** | S3, Cloudflare R2, local FS | 🚧 In Progress |
| **Analytics** | Plausible, PostHog, Sentry | 📋 Planned |
| **Maps** | Google Maps, Mapbox | 📋 Planned |

---

## Integration Pattern

```
Application → Integration Adapter → External Service
                  ↓
            API Key / OAuth Token
                  ↓
          Response ↔ Request Mapping
```

---

## Related

- → `../objects/integration.md` — Integration object type
- → `../api/_index.md` — Related API endpoints
- → `../features/external-integration.md` — Integration features
- → `../pipelines/_index.md` — Deployment pipelines
- → `../README.md` — Master index
