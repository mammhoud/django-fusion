"""
EmailExtractor — scans markdown/text files for email addresses.
"""
import re
from pathlib import Path
from typing import Iterator

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")


class EmailExtractor:
    """Extract unique email addresses from files in a directory."""

    def __init__(self, extensions: tuple[str, ...] = (".md", ".txt", ".rst")):
        self.extensions = extensions

    def extract_from_file(self, path: Path) -> list[str]:
        """Return deduplicated emails found in a single file."""
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return []
        return list(dict.fromkeys(EMAIL_RE.findall(text)))

    def extract_from_directory(self, directory: Path) -> Iterator[dict]:
        """
        Yield dicts with keys: email, source_file, source_spec.
        Deduplication is per-file; global dedup is handled by EmailCSVManager.
        """
        for ext in self.extensions:
            for filepath in sorted(directory.rglob(f"*{ext}")):
                # Extract spec name from path (e.g., .kiro/specs-organized/fixes/spec-name/file.md)
                parts = filepath.parts
                source_spec = ""
                try:
                    # Find the spec directory name (usually 2 levels up from the file)
                    if len(parts) >= 2:
                        source_spec = parts[-2]  # Parent directory name
                except (IndexError, AttributeError):
                    source_spec = ""

                for email in self.extract_from_file(filepath):
                    yield {
                        "email": email.lower(),
                        "source_file": str(filepath),
                        "source_spec": source_spec,
                    }
