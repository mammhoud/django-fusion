# Generated initial migration for FusionBranding
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='FusionBranding',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site_name', models.CharField(default='Fusion', max_length=100)),
                ('company_name', models.CharField(default='Fusion Inc.', max_length=100)),
                ('creator_name', models.CharField(default='Fusion Team', max_length=100)),
                ('primary_color', models.CharField(default='#00a1b3', max_length=7)),
                ('favicon', models.ImageField(blank=True, upload_to='branding/')),
            ],
            options={
                'verbose_name': 'Fusion Branding',
                'verbose_name_plural': 'Fusion Brandings',
            },
        ),
    ]
