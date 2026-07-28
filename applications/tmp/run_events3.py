import os, sys, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'ctc-research.settings'
os.chdir('/app/ctc-research')
sys.path.insert(0, '/app')
sys.path.insert(0, '/app/ctc-research')
django.setup()
from www.contrib.management.commands.populate_courses import Command
Command().handle(events_only=True, courses_only=False, dry_run=False, reset=False, verbosity=1, settings=None, pythonpath=None, traceback=False, no_color=False, force_color=False, skip_checks=False)
