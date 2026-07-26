# Generated manually — Django management commands unavailable (Wagtail env issue)

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lms', '0004_announcement_assignment_assignmentsubmission_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Withdrawal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(limit_value=0.01)], verbose_name='Amount')),
                ('current_balance', models.DecimalField(decimal_places=2, default=0.0, help_text='Instructor balance at time of request', max_digits=10, verbose_name='Current Balance')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('processing', 'Processing'), ('completed', 'Completed'), ('rejected', 'Rejected'), ('cancelled', 'Cancelled')], db_index=True, default='pending', max_length=20, verbose_name='Status')),
                ('payment_method', models.CharField(choices=[('paypal', 'PayPal'), ('bank_transfer', 'Bank Transfer'), ('stripe', 'Stripe')], default='paypal', max_length=20, verbose_name='Payment Method')),
                ('payment_details', models.JSONField(blank=True, default=dict, help_text='Payment method-specific details (email, account number, etc.)', verbose_name='Payment Details')),
                ('notes', models.TextField(blank=True, default='', help_text='Internal notes about this withdrawal (e.g., rejection reason)', verbose_name='Admin Notes')),
                ('reference', models.CharField(blank=True, default='', help_text='Payment processor reference (e.g., PayPal transaction ID)', max_length=255, verbose_name='Reference')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('processed_at', models.DateTimeField(blank=True, help_text='When the withdrawal was completed or rejected', null=True, verbose_name='Processed At')),
                ('instructor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='withdrawals', to=settings.AUTH_USER_MODEL, verbose_name='Instructor')),
                ('processed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='processed_withdrawals', to=settings.AUTH_USER_MODEL, verbose_name='Processed By')),
            ],
            options={
                'verbose_name': 'Withdrawal',
                'verbose_name_plural': 'Withdrawals',
                'db_table': 'lms_withdrawals',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='withdrawal',
            index=models.Index(fields=['instructor', 'status'], name='lms_withdraw_instr_50e6cd_idx'),
        ),
        migrations.AddIndex(
            model_name='withdrawal',
            index=models.Index(fields=['instructor', '-created_at'], name='lms_withdraw_instr_204bd2_idx'),
        ),
    ]
