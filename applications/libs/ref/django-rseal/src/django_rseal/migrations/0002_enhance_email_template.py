"""
Migration: Enhance EmailTemplate with advanced fields.

Adds all advanced fields from the pipelines EmailTemplate to the
django_rseal.email_template table, making it the single source of truth.

All new fields are optional (blank=True / null=True / default=...) to
maintain full backward compatibility with existing records.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_rseal', '0001_initial'),
    ]

    operations = [
        # ----------------------------------------------------------------
        # Create the EmailTemplate table (was previously only in pipelines)
        # ----------------------------------------------------------------
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                # --- Basic fields (original simple model) ---
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(
                    db_index=True,
                    max_length=255,
                    unique=True,
                    help_text='Template name for internal reference',
                )),
                ('subject', models.CharField(
                    max_length=255,
                    help_text='Email subject (for simple usage, use subject_template for dynamic content)',
                )),
                ('html_content', models.TextField(
                    help_text='HTML email content',
                )),
                ('text_content', models.TextField(
                    blank=True,
                    help_text='Plain text fallback content',
                )),
                ('description', models.TextField(
                    blank=True,
                    help_text='Template description',
                )),
                ('is_active', models.BooleanField(
                    db_index=True,
                    default=True,
                    help_text='Whether this template can be used',
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),

                # --- Scheduling ---
                ('go_live_at', models.DateTimeField(
                    blank=True,
                    null=True,
                    help_text='Schedule template to become active at this date/time',
                )),
                ('expire_at', models.DateTimeField(
                    blank=True,
                    null=True,
                    help_text='Schedule template to expire at this date/time',
                )),

                # --- Template source ---
                ('template_source', models.CharField(
                    choices=[
                        ('inline', 'Inline Content'),
                        ('file', 'Uploaded Files'),
                        ('path', 'Template Path'),
                        ('external', 'External URL'),
                    ],
                    default='inline',
                    max_length=20,
                    help_text='Where the template content comes from',
                )),
                ('template_path', models.CharField(
                    blank=True,
                    max_length=255,
                    help_text="Django template path (e.g., 'emails/newsletter.html')",
                )),
                ('external_url', models.URLField(
                    blank=True,
                    help_text='External URL to fetch template from',
                )),

                # --- Subject & preview ---
                ('subject_template', models.CharField(
                    blank=True,
                    max_length=255,
                    help_text='Subject template with variables like {{ title }}, {{ user_name }}',
                )),
                ('preview_text', models.CharField(
                    blank=True,
                    max_length=255,
                    help_text='Preview text shown in email clients',
                )),

                # --- File uploads ---
                ('html_file', models.FileField(
                    blank=True,
                    null=True,
                    upload_to='email_templates/html/%Y/%m/%d/',
                    help_text='Upload HTML template file',
                )),
                ('css_file', models.FileField(
                    blank=True,
                    null=True,
                    upload_to='email_templates/css/%Y/%m/%d/',
                    help_text='Upload CSS stylesheet file',
                )),
                ('css_content', models.TextField(
                    blank=True,
                    help_text='Inline CSS styles',
                )),

                # --- Template metadata ---
                ('template_type', models.CharField(
                    choices=[
                        ('invitation', 'Invitation'),
                        ('notification', 'Notification'),
                        ('newsletter', 'Newsletter'),
                        ('transactional', 'Transactional'),
                        ('welcome', 'Welcome'),
                        ('password_reset', 'Password Reset'),
                        ('order_confirmation', 'Order Confirmation'),
                        ('system_alert', 'System Alert'),
                        ('campaign', 'Campaign'),
                        ('promotional', 'Promotional'),
                        ('abandoned_cart', 'Abandoned Cart'),
                        ('receipt', 'Receipt'),
                        ('feedback', 'Feedback'),
                        ('announcement', 'Announcement'),
                    ],
                    default='notification',
                    max_length=50,
                    help_text='Template category',
                )),
                ('language', models.CharField(
                    choices=[
                        ('en', 'English'),
                        ('es', 'Spanish'),
                        ('fr', 'French'),
                        ('de', 'German'),
                        ('it', 'Italian'),
                        ('pt', 'Portuguese'),
                        ('ru', 'Russian'),
                        ('zh', 'Chinese'),
                        ('ja', 'Japanese'),
                        ('ar', 'Arabic'),
                        ('ko', 'Korean'),
                        ('hi', 'Hindi'),
                        ('tr', 'Turkish'),
                        ('nl', 'Dutch'),
                        ('pl', 'Polish'),
                    ],
                    default='en',
                    max_length=10,
                    help_text='Template language',
                )),
                ('version', models.PositiveIntegerField(
                    default=1,
                    help_text='Template version number',
                )),

                # --- Status & behaviour ---
                ('is_default', models.BooleanField(
                    default=False,
                    help_text='Mark as default template for this type',
                )),
                ('is_system', models.BooleanField(
                    default=False,
                    help_text='System templates cannot be deleted',
                )),
                ('is_draft', models.BooleanField(
                    default=False,
                    help_text='Draft templates are not available for use',
                )),

                # --- Email settings ---
                ('reply_to_email', models.EmailField(
                    blank=True,
                    help_text='Reply-to address',
                )),
                ('from_email', models.EmailField(
                    blank=True,
                    help_text='Sender email address',
                )),
                ('from_name', models.CharField(
                    blank=True,
                    max_length=100,
                    help_text='Sender display name',
                )),
                ('unsubscribe_url', models.URLField(
                    blank=True,
                    help_text='Unsubscribe link',
                )),

                # --- Categorisation & tagging ---
                ('category', models.CharField(
                    blank=True,
                    max_length=100,
                    help_text='Category for grouping templates',
                )),
                ('tags', models.JSONField(
                    blank=True,
                    default=list,
                    help_text='Tags for filtering and organizing',
                )),
                ('slug', models.SlugField(
                    blank=True,
                    max_length=200,
                    help_text='URL-friendly identifier',
                )),

                # --- Caching & performance ---
                ('cache_key', models.CharField(
                    blank=True,
                    max_length=100,
                    help_text='Auto-generated cache key',
                )),
                ('last_rendered', models.DateTimeField(
                    blank=True,
                    null=True,
                    help_text='When template was last rendered',
                )),
                ('render_count', models.PositiveIntegerField(
                    default=0,
                    help_text='Number of times template has been rendered',
                )),

                # --- Performance metrics ---
                ('open_rate', models.FloatField(
                    default=0.0,
                    help_text='Historical open rate percentage',
                )),
                ('click_rate', models.FloatField(
                    default=0.0,
                    help_text='Historical click rate percentage',
                )),
                ('conversion_rate', models.FloatField(
                    default=0.0,
                    help_text='Historical conversion rate percentage',
                )),
                ('bounce_rate', models.FloatField(
                    default=0.0,
                    help_text='Historical bounce rate percentage',
                )),
            ],
            options={
                'db_table': 'email_template',
                'ordering': ['template_type', 'name', 'version'],
            },
        ),

        # ----------------------------------------------------------------
        # Indexes
        # ----------------------------------------------------------------
        migrations.AddIndex(
            model_name='emailtemplate',
            index=models.Index(fields=['template_type', 'is_active'], name='et_type_active_idx'),
        ),
        migrations.AddIndex(
            model_name='emailtemplate',
            index=models.Index(fields=['language', 'is_active'], name='et_lang_active_idx'),
        ),
        migrations.AddIndex(
            model_name='emailtemplate',
            index=models.Index(fields=['is_default', 'is_active'], name='et_default_active_idx'),
        ),
        migrations.AddIndex(
            model_name='emailtemplate',
            index=models.Index(fields=['template_source'], name='et_source_idx'),
        ),
        migrations.AddIndex(
            model_name='emailtemplate',
            index=models.Index(fields=['cache_key'], name='et_cache_key_idx'),
        ),
        migrations.AddIndex(
            model_name='emailtemplate',
            index=models.Index(fields=['go_live_at'], name='et_go_live_idx'),
        ),
        migrations.AddIndex(
            model_name='emailtemplate',
            index=models.Index(fields=['expire_at'], name='et_expire_idx'),
        ),
        migrations.AddIndex(
            model_name='emailtemplate',
            index=models.Index(fields=['category'], name='et_category_idx'),
        ),
        migrations.AddIndex(
            model_name='emailtemplate',
            index=models.Index(fields=['is_draft', 'is_active'], name='et_draft_active_idx'),
        ),

        # ----------------------------------------------------------------
        # Unique constraint: only one default per type+language+version
        # ----------------------------------------------------------------
        migrations.AddConstraint(
            model_name='emailtemplate',
            constraint=models.UniqueConstraint(
                fields=['template_type', 'language', 'version'],
                condition=models.Q(is_default=True),
                name='unique_default_template_per_type_language_version',
            ),
        ),

        # ----------------------------------------------------------------
        # EmailLog and UserRole/UserGroup models
        # (these were missing from 0001_initial — add them here)
        # ----------------------------------------------------------------
        migrations.CreateModel(
            name='EmailLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(db_index=True)),
                ('recipient', models.EmailField(db_index=True)),
                ('subject', models.CharField(max_length=255)),
                ('status', models.CharField(
                    choices=[
                        ('queued', 'Queued'),
                        ('sending', 'Sending'),
                        ('sent', 'Sent'),
                        ('failed', 'Failed'),
                        ('bounced', 'Bounced'),
                    ],
                    db_index=True,
                    default='queued',
                    max_length=20,
                )),
                ('template_used', models.CharField(blank=True, max_length=255)),
                ('message_body', models.TextField(blank=True)),
                ('error_message', models.TextField(blank=True)),
                ('retry_count', models.PositiveIntegerField(default=0)),
                ('last_retry_at', models.DateTimeField(blank=True, null=True)),
                ('group_name', models.CharField(blank=True, max_length=100)),
                ('task_id', models.CharField(blank=True, db_index=True, max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('invitation_token', models.CharField(
                    blank=True,
                    db_index=True,
                    default=None,
                    max_length=255,
                    null=True,
                    unique=True,
                    help_text='Secure token for invitation links',
                )),
                ('token_expires_at', models.DateTimeField(
                    blank=True,
                    db_index=True,
                    null=True,
                    help_text='Token expiration time (default: 7 days)',
                )),
            ],
            options={
                'db_table': 'email_log',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='UserGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('score', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'user_group',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(
                    choices=[
                        ('supervisor', 'Supervisor'),
                        ('manager', 'Manager'),
                        ('instructor', 'Instructor'),
                        ('content_manager', 'Content Manager'),
                    ],
                    db_index=True,
                    max_length=50,
                )),
                ('assigned_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'user_role',
                'ordering': ['user', '-role'],
            },
        ),
    ]
