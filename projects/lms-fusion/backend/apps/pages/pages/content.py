"""
Shared static page content definitions for CTC Research.

Moved from ``www.api.pages`` to a reusable plugin module so that both the
API views and the django-fusion fragment components can import the same
canonical page data without circular imports.
"""


def cta(label, href, variant="primary"):
    return {"label": label, "href": href, "variant": variant}


STATIC_PAGES = {
    "home": {
        "slug": "home",
        "title": "CTC Research — Advancing Clinical Trials",
        "seo": {
            "title": "CTC Research | Advancing Clinical Trials Through Innovation",
            "description": "Leading clinical trial research organization dedicated to advancing medical science through innovative research methodologies and patient-centered approaches.",
        },
        "blocks": [
            {
                "type": "hero",
                "heading": "Advancing Clinical Trials Through Innovation",
                "intro": "CTC Research is a premier clinical research organization dedicated to accelerating the development of new therapies through rigorous scientific methods and patient-centered approaches.",
                "ctas": [
                    cta("Explore Our Services", "/services"),
                    cta("Contact Us", "/contact", "secondary"),
                ],
            },
            {
                "type": "stats",
                "items": [
                    {"label": "Clinical Trials", "value": "200+"},
                    {"label": "Patients Enrolled", "value": "15K+"},
                    {"label": "Research Sites", "value": "50+"},
                    {"label": "Years Experience", "value": "25+"},
                ],
            },
            {
                "type": "section_header",
                "key": "featured_services",
                "heading": "Our Research Services",
                "intro": "Comprehensive clinical trial management from concept to completion",
                "cta": cta("View All Services", "/services", "link"),
            },
            {
                "type": "cta",
                "heading": "Partner With Us",
                "intro": "Join leading pharmaceutical companies and research institutions in advancing medical science.",
                "ctas": [cta("Get Started", "/contact")],
            },
        ],
    },
    "about": {
        "slug": "about",
        "title": "About CTC Research",
        "seo": {
            "title": "About CTC Research | Our Mission & Values",
            "description": "Learn about CTC Research's mission to advance clinical trials through innovation, integrity, and patient-centered research.",
        },
        "blocks": [
            {
                "type": "hero",
                "heading": "About CTC Research",
                "intro": "For over 25 years, CTC Research has been at the forefront of clinical trial innovation, helping bring life-changing therapies to patients worldwide.",
            },
            {
                "type": "stats",
                "items": [
                    {
                        "label": "Years",
                        "value": "25+",
                        "description": "Of research excellence",
                    },
                    {
                        "label": "Countries",
                        "value": "30+",
                        "description": "Global research footprint",
                    },
                    {
                        "label": "Therapies",
                        "value": "40+",
                        "description": "FDA-approved therapies supported",
                    },
                ],
            },
            {
                "type": "rich_section",
                "heading": "Our Mission",
                "html": "<p>CTC Research is dedicated to accelerating the development of safe and effective therapies. We partner with pharmaceutical companies, biotech firms, and academic institutions to design and execute clinical trials that meet the highest standards of scientific rigor and ethical conduct.</p>",
                "items": [
                    {
                        "heading": "Scientific Excellence",
                        "text": "Rigorous methodologies backed by experienced researchers and state-of-the-art facilities",
                    },
                    {
                        "heading": "Patient First",
                        "text": "Every trial is designed with patient safety, comfort, and accessibility as top priorities",
                    },
                    {
                        "heading": "Regulatory Compliance",
                        "text": "Full compliance with FDA, EMA, and ICH GCP guidelines across all research activities",
                    },
                ],
            },
            {
                "type": "cta",
                "heading": "Learn More About Our Team",
                "intro": "Meet the experts driving clinical research forward.",
                "ctas": [cta("Meet Our Team", "/team")],
            },
        ],
    },
    "team": {
        "slug": "team",
        "title": "Our Team",
        "seo": {
            "title": "CTC Research Team | Clinical Research Experts",
            "description": "Meet the experienced team of clinical researchers, scientists, and support staff at CTC Research.",
        },
        "blocks": [
            {
                "type": "hero",
                "heading": "Our Team",
                "intro": "Meet the dedicated professionals driving clinical research excellence at CTC Research.",
            },
            {
                "type": "rich_section",
                "heading": "Leadership & Expertise",
                "html": "<p>Our team comprises board-certified physicians, PhD-level scientists, experienced clinical research coordinators, and regulatory affairs specialists. With decades of combined experience, we bring deep expertise across therapeutic areas including oncology, cardiology, neurology, and rare diseases.</p>",
            },
            {
                "type": "cta",
                "heading": "Join Our Team",
                "intro": "Explore career opportunities at CTC Research.",
                "ctas": [cta("View Open Positions", "/contact")],
            },
        ],
    },
    "services": {
        "slug": "services",
        "title": "Our Services",
        "seo": {
            "title": "Clinical Trial Services | CTC Research",
            "description": "Comprehensive clinical trial management services including protocol design, site management, data management, and regulatory affairs.",
        },
        "blocks": [
            {
                "type": "hero",
                "heading": "Our Services",
                "intro": "End-to-end clinical trial management services designed to accelerate your research timeline.",
            },
            {
                "type": "rich_section",
                "heading": "What We Offer",
                "html": "<p>From initial protocol design through final study report, CTC Research provides comprehensive support across the entire clinical trial lifecycle. Our services are tailored to meet the unique requirements of each study while maintaining the highest standards of quality and compliance.</p>",
                "items": [
                    {
                        "heading": "Protocol Design",
                        "text": "Scientific and regulatory expertise to design robust, efficient protocols",
                    },
                    {
                        "heading": "Site Management",
                        "text": "End-to-end site selection, activation, monitoring, and close-out",
                    },
                    {
                        "heading": "Data Management",
                        "text": "Secure, compliant data collection, cleaning, and analysis",
                    },
                    {
                        "heading": "Regulatory Affairs",
                        "text": "Navigating FDA, EMA, and local regulatory submissions and approvals",
                    },
                ],
            },
            {
                "type": "cta",
                "heading": "Ready to Start Your Trial?",
                "intro": "Contact our team to discuss how we can support your next clinical study.",
                "ctas": [cta("Contact Us", "/contact")],
            },
        ],
    },
    "privacy": {
        "slug": "privacy",
        "title": "Privacy Policy",
        "seo": {
            "title": "Privacy Policy | CTC Research",
            "description": "How CTC Research collects, uses, discloses, and safeguards personal information.",
        },
        "last_updated": "January 1, 2026",
        "blocks": [
            {
                "type": "rich_section",
                "heading": "1. Introduction",
                "html": "<p>Welcome to CTC Research. We respect your privacy and are committed to protecting your personal data. This privacy policy explains how we collect, use, disclose, and safeguard your information when you visit our platform.</p>",
            },
            {
                "type": "rich_section",
                "heading": "2. Information We Collect",
                "html": "<p>We may collect personal identification information (name, email, phone), professional credentials, research data, and technical data needed to operate our platform and conduct clinical research.</p>",
            },
            {
                "type": "rich_section",
                "heading": "3. How We Use Your Information",
                "html": "<p>We use your information to facilitate clinical trial participation, communicate study updates, ensure regulatory compliance, process research data, and improve our services.</p>",
            },
            {
                "type": "rich_section",
                "heading": "4. Data Sharing and Disclosure",
                "html": "<p>We do not sell personal information. We may share data with research sponsors, regulatory authorities, ethics committees, and service providers as required for clinical trial conduct and compliance.</p>",
            },
            {
                "type": "rich_section",
                "heading": "5. Data Security",
                "html": "<p>We implement technical and organizational measures including encryption, access controls, regular audits, and secure data centers to protect your information.</p>",
            },
            {
                "type": "rich_section",
                "heading": "6. Your Rights",
                "html": "<p>You may request access, correction, erasure, portability, or object to processing of your personal data in accordance with applicable regulations.</p>",
            },
            {
                "type": "rich_section",
                "heading": "7. Contact Us",
                "html": "<p>If you have questions about this policy, contact privacy@ctc-research.com.</p>",
            },
        ],
    },
    "faq": {
        "slug": "faq",
        "title": "Frequently Asked Questions",
        "seo": {
            "title": "FAQ | CTC Research",
            "description": "Answers to common questions about CTC Research clinical trials and services.",
        },
        "blocks": [
            {
                "type": "hero",
                "heading": "Frequently Asked Questions",
                "intro": "Find answers to common questions about our clinical research services",
            },
            {
                "type": "faq_groups",
                "groups": [
                    {
                        "title": "Clinical Trials",
                        "items": [
                            {
                                "question": "How do I participate in a clinical trial?",
                                "answer": "Contact our patient recruitment team through the contact form. We'll help match you with appropriate studies based on your medical history and eligibility criteria.",
                            },
                            {
                                "question": "Are clinical trials safe?",
                                "answer": "All trials follow strict protocols approved by ethics committees and regulatory authorities. Patient safety is our top priority throughout every study.",
                            },
                            {
                                "question": "How long do trials typically last?",
                                "answer": "Duration varies by study phase and therapeutic area. Early-phase trials may last months, while later-phase trials can extend over several years.",
                            },
                        ],
                    },
                    {
                        "title": "For Sponsors",
                        "items": [
                            {
                                "question": "How do I start a trial with CTC Research?",
                                "answer": "Contact our business development team through our contact form. We'll schedule a consultation to discuss your study requirements and timeline.",
                            },
                            {
                                "question": "What therapeutic areas do you cover?",
                                "answer": "We have expertise across oncology, cardiology, neurology, rare diseases, infectious diseases, and more. Contact us to discuss your specific therapeutic area.",
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
            "title": "Contact Us | CTC Research",
            "description": "Contact CTC Research for clinical trial inquiries, partnership opportunities, and general information.",
        },
        "blocks": [
            {
                "type": "hero",
                "heading": "Contact Us",
                "intro": "We'd love to hear from you. Reach out to discuss your clinical research needs.",
            },
            {
                "type": "contact_methods",
                "items": [
                    {
                        "type": "email",
                        "label": "Email",
                        "value": "info@ctc-research.com",
                        "href": "mailto:info@ctc-research.com",
                    },
                    {
                        "type": "phone",
                        "label": "Phone",
                        "value": "+1 (555) 234-5678",
                        "href": "tel:+15552345678",
                    },
                    {
                        "type": "address",
                        "label": "Address",
                        "value": "100 Research Drive, Innovation Park, MD 20850",
                    },
                    {
                        "type": "hours",
                        "label": "Hours",
                        "value": "Mon-Fri 8:00 AM - 6:00 PM EST",
                    },
                ],
            },
            {"type": "form", "heading": "Send us a message"},
        ],
    },
}


def normalize_slug(slug: str) -> str:
    """Normalize a URL slug to the keys used in ``STATIC_PAGES``."""
    return "home" if slug in ("", "home", "index") else slug.strip("/")
