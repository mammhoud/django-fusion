#!/usr/bin/env python
# Check which settings module Django is actually using
import sys
sys.path.insert(0, '/app/ctc-research')
import django
from django.conf import settings
# Force setup
if not settings.configured:
    django.setup()
import sys
mod = sys.modules.get('settings')
if mod:
    print('settings module:', mod.__file__)
    apps = [a for a in mod.INSTALLED_APPS if 'www' in a or 'lms' in a or 'plugin' in a]
    print('Local apps from module:', apps)
else:
    print('settings module not in sys.modules')

# Check the actual Django settings object
apps = [a for a in settings.INSTALLED_APPS if 'www' in a or 'lms' in a or 'plugin' in a or 'content' in a.lower()]
print('Local apps from django.conf.settings:', apps)

# Check which module file is providing the settings
import os
print('DJANGO_SETTINGS_MODULE:', os.environ.get('DJANGO_SETTINGS_MODULE'))
