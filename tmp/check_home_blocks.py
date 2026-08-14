#!/usr/bin/env python3
"""Inspect home page stream data for duplicated learning/listing blocks."""
import json
import os
import sqlite3
import sys

def dump(db_path, label):
    print(f"\n=== {label} ({db_path}) ===")
    if not os.path.exists(db_path):
        print("  DB not found")
        return
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Find the home page row + its content type
    try:
        cur.execute(
            "SELECT p.id, p.slug, p.title, ct.app_label, ct.model "
            "FROM wagtailcore_page p JOIN django_content_type ct ON p.content_type_id = ct.id "
            "WHERE p.slug = 'home'"
        )
        rows = cur.fetchall()
    except Exception as exc:
        print(f"  query failed: {exc}")
        conn.close()
        return

    for row in rows:
        print(f"  page id={row['id']} slug={row['slug']} type={row['app_label']}.{row['model']}")
        # Column names on the page model's table
        table = f"{row['app_label']}_{row['model']}"
        cols = [r[1] for r in cur.execute(f"PRAGMA table_info({table})").fetchall()]
        stream_cols = [c for c in cols if c in ('summary', 'head', 'body', 'stream')]
        for col in stream_cols:
            raw = cur.execute(f"SELECT {col} FROM {table} WHERE page_ptr_id = ?", (row['id'],)).fetchone()
            if not raw or not raw[0]:
                print(f"    {col}: <empty>")
                continue
            try:
                blocks = json.loads(raw[0])
            except Exception:
                print(f"    {col}: <unparseable>")
                continue
            kinds = {}
            for b in blocks:
                kinds[b.get('type', '?')] = kinds.get(b.get('type', '?'), 0) + 1
            print(f"    {col}: {len(blocks)} blocks -> {kinds}")
            for b in blocks:
                t = b.get('type')
                if 'listing' in t or 'course' in t or 'learning' in t:
                    v = b.get('value', {})
                    title = v.get('title') if isinstance(v, dict) else None
                    print(f"      - {t}: title={title!r} items={len(v.get('items', [])) if isinstance(v, dict) else '?'}")
    conn.close()

# Precis home page table: content_homepage or apps' home
for p in [
    "projects/precis/main/backend/db.sqlite3",
    "projects/precis/main/db.sqlite3",
    "projects/precis/main/frontend/db.sqlite3",
]:
    if os.path.exists(p):
        dump(p, "PRECIS")
        break
else:
    print("no precis db found")

for p in [
    "projects/precis/landi/db.sqlite3",
    "projects/precis/landi/backend/db.sqlite3",
]:
    if os.path.exists(p):
        dump(p, "LANDING-FUSION")
        break
else:
    print("no landing-fusion db found")
