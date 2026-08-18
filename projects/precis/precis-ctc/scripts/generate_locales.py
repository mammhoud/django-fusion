#!/usr/bin/env python3
"""Rebuild the es / sv / pt-br Django catalogs from the complete fr reference.

The fr/de/ar catalogs under assets/locale/<lang>/LC_MESSAGES/django.po are the
canonical, complete message sets (3,433 entries). The es/sv/pt-br catalogs were
stubs with only a handful of strings. This script rebuilds each stub so it
contains the *full* msgid set (preserving comments, locations, and entry order
from fr) with translations supplied by the bundled data modules.

Usage:
    python scripts/generate_locales.py            # write all three catalogs
    python scripts/generate_locales.py --dry-run  # report what would change
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOCALE_DIR = HERE.parent / "assets" / "locale"

# Translation data modules (scripts/data/<lang>.py) expose a dict keyed by msgid.
sys.path.insert(0, str(HERE / "data"))

TARGETS = [
    ("es", "es", "Spanish"),
    ("sv", "sv", "Swedish"),
    ("pt_BR", "pt-br", "Portuguese (Brazil)"),
]

ENTRY_RE = re.compile(r'msgid "(.*)"\nmsgstr "(.*)"', re.S)


def parse_po(path: Path) -> tuple[str, list[tuple[str, str, str]]]:
    """Return (header, [(block, msgid, msgstr), ...]).

    A block is the raw text from the start of its comment through the msgstr
    line (exclusive of the trailing blank line).
    """
    text = path.read_text(encoding="utf-8")
    # Header = everything up to the first blank line after the msgid "" block.
    header_match = re.match(r'(.*?\n\n)', text, re.S)
    header = header_match.group(1) if header_match else ""
    rest = text[len(header):]

    blocks = re.split(r'\n(?=#)', rest)
    entries: list[tuple[str, str, str]] = []
    for block in blocks:
        m = ENTRY_RE.search(block)
        if m:
            entries.append((block, m.group(1), m.group(2)))
    return header, entries


def rebuild(lang: str, translations: dict[str, str], dry_run: bool) -> None:
    fr_path = LOCALE_DIR / "fr" / "LC_MESSAGES" / "django.po"
    header, entries = parse_po(fr_path)

    # Replace the header Language/Plural-Forms metadata for the target locale.
    lang_label = next(t[2] for t in TARGETS if t[1] == lang)

    out = [header.strip(), ""]
    # Rewrite the header block's Language line to the target.
    header_lang = re.sub(
        r'(?m)^"Language: .*\\n"$',
        f'"Language: {lang_label}\\n"',
        header,
    )
    out = [header_lang.strip(), ""]

    stats = {"translated": 0, "fallback": 0}
    for block, msgid, _msgstr in entries:
        if not msgid:
            # The header entry — keep the (patched) header.
            continue
        translation = translations.get(msgid)
        if translation is None:
            translation = msgid  # safe fallback to the source string
            stats["fallback"] += 1
        else:
            stats["translated"] += 1
        # Replace msgstr in the block, preserving comments/order.
        new_block = ENTRY_RE.sub(
            lambda m: f'msgid "{m.group(1)}"\nmsgstr "{translation}"',
            block,
            count=1,
        )
        out.append(new_block.rstrip())

    target_dir = LOCALE_DIR / lang / "LC_MESSAGES"
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / "django.po"
    content = "\n\n".join(out) + "\n"

    if dry_run:
        print(f"[dry-run] {lang}: {stats['translated']} translated, "
              f"{stats['fallback']} fallback -> {target_path}")
        return

    target_path.write_text(content, encoding="utf-8")
    print(f"[written] {lang}: {stats['translated']} translated, "
          f"{stats['fallback']} fallback -> {target_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                        help="Report coverage without writing files")
    args = parser.parse_args()

    for dirname, lang, _label in TARGETS:
        try:
            module = __import__(dirname)
            rebuild(lang, module.TRANSLATIONS, args.dry_run)
        except ImportError as exc:
            print(f"[skip] {lang}: missing data module ({exc})", file=sys.stderr)


if __name__ == "__main__":
    main()
