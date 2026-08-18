import os, sys, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'ctc-research.settings'
os.chdir('/app/precis-ctc')
sys.path.insert(0, '/app')
sys.path.insert(0, '/app/precis-ctc')
django.setup()

from www.contrib.management.commands.populate_courses import Command
cmd = Command()
cmd.handle(reset=False, dry_run=False, courses_only=True, events_only=False,
           verbosity=1, settings=None, pythonpath=None, traceback=False,
           no_color=False, force_color=False, skip_checks=False)
