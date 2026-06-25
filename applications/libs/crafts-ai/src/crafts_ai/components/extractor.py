"""Utilities for extracting component candidates from HTML pages.

The extractor is intentionally framework agnostic so it can be used by CLI
commands, Django management commands, or offline Ollama indexing tasks.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable

ASSET_ATTRS = {
    "link": ("href",),
    "script": ("src",),
    "img": ("src", "srcset"),
    "source": ("src", "srcset"),
}
STYLE_EXTENSIONS = {".css", ".scss", ".sass", ".less"}
SCRIPT_EXTENSIONS = {".js", ".mjs", ".cjs", ".ts"}
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


@dataclass(frozen=True)
class ExtractedComponent:
    """A low-depth HTML container that can become a reusable component."""

    tag: str
    depth: int
    start_line: int
    end_line: int
    classes: tuple[str, ...]
    component_name: str
    html: str
    styles: tuple[str, ...]
    scripts: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


class _ComponentParser(HTMLParser):
    def __init__(self, max_depth: int) -> None:
        super().__init__(convert_charrefs=False)
        self.max_depth = max_depth
        self.stack: list[dict[str, object]] = []
        self.components: list[ExtractedComponent] = []
        self.styles: list[str] = []
        self.scripts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {name: value or "" for name, value in attrs}
        self._collect_asset(tag, attrs_dict)
        if tag in VOID_TAGS:
            if self.stack:
                self.stack[-1]["html"].append(self.get_starttag_text() or f"<{tag}>")
            return
        depth = sum(1 for item in self.stack if item.get("tag") == "div")
        start_line, _ = self.getpos()
        record = {
            "tag": tag,
            "depth": depth,
            "start_line": start_line,
            "attrs": attrs_dict,
            "html": [self.get_starttag_text() or f"<{tag}>"] ,
        }
        if tag == "div" and depth <= self.max_depth:
            record["candidate"] = True
        self.stack.append(record)

    def handle_endtag(self, tag: str) -> None:
        end_line, _ = self.getpos()
        if not self.stack:
            return
        record = self.stack.pop()
        record_html = "".join(record["html"]) + f"</{tag}>"
        if self.stack:
            self.stack[-1]["html"].append(record_html)
        if record.get("candidate") and record.get("tag") == tag:
            attrs = record["attrs"]
            classes = tuple(filter(None, attrs.get("class", "").split()))
            self.components.append(
                ExtractedComponent(
                    tag=tag,
                    depth=int(record["depth"]),
                    start_line=int(record["start_line"]),
                    end_line=end_line,
                    classes=classes,
                    component_name=_component_name(tag, classes, attrs.get("id", "")),
                    html=record_html,
                    styles=tuple(dict.fromkeys(self.styles)),
                    scripts=tuple(dict.fromkeys(self.scripts)),
                )
            )

    def handle_data(self, data: str) -> None:
        if self.stack:
            self.stack[-1]["html"].append(data)

    def _collect_asset(self, tag: str, attrs: dict[str, str]) -> None:
        for attr in ASSET_ATTRS.get(tag, ()):
            value = attrs.get(attr, "")
            if not value:
                continue
            for candidate in value.split(","):
                parts = candidate.strip().split()
                if not parts:
                    continue
                path = parts[0]
                suffix = Path(path.split("?", 1)[0]).suffix.lower()
                if suffix in STYLE_EXTENSIONS:
                    self.styles.append(path)
                elif suffix in SCRIPT_EXTENSIONS:
                    self.scripts.append(path)


def _component_name(tag: str, classes: tuple[str, ...], element_id: str) -> str:
    raw = classes[0] if classes else element_id or tag
    return "".join(char if char.isalnum() else "_" for char in raw).strip("_") or tag


def extract_components_from_html(html: str, *, max_depth: int = 2) -> list[ExtractedComponent]:
    """Return low-depth ``div`` containers with page asset references."""
    parser = _ComponentParser(max_depth=max_depth)
    parser.feed(html)
    return parser.components


def extract_components_from_file(path: str | Path, *, max_depth: int = 2) -> list[ExtractedComponent]:
    """Read an HTML file and extract reusable component candidates."""
    return extract_components_from_html(Path(path).read_text(encoding="utf-8"), max_depth=max_depth)


def write_component_files(
    components: Iterable[ExtractedComponent],
    output_dir: str | Path,
) -> list[Path]:
    """Write each component to a separate HTML file and return written paths."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for index, component in enumerate(components, start=1):
        filename = f"{index:03d}_{component.component_name}.html"
        path = output / filename
        path.write_text(component.html, encoding="utf-8")
        written.append(path)
    return written
