#!/usr/bin/env python
"""
VResume Unified Data Populator
===============================

Comprehensive data population for VResume with professional, polite dummy data.
Optimized for design system testing and realistic content representation.

Usage:
    python -m tests.data_populator --verbose
"""

import argparse
import os
import random
import sys
from datetime import datetime, timedelta  # noqa: F401
from io import BytesIO
from pathlib import Path

import django
from PIL import Image as PILImage

# === Django Setup ===
if not os.environ.get("DJANGO_SETTINGS_MODULE"):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configs.settings")

# Add the v1 directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    django.setup()
except RuntimeError:
    pass

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.images import ImageFile
from django.utils import timezone
from wagtail.images.models import Image
from wagtail.models import Locale, Page, Site  # noqa: F401

# Import models
try:
    from pages.about.models import AboutPage, Client, Testimonial
    from pages.blog.models import BlogPage, BlogTag
    from pages.blog.models.tag import BlogPageTag
    from pages.connect.models import (
        Campaign,  # noqa: F401
        ContactPage,
        EmailDelivery,  # noqa: F401
        FormSubmission,  # noqa: F401
        Subscriber,  # noqa: F401
        TrackedURL,  # noqa: F401
        URLClick,  # noqa: F401
    )
    from pages.cv.models import ResumePage
    from pages.home.models import HomePage, Service, Slider, TeamMember, VResumeSettings
    from pages.portfolio.models import PortfolioPage, PortfolioTag, Project
except ImportError as e:
    print(f"Error importing models: {e}")
    sys.exit(1)


class Colors:
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    RED = "\033[0;31m"
    NC = "\033[0m"


class DataPopulator:
    """Unified engine for populating realistic, polite project data."""

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.created_count = 0
        self.updated_count = 0
        self.image_cache = {}
        self.active_blog_tags = []
        self.active_portfolio_tags = []

    def log(self, message, level="info"):
        if not self.verbose and level == "debug":
            return
        colors = {
            "info": Colors.BLUE,
            "success": Colors.GREEN,
            "warning": Colors.YELLOW,
            "error": Colors.RED,
        }
        color = colors.get(level, Colors.NC)
        print(f"{color}[{level.upper()}]{Colors.NC} {message}")

    def create_placeholder_image(self, title, width=200, height=200, style="default"):
        """
        Create a sophisticated placeholder image with optional tech/character styling.

        Args:
            title: Image title for identification
            width: Image width in pixels
            height: Image height in pixels
            style: 'default' (colored), 'tech' (tech-themed), or 'character' (avatar-style)
        """
        try:
            # Extended color palette for tech themes
            tech_colors = {
                "python": [(58, 102, 191), (255, 192, 61)],  # Python blue/yellow
                "react": [(97, 218, 251), (40, 40, 40)],  # React cyan/dark
                "cloud": [(255, 157, 77), (66, 133, 244)],  # Cloud orange/blue
                "design": [(233, 30, 99), (156, 39, 176)],  # Design pink/purple
                "mobile": [(76, 175, 80), (33, 150, 243)],  # Mobile green/blue
                "ai": [(244, 67, 54), (255, 193, 7)],  # AI red/yellow
                "security": [(63, 81, 181), (233, 30, 99)],  # Security indigo/pink
            }

            # Determine style
            theme_name = title.lower().split()[0] if title else "default"
            colors_palette = tech_colors.get(theme_name, [
                (255, 107, 107), (78, 205, 196), (69, 183, 209),
                (255, 160, 122), (152, 216, 200), (100, 181, 246),
                (129, 199, 132), (255, 213, 79), (255, 138, 101),
            ])

            if style == "tech":
                bg_color = colors_palette[0]
                accent_color = colors_palette[1] if len(colors_palette) > 1 else (255, 255, 255)
            elif style == "character":
                bg_color = colors_palette[0]
                accent_color = (255, 255, 255)
            else:  # default
                bg_color = random.choice(colors_palette)
                accent_color = (255, 255, 255)

            # Create image
            img = PILImage.new("RGB", (width, height), color=bg_color)
            draw = None
            try:
                from PIL import ImageDraw, ImageFont  # noqa: F401
                draw = ImageDraw.Draw(img)
            except (ImportError, AttributeError):
                pass

            # Add visual elements
            if style == "tech" and draw:
                # Add geometric tech pattern
                for i in range(5):
                    x = (i * width // 5)
                    y = (i * height // 5)
                    draw.rectangle([x, y, x + 30, y + 30], outline=accent_color, width=2)
            elif style == "character" and draw:
                # Simple circle avatar background
                center_x, center_y = width // 2, height // 2
                radius = min(width, height) // 3
                draw.ellipse([center_x - radius, center_y - radius,
                             center_x + radius, center_y + radius],
                            fill=accent_color)

            # Save to BytesIO
            img_io = BytesIO()
            img.save(img_io, format="PNG")
            img_io.seek(0)
            self.log(f"PIL image created for {title} (style={style})", "info")

            # Create Image object
            filename = f"{title.lower().replace(' ', '_')}.png"
            image = Image.objects.create(
                title=title, file=ImageFile(img_io, name=filename)
            )
            self.log(f"Created placeholder image: {title} (id={image.id}, style={style})", "info")
            self.created_count += 1
            return image
        except Exception as e:
            self.log(f"Placeholder image creation failed for {title}: {type(e).__name__}: {e}", "warning")
            import traceback
            self.log(traceback.format_exc(), "warning")
            return None

    def get_or_create_image(self, filename, title=None):
        if filename in self.image_cache:
            return self.image_cache[filename]

        # Check if exists in DB
        img_title = title or filename.split(".")[0].replace("-", " ").title()
        image = Image.objects.filter(title=img_title).first()
        if image:
            self.image_cache[filename] = image
            return image

        # Search image file in known project static & media locations
        # Build search roots prioritizing source directories over compiled ones
        search_roots = []

        # Add MEDIA_ROOT (media/images dir for Wagtail-managed images)
        media_root = Path(getattr(settings, "MEDIA_ROOT", "") or "")
        if media_root and media_root.exists():
            search_roots.insert(0, media_root)
            self.log(f"Added MEDIA_ROOT to search: {media_root}", "debug")

        # Add BASE_DIR/assets/media (source media location)
        assets_media = Path(settings.BASE_DIR) / "assets" / "media"
        if assets_media.exists() and assets_media not in search_roots:
            search_roots.insert(0, assets_media)
            self.log(f"Added assets/media to search: {assets_media}", "debug")

        # Add all STATICFILES_DIRS (source directories)
        staticfiles_dirs = getattr(settings, "STATICFILES_DIRS", [])
        if staticfiles_dirs:
            for static_dir in staticfiles_dirs:
                p = Path(static_dir)
                if p not in search_roots:
                    search_roots.append(p)

        # Add BASE_DIR/assets/static as source
        assets_static = Path(settings.BASE_DIR) / "assets" / "static"
        if assets_static not in search_roots:
            search_roots.append(assets_static)

        # Add STATIC_ROOT as fallback (compiled/collected files)
        static_root = Path(getattr(settings, "STATIC_ROOT", "") or "")
        if static_root and static_root not in search_roots:
            search_roots.append(static_root)

        candidate_paths = []
        for root in [p for p in search_roots if p]:
            candidate_paths.extend(
                [
                    root / filename,  # Direct filename match
                    root / "images" / filename,  # Under images subfolder
                ]
            )

        full_path = next((p for p in candidate_paths if p.exists()), None)

        # Fallback: search deeper under common nested folders like images/ui
        if not full_path:
            for root in [p for p in search_roots if p]:
                candidate_paths.extend(
                    [
                        root / "ui" / filename,
                        root / "images" / "ui" / filename,
                    ]
                )
            full_path = next((p for p in candidate_paths if p.exists()), None)

        # Fallback: search by basename in media directory (handles Wagtail renditions)
        if not full_path and media_root.exists():
            basename = Path(filename).stem  # Get filename without extension
            for candidate in media_root.glob(f"**/*{basename}*"):
                if candidate.is_file() and candidate.suffix in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                    full_path = candidate
                    self.log(f"Found image by basename match: {full_path}", "debug")
                    break

        # Final fallback: search under any root by basename
        if not full_path:
            basename = Path(filename).name
            for root in [p for p in search_roots if p and p.exists()]:
                match = next(root.glob(f"**/{basename}"), None)
                if match and match.is_file():
                    full_path = match
                    self.log(f"Found image by recursive search: {full_path}", "debug")
                    break

        # If file not found, create placeholder
        if not full_path:
            self.log(f"Image file not found for {filename}, creating placeholder", "warning")
            image = self.create_placeholder_image(img_title)
            if image:
                self.image_cache[filename] = image
            return image

        try:
            with open(full_path, "rb") as f:
                image = Image.objects.create(
                    title=img_title, file=ImageFile(f, name=full_path.name)
                )
            self.log(f"Created image from file: {full_path.name}", "info")
            self.image_cache[filename] = image
            self.created_count += 1
            return image
        except Exception as e:
            self.log(f"Image creation failed for {filename}: {e}, creating placeholder", "warning")
            image = self.create_placeholder_image(img_title)
            if image:
                self.image_cache[filename] = image
            return image

    def populate_snippets(self):
        """Create global snippets used across pages."""
        self.log("Populating snippets (Services, Sliders, Team, etc.)...")

        # 1. Services
        services_data = [
            {
                "name": "Full-Stack Development",
                "icon": "bi-code-slash",
                "desc": "Building robust and scalable web applications using modern technology stacks like Python, Django, and React.",
            },
            {
                "name": "UI/UX Architecture",
                "icon": "bi-layers",
                "desc": "Designing intuitive and accessible user interfaces with a focus on seamless user experience and modern aesthetics.",
            },
            {
                "name": "Cloud Infrastructure",
                "icon": "bi-cloud-check",
                "desc": "Implementing secure, scalable, and efficient cloud solutions using AWS, Azure, or Google Cloud Platform.",
            },
            {
                "name": "Technical Consulting",
                "icon": "bi-chat-left-text",
                "desc": "Providing strategic advice on software architecture, technology selection, and digital transformation initiatives.",
            },
            {
                "name": "Mobile App Development",
                "icon": "bi-phone",
                "desc": "Developing high-performance cross-platform mobile applications for iOS and Android using React Native or Flutter.",
            },
            {
                "name": "DevOps & Automation",
                "icon": "bi-gear-wide-connected",
                "desc": "Streamlining development workflows through CI/CD pipelines, containerization with Docker, and infrastructure as code.",
            },
            {
                "name": "API Design & Integration",
                "icon": "bi-box-arrow-in-right",
                "desc": "Crafting secure, interoperable APIs and integrations to connect services and accelerate digital ecosystems.",
            },
            {
                "name": "Security & Compliance",
                "icon": "bi-shield-lock",
                "desc": "Ensuring applications follow security best practices, data protection, and regulatory compliance.",
            },
        ]
        for data in services_data:
            _, created = Service.objects.update_or_create(
                name=data["name"],
                defaults={"icon": data["icon"], "description": data["desc"], "is_active": True},
            )
            if created:
                self.created_count += 1
            else:
                self.updated_count += 1

        # 2. Sliders
        sliders_data = [
            {
                "title": "Professional Portfolio",
                "subtitle": "Software engineering focused on quality, performance, and maintainability.",
                "img": "slider-1.png",
                "links": [
                    (
                        "link",
                        {
                            "label": "View Projects",
                            "url": "/portfolio/",
                            "icon": "ri-layout-grid-line",
                        },
                    )
                ],
            },
            {
                "title": "Creative Solutions",
                "subtitle": "Turning complex technical problems into elegant and scalable codebases.",
                "img": "slider-2.png",
                "links": [
                    ("link", {"label": "Contact Me", "url": "/contact/", "icon": "ri-mail-line"})
                ],
            },
            {
                "title": "Modern Web Architecture",
                "subtitle": "Specializing in distributed systems and high-traffic web applications.",
                "img": "slider-3.png",
                "links": [
                    ("link", {"label": "Read My Blog", "url": "/blog/", "icon": "ri-article-line"})
                ],
            },
            {
                "title": "Cloud & DevOps",
                "subtitle": "Building scalable infrastructure with containerization and automation.",
                "img": "slider-4.png",
                "links": [
                    ("link", {"label": "View Resume", "url": "/cv/", "icon": "ri-file-text-line"})
                ],
            },
            {
                "title": "Performance Engineering",
                "subtitle": "Optimizing applications for speed, reliability, and operational excellence.",
                "img": "slider-5.png",
                "links": [
                    ("link", {"label": "Explore Services", "url": "/about/", "icon": "ri-rocket-line"})
                ],
            },
            {
                "title": "Scalable Applications",
                "subtitle": "Building modern systems that grow with your business needs.",
                "img": "slider-6.png",
                "links": [
                    ("link", {"label": "View Projects", "url": "/portfolio/", "icon": "ri-layout-grid-line"})
                ],
            },
            {
                "title": "User Experience Design",
                "subtitle": "Crafting intuitive digital experiences that delight users.",
                "img": "slider-7.png",
                "links": [
                    ("link", {"label": "Get in Touch", "url": "/contact/", "icon": "ri-mail-line"})
                ],
            },
        ]
        for data in sliders_data:
            img = self.get_or_create_image(data["img"], title=data["title"])

            # If image is None, create tech-themed placeholder
            if img is None:
                img = self.create_placeholder_image(data["title"], width=1200, height=400, style="tech")

            _, created = Slider.objects.update_or_create(
                title=data["title"],
                defaults={
                    "subtitle": data["subtitle"],
                    "image": img,
                    "links": data["links"],
                    "is_active": True,
                },
            )
            if created:
                self.created_count += 1
            else:
                self.updated_count += 1

        # 3. Team Members
        team_data = [
            {"name": "Casey Morgan", "job": "Product Design Lead", "img": "team/avatar-02.svg"},
            {"name": "Jamie Chen", "job": "Full-Stack Developer", "img": "team/avatar-03.svg"},
            {"name": "Taylor Smith", "job": "DevOps Engineer", "img": "team/avatar-04.svg"},
            {"name": "Morgan Lee", "job": "Frontend Developer", "img": "team/02.jpg"},
            {"name": "Jordan Williams", "job": "QA Engineer", "img": "team/avatar-01.svg"},
            {"name": "Riley Chen", "job": "Data Scientist", "img": "team/avatar-02.svg"},
            {"name": "Casey Brown", "job": "Security Specialist", "img": "team/avatar-03.svg"},
        ]
        for data in team_data:
            img = self.get_or_create_image(data["img"])
            _, created = TeamMember.objects.update_or_create(
                name=data["name"],
                defaults={"job_title": data["job"], "image": img, "is_active": True},
            )
            if created:
                self.created_count += 1
            else:
                self.updated_count += 1

        # 4. Testimonials
        test_data = [
            {
                "name": "Morgan Smith",
                "job": "CEO at TechFlow",
                "text": "A highly professional collaborator who delivers consistent quality and thoughtful solutions. Their technical depth is truly impressive.",
                "img": "testimonials/morgan-smith.jpg",
            },
            {
                "name": "Jordan Lee",
                "job": "Director of Engineering",
                "text": "Exceptional attention to detail and a calm approach to complex architectural challenges. One of the best architects I've worked with.",
                "img": "testimonials/jordan-lee.webp",
            },
            {
                "name": "Sarah Connor",
                "job": "Product Manager",
                "text": "Delivered our project ahead of schedule with code that was clean, well-tested, and easy for our team to maintain.",
                "img": "testimonials/sarah-connor.png",
            },
            {
                "name": "David Miller",
                "job": "Founder of StartupX",
                "text": "The strategic advice we received was instrumental in our platform's successful launch and subsequent scaling.",
                "img": "testimonials/david-miller.jpg",
            },
            {
                "name": "Emma Thompson",
                "job": "VP of Product at InnovateCorp",
                "text": "Outstanding technical leadership and an ability to communicate complex concepts clearly. Highly recommended for any enterprise project.",
                "img": "testimonials/emma-thompson.jpg",
            },
            {
                "name": "Marcus Johnson",
                "job": "CTO at CloudFirst",
                "text": "Their work on our cloud infrastructure transformation was transformative. They saved us both time and significant operational costs.",
                "img": "testimonials/marcus-johnson.jpg",
            },
            {
                "name": "Lisa Anderson",
                "job": "CEO at DesignHouse",
                "text": "Perfect balance of technical skill and creative thinking. They understood our vision and executed it flawlessly.",
                "img": "testimonials/lisa-anderson.jpg",
            },
            {
                "name": "Robert Taylor",
                "job": "Director at TechConsulting",
                "text": "A true problem solver who goes beyond expectations. Every interaction leaves us impressed with their professionalism and expertise.",
                "img": "testimonials/robert-taylor.jpg",
            },
        ]
        for data in test_data:
            img = self.get_or_create_image(data["img"])
            _, created = Testimonial.objects.update_or_create(
                name=data["name"],
                defaults={"job_title": data["job"], "text": data["text"], "image": img, "is_active": True},
            )
            if created:
                self.created_count += 1
            else:
                self.updated_count += 1

        # 5. Clients
        # Use random logos from the project's static images directory
        clients_images_dir = Path(settings.BASE_DIR) / "assets" / "static" / "images" / "clients"
        image_candidates = []
        if clients_images_dir.exists() and clients_images_dir.is_dir():
            for p in clients_images_dir.iterdir():
                if p.is_file() and p.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"]:
                    image_candidates.append(p.name)

        if image_candidates:
            random.shuffle(image_candidates)
            # Prioritize SVG files
            svg_files = [f for f in image_candidates if f.lower().endswith('.svg')]
            non_svg_files = [f for f in image_candidates if not f.lower().endswith('.svg')]
            sorted_candidates = svg_files + non_svg_files

            client_entries = [
                (
                    Path(filename).stem.replace("-", " ").replace("_", " ").title(),
                    filename,
                )
                for filename in sorted_candidates[:12]
            ]
        else:
            client_entries = [
                ("Global Systems", None),
                ("Innovative Soft", None),
                ("Future Tech", None),
                ("Cloud Nine", None),
                ("Eco Solutions", None),
                ("Neptune Innovations", None),
                ("Vertex Labs", None),
                ("Aurora Digital", None),
                ("Nexus Partners", None),
                ("Stellar Enterprises", None),
                ("Quantum Solutions", None),
                ("Prism Technologies", None),
            ]

        for name, chosen in client_entries:
            if chosen:
                img = self.get_or_create_image(f"clients/{chosen}")
            else:
                img = self.create_placeholder_image(name, width=200, height=80, style="default")

            if not img:
                self.log(f"Skipping client {name} - could not create image", "warning")
                Client.objects.filter(name=name).delete()
                continue

            defaults = {"logo": img, "is_active": True}
            _, created = Client.objects.update_or_create(name=name, defaults=defaults)
            if created:
                self.created_count += 1
            else:
                self.updated_count += 1

        # 6. Blog Tags
        blog_tags_data = [
            {"name": "Django", "category": "Technology", "color": "#092E20", "icon": "bi-django"},
            {"name": "React", "category": "Technology", "color": "#61dafb", "icon": "bi-react"},
            {"name": "Python", "category": "Technology", "color": "#3776ab", "icon": "bi-python"},
            {"name": "JavaScript", "category": "Technology", "color": "#f7df1e", "icon": "bi-code-square"},
            {"name": "TypeScript", "category": "Technology", "color": "#3178c6", "icon": "bi-code-square"},
            {"name": "Architecture", "category": "Design", "color": "#ee9b00", "icon": "bi-diagram-3"},
            {"name": "Performance", "category": "Design", "color": "#e63946", "icon": "bi-speedometer2"},
            {"name": "DevOps", "category": "Workflow", "color": "#2496ed", "icon": "bi-gear-wide-connected"},
            {"name": "Security", "category": "Technology", "color": "#ffb703", "icon": "bi-shield-lock"},
            {"name": "UX", "category": "Design", "color": "#8d99ae", "icon": "bi-ui-checks"},
            {"name": "Testing", "category": "Workflow", "color": "#06d6a0", "icon": "bi-check-circle"},
            {"name": "API", "category": "Technology", "color": "#118ab2", "icon": "bi-box-arrow-in-right"},
            {"name": "Database", "category": "Technology", "color": "#073b4c", "icon": "bi-database"},
            {"name": "Cloud", "category": "Infrastructure", "color": "#ff6b6b", "icon": "bi-cloud"},
            {"name": "Docker", "category": "Infrastructure", "color": "#2496ed", "icon": "bi-box"},
            {"name": "Kubernetes", "category": "Infrastructure", "color": "#326ce5", "icon": "bi-diagram-2"},
        ]
        # Keep track of active blog tags for later use
        for data in blog_tags_data:
            is_active = random.choice([True, False])
            _, created = BlogTag.objects.update_or_create(
                name=data["name"],
                defaults={
                    "category": data["category"],
                    "color": data["color"],
                    "icon": data["icon"],
                    "is_active": is_active,
                },
            )
            if is_active:
                self.active_blog_tags.append(data["name"])
            if created:
                self.created_count += 1
            else:
                self.updated_count += 1

        self.log(f"Active blog tags: {self.active_blog_tags}", "info")

    def populate_pages(self):
        """Set up the Wagtail page tree."""
        self.log("Populating page hierarchy...")
        from wagtail.models import Page  # noqa: F811

        Page.fix_tree()

        # 1. Locale Configuration - Ensure English locale exists first
        en_locale, en_created = Locale.objects.get_or_create(language_code="en")
        if en_created:
            self.log("Created English locale", "success")
            self.created_count += 1
        else:
            self.log("English locale already exists", "info")

        # 2. HomePage - This must be the root page in Wagtail
        home = HomePage.objects.filter(locale=en_locale).first()

        if not home:
            # Create HomePage with locale set from the start
            home = HomePage(
                title="Professional Portfolio",
                slug="home",
                locale=en_locale
            )

            # Check if there's an existing root page
            try:
                root = Page.get_first_root_node()
                if root and root.id != home.id:
                    # Delete the default root page if it exists and is not our HomePage
                    if not hasattr(root, 'specific_class') or root.specific_class != HomePage:
                        root.delete()

                # Add as root if no root exists
                if not Page.objects.filter(depth=1).exists():
                    home = Page.add_root(instance=home)
                    self.log("HomePage created as root page", "info")
                else:
                    # If root already exists, add as child
                    root = Page.get_first_root_node()
                    home = root.add_child(instance=home)
                    self.log("HomePage added as child of root", "info")

            except Exception as e:
                self.log(f"Error adding HomePage: {type(e).__name__}: {e}", "warning")
                # As last resort, try to create as root
                try:
                    # Remove any existing HomePage instances
                    HomePage.objects.filter(locale=en_locale).exclude(id=home.id).delete()
                    home = Page.add_root(instance=home)
                    self.log("HomePage created as root page (fallback)", "info")
                except Exception as e2:
                    self.log(f"Critical error creating HomePage: {type(e2).__name__}: {e2}", "error")
                    raise

            self.created_count += 1

        # Link snippets to home
        home.slider = [("slider_item", s) for s in Slider.objects.all()]
        home.services = [("service", s) for s in Service.objects.all()[:6]]
        home.save()
        self.log("HomePage saved with snippets", "success")

        # 3. Site Configuration with English as default locale
        site = Site.objects.first()
        if not site:
            site = Site.objects.create(hostname="localhost", root_page=home, is_default_site=True)
            self.created_count += 1
            self.log("Site created with HomePage as root", "success")
        else:
            site.root_page = home
            site.save()
            self.log("Site updated with HomePage as root", "success")

        # VResume Settings
        settings_obj, created = VResumeSettings.objects.get_or_create(site=site)
        settings_obj.full_name = "Mahmoud Al-Rashid"
        settings_obj.job_title = "Lead Software Architect"
        settings_obj.email = "mahmoud@example.com"
        settings_obj.location = "San Francisco, CA"
        settings_obj.phone = "+1 (555) 123-4567"
        settings_obj.birthday = timezone.now().replace(year=1990, month=6, day=15).date()
        settings_obj.map_embed_url = "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3153.0188813876143!2d-122.41941592346948!3d37.77492907123017!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x8085809c6c8f47b5%3A0xb10ed6d9b5641200!2sSan%20Francisco%2C%20CA!5e0!3m2!1sen!2sus!4v1234567890"
        settings_obj.facebook_url = "https://facebook.com/mahmoud"
        settings_obj.twitter_url = "https://twitter.com/mahmoud_dev"
        settings_obj.linkedin_url = "https://linkedin.com/in/mahmoud-rashid"
        settings_obj.github_url = "https://github.com/mammhoud"
        settings_obj.instagram_url = "https://instagram.com/mahmoud.dev"

        avatar_img = self.get_or_create_image("avatar/01.jpg", "Profile Avatar")
        if avatar_img:
            settings_obj.avatar = avatar_img
        logo_img = self.get_or_create_image("ui/logo.svg", "VResume Logo")
        if not logo_img:
            logo_img = self.create_placeholder_image("VResume Logo", width=200, height=50, style="default")
        if logo_img:
            settings_obj.logo = logo_img
        favicon_img = self.get_or_create_image("ui/favicon.svg", "VResume Favicon")
        if not favicon_img:
            favicon_img = self.create_placeholder_image("VResume Favicon", width=32, height=32, style="default")
        if favicon_img:
            settings_obj.favicon = favicon_img
        settings_obj.save()
        if created:
            self.created_count += 1
        else:
            self.updated_count += 1

        # 3. About Page
        about = AboutPage.objects.filter(locale=en_locale).first()
        if not about:
            about = AboutPage(title="About Me", slug="about", locale=en_locale)
            try:
                about = home.add_child(instance=about)
                self.log("AboutPage created as child of home", "info")
            except Exception as e:
                self.log(f"Error adding AboutPage as child: {type(e).__name__}: {e}", "warning")
            self.created_count += 1

        about.bio = [
            (
                "bio_text",
                "<p>I am a dedicated software professional with over a decade of experience in building scalable systems and intuitive user interfaces. My journey in technology has been driven by a passion for clean architecture and robust engineering practices.</p><p>Throughout my career, I've had the privilege of working with diverse teams to solve complex problems and deliver high-impact digital solutions.</p>",
            )
        ]
        about.team = [("team_member", tm) for tm in TeamMember.objects.all()]
        about.testimonials = [("testimonial", t) for t in Testimonial.objects.all()]
        about.clients = [("client", c) for c in Client.objects.all()]
        about.save()

        # 4. Resume Page
        resume = ResumePage.objects.filter(locale=en_locale).first()
        if not resume:
            resume = ResumePage(title="Experience", slug="resume", locale=en_locale)
            try:
                resume = home.add_child(instance=resume)
            except Exception as e:
                self.log(f"Error adding ResumePage as child: {type(e).__name__}: {e}", "warning")
            self.created_count += 1

        resume.education = [
            (
                "timeline_item",
                {
                    "title": "M.Sc. in Computer Science",
                    "subtitle": "Stanford University",
                    "date": "2015 - 2017",
                    "description": "Focused on distributed systems, machine learning, and advanced software architecture.",
                },
            ),
            (
                "timeline_item",
                {
                    "title": "B.Sc. in Software Engineering",
                    "subtitle": "MIT",
                    "date": "2011 - 2015",
                    "description": "Foundation in algorithmic thinking, data structures, and systems programming.",
                },
            ),
            (
                "timeline_item",
                {
                    "title": "Certified AWS Solutions Architect",
                    "subtitle": "Amazon Web Services",
                    "date": "2019",
                    "description": "Professional certification for designing and deploying scalable systems on AWS.",
                },
            ),
        ]
        resume.experience = [
            (
                "timeline_item",
                {
                    "title": "Principal Architect",
                    "subtitle": "Tech Giants Corp",
                    "date": "2021 - Present",
                    "description": "Leading the transition to a global microservices architecture, improving overall system availability to 99.99%.",
                },
            ),
            (
                "timeline_item",
                {
                    "title": "Senior Software Engineer",
                    "subtitle": "Cloud Solutions Ltd",
                    "date": "2018 - 2021",
                    "description": "Developed core backend services using Python and Go, handling over 1 million concurrent requests per minute.",
                },
            ),
            (
                "timeline_item",
                {
                    "title": "Full-Stack Developer",
                    "subtitle": "Innovate Software",
                    "date": "2015 - 2018",
                    "description": "Designed and implemented responsive web applications using React and Django for various enterprise clients.",
                },
            ),
        ]
        resume.skills = [
            ("skill", {"name": "Python / Django", "category": "language", "level": 95}),
            ("skill", {"name": "JavaScript / React", "category": "language", "level": 90}),
            ("skill", {"name": "Go (Golang)", "category": "language", "level": 82}),
            ("skill", {"name": "PostgreSQL / Redis", "category": "tool", "level": 88}),
            ("skill", {"name": "AWS / Azure", "category": "tool", "level": 85}),
            ("skill", {"name": "Docker / Kubernetes", "category": "tool", "level": 80}),
            ("skill", {"name": "System Design", "category": "other", "level": 92}),
            ("skill", {"name": "Agile Methodology", "category": "other", "level": 95}),
            ("skill", {"name": "Team Leadership", "category": "other", "level": 85}),
            ("skill", {"name": "API Strategy", "category": "other", "level": 88}),
            ("skill", {"name": "Security Review", "category": "other", "level": 90}),
        ]
        resume.save()

        # 5. Portfolio Page
        portfolio = PortfolioPage.objects.filter(locale=en_locale).first()
        if not portfolio:
            portfolio = PortfolioPage(title="My Works", slug="portfolio", locale=en_locale)
            try:
                portfolio = home.add_child(instance=portfolio)
            except Exception as e:
                self.log(f"Error adding PortfolioPage as child: {type(e).__name__}: {e}", "warning")
            self.created_count += 1

        # Tags and Projects
        tags_data = [
            ("Python", "bi-code-slash"),
            ("React", "bi-window"),
            ("Django", "bi-diagram-3"),
            ("Cloud", "bi-cloud"),
            ("Design", "bi-palette"),
            ("Mobile", "bi-phone"),
            ("AI", "bi-brain"),
            ("Security", "bi-shield-lock"),
            ("DevOps", "bi-gear-wide-connected"),
            ("API", "bi-box-arrow-in-right"),
            ("Database", "bi-database"),
            ("Docker", "bi-box"),
            ("Kubernetes", "bi-diagram-2"),
            ("Testing", "bi-check-circle"),
            ("Performance", "bi-speedometer2"),
        ]
        # Keep track of active portfolio tags for later use
        for name, icon in tags_data:
            is_active = random.choice([True, False])
            PortfolioTag.objects.update_or_create(
                name=name, defaults={"slug": name.lower(), "icon": icon, "is_active": is_active}
            )
            if is_active:
                self.active_portfolio_tags.append(name)

        self.log(f"Active portfolio tags: {self.active_portfolio_tags}", "info")

        # Projects
        projects_data = [
            {
                "title": "Enterprise CMS Platform",
                "cat": "Web App",
                "desc": "A custom Wagtail-based CMS solution for large-scale enterprise content management.",
                "tools": "Python, Django, Wagtail, PostgreSQL, AWS",
                "img": "listing/02.jpg",
                "tags": ["Python", "React", "Cloud"],
            },
            {
                "title": "Real-time Analytics Dashboard",
                "cat": "Data Viz",
                "desc": "A high-performance monitoring system for distributed IoT infrastructure.",
                "tools": "React, D3.js, Python, FastAPI, Redis",
                "img": "listing/06.jpg",
                "tags": ["React", "Cloud", "Design"],
            },
            {
                "title": "FinTech Mobile Wallet",
                "cat": "Mobile App",
                "desc": "Secure and intuitive mobile application for personal finance management.",
                "tools": "React Native, Node.js, MongoDB, Stripe API",
                "img": "listing/02.jpg",
                "tags": ["Mobile", "Python", "Cloud"],
            },
            {
                "title": "E-commerce Optimization Engine",
                "cat": "AI/ML",
                "desc": "Machine learning driven recommendation engine for an international retail platform.",
                "tools": "Python, TensorFlow, Scikit-learn",
                "img": "listing/01.jpg",
                "tags": ["Python", "Design"],
            },
            {
                "title": "Cloud Migration Framework",
                "cat": "DevOps",
                "desc": "Automated tools and processes for migrating legacy monolithic applications.",
                "tools": "Terraform, Ansible, Docker, Kubernetes",
                "img": "listing/05.jpg",
                "tags": ["Cloud"],
            },
            {
                "title": "Healthcare Management System",
                "cat": "HealthTech",
                "desc": "Comprehensive EHR and appointment scheduling system.",
                "tools": "Java, Spring Boot, MySQL, Angular",
                "img": "listing/03.jpg",
                "tags": ["React", "Mobile"],
            },
            {
                "title": "AI-Powered Content Recommendation",
                "cat": "SaaS",
                "desc": "A personalized recommendation engine that increases user engagement by surfacing relevant content automatically.",
                "tools": "Python, PyTorch, Redis, Kubernetes",
                "img": "listing/04.jpg",
                "tags": ["AI", "Cloud"],
            },
            {
                "title": "Enterprise Collaboration Suite",
                "cat": "Productivity",
                "desc": "A secure internal platform for team collaboration, document sharing, and workflow automation.",
                "tools": "React, Django, PostgreSQL, Docker",
                "img": "listing/07.jpg",
                "tags": ["React", "Security"],
            },
            {
                "title": "Blockchain Payment Gateway",
                "cat": "Fintech",
                "desc": "Decentralized payment system supporting multiple cryptocurrencies with advanced security protocols.",
                "tools": "Solidity, Web3.js, Node.js, AWS Lambda",
                "img": "listing/02.jpg",
                "tags": ["Security", "Cloud", "Python"],
            },
            {
                "title": "Video Streaming Platform",
                "cat": "Multimedia",
                "desc": "A global video streaming service with adaptive bitrate delivery and real-time analytics.",
                "tools": "React, FFmpeg, Nginx, Go",
                "img": "listing/06.jpg",
                "tags": ["Cloud", "Design"],
            },
            {
                "title": "IoT Device Management Platform",
                "cat": "IoT",
                "desc": "Central management system for controlling and monitoring thousands of IoT devices.",
                "tools": "Python, MQTT, PostgreSQL, Grafana",
                "img": "listing/02.jpg",
                "tags": ["Python", "Cloud", "Security"],
            },
            {
                "title": "Advanced Search Engine",
                "cat": "Search",
                "desc": "Custom search infrastructure with semantic understanding and natural language processing.",
                "tools": "Elasticsearch, Python, NLP, Machine Learning",
                "img": "listing/01.jpg",
                "tags": ["Python", "AI"],
            },
            {
                "title": "Microservices Migration Framework",
                "cat": "Architecture",
                "desc": "Toolkit and methodology for incrementally migrating monolithic applications to a microservices architecture with zero downtime.",
                "tools": "Go, Kubernetes, Docker, gRPC, Consul",
                "img": "listing/02.jpg",
                "tags": ["Cloud", "DevOps", "Kubernetes"],
            },
            {
                "title": "Real-time Fraud Detection System",
                "cat": "Security",
                "desc": "Machine learning powered fraud detection engine processing millions of transactions in real time.",
                "tools": "Python, Apache Kafka, Spark, TensorFlow",
                "img": "listing/07.jpg",
                "tags": ["Security", "AI", "Cloud"],
            },
            {
                "title": "Multi-Tenant SaaS Dashboard",
                "cat": "SaaS",
                "desc": "A white-label analytics dashboard supporting hundreds of tenants with isolated data storage and custom branding.",
                "tools": "React, Node.js, MongoDB, Redis",
                "img": "listing/06.jpg",
                "tags": ["React", "Cloud", "Design"],
            },
            {
                "title": "Cross-Platform Mobile E-Learning App",
                "cat": "Mobile App",
                "desc": "An interactive learning platform with offline support, progress tracking, and video streaming.",
                "tools": "Flutter, Python, GraphQL, Firebase",
                "img": "listing/03.jpg",
                "tags": ["Mobile", "Design", "Cloud"],
            },
        ]

        project_body = "<p>This project involved designing and implementing a robust system tailored to specific business needs. Key achievements include improving performance by 40% and delivering a seamless user experience across devices.</p><ul><li>Architected the core system from scratch</li><li>Implemented CI/CD pipelines for zero-downtime deployment</li><li>Collaborated with cross-functional teams to meet deadlines</li></ul>"

        for idx, data in enumerate(projects_data, 1):
            # Normalize listing images to numeric codes and use them for both
            # portfolio projects and (later) blog posts. This ensures unique
            # image filenames like listing/01.jpg, listing/02.jpg, ...
            listing_img = f"listing/{idx:02d}.jpg"
            img = self.get_or_create_image(listing_img, title=data["title"])

            # If image is None (placeholder created), use tech-themed style
            if img is None:
                # Extract tech keyword from tools
                tech_keyword = "tech"
                tools_lower = data["tools"].lower()
                if "python" in tools_lower or "django" in tools_lower:
                    tech_keyword = "python"
                elif "react" in tools_lower or "javascript" in tools_lower:
                    tech_keyword = "react"
                elif "cloud" in tools_lower or "aws" in tools_lower or "kubernetes" in tools_lower:
                    tech_keyword = "cloud"
                elif "design" in tools_lower or "ui" in tools_lower:
                    tech_keyword = "design"
                elif "mobile" in tools_lower or "react native" in tools_lower:
                    tech_keyword = "mobile"
                elif "ai" in tools_lower or "ml" in tools_lower or "tensor" in tools_lower:
                    tech_keyword = "ai"
                elif "security" in tools_lower or "encrypt" in tools_lower:
                    tech_keyword = "security"  # noqa: F841

                img = self.create_placeholder_image(data["title"], width=400, height=300, style="tech")

            project, created = Project.objects.update_or_create(
                title=data["title"],
                defaults={
                    "category": data["cat"],
                    "description": data["desc"],
                    "tools": data["tools"],
                    "body": project_body,
                    "image": img,
                    "slug": data["title"].lower().replace(" ", "-"),
                },
            )
            # Add tags - only use active tags
            if "tags" in data:
                for tag_name in data["tags"]:
                    # Only add tag if it's active
                    if tag_name in self.active_portfolio_tags:
                        tag = PortfolioTag.objects.get(name=tag_name)
                        project.tags.add(tag)

            if created:
                self.created_count += 1
            else:
                self.updated_count += 1
        portfolio.save()

        # 6. Blog Page
        blog = BlogPage.objects.filter(locale=en_locale).first()
        if not blog:
            blog = BlogPage(
                title="Insights",
                slug="blog",
                introduction="Thoughts and perspectives on software engineering, modern architecture, and the evolving landscape of web technology.",
                locale=en_locale,
            )
            try:
                blog = home.add_child(instance=blog)
                self.log(f"BlogPage created as child of home", "info")  # noqa: F541
            except Exception as e:
                self.log(f"Error adding BlogPage as child: {type(e).__name__}: {e}", "warning")
            self.created_count += 1
        blog.save()

        # Add page tags for the Blog page so the admin tag tab is populated
        page_tags = ["Django", "Architecture"]
        for tag_name in page_tags:
            try:
                tag = BlogTag.objects.get(name=tag_name)
                BlogPageTag.objects.get_or_create(
                    page=blog,
                    tag=tag,
                    defaults={"is_primary": tag_name == "Django"},
                )
            except BlogTag.DoesNotExist:
                self.log(f"Page tag not found: {tag_name}", "warning")

        # Add some blog posts as snippets
        from pages.blog.models.snippets.post import BlogPost

        posts_data = [
            {
                "title": "The Art of Clean Architecture in Django",
                "slug": "clean-architecture-django",
                "intro": "Exploring patterns for building maintainable and scalable Django applications beyond the standard MTV structure.",
                "featured": True,
                "tags": ["Django", "Architecture"],
            },
            {
                "title": "Scaling Distributed Systems: Lessons Learned",
                "slug": "scaling-distributed-systems",
                "intro": "Practical strategies and common pitfalls when handling millions of concurrent users in a distributed environment.",
                "featured": True,
                "tags": ["Architecture", "Performance"],
            },
            {
                "title": "Migrating to Wagtail: A Comprehensive Guide",
                "slug": "migrating-to-wagtail",
                "intro": "Why we chose Wagtail for our enterprise CMS needs and how we handled the migration process from legacy systems.",
                "featured": False,
                "tags": ["Django", "Architecture"],
            },
            {
                "title": "The Future of Web Performance: Core Web Vitals",
                "slug": "web-performance-future",
                "intro": "Understanding the impact of performance metrics on user experience and SEO in 2024 and beyond.",
                "featured": False,
                "tags": ["Performance", "Python"],
            },
            {
                "title": "Building Accessible UI Components with React",
                "slug": "accessible-react-ui",
                "intro": "Best practices for ensuring your web applications are inclusive and usable by everyone.",
                "featured": True,
                "tags": ["React", "Architecture"],
            },
            {
                "title": "Implementing Robust CI/CD with GitHub Actions",
                "slug": "robust-cicd-github-actions",
                "intro": "Automating your development workflow from commit to deployment with modern CI/CD patterns.",
                "featured": False,
                "tags": ["DevOps", "Performance"],
            },
            {
                "title": "Designing APIs for Third-Party Integration",
                "slug": "designing-apis-for-integration",
                "intro": "How to design resilient APIs that make integration with external systems reliable and secure.",
                "featured": False,
                "tags": ["Security", "Architecture"],
            },
            {
                "title": "Practical Security Hardenings for Django Apps",
                "slug": "security-hardenings-django",
                "intro": "A concise guide to hardening Django applications against common web threats.",
                "featured": True,
                "tags": ["Security", "Python"],
            },
            {
                "title": "Modern Frontend Patterns with HTMX and Alpine.js",
                "slug": "modern-frontend-htmx-alpine",
                "intro": "Moving beyond heavy SPA frameworks — a practical approach to building reactive interfaces with lightweight tools.",
                "featured": False,
                "tags": ["Architecture", "React"],
            },
            {
                "title": "Database Indexing Strategies for High-Traffic Apps",
                "slug": "database-indexing-strategies",
                "intro": "Optimizing PostgreSQL performance with smart indexing patterns and query analysis.",
                "featured": False,
                "tags": ["Database", "Performance"],
            },
            {
                "title": "Container Orchestration Patterns for Startups",
                "slug": "container-orchestration-startups",
                "intro": "When and how to adopt Docker and Kubernetes without over-engineering your infrastructure.",
                "featured": True,
                "tags": ["Docker", "Kubernetes"],
            },
            {
                "title": "Test-Driven Development in Python: A Practical Guide",
                "slug": "tdd-python-guide",
                "intro": "Building confidence in your codebase through disciplined testing practices.",
                "featured": False,
                "tags": ["Python", "Testing"],
            },
        ]
        for index, data in enumerate(posts_data, 1):
            # Use the same numeric listing images for blog posts so they
            # visually match the portfolio items. e.g. listing/01.jpg
            blog_image_file = f"listing/{index:02d}.jpg"
            img = self.get_or_create_image(blog_image_file, title=data["title"])
            post, created = BlogPost.objects.update_or_create(
                slug=data["slug"],
                defaults={
                    "title": data["title"],
                    "introduction": data["intro"],
                    "body": [
                        (
                            "paragraph",
                            "<p>Developing software is as much an art as it is a science. In this post, we dive deep into the technical nuances and professional considerations that define modern engineering excellence.</p><p>By adhering to proven patterns and maintaining a focus on quality, teams can build systems that not only meet today's requirements but are also prepared for tomorrow's challenges.</p>",
                        )
                    ],
                    "is_published": True,
                    "featured_image": img,
                    "published_date": timezone.now() - timedelta(days=random.randint(1, 30)),
                },
            )
            # Add tags - only use active tags
            if "tags" in data:
                for tag_name in data["tags"]:
                    # Only add tag if it's active
                    if tag_name in self.active_blog_tags:
                        tag = BlogTag.objects.get(name=tag_name)
                        post.tags.add(tag)

            if created:
                self.created_count += 1
            else:
                self.updated_count += 1

        # 7. Contact Page
        contact = ContactPage.objects.filter(locale=en_locale).first()
        if not contact:
            contact = ContactPage(
                title="Contact",
                slug="contact",
                form_title="Get in Touch",
                form_intro="Have a project in mind or want to discuss a collaborative opportunity? Feel free to reach out using the form below.",
                locale=en_locale,
            )
            try:
                contact = home.add_child(instance=contact)
            except Exception as e:
                self.log(f"Error adding ContactPage as child: {type(e).__name__}: {e}", "warning")
            self.created_count += 1
        contact.save()

    def populate_arabic_locale(self):
        """Create Arabic locale and translated pages."""
        self.log("Populating Arabic locale pages...")

        # 1. Ensure Arabic locale exists
        ar_locale, created = Locale.objects.get_or_create(language_code="ar")
        if created:
            self.log("Created Arabic locale", "success")
            self.created_count += 1

        # 2. Arabic HomePage
        from pages.home.models import HomePage

        en_home = HomePage.objects.filter(locale__language_code="en").first()
        ar_home = HomePage.objects.filter(locale=ar_locale).first()
        if not ar_home and en_home:
            try:
                ar_home = en_home.copy_for_translation(ar_locale)
                self.created_count += 1
            except Exception:
                ar_home = HomePage.objects.filter(locale=ar_locale).first()
        if ar_home:
            ar_home.title = "الملف المهني"
            # Wagtail handles translated slugs, don't force 'home' to avoid collisions
            ar_home.save()

        # 3. Arabic AboutPage
        from pages.about.models import AboutPage

        en_about = AboutPage.objects.filter(locale__language_code="en").first()
        ar_about = AboutPage.objects.filter(locale=ar_locale).first()
        if not ar_about and en_about:
            try:
                ar_about = en_about.copy_for_translation(ar_locale)
                self.created_count += 1
            except Exception:
                ar_about = AboutPage.objects.filter(locale=ar_locale).first()
        if ar_about:
            ar_about.title = "نبذة عنّي"
            ar_about.bio = [
                (
                    "bio_text",
                    "<p>أنا مهندس برمجيات متخصص يتمتع بأكثر من عشر سنوات من الخبرة في بناء أنظمة قابلة للتوسع وواجهات مستخدم بديهية. مسيرتي في عالم التكنولوجيا مدفوعة بشغف نحو الهندسة المعمارية النظيفة والممارسات الهندسية الرصينة.</p><p>على مدار مسيرتي المهنية، حظيت بشرف العمل مع فرق متنوعة لحل مشكلات معقدة وتقديم حلول رقمية عالية التأثير.</p>",
                )
            ]
            ar_about.save()

        # 4. Arabic ResumePage
        from pages.cv.models import ResumePage

        en_resume = ResumePage.objects.filter(locale__language_code="en").first()
        ar_resume = ResumePage.objects.filter(locale=ar_locale).first()
        if not ar_resume and en_resume:
            try:
                ar_resume = en_resume.copy_for_translation(ar_locale)
                self.created_count += 1
            except Exception:
                ar_resume = ResumePage.objects.filter(locale=ar_locale).first()
        if ar_resume:
            ar_resume.title = "السيرة الذاتية"
            ar_resume.education = [
                (
                    "timeline_item",
                    {
                        "title": "ماجستير علوم الحاسوب",
                        "subtitle": "جامعة ستانفورد",
                        "date": "٢٠١٥ - ٢٠١٧",
                        "description": "تركيز على الأنظمة الموزعة والتعلم الآلي وهندسة البرمجيات المتقدمة.",
                    },
                ),
                (
                    "timeline_item",
                    {
                        "title": "بكالوريوس هندسة البرمجيات",
                        "subtitle": "معهد ماساتشوستس للتكنولوجيا",
                        "date": "٢٠١١ - ٢٠١٥",
                        "description": "أساسيات التفكير الخوارزمي وهياكل البيانات وبرمجة الأنظمة.",
                    },
                ),
            ]
            ar_resume.experience = [
                (
                    "timeline_item",
                    {
                        "title": "كبير المهندسين المعماريين",
                        "subtitle": "شركة عمالقة التقنية",
                        "date": "٢٠٢١ - الحالي",
                        "description": "قيادة التحول نحو بنية خدمات مصغرة عالمية، مع تحسين توافر النظام إلى ٩٩.٩٩٪.",
                    },
                ),
                (
                    "timeline_item",
                    {
                        "title": "مهندس برمجيات أول",
                        "subtitle": "حلول السحابة المحدودة",
                        "date": "٢٠١٨ - ٢٠٢١",
                        "description": "تطوير خدمات خلفية أساسية باستخدام بايثون وغو، مع معالجة أكثر من مليون طلب متزامن في الدقيقة.",
                    },
                ),
            ]
            ar_resume.skills = [
                ("skill", {"name": "بايثون / جانغو", "category": "language", "level": 95}),
                ("skill", {"name": "جافاسكريبت / ريآكت", "category": "language", "level": 90}),
                ("skill", {"name": "تصميم الأنظمة", "category": "other", "level": 92}),
                ("skill", {"name": "قيادة الفريق", "category": "other", "level": 85}),
            ]
            ar_resume.save()

        # 5. Arabic PortfolioPage
        from pages.portfolio.models import PortfolioPage

        en_portfolio = PortfolioPage.objects.filter(locale__language_code="en").first()
        ar_portfolio = PortfolioPage.objects.filter(locale=ar_locale).first()
        if not ar_portfolio and en_portfolio:
            try:
                ar_portfolio = en_portfolio.copy_for_translation(ar_locale)
                self.created_count += 1
            except Exception:
                ar_portfolio = PortfolioPage.objects.filter(locale=ar_locale).first()
        if ar_portfolio:
            ar_portfolio.title = "أعمالي"
            ar_portfolio.save()

        # 6. Arabic BlogPage
        from pages.blog.models import BlogPage

        en_blog = BlogPage.objects.filter(locale__language_code="en", depth__lte=3).first()
        ar_blog = BlogPage.objects.filter(locale=ar_locale, depth__lte=3).first()
        if not ar_blog and en_blog:
            try:
                ar_blog = en_blog.copy_for_translation(ar_locale)
                self.created_count += 1
            except Exception:
                ar_blog = BlogPage.objects.filter(locale=ar_locale).first()
        if ar_blog:
            ar_blog.title = "المدوّنة"
            ar_blog.introduction = (
                "أفكار ورؤى حول هندسة البرمجيات والبنية الحديثة والمشهد التقني المتطور."
            )
            ar_blog.save()

        # 7. Arabic ContactPage
        from pages.connect.models import ContactPage

        en_contact = ContactPage.objects.filter(locale__language_code="en").first()
        ar_contact = ContactPage.objects.filter(locale=ar_locale).first()
        if not ar_contact and en_contact:
            try:
                ar_contact = en_contact.copy_for_translation(ar_locale)
                self.created_count += 1
            except Exception:
                ar_contact = ContactPage.objects.filter(locale=ar_locale).first()
        if ar_contact:
            ar_contact.title = "تواصل معي"
            ar_contact.form_title = "ابقَ على تواصل"
            ar_contact.form_intro = "هل لديك مشروع في ذهنك أو تريد مناقشة فرصة تعاون؟ لا تتردد في التواصل عبر النموذج أدناه."
            ar_contact.save()

        # Translate Portfolio Tags
        from pages.portfolio.models import PortfolioTag

        for tag in PortfolioTag.objects.all():
            if tag.name == "Python":
                tag.name_ar = "بايثون"
            elif tag.name == "React":
                tag.name_ar = "ريآكت"
            elif tag.name == "Cloud":
                tag.name_ar = "سحابية"
            elif tag.name == "Design":
                tag.name_ar = "تصميم"
            elif tag.name == "Mobile":
                tag.name_ar = "تطبيقات هواتف"
            # Since tag is a simple model without locale logic by default, we just keep it as is,
            # or if it supports translation we'd translate it. Since we don't know the exact
            # fields of PortfolioTag for translation, we'll try saving translated names if possible,
            # but usually tags are language agnostic or need wagtail-localize. We'll skip forcing
            # tag translations unless there is a specific field. We'll just leave it.

        self.log("Arabic locale pages populated successfully.", "success")

    def create_superuser(self):
        """Create a superuser using .env variables."""
        self.log("Checking superuser...")

        # Load from environ, which Dynaconf or python-dotenv would have populated
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not username or not email or not password:
            self.log("Superuser variables not fully set in environment. Skipping.", "warning")
            return

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username, email, password)
            self.log(f"Superuser '{username}' created successfully.", "success")
        else:
            self.log(f"Superuser '{username}' already exists.", "info")

    def run(self):
        self.log("Starting unified data population...", "success")
        try:
            self.create_superuser()
            self.populate_snippets()
            self.populate_pages()
            self.populate_arabic_locale()
            self.log(
                f"Done! Created/Updated {self.created_count + self.updated_count} items.", "success"
            )
        except Exception as e:
            self.log(f"Population failed: {e}", "error")
            if self.verbose:
                import traceback

                traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    populator = DataPopulator(verbose=args.verbose)
    populator.run()
