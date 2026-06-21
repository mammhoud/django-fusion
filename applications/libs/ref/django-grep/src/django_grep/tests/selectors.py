"""
Selector loader for yaml-based selectors.

Usage:
    selectors = load_selectors("example_site")
    username_sel = selectors["login"]["username"]
"""
from pathlib import Path
import os
import yaml


def load_selectors(site_name: str | None = None):
    """
    Load selectors YAML for a given site_name. Searches in this order:
    - SELENIUM_SELECTORS_FILE env var
    - project tests/selectors/<site_name>.yml (cwd)
    - package tests/selectors/<site_name>.yml (installed package)

    Returns dict or raises FileNotFoundError.
    """
    env_path = os.getenv("SELENIUM_SELECTORS_FILE")
    if env_path:
        path = Path(env_path)
        if path.exists():
            return yaml.safe_load(path.read_text()) or {}

    if site_name:
        # try project-level selectors (cwd/tests/selectors)
        project_path = Path.cwd() / "tests" / "selectors" / f"{site_name}.yml"
        if project_path.exists():
            return yaml.safe_load(project_path.read_text()) or {}
        # fallback to package selectors (installed package location)
        pkg_path = Path(__file__).parent / "selectors" / f"{site_name}.yml"
        if pkg_path.exists():
            return yaml.safe_load(pkg_path.read_text()) or {}

    # Try a default selectors file
    default_project = Path.cwd() / "tests" / "selectors" / "default.yml"
    if default_project.exists():
        return yaml.safe_load(default_project.read_text()) or {}
    default_pkg = Path(__file__).parent / "selectors" / "default.yml"
    if default_pkg.exists():
        return yaml.safe_load(default_pkg.read_text()) or {}

    raise FileNotFoundError(f"No selectors YAML found for site {site_name!r}")
