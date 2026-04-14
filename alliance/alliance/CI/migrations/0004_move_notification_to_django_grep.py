from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CI', '0003_move_call_to_django_grep'),
    ]

    operations = [
        # No-op migration: Notification model was already moved to django_grep
        # This migration is kept for historical purposes
    ]
