# Generated migration for www.content app.
"""Initial migration — ~26 content models (snippets, pages, settings)."""

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
import wagtail.fields
import wagtail.search.index


class Migration(migrations.Migration):
    """Creates all www.content models.

    Dependencies on external apps:
        wagtailcore, wagtailimages, wagtail.contrib.settings, contenttypes, auth.
    """

    initial = True

    dependencies = [
        ("wagtailcore", "0094_alter_page_locale"),       # Latest Wagtail 5.x page migration
        ("wagtailimages", "0025_alter_image_file_alter_rendition_file"),
        ("wagtailcontrib_settings", "__first__"),         # BaseSiteSetting table
        ("contenttypes", "0002_remove_content_type_name"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # ───────────────────────────────────────────────────────────────
        # 1. CourseCategory (no FKs — referenced by Course below)
        # ───────────────────────────────────────────────────────────────
        migrations.CreateModel(
            name="CourseCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True)),
                ("slug", models.SlugField(max_length=100, unique=True)),
                ("icon", models.CharField(blank=True, default="", max_length=100)),
                ("description", models.TextField(blank=True, default="")),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("sort_order", models.IntegerField(default=0)),
            ],
            options={"verbose_name": "course category", "verbose_name_plural": "course categories", "ordering": ["sort_order", "name"], "app_label": "content"},
        ),

        # ───────────────────────────────────────────────────────────────
        # 2. Token (FK to AUTH_USER_MODEL)
        # ───────────────────────────────────────────────────────────────
        migrations.CreateModel(
            name="Token",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("token_hash", models.CharField(db_index=True, max_length=64, unique=True)),
                ("key_prefix", models.CharField(max_length=8, help_text="First 8 chars of raw token for display")),
                ("token_type", models.CharField(choices=[("access", "Access"), ("api", "API"), ("sync", "Sync"), ("refresh", "Refresh")], db_index=True, default="access", max_length=10)),
                ("category", models.CharField(blank=True, db_index=True, default="", help_text="Freeform grouping label", max_length=50)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("last_used_at", models.DateTimeField(blank=True, null=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="auth_tokens", to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "token", "verbose_name_plural": "tokens", "ordering": ["-created_at"], "app_label": "content"},
        ),
        migrations.AddIndex(
            model_name="Token",
            index=models.Index(fields=["token_hash"], name="content_tok_token_h_eea4c4_idx"),
        ),
        migrations.AddIndex(
            model_name="Token",
            index=models.Index(fields=["user", "token_type", "created_at"], name="content_tok_user_id_7aac0e_idx"),
        ),

        # ───────────────────────────────────────────────────────────────
        # 3. DataToken (FK → Token, GFK → contenttypes)
        # ───────────────────────────────────────────────────────────────
        migrations.CreateModel(
            name="DataToken",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("object_id", models.PositiveIntegerField()),
                ("snapshot", models.JSONField(blank=True, default=dict, help_text="Optional serialized snapshot for offline sync replay")),
                ("is_sync", models.BooleanField(db_index=True, default=False, help_text="Whether this data has been synced")),
                ("synced_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("content_type", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="contenttypes.ContentType")),
                ("token", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="data_tokens", to="content.Token")),
            ],
            options={"verbose_name": "data token", "verbose_name_plural": "data tokens", "ordering": ["-created_at"], "app_label": "content"},
        ),
        migrations.AddIndex(
            model_name="DataToken",
            index=models.Index(fields=["token", "is_sync"], name="content_dat_token_i_30ecde_idx"),
        ),
        migrations.AddIndex(
            model_name="DataToken",
            index=models.Index(fields=["content_type", "object_id"], name="content_dat_content_ddf0d4_idx"),
        ),

        # ───────────────────────────────────────────────────────────────
        # 4. TeamMember (snippet, FK → wagtailimages.Image)
        # ───────────────────────────────────────────────────────────────
        migrations.CreateModel(
            name="TeamMember",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("title", models.CharField(blank=True, default="", max_length=200)),
                ("bio", models.TextField(blank=True, default="")),
                ("email", models.EmailField(blank=True, default="", max_length=254)),
                ("social_links", models.JSONField(blank=True, default=dict, help_text='{"twitter": "...", "linkedin": "...", "github": "..."}')),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("sort_order", models.IntegerField(default=0)),
                ("photo", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="+", to="wagtailimages.Image")),
            ],
            options={"verbose_name": "team member", "verbose_name_plural": "team members", "ordering": ["sort_order", "name"], "app_label": "content"},
            bases=(wagtail.search.index.Indexed, models.Model),
        ),

        # ───────────────────────────────────────────────────────────────
        # 5. ContactSubmission (no FKs)
        # ───────────────────────────────────────────────────────────────
        migrations.CreateModel(
            name="ContactSubmission",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("email", models.EmailField(max_length=254)),
                ("subject", models.CharField(max_length=300)),
                ("message", models.TextField()),
                ("is_read", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"verbose_name": "contact submission", "verbose_name_plural": "contact submissions", "ordering": ["-created_at"], "app_label": "content"},
        ),

        # ───────────────────────────────────────────────────────────────
        # 6. SocialLink (snippet, no FKs)
        # ───────────────────────────────────────────────────────────────
        migrations.CreateModel(
            name="SocialLink",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("platform", models.CharField(choices=[("facebook", "Facebook"), ("twitter", "Twitter / X"), ("instagram", "Instagram"), ("linkedin", "LinkedIn"), ("youtube", "YouTube"), ("whatsapp", "WhatsApp"), ("tiktok", "TikTok"), ("github", "GitHub"), ("discord", "Discord"), ("other", "Other")], default="facebook", max_length=20)),
                ("label", models.CharField(blank=True, default="", help_text="Display name (e.g., 'Follow us on Facebook')", max_length=100)),
                ("url", models.URLField(max_length=300)),
                ("icon_svg", models.CharField(blank=True, default="", help_text="Path to SVG icon (e.g., '/assets/img/icons/facebook.svg')", max_length=200)),
                ("icon_class", models.CharField(blank=True, default="", help_text="CSS class for icon font (e.g., 'fab fa-facebook')", max_length=100)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("sort_order", models.IntegerField(default=0)),
            ],
            options={"verbose_name": "social link", "verbose_name_plural": "social links", "ordering": ["sort_order", "platform"], "app_label": "content"},
        ),

        # ───────────────────────────────────────────────────────────────
        # 7. Feature (snippet, FK → wagtailimages.Image)
        # ───────────────────────────────────────────────────────────────
        migrations.CreateModel(
            name="Feature",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("page", models.CharField(default="home_1", help_text="Which home page version this feature belongs to", max_length=50)),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True, default="")),
                ("icon_class", models.CharField(blank=True, default="", max_length=100)),
                ("sort_order", models.IntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("icon", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="wagtailimages.Image")),
            ],
            options={"verbose_name": "feature", "verbose_name_plural": "features", "ordering": ["page", "sort_order"], "app_label": "content"},
        ),

        # ───────────────────────────────────────────────────────────────
        # 8. Instructor (snippet, FK → wagtailimages.Image)
        # ───────────────────────────────────────────────────────────────
        migrations.CreateModel(
            name="Instructor",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("designation", models.CharField(blank=True, default="", max_length=200)),
                ("bio", models.TextField(blank=True, default="")),
                ("rating", models.DecimalField(decimal_places=1, default=0, max_digits=3)),
                ("course_count", models.IntegerField(default=0)),
                ("student_count", models.IntegerField(default=0)),
                ("social_links", models.JSONField(blank=True, default=dict)),
                ("sort_order", models.IntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("avatar", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="wagtailimages.Image")),
            ],
            options={"verbose_name": "instructor", "verbose_name_plural": "instructors", "ordering": ["sort_order"], "app_label": "content"},
        ),

        # ───────────────────────────────────────────────────────────────
        # 9. Faq (snippet, no FKs)
        # ───────────────────────────────────────────────────────────────
        migrations.CreateModel(
            name="Faq",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("page", models.CharField(default="home_1", help_text="Which home page version this FAQ belongs to", max_length=50)),
                ("question", models.TextField()),
                ("answer", models.TextField()),
                ("sort_order", models.IntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"verbose_name": "FAQ", "verbose_name_plural": "FAQs", "ordering": ["page", "sort_order"], "app_label": "content"},
        ),

        # ───────────────────────────────────────────────────────────────
        # 10. DashboardCounter (snippet, no FKs)
        # ───────────────────────────────────────────────────────────────
        migrations.CreateModel(
            name="DashboardCounter",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("label", models.CharField(max_length=200)),
                ("value", models.IntegerField(default=0)),
                ("icon_class", models.CharField(blank=True, default="", max_length=100)),
                ("prefix", models.CharField(blank=True, default="", max_length=20)),
                ("suffix", models.CharField(blank=True, default="", max_length=20)),
                ("sort_order", models.IntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"verbose_name": "dashboard counter", "verbose_name_plural": "dashboard counters", "ordering": ["sort_order"], "app_label": "content"},
        ),

        # ───────────────────────────────────────────────────────────────
        # 11. ShopProduct (snippet, FK → wagtailimages.Image)
        # ───────────────────────────────────────────────────────────────
        migrations.CreateModel(
            name="ShopProduct",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("slug", models.SlugField(blank=True, max_length=200, unique=True)),
                ("description", models.TextField(blank=True, default="")),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("sale_price", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ("category", models.CharField(blank=True, default="", max_length=100)),
                ("rating", models.DecimalField(decimal_places=1, default=0, max_digits=3)),
                ("stock_status", models.CharField(choices=[("in_stock", "In Stock"), ("out_of_stock", "Out of Stock"), ("coming_soon", "Coming Soon")], default="in_stock", max_length=20)),
                ("is_active", models.BooleanField(default=True)),
                ("image", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="wagtailimages.Image")),
            ],
            options={"verbose_name": "shop product", "verbose_name_plural": "shop products", "ordering": ["title"], "app_label": "content"},
        ),

        # ───────────────────────────────────────────────────────────────
        # 12. MenuItem (snippet, FK → self)
        # ───────────────────────────────────────────────────────────────
        migrations.CreateModel(
            name="MenuItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("link", models.CharField(blank=True, default="#", max_length=500)),
                ("menu_class", models.CharField(blank=True, default="", help_text="CSS class for mega-menu container", max_length=100)),
                ("badge", models.CharField(blank=True, default="", help_text="Badge text like 'Hot' or 'New'", max_length=100)),
                ("badge_class", models.CharField(blank=True, default="", help_text="Badge color variant like 'tg-badge'", max_length=100)),
                ("icon", models.CharField(blank=True, default="", max_length=100)),
                ("sort_order", models.IntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("parent", models.ForeignKey(blank=True, help_text="Parent menu item for nested menus", null=True, on_delete=django.db.models.deletion.CASCADE, related_name="children", to="content.MenuItem")),
            ],
            options={"verbose_name": "menu item", "verbose_name_plural": "menu items", "ordering": ["sort_order"], "app_label": "content"},
        ),

        # ───────────────────────────────────────────────────────────────
        # 13. BlogPost (snippet, FK → wagtailimages.Image)
        # ───────────────────────────────────────────────────────────────
        migrations.CreateModel(
            name="BlogPost",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=300)),
                ("slug", models.SlugField(max_length=300, unique=True)),
                ("excerpt", models.TextField(blank=True, default="")),
                ("content", models.TextField(blank=True, default="")),
                ("author", models.CharField(blank=True, default="", max_length=200)),
                ("category", models.JSONField(blank=True, default=dict)),
                ("published_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("is_published", models.BooleanField(db_index=True, default=True)),
                ("featured_image", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="+", to="wagtailimages.Image")),
            ],
            options={"verbose_name": "blog post", "verbose_name_plural": "blog posts", "ordering": ["-published_at"], "app_label": "content"},
            bases=(wagtail.search.index.Indexed, models.Model),
        ),

        # ───────────────────────────────────────────────────────────────
        # 14. Event (snippet, FK → wagtailimages.Image)
        # ───────────────────────────────────────────────────────────────
        migrations.CreateModel(
            name="Event",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=300)),
                ("slug", models.SlugField(max_length=300, unique=True)),
                ("description", models.TextField(blank=True, default="")),
                ("location", models.CharField(blank=True, default="", max_length=300)),
                ("event_date", models.DateTimeField(blank=True, null=True)),
                ("is_published", models.BooleanField(db_index=True, default=True)),
                ("image", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="+", to="wagtailimages.Image")),
            ],
            options={"verbose_name": "event", "verbose_name_plural": "events", "ordering": ["event_date"], "app_label": "content"},
            bases=(wagtail.search.index.Indexed, models.Model),
        ),

        # ───────────────────────────────────────────────────────────────
        # 15. Testimonial (snippet, FK → wagtailimages.Image)
        # ───────────────────────────────────────────────────────────────
        migrations.CreateModel(
            name="Testimonial",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("designation", models.CharField(blank=True, default="", max_length=200)),
                ("quote", models.TextField(blank=True, default="")),
                ("rating", models.DecimalField(decimal_places=1, default=0, max_digits=3)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("sort_order", models.IntegerField(default=0)),
                ("avatar", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="+", to="wagtailimages.Image")),
            ],
            options={"verbose_name": "testimonial", "verbose_name_plural": "testimonials", "ordering": ["sort_order"], "app_label": "content"},
        ),

        # ───────────────────────────────────────────────────────────────
        # 16. PublicationCategory (snippet, no FKs)
        # ───────────────────────────────────────────────────────────────
        migrations.CreateModel(
            name="PublicationCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True)),
                ("slug", models.SlugField(max_length=100, unique=True)),
                ("description", models.TextField(blank=True, default="")),
                ("sort_order", models.IntegerField(default=0)),
            ],
            options={"verbose_name": "publication category", "verbose_name_plural": "publication categories", "ordering": ["sort_order", "name"], "app_label": "content"},
        ),

        # ───────────────────────────────────────────────────────────────
        # 17. Publication (snippet, FK → PublicationCategory)
        # ───────────────────────────────────────────────────────────────
        migrations.CreateModel(
            name="Publication",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=500)),
                ("slug", models.SlugField(max_length=500, unique=True)),
                ("abstract", wagtail.fields.RichTextField(blank=True, default="")),
                ("authors", models.CharField(blank=True, default="", max_length=500)),
                ("published_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("is_published", models.BooleanField(db_index=True, default=True)),
                ("external_url", models.URLField(blank=True, default="")),
                ("category", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="publications", to="content.PublicationCategory")),
            ],
            options={"verbose_name": "publication", "verbose_name_plural": "publications", "ordering": ["-published_at"], "app_label": "content"},
            bases=(wagtail.search.index.Indexed, models.Model),
        ),

        # ───────────────────────────────────────────────────────────────
        # 18. Course (snippet, FK → CourseCategory)
        # ───────────────────────────────────────────────────────────────
        migrations.CreateModel(
            name="Course",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=300)),
                ("slug", models.SlugField(max_length=300, unique=True)),
                ("description", wagtail.fields.RichTextField(blank=True, default="")),
                ("short_description", models.CharField(blank=True, default="", max_length=255)),
                ("skill_level", models.CharField(choices=[("beginner", "Beginner"), ("intermediate", "Intermediate"), ("advanced", "Advanced"), ("all_levels", "All Levels")], default="beginner", max_length=20)),
                ("language", models.CharField(default="English", max_length=50)),
                ("price", models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ("rating", models.DecimalField(decimal_places=1, default=0, max_digits=3)),
                ("instructor", models.CharField(blank=True, default="", max_length=200)),
                ("duration", models.CharField(blank=True, default="", max_length=50)),
                ("enrolled_count", models.IntegerField(default=0)),
                ("is_published", models.BooleanField(db_index=True, default=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("category", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="courses", to="content.CourseCategory")),
            ],
            options={"verbose_name": "course", "verbose_name_plural": "courses", "ordering": ["-created_at"], "app_label": "content"},
            bases=(wagtail.search.index.Indexed, models.Model),
        ),

        # ───────────────────────────────────────────────────────────────
        # 19. SiteSettings (BaseSiteSetting + ClusterableModel)
        # ───────────────────────────────────────────────────────────────
        migrations.CreateModel(
            name="SiteSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("site_name", models.CharField(default="TharaaEdu", help_text="Site name displayed in footer/titles", max_length=200)),
                ("site_tagline", models.CharField(blank=True, default="", help_text="Short tagline", max_length=300)),
                ("footer_description", models.TextField(blank=True, default="", help_text="Company description in footer")),
                ("footer_address", models.CharField(blank=True, default="", help_text="Physical address", max_length=300)),
                ("footer_phone", models.CharField(blank=True, default="", help_text="Contact phone number", max_length=50)),
                ("footer_email", models.EmailField(blank=True, default="", help_text="Contact email", max_length=254)),
                ("footer_copyright", models.CharField(default="\u00a9 2025 TharaaEdu. All rights reserved.", help_text="Copyright text in footer bottom", max_length=200)),
                ("google_play_url", models.URLField(blank=True, default="", help_text="Google Play store link")),
                ("apple_store_url", models.URLField(blank=True, default="", help_text="Apple App Store link")),
                ("privacy_policy_url", models.CharField(blank=True, default="/contact", help_text="Link to privacy policy page", max_length=300)),
                ("terms_of_use_url", models.CharField(blank=True, default="/contact", help_text="Link to terms of use page", max_length=300)),
                ("logo", models.ForeignKey(blank=True, help_text="Site logo for footer/header", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="+", to="wagtailimages.Image")),
                ("site", models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, to="wagtailcore.Site")),
            ],
            options={"verbose_name": "site settings", "verbose_name_plural": "site settings", "app_label": "content"},
            bases=("wagtailcontrib_settings.basesitesetting", models.Model),
        ),

        # ───────────────────────────────────────────────────────────────
        # 20. FooterLinkGroup (ParentalKey → SiteSettings)
        # ───────────────────────────────────────────────────────────────
        migrations.CreateModel(
            name="FooterLinkGroup",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(help_text="e.g., 'Useful Links', 'Our Company'", max_length=100)),
                ("sort_order", models.IntegerField(default=0)),
                ("setting", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="footer_link_groups", to="content.SiteSettings")),
            ],
            options={"ordering": ["sort_order"], "app_label": "content"},
        ),

        # ───────────────────────────────────────────────────────────────
        # 21. FooterLink (ParentalKey → FooterLinkGroup)
        # ───────────────────────────────────────────────────────────────
        migrations.CreateModel(
            name="FooterLink",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("label", models.CharField(max_length=100)),
                ("url", models.CharField(max_length=300)),
                ("sort_order", models.IntegerField(default=0)),
                ("group", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="links", to="content.FooterLinkGroup")),
            ],
            options={"ordering": ["sort_order"], "app_label": "content"},
        ),

        # ───────────────────────────────────────────────────────────────
        # 22. HomePage (multi-table inheritance → wagtailcore.Page)
        # ───────────────────────────────────────────────────────────────
        migrations.CreateModel(
            name="HomePage",
            fields=[
                ("page_ptr", models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to="wagtailcore.Page")),
                ("seo_title", models.CharField(blank=True, default="", help_text="Override the page title for SEO purposes.", max_length=255)),
                ("seo_description", models.TextField(blank=True, default="", help_text="Meta description for search engines.")),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("body", wagtail.fields.StreamField([("hero", 0), ("stats", 1), ("section_header", 2), ("rich_section", 3), ("cta", 4), ("faq_groups", 5), ("contact_methods", 6), ("form", 7)], blank=True, block_lookup={
                    0: ("www.content.models.blocks.HeroBlock", [], {}),
                    1: ("www.content.models.blocks.StatsBlock", [], {}),
                    2: ("www.content.models.blocks.SectionHeaderBlock", [], {}),
                    3: ("www.content.models.blocks.RichSectionBlock", [], {}),
                    4: ("www.content.models.blocks.CtaBlock", [], {}),
                    5: ("www.content.models.blocks.FaqGroupsBlock", [], {}),
                    6: ("www.content.models.blocks.ContactMethodsBlock", [], {}),
                    7: ("www.content.models.blocks.FormBlock", [], {}),
                })),
            ],
            options={"verbose_name": "home page", "verbose_name_plural": "home pages", "app_label": "content"},
            bases=("wagtailcore.page",),
        ),

        # ───────────────────────────────────────────────────────────────
        # 23. AboutPage
        # ───────────────────────────────────────────────────────────────
        migrations.CreateModel(
            name="AboutPage",
            fields=[
                ("page_ptr", models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to="wagtailcore.Page")),
                ("seo_title", models.CharField(blank=True, default="", help_text="Override the page title for SEO purposes.", max_length=255)),
                ("seo_description", models.TextField(blank=True, default="", help_text="Meta description for search engines.")),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("body", wagtail.fields.StreamField([("hero", 0), ("stats", 1), ("section_header", 2), ("rich_section", 3), ("cta", 4), ("faq_groups", 5), ("contact_methods", 6), ("form", 7)], blank=True, block_lookup={
                    0: ("www.content.models.blocks.HeroBlock", [], {}),
                    1: ("www.content.models.blocks.StatsBlock", [], {}),
                    2: ("www.content.models.blocks.SectionHeaderBlock", [], {}),
                    3: ("www.content.models.blocks.RichSectionBlock", [], {}),
                    4: ("www.content.models.blocks.CtaBlock", [], {}),
                    5: ("www.content.models.blocks.FaqGroupsBlock", [], {}),
                    6: ("www.content.models.blocks.ContactMethodsBlock", [], {}),
                    7: ("www.content.models.blocks.FormBlock", [], {}),
                })),
            ],
            options={"verbose_name": "about page", "verbose_name_plural": "about pages", "app_label": "content"},
            bases=("wagtailcore.page",),
        ),

        # ───────────────────────────────────────────────────────────────
        # 24. FaqPage
        # ───────────────────────────────────────────────────────────────
        migrations.CreateModel(
            name="FaqPage",
            fields=[
                ("page_ptr", models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to="wagtailcore.Page")),
                ("seo_title", models.CharField(blank=True, default="", help_text="Override the page title for SEO purposes.", max_length=255)),
                ("seo_description", models.TextField(blank=True, default="", help_text="Meta description for search engines.")),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("body", wagtail.fields.StreamField([("hero", 0), ("stats", 1), ("section_header", 2), ("rich_section", 3), ("cta", 4), ("faq_groups", 5), ("contact_methods", 6), ("form", 7)], blank=True, block_lookup={
                    0: ("www.content.models.blocks.HeroBlock", [], {}),
                    1: ("www.content.models.blocks.StatsBlock", [], {}),
                    2: ("www.content.models.blocks.SectionHeaderBlock", [], {}),
                    3: ("www.content.models.blocks.RichSectionBlock", [], {}),
                    4: ("www.content.models.blocks.CtaBlock", [], {}),
                    5: ("www.content.models.blocks.FaqGroupsBlock", [], {}),
                    6: ("www.content.models.blocks.ContactMethodsBlock", [], {}),
                    7: ("www.content.models.blocks.FormBlock", [], {}),
                })),
            ],
            options={"verbose_name": "FAQ page", "verbose_name_plural": "FAQ pages", "app_label": "content"},
            bases=("wagtailcore.page",),
        ),

        # ───────────────────────────────────────────────────────────────
        # 25. PrivacyPage
        # ───────────────────────────────────────────────────────────────
        migrations.CreateModel(
            name="PrivacyPage",
            fields=[
                ("page_ptr", models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to="wagtailcore.Page")),
                ("seo_title", models.CharField(blank=True, default="", help_text="Override the page title for SEO purposes.", max_length=255)),
                ("seo_description", models.TextField(blank=True, default="", help_text="Meta description for search engines.")),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("body", wagtail.fields.StreamField([("hero", 0), ("stats", 1), ("section_header", 2), ("rich_section", 3), ("cta", 4), ("faq_groups", 5), ("contact_methods", 6), ("form", 7)], blank=True, block_lookup={
                    0: ("www.content.models.blocks.HeroBlock", [], {}),
                    1: ("www.content.models.blocks.StatsBlock", [], {}),
                    2: ("www.content.models.blocks.SectionHeaderBlock", [], {}),
                    3: ("www.content.models.blocks.RichSectionBlock", [], {}),
                    4: ("www.content.models.blocks.CtaBlock", [], {}),
                    5: ("www.content.models.blocks.FaqGroupsBlock", [], {}),
                    6: ("www.content.models.blocks.ContactMethodsBlock", [], {}),
                    7: ("www.content.models.blocks.FormBlock", [], {}),
                })),
            ],
            options={"verbose_name": "privacy page", "verbose_name_plural": "privacy pages", "app_label": "content"},
            bases=("wagtailcore.page",),
        ),

        # ───────────────────────────────────────────────────────────────
        # 26. ContactPage
        # ───────────────────────────────────────────────────────────────
        migrations.CreateModel(
            name="ContactPage",
            fields=[
                ("page_ptr", models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to="wagtailcore.Page")),
                ("seo_title", models.CharField(blank=True, default="", help_text="Override the page title for SEO purposes.", max_length=255)),
                ("seo_description", models.TextField(blank=True, default="", help_text="Meta description for search engines.")),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("body", wagtail.fields.StreamField([("hero", 0), ("stats", 1), ("section_header", 2), ("rich_section", 3), ("cta", 4), ("faq_groups", 5), ("contact_methods", 6), ("form", 7)], blank=True, block_lookup={
                    0: ("www.content.models.blocks.HeroBlock", [], {}),
                    1: ("www.content.models.blocks.StatsBlock", [], {}),
                    2: ("www.content.models.blocks.SectionHeaderBlock", [], {}),
                    3: ("www.content.models.blocks.RichSectionBlock", [], {}),
                    4: ("www.content.models.blocks.CtaBlock", [], {}),
                    5: ("www.content.models.blocks.FaqGroupsBlock", [], {}),
                    6: ("www.content.models.blocks.ContactMethodsBlock", [], {}),
                    7: ("www.content.models.blocks.FormBlock", [], {}),
                })),
            ],
            options={"verbose_name": "contact page", "verbose_name_plural": "contact pages", "app_label": "content"},
            bases=("wagtailcore.page",),
        ),
    ]
