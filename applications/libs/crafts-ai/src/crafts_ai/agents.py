"""Generate Kilo agent configs from component templates."""
from __future__ import annotations

import json
from pathlib import Path


def generate_agent_configs(root: Path, model: str = "gpt-5.5", ttl: int = 300) -> list[Path]:
    templates = list(root.glob("**/assets/templates/components/**/*.html")) + list(root.glob("**/templates/components/**/*.html"))
    out_dir = root / ".kilo" / "agent"
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for template in sorted(set(templates)):
        rel = template.relative_to(root).as_posix()
        name = rel.replace("/", "__").replace(".html", ".json")
        data = {"component_path": rel, "default_model": model, "viewset": template.stem.title().replace("_", "") + "ViewSet", "cache_ttl": ttl}
        target = out_dir / name
        target.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        written.append(target)
    return written
