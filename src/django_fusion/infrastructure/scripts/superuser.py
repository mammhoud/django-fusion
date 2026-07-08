import os
import sys

import django


def create_superuser():
    # Set up Django environment if not already set
    if not os.environ.get('DJANGO_SETTINGS_MODULE'):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configs.settings')

    # Add current directory to path so it can find settings
    sys.path.insert(0, os.getcwd())

    django.setup()

    from django.contrib.auth import get_user_model
    User = get_user_model()

    # Get credentials from environment variables
    username = os.environ.get('SUPERUSER_USERNAME', 'admin')
    email = os.environ.get('SUPERUSER_EMAIL', 'admin@example.com')
    password = os.environ.get('SUPERUSER_PASSWORD', 'p@aAssSwW0oOrRd123!')

    if not username or not password:
        print("❌ Error: SUPERUSER_USERNAME and SUPERUSER_PASSWORD must be set.")
        return

    try:
        if not User.objects.filter(username=username).exists():
            print(f"🚀 Creating superuser: {username} ({email})...")
            User.objects.create_superuser(username=username, email=email, password=password)
            print("✅ Superuser created successfully!")
        else:
            print(f"ℹ️  Superuser '{username}' already exists. Skipping creation.")
    except Exception as e:
        print(f"❌ Failed to create superuser: {e}")

if __name__ == "__main__":
    create_superuser()
