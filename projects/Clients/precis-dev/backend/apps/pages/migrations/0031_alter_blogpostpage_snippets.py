import wagtail.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0030_productpage_clear_legacy_snippets'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpostpage',
            name='snippets',
            field=wagtail.fields.StreamField([('snippets', 9)], blank=True, block_lookup={0: ('wagtail.blocks.CharBlock', (), {'label': 'Eyebrow', 'max_length': 80, 'required': False}), 1: ('wagtail.blocks.CharBlock', (), {'label': 'Title', 'max_length': 200}), 2: ('wagtail.blocks.TextBlock', (), {'label': 'Description', 'required': False}), 3: ('wagtail.blocks.CharBlock', (), {'label': 'Language', 'max_length': 40, 'required': False}), 4: ('wagtail.blocks.TextBlock', (), {'help_text': 'The snippet body — kept verbatim.', 'label': 'Code'}), 5: ('wagtail.blocks.BooleanBlock', (), {'default': False, 'help_text': 'For a safe HTML sample, show a sandboxed live preview beside the code. Only enable this for self-contained HTML without scripts.', 'label': 'Render HTML preview', 'required': False}), 6: ('wagtail.blocks.PageChooserBlock', (), {'help_text': 'Pick a BlogPostPage that hosts this code. This keeps code sections inside engineering posts rather than product or catalog pages.', 'label': 'Deep-dive post', 'page_type': ['pages.BlogPostPage'], 'required': False}), 7: ('wagtail.blocks.StructBlock', [[('title', 1), ('language', 3), ('code', 4), ('render_preview', 5), ('related_post', 6)]], {}), 8: ('wagtail.blocks.ListBlock', (7,), {'label': 'Snippets'}), 9: ('wagtail.blocks.StructBlock', [[('eyebrow', 0), ('title', 1), ('description', 2), ('snippets', 8)]], {})}, help_text="Code for this post's engineering deep dive. Keep implementation sections on BlogPostPage records, not product or catalog pages.", verbose_name='Code sections'),
        ),
    ]
