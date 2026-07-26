#!/usr/bin/env python3
"""
Mock LMS API server — serves realistic JSON data for all /apis/ endpoints.

Run with: python mock_server.py
This starts an HTTP server on port 8000 that the Next.js frontend can use
for end-to-end testing.
"""

import json
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# ── Mock data ────────────────────────────────────────────────────────

def _make_course(c):
    """Convert internal course dict to frontend Course interface format."""
    cat_name = c["category_name"]
    instructor_name = c["instructor_name"]
    return {
        "id": c["id"],
        "title": c["title"],
        "slug": c["slug"],
        "description": c["description"],
        "short_description": c["short_description"],
        "price": float(c["price"]),
        "discounted_price": None if c.get("is_free") else round(float(c["price"]) * 0.9, 2),
        "thumbnail": "/media/courses/default.jpg",
        "category": c["category"],
        "category_name": cat_name,
        "instructor": c["instructor"],
        "instructor_name": instructor_name,
        "duration": f"{c['duration_hours']}h",
        "level": c["level"],
        "language": c["language"],
        "curriculum": [],
        "students_count": c["students_count"],
        "rating": c["rating"],
        "reviews_count": c.get("reviews_count", 0),
        "is_published": True,
        "created_at": c["created_at"],
        "updated_at": c["created_at"],
    }


MOCK_COURSES_RAW = [
    {"id": 1, "title": "Python for Data Science", "slug": "python-data-science", "description": "Master Python programming for data analysis, visualization, and machine learning. This comprehensive course covers NumPy, Pandas, Matplotlib, and Scikit-learn.", "short_description": "Learn Python for data analysis and ML", "price": "49.99", "is_free": False, "category": 1, "category_name": "Data Science", "instructor": 1, "instructor_name": "Dr. Ahmed Hassan", "rating": 4.8, "students_count": 1234, "reviews_count": 89, "duration_hours": 16, "level": "intermediate", "language": "ar", "created_at": "2026-01-15T08:00:00Z"},
    {"id": 2, "title": "Web Development with Django", "slug": "web-dev-django", "description": "Build robust web applications using Django framework. From models to views, templates to REST APIs.", "short_description": "Full-stack web development with Django", "price": "39.99", "is_free": False, "category": 2, "category_name": "Web Development", "instructor": 2, "instructor_name": "Sara Khalid", "rating": 4.6, "students_count": 2156, "reviews_count": 156, "duration_hours": 20, "level": "beginner", "language": "ar", "created_at": "2026-02-20T10:00:00Z"},
    {"id": 3, "title": "Introduction to Artificial Intelligence", "slug": "intro-ai", "description": "Explore the fundamentals of AI including search algorithms, neural networks, and natural language processing.", "short_description": "AI fundamentals for beginners", "price": "0", "is_free": True, "category": 3, "category_name": "Artificial Intelligence", "instructor": 3, "instructor_name": "Prof. Omar Mahmoud", "rating": 4.9, "students_count": 3451, "reviews_count": 203, "duration_hours": 12, "level": "beginner", "language": "ar", "created_at": "2026-03-01T09:00:00Z"},
    {"id": 4, "title": "Mobile App Development with Flutter", "slug": "flutter-mobile", "description": "Create beautiful cross-platform mobile apps using Flutter and Dart.", "short_description": "Cross-platform mobile apps with Flutter", "price": "59.99", "is_free": False, "category": 4, "category_name": "Mobile Development", "instructor": 1, "instructor_name": "Dr. Ahmed Hassan", "rating": 4.7, "students_count": 1890, "reviews_count": 67, "duration_hours": 24, "level": "intermediate", "language": "en", "created_at": "2026-04-10T11:00:00Z"},
]
MOCK_COURSES = [_make_course(c) for c in MOCK_COURSES_RAW]

MOCK_CATEGORIES = [
    {"id": 1, "name": "Data Science", "slug": "data-science", "courses_count": 12},
    {"id": 2, "name": "Web Development", "slug": "web-dev", "courses_count": 18},
    {"id": 3, "name": "Artificial Intelligence", "slug": "ai", "courses_count": 8},
    {"id": 4, "name": "Mobile Development", "slug": "mobile", "courses_count": 6},
    {"id": 5, "name": "Design", "slug": "design", "courses_count": 10},
]

MOCK_BLOG_POSTS = [
    {"id": 1, "title": "مستقبل التعلم الإلكتروني في العالم العربي", "slug": "future-elearning-arab-world", "content": "يشهد التعلم الإلكتروني نمواً متسارعاً في العالم العربي...", "excerpt": "تعرف على أحدث اتجاهات التعلم الإلكتروني وتأثيرها على التعليم في العالم العربي", "author": 1, "author_name": "أ. محمد علي", "author_avatar": "/media/authors/mohamed.jpg", "category": 1, "category_name": "التعليم الإلكتروني", "tags": ["تعليم", "تكنولوجيا", "ابتكار"], "featured_image": "/media/blog/elearning.jpg", "is_published": True, "view_count": 245, "created_at": "2026-06-15T08:00:00Z", "updated_at": "2026-06-15T08:00:00Z"},
    {"id": 2, "title": "How to Master Python in 30 Days", "slug": "master-python-30-days", "content": "Python is one of the most versatile programming languages...", "excerpt": "A practical roadmap to learn Python programming from scratch in just 30 days", "author": 2, "author_name": "Sara Khalid", "author_avatar": "/media/authors/sara.jpg", "category": 2, "category_name": "Programming", "tags": ["Python", "Programming", "Tutorial"], "featured_image": "/media/blog/python.jpg", "is_published": True, "view_count": 189, "created_at": "2026-06-10T10:00:00Z", "updated_at": "2026-06-10T10:00:00Z"},
    {"id": 3, "title": "دليل شامل لتعلم الآلة", "slug": "comprehensive-ml-guide", "content": "تعلم الآلة هو فرع من الذكاء الاصطناعي...", "excerpt": "دليل شامل للمبتدئين في تعلم الآلة يشرح المفاهيم الأساسية والتطبيقات العملية", "author": 1, "author_name": "أ. محمد علي", "author_avatar": "/media/authors/mohamed.jpg", "category": 3, "category_name": "الذكاء الاصطناعي", "tags": ["تعلم آلة", "ذكاء اصطناعي", "بايثون"], "featured_image": "/media/blog/ml-guide.jpg", "is_published": True, "view_count": 312, "created_at": "2026-05-28T09:00:00Z", "updated_at": "2026-05-28T09:00:00Z"},
]

MOCK_INSTRUCTORS_RAW = [
    {"id": 1, "user": 1, "username": "ahmed.hassan", "email": "ahmed@structa.cloud", "first_name": "Ahmed", "last_name": "Hassan", "slug": "ahmed-hassan", "title": "خبير في علوم البيانات والذكاء الاصطناعي", "bio": "خبير في علوم البيانات والذكاء الاصطناعي مع أكثر من 15 عاماً من الخبرة في تحليل البيانات وتطوير نماذج التعلم الآلي. درّس أكثر من 3000 طالب في مختلف أنحاء العالم العربي.", "avatar": "/media/instructors/ahmed.jpg", "specialty": "Data Science & AI", "expertise": ["Python", "Machine Learning", "Data Analysis", "Deep Learning", "Statistics"], "average_rating": 4.8, "rating": 4.8, "students_count": 3124, "courses_count": 8, "reviews_count": 156, "joined_at": "2024-01-15T08:00:00Z"},
    {"id": 2, "user": 2, "username": "sara.khalid", "email": "sara@structa.cloud", "first_name": "Sara", "last_name": "Khalid", "slug": "sara-khalid", "title": "مطورة ويب محترفة", "bio": "مطورة ويب محترفة ومتخصصة في Django و React. لديها خبرة تزيد عن 10 سنوات في تطوير تطبيقات الويب وتعليم البرمجة للمبتدئين والمحترفين.", "avatar": "/media/instructors/sara.jpg", "specialty": "Web Development", "expertise": ["Django", "React", "TypeScript", "REST APIs", "PostgreSQL"], "average_rating": 4.6, "rating": 4.6, "students_count": 2156, "courses_count": 5, "reviews_count": 98, "joined_at": "2024-03-20T08:00:00Z"},
    {"id": 3, "user": 3, "username": "omar.mahmoud", "email": "omar@structa.cloud", "first_name": "Omar", "last_name": "Mahmoud", "slug": "omar-mahmoud", "title": "أستاذ الذكاء الاصطناعي", "bio": "أستاذ الذكاء الاصطناعي في جامعة القاهرة، متخصص في معالجة اللغة الطبيعية ورؤية الكمبيوتر. حاصل على الدكتوراه في الذكاء الاصطناعي.", "avatar": "/media/instructors/omar.jpg", "specialty": "Artificial Intelligence", "expertise": ["Natural Language Processing", "Computer Vision", "Neural Networks", "Reinforcement Learning"], "average_rating": 4.9, "rating": 4.9, "students_count": 3451, "courses_count": 3, "reviews_count": 203, "joined_at": "2024-06-10T08:00:00Z"},
]


def _make_instructor_detail(i):
    """Enrich instructor data with frontend-facing fields for detail page."""
    name = f"{i['first_name']} {i['last_name']}"
    skills = i.get("expertise", [i.get("specialty", "")])
    # Build an instructor course list from MOCK_COURSES that belong to this instructor
    instructor_courses = [c for c in MOCK_COURSES if c["instructor"] == i["id"]]
    if not instructor_courses:
        instructor_courses = MOCK_COURSES[:3]
    return {
        **i,
        "name": name,
        "role": i["title"],
        "cover": f"https://picsum.photos/seed/{i['id']}/1200/400",
        "studentsCount": i["students_count"],
        "coursesCount": i["courses_count"],
        "reviewsCount": i["reviews_count"],
        "total_reviews": i["reviews_count"],
        "skills": skills,
        "social": {
            "website": f"https://{i['slug']}.dev",
            "twitter": f"@{i['first_name'].lower()}_{i['last_name'].lower()}",
            "github": i["slug"],
        },
        "courses": [
            {"id": c["id"], "title": c["title"], "students": c["students_count"], "rating": c["rating"], "price": c["price"], "image": c.get("thumbnail", "/media/courses/default.jpg")}
            for c in instructor_courses
        ],
    }


MOCK_INSTRUCTORS = MOCK_INSTRUCTORS_RAW

MOCK_EVENTS = [
    {"id": 1, "title": "مؤتمر التعلم الإلكتروني 2026", "slug": "elearning-conf-2026", "description": "المؤتمر السنوي للتعلم الإلكتروني يجمع نخبة من الخبراء", "start_date": "2026-09-15T09:00:00Z", "end_date": "2026-09-16T18:00:00Z", "location": "القاهرة", "type": "conference", "image": "/media/events/conf.jpg", "capacity": 500, "registered_count": 320, "is_free": True, "price": "0"},
    {"id": 2, "title": "ورشة عمل: بايثون للمبتدئين", "slug": "python-workshop", "description": "ورشة عمل عملية لتعلم أساسيات لغة بايثون", "start_date": "2026-08-20T10:00:00Z", "end_date": "2026-08-20T14:00:00Z", "location": "أونلاين", "type": "workshop", "image": "/media/events/workshop.jpg", "capacity": 100, "registered_count": 75, "is_free": False, "price": "99.00"},
]

def _make_page(slug, title, blocks):
    return {
        "slug": slug,
        "title": title,
        "seo": {"title": title, "description": title},
        "last_updated": "2026-07-01T00:00:00Z",
        "blocks": blocks,
    }


MOCK_PAGES = {
    "home": _make_page("home", "Learn Without Limits", [
        {"type": "hero", "heading": "Learn Without Limits", "intro": "Master new skills with expert-led courses, interactive content, and a community of learners.", "ctas": [{"label": "Explore Courses", "href": "/courses"}, {"label": "Get Started Free", "href": "/registration"}]},
        {"type": "stats", "key": "stats", "items": [{"label": "Students", "value": "5K+"}, {"label": "Reviews", "value": "12K+"}]},
        {"type": "featured", "key": "featured_courses", "heading": "Featured Courses", "intro": "Most popular courses picked for you"},
        {"type": "cta", "heading": "Start Learning Today", "intro": "Join thousands of students and start your learning journey today.", "ctas": [{"label": "Create Free Account", "href": "/registration"}]},
    ]),
    "about-us": _make_page("about-us", "About Us", [
        {"type": "hero", "heading": "About Structa LMS", "intro": "Empowering learners worldwide with expert-led courses and cutting-edge content."},
        {"type": "rich_section", "heading": "Our Mission", "html": "<p>We are a leading educational platform dedicated to providing high-quality technical education. Our mission is to bridge the gap between traditional education and the evolving demands of the job market.</p>"},
        {"type": "cta", "heading": "Ready to Start Learning?", "intro": "Join thousands of successful students today.", "ctas": [{"label": "Create Free Account", "href": "/registration"}]},
    ]),
    "faq": _make_page("faq", "Frequently Asked Questions", [
        {"type": "hero", "heading": "Frequently Asked Questions", "intro": "Find answers to common questions about our platform, courses, and services."},
        {"type": "faq_groups", "groups": [
            {"title": "Getting Started", "items": [
                {"question": "How do I create an account?", "answer": "Click the 'Sign Up' button on the top right corner. Fill in your name, email, and password. You'll receive a confirmation email to activate your account."},
                {"question": "Are the courses free?", "answer": "We offer both free and paid courses. Free courses provide full access to all content. Paid courses require a one-time purchase for lifetime access."},
                {"question": "How do I enroll in a course?", "answer": "Browse our course catalog, click on a course you're interested in, and click the 'Enroll Now' button. Free courses enroll immediately, paid courses will guide you through payment."},
            ]},
            {"title": "Payments & Billing", "items": [
                {"question": "What payment methods do you accept?", "answer": "We accept all major credit cards (Visa, MasterCard, American Express), PayPal, and local payment methods depending on your region."},
                {"question": "Can I get a refund?", "answer": "Yes, we offer a 30-day money-back guarantee on all paid courses. If you're not satisfied, contact our support team for a full refund."},
                {"question": "Do you offer certificates?", "answer": "Yes, upon completing a course you will receive a verifiable certificate of completion that you can share on LinkedIn or your resume."},
            ]},
            {"title": "Technical Support", "items": [
                {"question": "What if I have trouble accessing a course?", "answer": "Try clearing your browser cache or using a different browser. If problems persist, contact our support team and we'll help you resolve the issue."},
                {"question": "Can I download course materials?", "answer": "Yes, most course materials including PDFs, code samples, and resources are available for download. Video lessons are streamed online."},
            ]},
        ]},
        {"type": "cta", "heading": "Still have questions?", "intro": "Our support team is here to help you 24/7.", "ctas": [{"label": "Contact Support", "href": "/contact"}]},
    ]),
    "contact": _make_page("contact", "اتصل بنا", [
        {"type": "hero", "heading": "اتصل بنا", "intro": "نحن هنا لمساعدتك! تواصل معنا عبر أي من القنوات المتاحة."},
        {"type": "contact_methods", "items": [
            {"type": "email", "label": "Email", "value": "info@structa.cloud", "href": "mailto:info@structa.cloud"},
            {"type": "phone", "label": "Phone", "value": "+201234567890", "href": "tel:+201234567890"},
            {"type": "address", "label": "Address", "value": "القاهرة، مصر"},
        ]},
    ]),
    "privacy": _make_page("privacy", "سياسة الخصوصية", [
        {"type": "rich_section", "heading": "سياسة الخصوصية", "html": "<p>نحن نلتزم بحماية خصوصية مستخدمينا...</p>"},
    ]),
}

MOCK_REVIEWS = [
    {"id": 1, "course": 1, "user": "مستخدم 1", "rating": 5, "comment": "دورة ممتازة! المحتوى غني والشرح واضح.", "created_at": "2026-04-01T08:00:00Z"},
    {"id": 2, "course": 1, "user": "مستخدم 2", "rating": 4, "comment": "Good course, but could use more exercises.", "created_at": "2026-04-15T10:00:00Z"},
]

MOCK_SHOP_PRODUCTS = [
    {"id": 1, "name": "دفتر ملاحظات المبرمج", "slug": "programmer-notebook", "description": "دفتر ملاحظات عالي الجودة للمبرمجين، مصمم خصيصاً لتناسب احتياجات المبرمجين مع ورق عالي الجودة وتصميم أنيق.", "price": 49.99, "discounted_price": 39.99, "original_price": 69.99, "images": ["/media/shop/notebook.jpg", "/media/shop/notebook2.jpg", "/media/shop/notebook3.jpg"], "category": 1, "category_name": "قرطاسية", "stock": 50, "rating": 4.5, "reviewCount": 124, "inStock": True, "is_available": True, "features": ["ورق عالي الجودة", "تصميم أنيق ومتين", "100 صفحة", "مقاس A5", "غلاف مقوى"], "colors": ["أسود", "أزرق", "أخضر"], "sizes": ["A5", "A4"], "reviews": [
        {"id": 1, "author": "محمد أ.", "rating": 5, "text": "نوت بوك ممتاز جداً، الورق عالي الجودة والتصميم أنيق.", "date": "منذ أسبوعين"},
        {"id": 2, "author": "Sara K.", "rating": 4, "text": "Perfect for taking notes during coding sessions. Love the quality!", "date": "منذ شهر"},
        {"id": 3, "author": "أحمد ر.", "rating": 5, "text": "جودة ممتازة وسعر مناسب، أنصح به كل مبرمج.", "date": "منذ شهرين"},
    ], "created_at": "2026-01-15T08:00:00Z"},
    {"id": 2, "name": "تي شورت مبرمج", "slug": "programmer-tshirt", "description": "تي شورت قطني مريح بشعارات برمجية، مصنوع من قطن عضوي 100% للراحة أثناء العمل.", "price": 89.99, "discounted_price": None, "original_price": None, "images": ["/media/shop/tshirt.jpg", "/media/shop/tshirt2.jpg", "/media/shop/tshirt3.jpg"], "category": 2, "category_name": "ملابس", "stock": 30, "rating": 4.2, "reviewCount": 67, "inStock": True, "is_available": True, "features": ["قطن عضوي 100%"], "colors": ["أسود", "أبيض", "رمادي"], "sizes": ["S", "M", "L", "XL", "2XL"], "reviews": [
        {"id": 4, "author": "Ali M.", "rating": 4, "text": "جودة ممتازة والطباعة واضحة، القياس مناسب.", "date": "منذ شهر"},
    ], "created_at": "2026-02-20T08:00:00Z"},
]

MOCK_CART = {
    "items": [
        {"id": 1, "product_name": "دفتر ملاحظات المبرمج", "product_price": 49.99, "quantity": 2, "subtotal": 99.98, "product": MOCK_SHOP_PRODUCTS[0]},
    ],
    "total": 99.98,
}

MOCK_SETTINGS = {
    "site_name": "Structa LMS",
    "site_description": "منصة التعلم الإلكتروني الرائدة",
    "logo": "/media/logo.png",
    "favicon": "/media/favicon.ico",
    "social_links": {
        "facebook": "https://facebook.com/structa",
        "twitter": "https://twitter.com/structa",
        "linkedin": "https://linkedin.com/company/structa",
    },
    "contact_email": "info@structa.cloud",
    "support_phone": "+201234567890",
}


def make_paginated(items, page=1, page_size=20):
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "results": items[start:end],
        "count": total,
        "next": f"/apis/?page={page + 1}" if end < total else None,
        "previous": f"/apis/?page={page - 1}" if page > 1 else None,
    }


class MockAPIHandler(BaseHTTPRequestHandler):
    """Simple mock API server — returns realistic JSON for all LMS endpoints."""

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _send_error(self, message, status=400):
        self._send_json({"error": message, "success": False}, status)

    def do_OPTIONS(self):
        self._send_json({})

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        params = parse_qs(parsed.query)
        page = int(params.get("page", [1])[0])

        # ── Auth ──
        if path == "/apis/auth/profile":
            return self._send_json({
                "id": 1, "username": "student1", "email": "student@structa.cloud",
                "first_name": "Ahmed", "last_name": "Ali",
                "avatar": "/media/avatars/default.jpg",
                "bio": "طالب مهتم بتعلم البرمجة", "joined_at": "2026-01-15T08:00:00Z",
                "is_student": True, "is_instructor": False,
                "enrolled_courses_count": 3, "completed_courses_count": 1,
            })

        # ── Courses ──
        if path == "/apis/courses":
            return self._send_json(make_paginated(MOCK_COURSES, page))

        if path == "/apis/courses/featured":
            return self._send_json(MOCK_COURSES[:3])

        if path.startswith("/apis/courses/"):
            try:
                cid = int(path.split("/")[-1])
                for c in MOCK_COURSES:
                    if c["id"] == cid:
                        return self._send_json({**c, "reviews": MOCK_REVIEWS, "curriculum": [
                            {"title": "Introduction", "lessons": [{"title": "Getting Started", "duration": "30:00", "is_free": True}]},
                            {"title": "Core Concepts", "lessons": [{"title": "Main Topics", "duration": "45:00", "is_free": False}]},
                        ]})
                return self._send_error("Course not found", 404)
            except ValueError:
                pass

        # ── Categories (expects plain array, not paginated wrapper)
        if path == "/apis/categories":
            return self._send_json(MOCK_CATEGORIES)

        # ── Blog ──
        if path == "/apis/blog" or path == "/apis/blog/":
            return self._send_json(make_paginated(MOCK_BLOG_POSTS, page))

        if path == "/apis/blog/featured":
            return self._send_json(MOCK_BLOG_POSTS[:2])

        if path == "/apis/blog/categories":
            return self._send_json([
                {"id": 1, "name": "التعليم الإلكتروني", "slug": "elearning", "post_count": 5},
                {"id": 2, "name": "Programming", "slug": "programming", "post_count": 8},
                {"id": 3, "name": "الذكاء الاصطناعي", "slug": "ai", "post_count": 3},
            ])

        # ── Blog: Related Posts ──
        blog_parts = path.split("/")
        if len(blog_parts) >= 5 and blog_parts[-1] == "related":
            try:
                bid = int(blog_parts[-2])
                return self._send_json([p for p in MOCK_BLOG_POSTS if p["id"] != bid][:2])
            except ValueError:
                pass

        if path.startswith("/apis/blog/"):
            try:
                bid = int(path.split("/")[-1])
                for b in MOCK_BLOG_POSTS:
                    if b["id"] == bid:
                        return self._send_json(b)
                return self._send_error("Post not found", 404)
            except ValueError:
                pass

        # ── Instructors ──
        if path == "/apis/instructors" or path == "/apis/instructors/":
            return self._send_json(make_paginated(MOCK_INSTRUCTORS, page))

        if path.startswith("/apis/instructors/"):
            parts = path.split("/")
            try:
                iid = int(parts[3])
                for i in MOCK_INSTRUCTORS:
                    if i["id"] == iid:
                        if "dashboard" in path:
                            return self._send_json({**i, "total_revenue": "15000.00", "monthly_students": 120})
                        if "courses" in path:
                            return self._send_json(MOCK_COURSES[:2])
                        if "reviews" in path:
                            return self._send_json(make_paginated(MOCK_REVIEWS))
                        return self._send_json(_make_instructor_detail(i))
                return self._send_error("Instructor not found", 404)
            except ValueError:
                pass

        # ── Events ──
        if path == "/apis/events" or path == "/apis/events/":
            return self._send_json(make_paginated(MOCK_EVENTS, page))

        if path == "/apis/events/upcoming":
            return self._send_json(MOCK_EVENTS)

        if path.startswith("/apis/events/"):
            try:
                eid = int(path.split("/")[-1])
                for e in MOCK_EVENTS:
                    if e["id"] == eid:
                        return self._send_json(e)
                return self._send_error("Event not found", 404)
            except ValueError:
                pass

        # ── Pages ──
        if path.startswith("/apis/pages/"):
            slug = path.split("/")[-1]
            if slug in MOCK_PAGES:
                return self._send_json(MOCK_PAGES[slug])
            return self._send_error("Page not found", 404)

        # ── Students ──
        if path == "/apis/students" or path == "/apis/students/":
            return self._send_json(make_paginated([
                {"id": 1, "username": "student1", "email": "student@structa.cloud", "enrolled_count": 3},
            ], page))

        # This student detail handler is placed AFTER the "students list" check
        # but BEFORE the student detail fallback above.
        if path.startswith("/apis/students/"):
            parts = path.split("/")
            sid = parts[3]
            if "dashboard" in path:
                return self._send_json({
                    "student": {"id": 1, "name": "Ahmed Ali"},
                    "enrolled_courses": 3, "completed_courses": 1,
                    "in_progress": 2, "total_hours": 28,
                    "recent_activity": [
                        {"type": "lesson_completed", "course": "Python for Data Science", "timestamp": "2026-07-20T14:00:00Z"},
                        {"type": "course_enrolled", "course": "Web Development with Django", "timestamp": "2026-07-18T10:00:00Z"},
                    ],
                    "achievements": [
                        {"title": "First Course", "description": "Complete your first course", "earned": True},
                        {"title": "Fast Learner", "description": "Complete 5 lessons in one day", "earned": True},
                        {"title": "Quiz Master", "description": "Score 100% on any quiz", "earned": False},
                    ]
                })
            if "enrollments" in path:
                return self._send_json({"results": [
                    {"id": 1, "course": 1, "course_title": "Python for Data Science", "course_thumbnail": "/media/courses/default.jpg", "status": "active", "progress": 65, "enrolled_at": "2026-06-01T08:00:00Z", "completed_at": None, "is_completed": False},
                    {"id": 2, "course": 3, "course_title": "Introduction to Artificial Intelligence", "course_thumbnail": "/media/courses/default.jpg", "status": "completed", "progress": 100, "enrolled_at": "2026-03-01T09:00:00Z", "completed_at": "2026-05-15T10:00:00Z", "is_completed": True},
                    {"id": 3, "course": 2, "course_title": "Web Development with Django", "course_thumbnail": "/media/courses/default.jpg", "status": "active", "progress": 30, "enrolled_at": "2026-07-01T08:00:00Z", "completed_at": None, "is_completed": False},
                ]})

        # ── Shop ──
        if path == "/apis/shop/products" or path == "/apis/shop/products/":
            return self._send_json(make_paginated(MOCK_SHOP_PRODUCTS, page))

        if path.startswith("/apis/shop/products/"):
            try:
                pid = int(path.split("/")[-1])
                for p in MOCK_SHOP_PRODUCTS:
                    if p["id"] == pid:
                        return self._send_json(p)
                return self._send_error("Product not found", 404)
            except ValueError:
                pass

        if path == "/apis/shop/cart" or path == "/apis/shop/cart/":
            return self._send_json(MOCK_CART["items"])

        # ── Shop Orders ──
        if path == "/apis/shop/orders" or path == "/apis/shop/orders/":
            return self._send_json(make_paginated([
                {"id": 1, "order_number": "ORD-20260722-001", "status": "completed", "total": "99.98", "items_count": 2, "created_at": "2026-07-22T00:00:00Z"},
                {"id": 2, "order_number": "ORD-20260715-002", "status": "pending", "total": "89.99", "items_count": 1, "created_at": "2026-07-15T10:00:00Z"},
            ], page))

        # ── Contact Inquiries ──
        if path == "/apis/contact/inquiries" or path == "/apis/contact/inquiries/":
            return self._send_json(make_paginated([
                {"id": 1, "name": "أحمد علي", "email": "ahmed@example.com", "subject": "استفسار عن الدورات", "message": "أريد معرفة المزيد عن دورات البيانات", "created_at": "2026-07-20T08:00:00Z", "is_read": False},
                {"id": 2, "name": "Sara", "email": "sara@example.com", "subject": "Payment Issue", "message": "I have a problem with my payment", "created_at": "2026-07-19T14:00:00Z", "is_read": True},
            ], page))

        # ── Students detail ──
        if path.startswith("/apis/students/"):
            parts = path.split("/")
            if len(parts) == 4:  # Just /apis/students/{id}
                return self._send_json({"id": 1, "username": "student1", "email": "student@structa.cloud", "enrolled_count": 3})

        # ── Fallback ──
        self._send_error(f"Endpoint not found: {path}", 404)

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            body = {}

        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        # ── Auth ──
        if path == "/apis/auth/login":
            username = body.get("username", body.get("email", ""))
            password = body.get("password", "")
            if username and password:
                return self._send_json({
                    "access": "mock-jwt-access-token-for-testing",
                    "refresh": "mock-jwt-refresh-token-for-testing",
                    "user": {"id": 1, "username": username, "email": f"{username}@structa.cloud"},
                    "expires_in": 3600,
                })
            return self._send_error("Invalid credentials", 401)

        if path == "/apis/auth/register":
            return self._send_json({
                "access": "mock-jwt-access-token-for-testing",
                "refresh": "mock-jwt-refresh-token-for-testing",
                "user": {"id": 2, "username": body.get("username", "newuser"), "email": body.get("email", "new@structa.cloud")},
                "expires_in": 3600,
            })

        if path == "/apis/auth/refresh":
            return self._send_json({
                "access": "new-mock-jwt-access-token",
                "refresh": body.get("refresh", "mock-jwt-refresh-token"),
                "expires_in": 3600,
            })

        if path == "/apis/auth/logout":
            return self._send_json({"success": True, "message": "Logged out successfully"})

        if path == "/apis/auth/password-reset":
            return self._send_json({"success": True, "message": "Password reset email sent"})

        if path == "/apis/auth/change-password":
            return self._send_json({"success": True, "message": "Password changed successfully"})

        # ── Enrollments ──
        if path == "/apis/enrollments" or path == "/apis/enrollments":
            course_id = body.get("course_id")
            return self._send_json({
                "id": 4,
                "course": next((c for c in MOCK_COURSES if c["id"] == course_id), MOCK_COURSES[0]),
                "status": "active",
                "progress": 0,
                "enrolled_at": "2026-07-22T00:00:00Z",
                "completed_at": None,
                "is_paid": not next((c for c in MOCK_COURSES if c["id"] == course_id), MOCK_COURSES[0]).get("is_free", True),
            }, 201)

        # ── Payment Init ──
        if path.endswith("/payment/init"):
            provider = body.get("provider", "stripe")
            if provider == "stripe":
                return self._send_json({
                    "provider": "stripe",
                    "client_secret": "pi_mock_secret_test_for_stripe",
                    "transaction_id": "tx_mock_123456",
                })
            elif provider == "paypal":
                return self._send_json({
                    "provider": "paypal",
                    "payment_url": "https://www.paypal.com/checkout?token=mock_token",
                    "transaction_id": "tx_mock_123456",
                })
            else:
                return self._send_json({
                    "provider": provider,
                    "payment_url": f"https://payment-gateway.com/pay/{provider}/mock_token",
                    "transaction_id": "tx_mock_123456",
                })

        # ── Payment Verify ──
        if path.startswith("/apis/payments/") and path.endswith("/verify"):
            return self._send_json({
                "status": "completed",
                "transaction_id": path.split("/")[-2],
                "verified_at": "2026-07-22T00:00:00Z",
            })

        # ── Progress Update ──
        if path.endswith("/progress"):
            return self._send_json({
                "id": 1,
                "progress": body.get("progress", 0),
                "completed_lessons": body.get("completed_lessons", []),
                "updated_at": "2026-07-22T00:00:00Z",
            })

        # ── Events Registration ──
        if path == "/apis/events/register" or path == "/apis/events/register":
            return self._send_json({
                "success": True,
                "registration": {"id": 1, "event_id": body.get("event_id"), "status": "confirmed"},
            }, 201)

        # ── Contact ──
        # ── Contact Submit ──
        if path == "/apis/contact" or path == "/apis/contact/":
            return self._send_json({
                "success": True,
                "message": "تم استلام رسالتك بنجاح. سنتواصل معك قريباً.",
            }, 201)

        # ── Contact Mark Read ──
        if path.startswith("/apis/contact/") and path.endswith("/mark-read"):
            return self._send_json({"success": True, "message": "Inquiry marked as read"})

        # ── Shop Cart ──
        if path == "/apis/shop/cart/add" or path == "/apis/shop/cart/add":
            product_id = body.get("product_id")
            return self._send_json({
                "id": 2,
                "product": next((p for p in MOCK_SHOP_PRODUCTS if p["id"] == product_id), MOCK_SHOP_PRODUCTS[0]),
                "quantity": body.get("quantity", 1),
                "subtotal": "49.99",
            }, 201)

        # ── Shop Orders (create) ──
        if path == "/apis/shop/orders" or path == "/apis/shop/orders/":
            return self._send_json({
                "id": 1,
                "order_number": "ORD-20260722-001",
                "status": "pending",
                "total": "99.98",
                "items": MOCK_CART["items"],
                "created_at": "2026-07-22T00:00:00Z",
            }, 201)

        # ── Fallback ──
        return self._send_json({"success": True, "message": f"Mock POST to {path} received"})

    def do_PATCH(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/apis/auth/profile":
            return self._send_json({"success": True, "message": "Profile updated"})

        return self._send_json({"success": True, "message": f"Mock PATCH to {path} received"})

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        return self._send_json({"success": True, "message": f"Mock DELETE to {path} succeeded"})

    def log_message(self, format, *args):
        """Silence default HTTP server logs — too noisy."""
        pass


if __name__ == "__main__":
    port = 8000
    server = HTTPServer(("0.0.0.0", port), MockAPIHandler)
    print(f"🎯 Mock LMS API server running on http://localhost:{port}")
    print(f"   Endpoints: /apis/ auth, courses, blog, instructors, events, shop, pages, students, contact")
    print()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()
