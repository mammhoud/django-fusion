from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0012_marketingpage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sitesettings',
            name='primary_color',
            field=models.CharField(blank=True, default='#E61919', help_text='Primary brand color (hex)', max_length=7),
        ),
    ]
