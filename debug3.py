#!/usr/bin/env python
import sys
sys.path.insert(0, '/app/ctc-research')
import settings
local = [a for a in settings.INSTALLED_APPS if 'www' in a or 'lms' in a or 'content' in a.lower()]
print('LOCAL APPS:', local)
print('Total:', len(settings.INSTALLED_APPS))
