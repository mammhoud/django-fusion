#!/usr/bin/env python
import sys
sys.path.insert(0, '/app/ctc-research')
import configs.settings as cs
print('Has INSTALLED_APPS:', hasattr(cs, 'INSTALLED_APPS'))
if hasattr(cs, 'INSTALLED_APPS'):
    local = [a for a in cs.INSTALLED_APPS if 'www' in a or 'content' in a.lower() or 'lms' in a.lower() or 'plugin' in a.lower()]
    print('Local apps:', local)
    print('Total apps:', len(cs.INSTALLED_APPS))
