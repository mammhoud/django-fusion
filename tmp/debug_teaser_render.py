#!/usr/bin/env python3
"""Debug: render home/main.html + home/fragment.html against the test DB."""
import os
import sys

sys.path.insert(0, "/home/structa.cloud/projects/precis/backend")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

import django

django.setup()

from django.shortcuts import render
from django.test import RequestFactory
from apps.content.models.pages.home import HomePage
from wagtail.models import Page

print("homepage rows:", HomePage.objects.count())
home = HomePage.objects.filter(slug="home").first()
print("english home:", home, "| depth:", getattr(home, "depth", None))

rf = RequestFactory()
html_main = render(rf.get("/"), "home/main.html", {"page": home}).content.decode()
print("main.html len:", len(html_main))
print("  PREVIEW count:", html_main.count("[ LEARNING / PREVIEW ]"))
i = html_main.find("LEARNING")
print("  first LEARNING ctx:", html_main[max(0, i - 120): i + 80].replace("\n", " ") if i >= 0 else "NONE")

html_frag = render(rf.get("/"), "home/fragment.html", {"page": home}).content.decode()
print("fragment.html len:", len(html_frag))
print("  PREVIEW count:", html_frag.count("[ LEARNING / PREVIEW ]"))

# template loaders — where do these resolve?
from django.template.loader import get_template
for name in ("home/main.html", "home/fragment.html"):
    try:
        t = get_template(name)
        print(f"  {name} -> {t.origin.name if hasattr(t, 'origin') else t.template.origin.name}")
    except Exception as exc:
        print(f"  {name} -> ERROR {exc}")
