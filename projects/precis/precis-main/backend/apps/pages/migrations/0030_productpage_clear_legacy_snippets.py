from django.db import migrations


def clear_legacy_product_snippets(apps, schema_editor):
    """Remove code sections from product pages after the post-only migration.

    The compatibility column remains in the model so old revisions can be
    migrated safely, but no product page should retain or publish code data.
    """
    ProductPage = apps.get_model("pages", "ProductPage")
    for page in ProductPage.objects.all().iterator():
        if page.snippets:
            page.snippets = []
            page.save(update_fields=["snippets"])


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0029_blogpost_snippet_render_preview"),
    ]

    operations = [
        migrations.RunPython(
            clear_legacy_product_snippets,
            migrations.RunPython.noop,
        ),
    ]
