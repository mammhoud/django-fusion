from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('branding', '0002_fusionbranding_logo_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fusionbranding',
            name='primary_color',
            field=models.CharField(default='#E61919', help_text='Primary brand color (hex)', max_length=7),
        ),
    ]
