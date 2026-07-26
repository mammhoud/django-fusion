# Generated migration for FusionPage models
from django.db import migrations, models
import django.db.models.deletion
import wagtail.fields


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("wagtailcore", "0094_alter_page_locale"),
        ("wagtailimages", "0026_alter_image_file"),
    ]

    operations = [
        migrations.CreateModel(
            name="FusionHomePage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.Page",
                    ),
                ),
                (
                    "layout",
                    models.CharField(
                        choices=[
                            ("default", "Default (Header + Content + Footer)"),
                            ("full_width", "Full Width (No sidebar, edge-to-edge)"),
                            ("sidebar", "Sidebar (Content + Sidebar)"),
                            ("blank", "Blank (Content only, no chrome)"),
                        ],
                        default="default",
                        max_length=20,
                    ),
                ),
                (
                    "fusion_render_first",
                    models.BooleanField(default=False),
                ),
                (
                    "fragment_name",
                    models.CharField(blank=True, default="", max_length=255),
                ),
                (
                    "show_in_nav",
                    models.BooleanField(default=True),
                ),
                (
                    "custom_css",
                    models.TextField(blank=True, default=""),
                ),
                (
                    "hero_heading",
                    models.CharField(blank=True, default="Welcome to Fusion", max_length=255),
                ),
                (
                    "hero_subheading",
                    models.TextField(blank=True, default="A modern platform powered by django-fusion and django-bolt."),
                ),
            ],
            options={
                "verbose_name": "Fusion Home Page",
                "verbose_name_plural": "Fusion Home Pages",
            },
            bases=("wagtailcore.Page",),
        ),
        migrations.CreateModel(
            name="FusionContentPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.Page",
                    ),
                ),
                (
                    "layout",
                    models.CharField(
                        choices=[
                            ("default", "Default (Header + Content + Footer)"),
                            ("full_width", "Full Width (No sidebar, edge-to-edge)"),
                            ("sidebar", "Sidebar (Content + Sidebar)"),
                            ("blank", "Blank (Content only, no chrome)"),
                        ],
                        default="default",
                        max_length=20,
                    ),
                ),
                (
                    "fusion_render_first",
                    models.BooleanField(default=False),
                ),
                (
                    "fragment_name",
                    models.CharField(blank=True, default="", max_length=255),
                ),
                (
                    "show_in_nav",
                    models.BooleanField(default=True),
                ),
                (
                    "custom_css",
                    models.TextField(blank=True, default=""),
                ),
                (
                    "body",
                    wagtail.fields.RichTextField(blank=True, default=""),
                ),
                (
                    "featured_image",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailimages.Image",
                    ),
                ),
            ],
            options={
                "verbose_name": "Fusion Content Page",
                "verbose_name_plural": "Fusion Content Pages",
            },
            bases=("wagtailcore.Page",),
        ),
    ]
