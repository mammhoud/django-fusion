#!/usr/bin/env python3
"""Generate and compile the CTC Research es/sv/pt-BR catalogs.

The French catalog is used as the complete message-set reference. Target
modules provide exact translations and regex patterns for recurring labels.
Untranslated entries remain present with an explicit English fallback; the
summary reports that coverage so human reviewers can finish the remainder.

Usage:
    python scripts/generate_locales.py
    python scripts/generate_locales.py --dry-run
    python scripts/generate_locales.py --no-compile
"""

from __future__ import annotations

import argparse
import ast
import importlib
import json
import re
import struct
import sys
from pathlib import Path
from typing import Iterable

HERE = Path(__file__).resolve().parent
LOCALE_DIR = HERE.parent / "assets" / "locale"
sys.path.insert(0, str(HERE / "data"))

TARGETS = [
    ("es", "es", "Spanish", "nplurals=2; plural=(n != 1);"),
    ("sv", "sv", "Swedish", "nplurals=2; plural=(n != 1);"),
    ("pt_BR", "pt_BR", "Portuguese (Brazil)", "nplurals=2; plural=(n > 1);"),
]


def blocks(text: str) -> list[str]:
    """Split a PO file into blank-line-delimited entry blocks."""
    return [block for block in re.split(r"\n\s*\n", text.strip()) if block.strip()]


def quoted_value(line: str) -> str:
    return ast.literal_eval(line.strip())


def field_value(block: str, field: str) -> str | None:
    """Read a PO field, including its following multiline continuations."""
    lines = block.splitlines()
    prefix = f"{field} "
    for index, line in enumerate(lines):
        if line.startswith(prefix):
            value = quoted_value(line[len(field) + 1 :])
            for continuation in lines[index + 1 :]:
                if not continuation.startswith('"'):
                    break
                value += quoted_value(continuation)
            return value
    return None


def field_start_indices(block: str) -> Iterable[tuple[int, str]]:
    for index, line in enumerate(block.splitlines()):
        for field in ("msgstr", "msgstr[0]", "msgstr[1]", "msgstr[2]"):
            if line.startswith(f"{field} "):
                yield index, field


def replace_field(block: str, field: str, value: str) -> str:
    """Replace one PO field and all continuation lines with a safe one-line value."""
    lines = block.splitlines()
    for index, line in enumerate(lines):
        if not line.startswith(f"{field} "):
            continue
        end = index + 1
        while end < len(lines) and lines[end].startswith('"'):
            end += 1
        lines[index:end] = [f"{field} {json.dumps(value, ensure_ascii=False)}"]
        return "\n".join(lines)
    return block


def patch_header(header: str, language: str, plural_forms: str) -> str:
    # Callable replacements prevent re.sub from interpreting the PO literal
    # ``\\n`` as an actual line break.
    header = re.sub(
        r'"Language: .*?\\n"',
        lambda _match: f'"Language: {language}\\n"',
        header,
    )
    header = re.sub(
        r'"Plural-Forms: .*?\\n"',
        lambda _match: f'"Plural-Forms: {plural_forms}\\n"',
        header,
    )
    return header


def resolve_translation(msgid: str, module: object) -> tuple[str | None, str]:
    translations = getattr(module, "TRANSLATIONS", {})
    if msgid in translations:
        return translations[msgid], "exact"
    for pattern, replacement in getattr(module, "PATTERNS", []):
        match = re.match(pattern, msgid)
        if match:
            return match.expand(replacement), "pattern"
    return None, "fallback"


def parse_po_entries(text: str) -> list[tuple[str, str, str]]:
    """Return (msgid, msgid_plural, msgstr) tuples from a generated PO file."""
    result = []
    for block in blocks(text):
        msgid = field_value(block, "msgid")
        if msgid is None:
            continue
        msgid_plural = field_value(block, "msgid_plural") or ""
        if msgid_plural:
            values = []
            for index in range(10):
                value = field_value(block, f"msgstr[{index}]")
                if value is None:
                    break
                values.append(value)
            msgstr = "\x00".join(values)
        else:
            msgstr = field_value(block, "msgstr") or ""
        result.append((msgid, msgid_plural, msgstr))
    return result


def compile_mo(po_path: Path, mo_path: Path) -> None:
    """Compile a PO file to GNU MO format using only the Python stdlib."""
    entries = parse_po_entries(po_path.read_text(encoding="utf-8"))
    catalog: dict[str, str] = {}
    for msgid, msgid_plural, msgstr in entries:
        if not msgid and not msgid_plural:
            key = ""
        elif msgid_plural:
            key = f"{msgid}\x00{msgid_plural}"
        else:
            key = msgid
        catalog[key] = msgstr

    ids = sorted(catalog)
    originals = b"\x00".join(key.encode("utf-8") for key in ids) + b"\x00"
    translations = b"\x00".join(catalog[key].encode("utf-8") for key in ids) + b"\x00"
    n = len(ids)
    header_size = 7 * 4
    orig_table = header_size
    trans_table = orig_table + n * 8
    orig_data = trans_table + n * 8
    trans_data = orig_data + len(originals)
    original_offsets = []
    cursor = 0
    for key in ids:
        raw = key.encode("utf-8")
        original_offsets.append((len(raw), orig_data + cursor))
        cursor += len(raw) + 1
    translation_offsets = []
    cursor = 0
    for key in ids:
        raw = catalog[key].encode("utf-8")
        translation_offsets.append((len(raw), trans_data + cursor))
        cursor += len(raw) + 1

    data = [
        struct.pack("<7I", 0x950412DE, 0, n, orig_table, trans_table, 0, 0),
        b"".join(struct.pack("<2I", *item) for item in original_offsets),
        b"".join(struct.pack("<2I", *item) for item in translation_offsets),
        originals,
        translations,
    ]
    mo_path.parent.mkdir(parents=True, exist_ok=True)
    mo_path.write_bytes(b"".join(data))


def rebuild(dirname: str, language: str, label: str, plural_forms: str, module: object, dry_run: bool, compile: bool) -> None:
    reference = LOCALE_DIR / "fr" / "LC_MESSAGES" / "django.po"
    reference_blocks = blocks(reference.read_text(encoding="utf-8"))
    header = patch_header(reference_blocks[0], language, plural_forms)
    output = [header]
    stats = {"exact": 0, "pattern": 0, "fallback": 0, "entries": 0}

    for block in reference_blocks[1:]:
        msgid = field_value(block, "msgid")
        if not msgid:
            continue
        translation, source = resolve_translation(msgid, module)
        if translation is None:
            translation = msgid
        stats[source] += 1
        stats["entries"] += 1
        if field_value(block, "msgid_plural"):
            # Keep plural structure and use the translated phrase for both
            # forms when a target-specific plural pair is not supplied.
            plural_indices = [field for _, field in field_start_indices(block) if field.startswith("msgstr[")]
            if not plural_indices:
                plural_indices = ["msgstr[0]", "msgstr[1]"]
            for field in plural_indices:
                block = replace_field(block, field, translation)
        else:
            block = replace_field(block, "msgstr", translation)
        output.append(block)

    target = LOCALE_DIR / dirname / "LC_MESSAGES" / "django.po"
    content = "\n\n".join(output) + "\n"
    mo_path = target.with_suffix(".mo")
    if not dry_run:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        if compile:
            compile_mo(target, mo_path)
    suffix = f" -> {target}" + (f" + {mo_path}" if compile else "")
    print(f"[{('dry-run' if dry_run else 'written')}] {language}: "
          f"{stats['entries']} entries; exact={stats['exact']}, "
          f"pattern={stats['pattern']}, fallback={stats['fallback']}{suffix}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-compile", action="store_true", help="Do not write .mo files")
    args = parser.parse_args()
    for dirname, language, label, plural_forms in TARGETS:
        module = importlib.import_module(dirname)
        rebuild(dirname, language, label, plural_forms, module, args.dry_run, not args.no_compile)


if __name__ == "__main__":
    main()
