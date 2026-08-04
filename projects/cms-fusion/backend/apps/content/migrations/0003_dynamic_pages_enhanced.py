# Generated migration for new dynamic page models

from django.db import migrations, models
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ("wagtailcore", "__latest__"),
    ]

    operations = [
        migrations.CreateModel(
            name="DynamicPricingPage",
            fields=[
                ("page_ptr", models.OneToOneField(
                    auto_created=True,
                    on_delete=models.CASCADE,
                    parent_link=True,
                    primary_key=True,
                    serialize=False,
                    to="wagtailcore.Page",
                )),
                ("seo_description", models.TextField(blank=True, default="",
                    help_text="Meta description for search engines.")),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("body", wagtail.fields.StreamField(
                    [], blank=True, null=True, use_json_field=True,
                )),
            ],
            options={
                "verbose_name": "pricing page",
                "verbose_name_plural": "pricing pages",
                "db_table": "content_dynamic_pricingpage",
            },
            bases=("wagtailcore.page", models.Model),
        ),
        migrations.CreateModel(
            name="DynamicTestimonialsPage",
            fields=[
                ("page_ptr", models.OneToOneField(
                    auto_created=True,
                    on_delete=models.CASCADE,
                    parent_link=True,
                    primary_key=True,
                    serialize=False,
                    to="wagtailcore.Page",
                )),
                ("seo_description", models.TextField(blank=True, default="",
                    help_text="Meta description for search engines.")),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("body", wagtail.fields.StreamField(
                    [], blank=True, null=True, use_json_field=True,
                )),
            ],
            options={
                "verbose_name": "testimonials page",
                "verbose_name_plural": "testimonials pages",
                "db_table": "content_dynamic_testimonialspage",
            },
            bases=("wagtailcore.page", models.Model),
        ),
        migrations.CreateModel(
            name="DynamicTermsPage",
            fields=[
                ("page_ptr", models.OneToOneField(
                    auto_created=True,
                    on_delete=models.CASCADE,
                    parent_link=True,
                    primary_key=True,
                    serialize=False,
                    to="wagtailcore.Page",
                )),
                ("seo_description", models.TextField(blank=True, default="",
                    help_text="Meta description for search engines.")),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("body", wagtail.fields.StreamField(
                    [], blank=True, null=True, use_json_field=True,
                )),
            ],
            options={
                "verbose_name": "terms page",
                "verbose_name_plural": "terms pages",
                "db_table": "content_dynamic_termspage",
            },
            bases=("wagtailcore.page", models.Model),
        ),
        migrations.CreateModel(
            name="DynamicServicesPage",
            fields=[
                ("page_ptr", models.OneToOneField(
                    auto_created=True,
                    on_delete=models.CASCADE,
                    parent_link=True,
                    primary_key=True,
                    serialize=False,
                    to="wagtailcore.Page",
                )),
                ("seo_description", models.TextField(blank=True, default="",
                    help_text="Meta description for search engines.")),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("body", wagtail.fields.StreamField(
                    [], blank=True, null=True, use_json_field=True,
                )),
            ],
            options={
                "verbose_name": "services page",
                "verbose_name_plural": "services pages",
                "db_table": "content_dynamic_servicespage",
            },
            bases=("wagtailcore.page", models.Model),
        ),
        migrations.CreateModel(
            name="DynamicTeamPage",
            fields=[
                ("page_ptr", models.OneToOneField(
                    auto_created=True,
                    on_delete=models.CASCADE,
                    parent_link=True,
                    primary_key=True,
                    serialize=False,
                    to="wagtailcore.Page",
                )),
                ("seo_description", models.TextField(blank=True, default="",
                    help_text="Meta description for search engines.")),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("body", wagtail.fields.StreamField(
                    [], blank=True, null=True, use_json_field=True,
                )),
            ],
            options={
                "verbose_name": "team page",
                "verbose_name_plural": "team pages",
                "db_table": "content_dynamic_teampage",
            },
            bases=("wagtailcore.page", models.Model),
        ),
    ]
