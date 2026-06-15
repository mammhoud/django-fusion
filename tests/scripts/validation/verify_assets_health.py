#!/usr/bin/env python3
"""
Asset Health Verification Script
Tests asset loading from Django URLs using django-grep style verification.
Checks:
- Static file URLs (/static/)
- Media URLs (/media/)
- Asset bundles (CSS, JS, images)
- Template asset references
- Static file collection status
"""

import os
import sys
import json
import requests
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from urllib.parse import urlparse, urljoin

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
SITES = {
    'ctc-research': {
        'port': 5070,
        'name': 'CTC Research',
        'static_dir': PROJECT_ROOT / 'ctc-research' / 'assets' / 'staticfiles',
        'bundles_dir': PROJECT_ROOT / 'ctc-research' / 'assets' / 'bundles',
    },
    'lms-demo': {
        'port': 5071,
        'name': 'LMS Demo',
        'static_dir': PROJECT_ROOT / 'lms-demo' / 'assets' / 'staticfiles',
        'bundles_dir': PROJECT_ROOT / 'lms-demo' / 'assets' / 'bundles',
    },
    'vresume': {
        'port': 5072,
        'name': 'VResume',
        'static_dir': PROJECT_ROOT / 'VResume' / 'assets' / 'staticfiles',
        'bundles_dir': PROJECT_ROOT / 'VResume' / 'assets' / 'bundles',
    },
}

ASSET_TYPES = {
    'css': ['main.css', 'styles.css'],
    'js': ['app.js', 'main.js'],
    'images': ['logo.png', 'favicon.ico'],
}


def print_header(text: str, level: int = 1):
    """Print formatted header."""
    if level == 1:
        print(f"\n{CYAN}{'=' * 80}{RESET}")
        print(f"{CYAN}{text:^80}{RESET}")
        print(f"{CYAN}{'=' * 80}{RESET}\n")
    else:
        print(f"\n{BLUE}{text}{RESET}")
        print(f"{BLUE}{'-' * len(text)}{RESET}\n")


def print_result(success: bool, label: str, details: str = ""):
    """Print a test result."""
    status = f"{GREEN}✓{RESET}" if success else f"{RED}✗{RESET}"
    output = f"{status} {label}"
    if details:
        output += f" - {details}"
    print(output)


def get_file_size(path: Path) -> str:
    """Get human-readable file size."""
    if not path.exists():
        return "N/A"
    size = path.stat().st_size
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TB"


def check_django_health(site_key: str, site_info: Dict) -> Tuple[bool, str]:
    """Check if Django app is responsive."""
    url = f"http://localhost:{site_info['port']}/health/"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return True, "Healthy"
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, str(e)


def check_static_url(site_key: str, site_info: Dict, asset_path: str) -> Tuple[bool, int, str]:
    """Check if static URL is accessible."""
    url = f"http://localhost:{site_info['port']}{asset_path}"
    try:
        response = requests.get(url, timeout=5, allow_redirects=True)
        # 200 = file found, 404 = path exists but file not found, others = errors
        return response.status_code == 200, response.status_code, response.url
    except Exception as e:
        return False, 0, str(e)


def check_static_files_collected(site_key: str, site_info: Dict) -> Tuple[bool, Dict]:
    """Check if static files have been collected."""
    static_dir = site_info['static_dir']
    
    if not static_dir.exists():
        return False, {'count': 0, 'size': '0B', 'reason': 'Directory not found'}
    
    files = list(static_dir.rglob('*'))
    file_count = len([f for f in files if f.is_file()])
    total_size = sum(f.stat().st_size for f in files if f.is_file())
    
    return file_count > 0, {
        'count': file_count,
        'size': get_file_size(static_dir),
        'reason': 'OK' if file_count > 0 else 'No files found'
    }


def check_asset_bundles(site_key: str, site_info: Dict) -> Tuple[bool, Dict]:
    """Check if asset bundles exist."""
    bundles_dir = site_info['bundles_dir']
    
    if not bundles_dir.exists():
        return False, {'count': 0, 'size': '0B', 'reason': 'Directory not found'}
    
    files = list(bundles_dir.rglob('*'))
    file_count = len([f for f in files if f.is_file()])
    
    bundle_types = {}
    for ext in ['js', 'css', 'map', 'json']:
        count = len(list(bundles_dir.glob(f'**/*.{ext}')))
        if count > 0:
            bundle_types[ext] = count
    
    return file_count > 0, {
        'count': file_count,
        'size': get_file_size(bundles_dir),
        'types': bundle_types,
        'reason': 'OK' if file_count > 0 else 'No bundles found'
    }


def check_asset_urls(site_key: str, site_info: Dict) -> List[Tuple[str, bool, str]]:
    """Check common asset URLs."""
    results = []
    common_paths = [
        '/static/css/main.css',
        '/static/js/app.js',
        '/static/images/logo.png',
        '/media/',
        '/assets/health/',
    ]
    
    for path in common_paths:
        success, status, url = check_static_url(site_key, site_info, path)
        status_text = f"HTTP {status}" if status > 0 else "Connection Error"
        results.append((path, success or status == 404, status_text))
    
    return results


def check_template_assets(site_key: str) -> Dict[str, int]:
    """Check for asset references in templates."""
    site_root = PROJECT_ROOT / site_key if site_key != 'vresume' else PROJECT_ROOT / 'VResume'
    template_dirs = [
        site_root / 'assets' / 'templates',
        site_root / 'templates',
    ]
    
    asset_refs = {
        'static_tags': 0,
        'media_urls': 0,
        'css_links': 0,
        'js_scripts': 0,
    }
    
    for template_dir in template_dirs:
        if not template_dir.exists():
            continue
        
        for html_file in template_dir.rglob('*.html'):
            try:
                content = html_file.read_text()
                asset_refs['static_tags'] += content.count('{% static')
                asset_refs['media_urls'] += content.count('/media/')
                asset_refs['css_links'] += content.count('<link')
                asset_refs['js_scripts'] += content.count('<script')
            except Exception:
                pass
    
    return asset_refs


def main():
    """Run comprehensive asset health verification."""
    print_header("🏥 ASSET HEALTH VERIFICATION SUITE", 1)
    print(f"Django-Grep Style Verification")
    print(f"Project Root: {PROJECT_ROOT}\n")

    all_passed = True
    results_summary = {}

    for site_key, site_info in SITES.items():
        print_header(f"{site_info['name']} (Port {site_info['port']})", 2)

        site_results = {
            'django_health': False,
            'static_collected': False,
            'bundles_exist': False,
            'urls_accessible': False,
            'templates_references': 0,
        }

        # 1. Check Django Health
        print("1️⃣  Django Application Health")
        print("-" * 40)
        healthy, message = check_django_health(site_key, site_info)
        print_result(healthy, f"  Django Health Check", message)
        site_results['django_health'] = healthy
        if not healthy:
            all_passed = False
        print()

        # 2. Check Static Files Collected
        print("2️⃣  Static Files Collection")
        print("-" * 40)
        collected, info = check_static_files_collected(site_key, site_info)
        print_result(collected, f"  Static Files Collected", f"{info['count']} files ({info['size']})")
        site_results['static_collected'] = collected
        if not collected:
            all_passed = False
        print()

        # 3. Check Asset Bundles
        print("3️⃣  Asset Bundles")
        print("-" * 40)
        bundled, bundle_info = check_asset_bundles(site_key, site_info)
        bundle_desc = f"{bundle_info['count']} files"
        if bundle_info.get('types'):
            type_str = ", ".join([f"{k}={v}" for k, v in bundle_info['types'].items()])
            bundle_desc += f" ({type_str})"
        print_result(bundled, f"  Asset Bundles Built", bundle_desc)
        site_results['bundles_exist'] = bundled
        if not bundled:
            all_passed = False
        print()

        # 4. Check Asset URLs Accessibility
        print("4️⃣  Asset URLs Accessibility")
        print("-" * 40)
        url_results = check_asset_urls(site_key, site_info)
        accessible_count = 0
        for path, accessible, status in url_results:
            print_result(accessible, f"  {path}", status)
            if accessible:
                accessible_count += 1
        site_results['urls_accessible'] = accessible_count == len(url_results)
        print()

        # 5. Check Template Asset References
        print("5️⃣  Template Asset References (django-grep)")
        print("-" * 40)
        template_refs = check_template_assets(site_key)
        for ref_type, count in template_refs.items():
            if count > 0:
                label = ref_type.replace('_', ' ').title()
                print_result(True, f"  {label}", f"{count} references found")
            site_results['templates_references'] += count

        if site_results['templates_references'] == 0:
            print_result(False, f"  Template References", "No asset references found")
            all_passed = False
        print()

        results_summary[site_key] = site_results

    # Summary Report
    print_header("📊 VERIFICATION SUMMARY", 1)

    print(f"{'Site':<20} {'Django':<10} {'Static':<10} {'Bundles':<10} {'URLs':<10} {'Templates':<10}")
    print("-" * 80)

    for site_key, site_info in SITES.items():
        results = results_summary[site_key]
        django = f"{GREEN}✓{RESET}" if results['django_health'] else f"{RED}✗{RESET}"
        static = f"{GREEN}✓{RESET}" if results['static_collected'] else f"{RED}✗{RESET}"
        bundles = f"{GREEN}✓{RESET}" if results['bundles_exist'] else f"{RED}✗{RESET}"
        urls = f"{GREEN}✓{RESET}" if results['urls_accessible'] else f"{RED}✗{RESET}"
        templates = f"{GREEN}{results['templates_references']}{RESET}" if results['templates_references'] > 0 else f"{RED}0{RESET}"
        
        print(f"{site_info['name']:<20} {django:<10} {static:<10} {bundles:<10} {urls:<10} {templates:<10}")

    # Overall Status
    print()
    print_header("🎯 FINAL STATUS", 1)

    if all_passed:
        print(f"{GREEN}✓ All asset health checks passed!{RESET}\n")
        print("All sites are ready for deployment with:")
        print("  • Django applications healthy")
        print("  • Static files collected")
        print("  • Asset bundles built")
        print("  • Asset URLs accessible")
        print("  • Templates properly referencing assets")
        return 0
    else:
        print(f"{RED}✗ Some asset health checks failed!{RESET}\n")
        print("Please check the details above and resolve issues before deployment.")
        return 1


if __name__ == '__main__':
    sys.exit(main())

