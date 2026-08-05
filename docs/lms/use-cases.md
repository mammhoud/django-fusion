# LMS — Use Cases

> Real-world scenarios for deploying and customizing the LMS platform.

---

## 1. Online Course Platform (`e-learning`)

- **Purpose:** Sell and deliver online courses with video lessons, quizzes, and certificates
- **Key features:** Course management, student progress tracking, certificate generation, enrollment workflow
- **Configuration:** Enable `plugins.lms`, set up Stripe/PayPal, configure `LMS_CERTIFICATE_TEMPLATE`
- **Customization:** Add custom course page templates, quiz components, progress widgets

---

## 2. Corporate Training Portal (`corporate-training`)

- **Purpose:** Internal employee training with mandatory courses and compliance tracking
- **Key features:** Learning paths with prerequisites, completion tracking, reporting dashboard
- **Configuration:** Set `LMS_ENROLLMENT_CONFIRMATION=true`, configure learning path rules
- **Customization:** Add role-based course assignments, compliance report exports

---

## 3. Certification Authority (`certifications`)

- **Purpose:** Issue professional certifications with verification codes
- **Key features:** Certificate generation, verification API, PDF export with branding
- **Configuration:** Customize `LMS_CERTIFICATE_TEMPLATE`, set up verification endpoint
- **Customization:** Add QR codes, certificate verification page, branded PDF templates

---

## 4. Membership Site (`membership`)

- **Purpose:** Gated content with subscription tiers
- **Key features:** Payment integration, membership levels, gated course access
- **Configuration:** Set up Stripe subscriptions, configure `PRODUCT_CURRENCY`
- **Customization:** Add membership tiers plugin, gated content middleware

---

## 5. Academic Institution LMS (`academic`)

- **Purpose:** University or school course management system
- **Key features:** Semester-based courses, grade books, instructor dashboards
- **Configuration:** Add semester/term models, grade tracking, instructor roles
- **Customization:** Create academic calendar, grade book views, student transcripts

---

## 6. Community Learning Hub (`community`)

- **Purpose:** Free community-driven learning with discussion forums
- **Key features:** User profiles, discussion boards, peer reviews, badges
- **Configuration:** Disable payment integration, enable social auth
- **Customization:** Add forum plugin, peer review system, gamification badges

---

## Related

| Resource | Path |
|----------|------|
| LMS site docs | [`README.md`](README.md) |
| LMS configuration | [`configuration.md`](configuration.md) |
| Clone guide | [`clone-guide.md`](clone-guide.md) |
