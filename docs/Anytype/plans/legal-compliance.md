---
# yaml-language-server: $schema=../schemas/page.schema.json
Object type: Plan
Tags: legal, compliance, privacy, gdpr
Status: Published
Type: Annual
Related Plans: operational-plan, risk-management
Related Goals: business-goal
---

# Legal & Regulatory Compliance

> **Type:** Plan 📋
> **Emoji:** ⚖️
> **Description:** Compliance framework ensuring Structa Cloud and all its sites meet legal, regulatory, and industry standards.

---

## 1. Compliance Areas

| Area | Requirements | Status | Owner |
|------|-------------|--------|-------|
| **Business Registration** | Company registration, tax ID, business license | ✅ Complete | Legal |
| **Data Privacy (GDPR)** | User consent, data access, right to deletion | ✅ Complete | Legal |
| **Intellectual Property** | Open source license (MIT), trademarks | ✅ Complete | Legal |
| **Terms of Service** | User agreement, acceptable use, liability | ✅ Complete | Legal |
| **Privacy Policy** | Data collection, cookies, sharing | ✅ Complete | Legal |
| **Accessibility (WCAG 2.1)** | AA compliance for public pages | 🚧 In Progress | Design |

## 2. Data Privacy

| Requirement | Implementation | Verification |
|-------------|----------------|--------------|
| **User consent** | Cookie consent banner, privacy notice | User flow test |
| **Data access** | User data export feature | Manual test |
| **Right to deletion** | Account deletion with data purge | Automated test |
| **Data breach notification** | Incident response plan | Annual review |
| **Data processing records** | Processing activity register | Quarterly review |

## 3. Intellectual Property

| Asset | Type | Protection |
|-------|------|------------|
| **Structa Cloud Platform** | Source code | MIT license |
| **django-fusion** | Source code | MIT license |
| **ceptor-ai** | Source code | MIT license |
| **Documentation** | Written content | CC BY-SA 4.0 |
| **Brand marks** | Logo, name | Trademark pending |

## 4. Security & Data Protection

| Measure | Implementation | Standard |
|---------|----------------|----------|
| **Encryption at rest** | PostgreSQL encryption | AES-256 |
| **Encryption in transit** | HTTPS, TLS 1.3 | All connections |
| **Access control** | Role-based permissions | Least privilege |
| **API authentication** | JWT tokens | Per-endpoint |
| **Dependency scanning** | Dependabot, uv audit | Weekly |

---

## 5. Compliance Schedule

| Review | Frequency | Responsible |
|--------|:---------:|-------------|
| Terms of Service | Annually | Legal team |
| Privacy Policy | Annually | Legal team |
| Accessibility audit | Bi-annually | Design team |
| Security audit | Annually | DevOps team |
| License compliance | Per release | CI pipeline |

---

## Related Docs

- → `risk-management.md` — Security risk assessment
- → `operational-plan.md` — Security operations
- → `../guides/auth.md` — Authentication & access
- → `../guides/deployment.md` — Deployment security
- → `../README.md` — Master index
