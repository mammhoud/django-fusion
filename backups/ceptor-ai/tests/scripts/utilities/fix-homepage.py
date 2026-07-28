#!/usr/bin/env python
import os
import sys
from pathlib import Path

def configure(site: str) -> None:
    repo_root = Path(__file__).resolve().parents[3]
    os.chdir(repo_root)
    sys.path.insert(0, str(repo_root))
    
    from configs.site import configure_site_environment, site_dir_for
    configure_site_environment(site)
    site_dir = site_dir_for(site)
    for path in (site_dir, repo_root):
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

def fix_homepage():
    site_name = os.getenv("DJANGO_SITE") or "ctc-research"
    configure(site_name)
    
    import django
    django.setup()
    
    from django.contrib.contenttypes.models import ContentType
    from wagtail.models import Page, Site
    
    site = Site.objects.get(is_default_site=True)
    current_root = site.root_page
    
    try:
        from www.core.content.models.pages.home import HomePage
        homepage_ct = ContentType.objects.get_for_model(HomePage)
    except Exception as e:
        print(f"Error getting HomePage model: {e}")
        return False
        
    homepages = Page.objects.filter(content_type=homepage_ct, depth=2)
    if homepages.exists():
        new_root = homepages.first()
        site.root_page = new_root
        site.save()
        print(f"✓ Site root updated to: {new_root.title}")
        return True
    else:
        print("⚠ No HomePage found")
        return False

if __name__ == '__main__':
    fix_homepage()
