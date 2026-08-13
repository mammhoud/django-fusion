import django.db.models.deletion
import modelcluster.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0003_sitelanguage'),
        ('wagtailcore', '0097_baselogentry_uuid_action_timestamp_indexes'),
        ('wagtailimages', '0027_image_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='FooterLinkGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text="e.g., 'Useful Links', 'Our Company'", max_length=100)),
                ('sort_order', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ['sort_order'],
            },
        ),
        migrations.CreateModel(
            name='SocialLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('platform', models.CharField(choices=[('facebook', 'Facebook'), ('twitter', 'Twitter / X'), ('instagram', 'Instagram'), ('linkedin', 'LinkedIn'), ('youtube', 'YouTube'), ('whatsapp', 'WhatsApp'), ('tiktok', 'TikTok'), ('github', 'GitHub'), ('discord', 'Discord'), ('other', 'Other')], default='facebook', max_length=20)),
                ('label', models.CharField(blank=True, default='', help_text="Display name (e.g., 'Follow us on Facebook')", max_length=100)),
                ('url', models.URLField(max_length=300)),
                ('icon_svg', models.CharField(blank=True, default='', help_text="Path to SVG icon (e.g., '/assets/img/icons/facebook.svg')", max_length=200)),
                ('icon_class', models.CharField(blank=True, default='', help_text="CSS class for icon font (e.g., 'fab fa-facebook')", max_length=100)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('sort_order', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': 'social link',
                'verbose_name_plural': 'social links',
                'ordering': ['sort_order', 'platform'],
            },
        ),
        migrations.CreateModel(
            name='FooterLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=100)),
                ('url', models.CharField(max_length=300)),
                ('sort_order', models.IntegerField(default=0)),
                ('group', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='links', to='pages.footerlinkgroup')),
            ],
            options={
                'ordering': ['sort_order'],
            },
        ),
        migrations.CreateModel(
            name='SiteSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site_name', models.CharField(default='TharaaEdu', help_text='Site name displayed in footer/titles', max_length=200)),
                ('site_tagline', models.CharField(blank=True, default='', help_text='Short tagline', max_length=300)),
                ('footer_description', models.TextField(blank=True, default='', help_text='Company description in footer')),
                ('footer_address', models.CharField(blank=True, default='', help_text='Physical address', max_length=300)),
                ('footer_phone', models.CharField(blank=True, default='', help_text='Contact phone number', max_length=50)),
                ('footer_email', models.EmailField(blank=True, default='', help_text='Contact email', max_length=254)),
                ('footer_copyright', models.CharField(default='© 2025 TharaaEdu. All rights reserved.', help_text='Copyright text in footer bottom', max_length=200)),
                ('google_play_url', models.URLField(blank=True, default='', help_text='Google Play store link')),
                ('apple_store_url', models.URLField(blank=True, default='', help_text='Apple App Store link')),
                ('privacy_policy_url', models.CharField(blank=True, default='/contact', help_text='Link to privacy policy page', max_length=300)),
                ('terms_of_use_url', models.CharField(blank=True, default='/contact', help_text='Link to terms of use page', max_length=300)),
                ('logo', models.ForeignKey(blank=True, help_text='Site logo for footer/header', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image')),
                ('site', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, to='wagtailcore.site')),
            ],
            options={
                'verbose_name': 'site settings',
                'verbose_name_plural': 'site settings',
            },
        ),
        migrations.AddField(
            model_name='footerlinkgroup',
            name='setting',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='footer_link_groups', to='pages.sitesettings'),
        ),
    ]
