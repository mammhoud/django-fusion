"""Utilities for converting template and style identifiers to strict BEM."""
from __future__ import annotations

import re
from pathlib import Path

CLASS_RE = re.compile(r'class=["\']([^"\']+)["\']')
ID_RE = re.compile(r'id=["\']([^"\']+)["\']')
STYLE_RE = re.compile(r'([.#])([A-Za-z][\w-]*)')


def to_bem(name: str, block: str = "component") -> str:
    value = re.sub(r"[^A-Za-z0-9_-]+", "-", name.strip()).strip("-_")
    value = value.replace("_", "-").lower()
    if "__" in value and "--" in value:
        return value
    if value.startswith(f"{block}__"):
        return value
    if value.startswith(f"{block}--"):
        return value
    parts = [p for p in value.split("-") if p]
    if not parts:
        return f"{block}__item"
    if len(parts) == 1:
        return f"{block}__{parts[0]}"
    return f"{block}__{parts[0]}--{'-'.join(parts[1:])}"


def rewrite_text(text: str, block: str = "component") -> tuple[str, dict[str, str]]:
    mapping: dict[str, str] = {}

    def map_name(name: str) -> str:
        if name.startswith(("js-", "is-", "has-", "htmx-")):
            return name
        mapping.setdefault(name, to_bem(name, block))
        return mapping[name]

    def class_sub(match: re.Match[str]) -> str:
        classes = " ".join(map_name(c) for c in match.group(1).split())
        return f'class="{classes}"'

    def id_sub(match: re.Match[str]) -> str:
        return f'id="{map_name(match.group(1))}"'

    text = CLASS_RE.sub(class_sub, text)
    text = ID_RE.sub(id_sub, text)

    def style_sub(match: re.Match[str]) -> str:
        prefix, name = match.groups()
        return f".{map_name(name)}" if prefix in {'.', '#'} else match.group(0)

    text = STYLE_RE.sub(style_sub, text)
    return text, mapping


def convert_paths(paths: list[Path], block: str = "component", write: bool = True) -> dict[str, str]:
    combined: dict[str, str] = {}
    for path in paths:
        if not path.exists() or path.suffix not in {".html", ".scss", ".css"}:
            continue
        original = path.read_text(encoding="utf-8")
        updated, mapping = rewrite_text(original, block)
        combined.update(mapping)
        if write and updated != original:
            path.write_text(updated, encoding="utf-8")
    return combined
