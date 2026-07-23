"""Static public page content API for the LMS Next.js frontend.

The response shape intentionally mirrors Wagtail page concepts: top-level SEO
metadata plus ordered content blocks that can represent headings, rich text,
CTAs, media, FAQ groups, stats, and contact methods. When matching Wagtail page
models are introduced, this module can swap `STATIC_PAGES` for model-backed
serializers without changing the frontend contract.
"""

from www.api.data_adapter import bolt_view


def cta(label, href, variant="primary"):
    return {"label": label, "href": href, "variant": variant}


STATIC_PAGES = {
    "home": {
        "slug": "home",
        "title": "Learn Without Limits",
        "seo": {
            "title": "LMS Platform | Learn Without Limits",
            "description": "Master new skills with expert-led courses, interactive content, and a community of learners.",
        },
        "blocks": [
            {
                "type": "hero",
                "heading": "Learn Without Limits",
                "intro": "Master new skills with expert-led courses, interactive content, and a community of learners.",
                "ctas": [
                    cta("Explore Courses", "/courses"),
                    cta("Get Started Free", "/registration", "secondary"),
                ],
            },
            {
                "type": "stats",
                "items": [
                    {"label": "Students", "value": "5K+"},
                    {"label": "Reviews", "value": "12K+"},
                ],
            },
            {
                "type": "section_header",
                "key": "featured_courses",
                "heading": "Featured Courses",
                "intro": "Most popular courses picked for you",
                "cta": cta("View All", "/courses", "link"),
            },
            {
                "type": "cta",
                "heading": "Start Learning Today",
                "intro": "Join thousands of students building skills for their next opportunity.",
                "ctas": [cta("Create Free Account", "/registration")],
            },
        ],
    },
    "about-us": {
        "slug": "about-us",
        "title": "About LMS Platform",
        "seo": {
            "title": "About LMS Platform",
            "description": "Empowering learners worldwide with quality education and expert-led courses.",
        },
        "blocks": [
            {
                "type": "hero",
                "heading": "About LMS Platform",
                "intro": "Empowering learners worldwide with quality education and expert-led courses.",
            },
            {
                "type": "stats",
                "items": [
                    {
                        "label": "Students",
                        "value": "5K+",
                        "description": "Active learners worldwide",
                    },
                    {
                        "label": "Countries",
                        "value": "50+",
                        "description": "Global reach",
                    },
                ],
            },
            {
                "type": "rich_section",
                "heading": "Our Mission",
                "html": "<p>We believe quality education should be accessible to everyone. Our platform connects passionate instructors with eager learners, creating a community where knowledge knows no boundaries.</p>",
                "items": [
                    {
                        "heading": "Quality Content",
                        "text": "Courses crafted by industry experts with real-world experience",
                    },
                    {
                        "heading": "Flexible Learning",
                        "text": "Learn at your own pace with lifetime access to all materials",
                    },
                    {
                        "heading": "Community Driven",
                        "text": "Join a global community of learners and instructors",
                    },
                ],
            },
            {
                "type": "cta",
                "heading": "Ready to Get Started?",
                "intro": "Join our community and start learning today.",
                "ctas": [cta("Create Free Account", "/registration")],
            },
        ],
    },
    "privacy": {
        "slug": "privacy",
        "title": "Privacy Policy",
        "seo": {
            "title": "Privacy Policy",
            "description": "How LMS Platform collects, uses, discloses, and safeguards user information.",
        },
        "last_updated": "January 1, 2026",
        "blocks": [
            {
                "type": "rich_section",
                "heading": "1. Introduction",
                "html": "<p>Welcome to LMS Platform. We respect your privacy and are committed to protecting your personal data. This privacy policy explains how we collect, use, disclose, and safeguard your information when you visit our platform.</p>",
            },
            {
                "type": "rich_section",
                "heading": "2. Information We Collect",
                "html": "<p>We may collect account, profile, learning, payment, and technical data needed to operate the platform.</p>",
            },
            {
                "type": "rich_section",
                "heading": "3. How We Use Your Information",
                "html": "<p>We use your information to provide courses, process enrollments, personalize learning, communicate updates, issue certificates, prevent fraud, and comply with legal obligations.</p>",
            },
            {
                "type": "rich_section",
                "heading": "4. Data Sharing and Disclosure",
                "html": "<p>We do not sell personal information. We may share data with service providers, instructors for enrolled courses, and legal authorities when required.</p>",
            },
            {
                "type": "rich_section",
                "heading": "5. Data Security",
                "html": "<p>We use technical and organizational measures including encryption in transit, secure data centers, and access controls.</p>",
            },
            {
                "type": "rich_section",
                "heading": "6. Your Rights",
                "html": "<p>You may request access, correction, erasure, portability, or object to marketing-related processing.</p>",
            },
            {
                "type": "rich_section",
                "heading": "7. Cookies",
                "html": "<p>We use cookies and similar technologies to improve browsing, analyze traffic, and understand user journeys.</p>",
            },
            {
                "type": "rich_section",
                "heading": "8. Third-Party Links",
                "html": "<p>Our platform may link to third-party websites with their own privacy practices.</p>",
            },
            {
                "type": "rich_section",
                "heading": "9. Changes to This Policy",
                "html": "<p>We may update this privacy policy and will post the updated date on this page.</p>",
            },
            {
                "type": "rich_section",
                "heading": "10. Contact Us",
                "html": "<p>If you have questions about this policy, contact privacy@lmsplatform.com.</p>",
            },
        ],
    },
    "faq": {
        "slug": "faq",
        "title": "Frequently Asked Questions",
        "seo": {
            "title": "Frequently Asked Questions",
            "description": "Answers to common questions about LMS Platform.",
        },
        "blocks": [
            {
                "type": "hero",
                "heading": "Frequently Asked Questions",
                "intro": "Find answers to common questions about our platform",
            },
            {
                "type": "faq_groups",
                "groups": [
                    {
                        "title": "Getting Started",
                        "items": [
                            {
                                "question": "How do I create an account?",
                                "answer": "Click the Sign Up button, fill in your details, choose your role, and verify your email address.",
                            },
                            {
                                "question": "Is there a free trial?",
                                "answer": "Yes. New students can start with a 7-day free trial and no credit card is required.",
                            },
                            {
                                "question": "How do I enroll in a course?",
                                "answer": "Browse the course catalog, select a course, and click Enroll Now.",
                            },
                            {
                                "question": "Can I access courses on mobile?",
                                "answer": "Yes. The platform is responsive across phones, tablets, and desktops.",
                            },
                        ],
                    },
                    {
                        "title": "Account & Billing",
                        "items": [
                            {
                                "question": "What payment methods do you accept?",
                                "answer": "We accept major credit cards, PayPal, and selected local payment methods.",
                            },
                            {
                                "question": "Can I get a refund?",
                                "answer": "We offer a 30-day money-back guarantee for eligible course purchases.",
                            },
                        ],
                    },
                    {
                        "title": "Learning Experience",
                        "items": [
                            {
                                "question": "How are courses structured?",
                                "answer": "Courses are organized into modules and lessons with videos, readings, exercises, quizzes, and projects.",
                            },
                            {
                                "question": "Do I get a certificate?",
                                "answer": "Yes. Completed courses include a verifiable certificate.",
                            },
                        ],
                    },
                    {
                        "title": "For Instructors",
                        "items": [
                            {
                                "question": "How do I become an instructor?",
                                "answer": "Register as an instructor, complete your profile, and submit your course for review.",
                            }
                        ],
                    },
                    {
                        "title": "Technical Support",
                        "items": [
                            {
                                "question": "What browsers are supported?",
                                "answer": "Current versions of Chrome, Firefox, Safari, and Edge are supported.",
                            },
                            {
                                "question": "How do I reset my password?",
                                "answer": "Use Forgot Password on the login page and follow the emailed reset link.",
                            },
                        ],
                    },
                ],
            },
            {
                "type": "cta",
                "heading": "Still have questions?",
                "intro": "Can't find the answer you're looking for? We're here to help.",
                "ctas": [cta("Contact Support", "/contact")],
            },
        ],
    },
    "contact": {
        "slug": "contact",
        "title": "Contact Us",
        "seo": {
            "title": "Contact Us",
            "description": "Contact LMS Platform support and sales.",
        },
        "blocks": [
            {
                "type": "hero",
                "heading": "Contact Us",
                "intro": "We'd love to hear from you",
            },
            {
                "type": "contact_methods",
                "items": [
                    {
                        "type": "email",
                        "label": "Email",
                        "value": "support@lmsplatform.com",
                        "href": "mailto:support@lmsplatform.com",
                    },
                    {
                        "type": "phone",
                        "label": "Phone",
                        "value": "+1 (555) 123-4567",
                        "href": "tel:+15551234567",
                    },
                    {
                        "type": "address",
                        "label": "Address",
                        "value": "123 Learning St, Education City, EC 10001",
                    },
                    {
                        "type": "hours",
                        "label": "Hours",
                        "value": "Mon-Fri 9:00 AM - 6:00 PM EST",
                    },
                ],
            },
            {"type": "form", "heading": "Send us a message"},
        ],
    },
}


@bolt_view
def page_detail(request, slug):
    """GET /apis/pages/<slug>/ — return public page content."""
    normalized = "home" if slug in ("", "home", "index") else slug.strip("/")
    page = STATIC_PAGES.get(normalized)
    if page is None:
        return {"status": "error", "message": "Page not found"}, 404
    return page
