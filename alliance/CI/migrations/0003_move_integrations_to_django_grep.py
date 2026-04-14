from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CI', '0002_cart'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.DeleteModel(name='Integration'),
            ],
        )
    ]
