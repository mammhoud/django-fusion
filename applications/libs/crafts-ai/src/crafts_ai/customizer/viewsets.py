"""Component viewset generation helpers."""
from __future__ import annotations

import re
from pathlib import Path


def class_name_for_template(path: Path) -> str:
    stem = re.sub(r"[^A-Za-z0-9]+", " ", path.stem).title().replace(" ", "")
    return f"{stem or 'Component'}ViewSet"


def generate_component_viewsets(component_dir: Path) -> str:
    lines = ["# Generated ComponentViewSet declarations", ""]
    for template in sorted(component_dir.rglob("*.html")):
        rel = template.relative_to(component_dir).as_posix()
        lines.append(f"class {class_name_for_template(template)}(ComponentViewSet):")
        lines.append(f"    template_name = {rel!r}")
        lines.append("")
    return "\n".join(lines)
