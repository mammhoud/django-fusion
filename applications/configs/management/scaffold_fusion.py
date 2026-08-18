#!/usr/bin/env python3
"""Scaffold the new Fusion LMS and CMS projects from ctc-research.

This script creates isolated directories under projects/precis/precis-main and
projects/cms-fusion, copies the precis-ctc backend/frontend structure,
renames CSS classes from ctc-* to fu-*, and installs the dynamic branding
and fusion_render_first boilerplate.

Run from the repository root::

    python tools/scaffold_fusion.py

"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "projects" / "cms" / "precis-ctc"
TARGETS = {
    "precis-main": "Fusion Precis",
    "cms-fusion": "Fusion CMS",
}


def _safe_copytree(src: Path, dst: Path, *, ignore=None) -> None:
    """Copy a directory tree, skipping broken symlinks and unreadable files."""
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        dest_item = dst / item.name
        try:
            if item.is_symlink() and not item.exists():
                continue
            if item.is_dir():
                shutil.copytree(item, dest_item, ignore=ignore)
            elif item.is_file():
                shutil.copy2(item, dest_item)
        except (OSError, shutil.Error) as exc:
            print(f"  [skip] {item}: {exc}")


def copy_tree(src: Path, dst: Path, *, ignore=None) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    _safe_copytree(src, dst, ignore=ignore)


def replace_in_file(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")


def rename_ctc_to_fu(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = text.replace("ctc-", "fu-")
    text = text.replace("CTC", "Fusion")
    path.write_text(text, encoding="utf-8")


def scaffold_backend(name: str, display_name: str, target: Path) -> None:
    print(f"[scaffold] backend: {target}")
    backend_src = SOURCE
    backend_dst = target / "backend"
    copy_tree(backend_src, backend_dst)

    # Update site identifiers first, before any global ctc-* rename, so the
    # literal strings are still present in settings.py / server files.
    settings_file = backend_dst / "settings.py"
    if settings_file.exists():
        replace_in_file(settings_file, "precis-ctc", name)
        replace_in_file(settings_file, "CTC Research", display_name)
        replace_in_file(settings_file, "module=\"LMS\"", "module=\"FUSION\"")
        replace_in_file(
            settings_file,
            '"django_fusion.fragments.analyzer.apps.AnalyzerAppConfig",\n]\nINSTALLED_APPS += LOCAL_APPS',
            '"django_fusion.fragments.analyzer.apps.AnalyzerAppConfig",\n    "plugins.branding.apps.BrandingConfig",\n]\nINSTALLED_APPS += LOCAL_APPS\n\n# Dynamic branding context processor (canonical django-fusion built-in)\nTEMPLATES[0]["OPTIONS"]["context_processors"].append(\n    "django_fusion.contrib.branding.context_processors.fusion_branding_context"\n)',
        )
    for env_file in (backend_dst / "__main__.py", backend_dst / "server.py"):
        if env_file.exists():
            replace_in_file(env_file, "precis-ctc", name)

    # Rename ctc-* -> fu-* ONLY in styles/templates where the prefix denotes
    # a CSS class namespace. Python/JS/TS files are left untouched to avoid
    # breaking imports, URLs, and identifiers.
    for ext in ("*.scss", "*.css", "*.html"):
        for file_path in backend_dst.rglob(ext):
            rename_ctc_to_fu(file_path)

    # Update __main__.py / server.py env vars
    for env_file in (backend_dst / "__main__.py", backend_dst / "server.py"):
        if env_file.exists():
            replace_in_file(env_file, "precis-ctc", name)

    print(f"[scaffold] backend complete: {backend_dst}")


def scaffold_frontend(name: str, display_name: str, target: Path) -> None:
    print(f"[scaffold] frontend: {target / 'frontend'}")
    # Minimal Next.js frontend placeholder
    frontend = target / "frontend"
    frontend.mkdir(parents=True, exist_ok=True)
    (frontend / "package.json").write_text(
        f'{{"name": "{name}-frontend", "version": "0.1.0", "private": true}}\n'
    )
    src = frontend / "src" / "app"
    src.mkdir(parents=True, exist_ok=True)
    (src / "page.tsx").write_text(
        "export default function HomePage() {\n"
        "  return <main><h1>{display_name}</h1></main>;\n"
        "}\n".replace("{display_name}", display_name)
    )
    (src / "layout.tsx").write_text(
        "export default function RootLayout({ children }: {{ children: React.ReactNode }}) {\n"
        "  return <html><body>{children}</body></html>;\n"
        "}\n"
    )
    print(f"[scaffold] frontend complete: {frontend}")


def scaffold_assets(name: str, display_name: str, target: Path) -> None:
    print(f"[scaffold] assets: {target / 'assets'}")
    assets = target / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    (assets / "README.md").write_text(
        f"# {display_name} Assets\n\n"
        "Product-line-specific static assets, images, and theme overrides.\n"
        "Shared SCSS is imported from the backend `main.scss` via the `~shared` alias.\n"
    )
    # Theme override file
    styles = assets / "styles"
    styles.mkdir(parents=True, exist_ok=True)
    (styles / "fusion-theme.scss").write_text(
        f"/* {display_name} theme overrides */\n"
        ":root {\n"
        "  --fu-primary: #00a1b3;\n"
        "  --fu-secondary: #008080;\n"
        "}\n"
    )
    print(f"[scaffold] assets complete: {assets}")


def _write_migration(branding: Path) -> None:
    migrations = branding / "migrations"
    migrations.mkdir(parents=True, exist_ok=True)
    (migrations / "__init__.py").write_text("")
    (migrations / "0001_initial.py").write_text(
        "# Generated initial migration for FusionBranding\n"
        "from django.db import migrations, models\n\n"
        "class Migration(migrations.Migration):\n"
        "    initial = True\n\n"
        "    dependencies = []\n\n"
        "    operations = [\n"
        "        migrations.CreateModel(\n"
        "            name='FusionBranding',\n"
        "            fields=[\n"
        "                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),\n"
        "                ('site_name', models.CharField(default='Fusion', max_length=100)),\n"
        "                ('company_name', models.CharField(default='Fusion Inc.', max_length=100)),\n"
        "                ('creator_name', models.CharField(default='Fusion Team', max_length=100)),\n"
        "                ('primary_color', models.CharField(default='#00a1b3', max_length=7)),\n"
        "                ('favicon', models.ImageField(blank=True, upload_to='branding/')),\n"
        "            ],\n"
        "            options={\n"
        "                'verbose_name': 'Fusion Branding',\n"
        "                'verbose_name_plural': 'Fusion Brandings',\n"
        "            },\n"
        "        ),\n"
        "    ]\n"
    )


def scaffold_branding_app(target: Path, display_name: str) -> None:
    print(f"[scaffold] branding app: {target / 'backend' / 'plugins' / 'branding'}")
    branding = target / "backend" / "plugins" / "branding"
    branding.mkdir(parents=True, exist_ok=True)
    (branding / "__init__.py").write_text('"""Dynamic branding for Fusion."""\n')
    (branding / "apps.py").write_text(
        "from django.apps import AppConfig\n\n"
        "class BrandingConfig(AppConfig):\n"
        "    default_auto_field = 'django.db.models.BigAutoField'\n"
        "    name = 'plugins.branding'\n"
        "    verbose_name = 'Branding'\n"
    )
    models = branding / "models.py"
    models.write_text(
        "from django.db import models\n"
        "from wagtail.snippets.models import register_snippet\n"
        "from wagtail.admin.panels import FieldPanel\n\n"
        "@register_snippet\n"
        "class FusionBranding(models.Model):\n"
        "    site_name = models.CharField(max_length=100, default='Fusion')\n"
        "    company_name = models.CharField(max_length=100, default='Fusion Inc.')\n"
        "    creator_name = models.CharField(max_length=100, default='Fusion Team')\n"
        "    primary_color = models.CharField(max_length=7, default='#00a1b3')\n"
        "    favicon = models.ImageField(upload_to='branding/', blank=True)\n\n"
        "    panels = [\n"
        "        FieldPanel('site_name'),\n"
        "        FieldPanel('company_name'),\n"
        "        FieldPanel('creator_name'),\n"
        "        FieldPanel('primary_color'),\n"
        "        FieldPanel('favicon'),\n"
        "    ]\n\n"
        "    class Meta:\n"
        "        verbose_name = 'Fusion Branding'\n"
        "        verbose_name_plural = 'Fusion Brandings'\n\n"
        "    def __str__(self):\n"
        "        return self.site_name\n"
    )
    # The branding context processor is provided by django-fusion
    # (django_fusion.contrib.branding.context_processors.fusion_branding_context);
    # only the site-local FusionBranding snippet model is scaffolded here.
    _write_migration(branding)
    print("[scaffold] branding app complete")


def main() -> int:
    if not SOURCE.exists():
        print(f"Source not found: {SOURCE}", file=sys.stderr)
        return 1

    for name, display_name in TARGETS.items():
        target = ROOT / "projects" / name
        if target.exists():
            print(f"Removing existing {target}")
            shutil.rmtree(target)
        target.mkdir(parents=True, exist_ok=True)

        scaffold_backend(name, display_name, target)
        scaffold_frontend(name, display_name, target)
        scaffold_assets(name, display_name, target)
        scaffold_branding_app(target, display_name)

        print(f"[scaffold] {name} complete\n")

    print("Next: add new site aliases in assets/scripts/workspace.mjs and run migrations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
