#!/usr/bin/env python3
"""Inspect pages_homepage schema + stream columns."""
import json
import os
import sqlite3

def dump(db_path, label):
    print(f"\n=== {label} ({db_path}) ===")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(pages_homepage)")
    cols = [r[1] for r in cur.fetchall()]
    print("  columns:", cols)
    cur.execute("SELECT page_ptr_id FROM pages_homepage")
    for (pid,) in cur.fetchall():
        print(f"  home page_ptr_id={pid}")
        for col in cols:
            if col in ("summary", "head", "body", "stream", "content", "hero"):
                raw = cur.execute(
                    f"SELECT {col} FROM pages_homepage WHERE page_ptr_id = ?", (pid,)
                ).fetchone()
                if not raw or not raw[0]:
                    print(f"    {col}: <empty>")
                    continue
                text = raw[0]
                if text.lstrip().startswith("[") or text.lstrip().startswith("{"):
                    try:
                        blocks = json.loads(text)
                        kinds = {}
                        for b in blocks:
                            kinds[b.get("type", "?")] = kinds.get(b.get("type", "?"), 0) + 1
                        print(f"    {col}: {len(blocks)} blocks -> {kinds}")
                    except Exception as exc:
                        print(f"    {col}: unparseable ({exc}); first 120 chars: {text[:120]!r}")
                else:
                    print(f"    {col}: {text[:120]!r}")
    conn.close()

for db, label in [
    ("projects/precis/precis-lms/backend/db.sqlite3", "PRECIS"),
    ("projects/precis/landi/db.sqlite3", "LANDING-FUSION"),
]:
    if os.path.exists(db):
        dump(db, label)
    else:
        print(f"\n=== {label}: db not found ===")
