#!/usr/bin/env python
"""Check Django installed apps - must run via manage.py in precis-ctc context."""
import sys, traceback
sys.path.insert(0, '/app/precis-ctc')
sys.path.insert(0, '/app/precis-ctc/www')

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

try:
    import django
    django.setup()
    from django.conf import settings
    apps = settings.INSTALLED_APPS
    local_apps = [a for a in apps if any(x in a for x in ('www', 'lms', 'content', 'plugins', 'pages'))]
    sys.stderr.write('Total INSTALLED_APPS: ' + str(len(apps)) + '\n')
    sys.stderr.write('Local/content apps: ' + str(local_apps) + '\n')
    sys.stderr.write('SITE_DOMAIN: ' + str(getattr(settings, 'SITE_DOMAIN', 'N/A')) + '\n')
    sys.stderr.write('DEBUG: ' + str(settings.DEBUG) + '\n')
except Exception as e:
    sys.stderr.write('ERROR: ' + str(e) + '\n')
    traceback.print_exc()
