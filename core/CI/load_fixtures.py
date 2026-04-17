"""
Fixture loading script — run directly with python (not django shell).
Copies into container at /tmp/load_fixtures.py via docker cp.
"""
import os
import sys

# Ensure /app is on the path so Django settings can be found
sys.path.insert(0, "/app")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configs.settings")
os.environ.setdefault("DJANGO_PRINT_ENV", "false")

import django
django.setup()

from django.core.management import call_command
from django.contrib.auth import get_user_model

results = []
for f in ["/app/ctc-research-data.json", "/app/wagtail_pages_dump.json"]:
    try:
        call_command("loaddata", f, "--ignorenonexistent", verbosity=0)
        results.append("OK:" + f.split("/")[-1])
    except Exception as e:
        results.append("WARN:" + f.split("/")[-1] + ":" + str(e)[:60])

User = get_user_model()
latest = User.objects.order_by("-date_joined").first()
ts = str(latest.date_joined) if latest else "no_records"
print("LOADDATA_RESULTS:" + "|".join(results) + "|TS:" + ts)
