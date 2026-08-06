#!/usr/bin/env python3
"""Make a .env file safe for dotenvy 0.15.x parsing.

dotenvy aborts parsing the WHOLE file when any line fails, so a single bad
line silently drops every var (SUPERUSER_*, USE_AUTH, SMTP_*, ...) at runtime.
Two failure modes are fixed here:

1. Non-ASCII decorative characters (em-dash, box-drawing) in comment lines.
2. Unquoted values containing spaces (e.g. `SMTP_FROM_NAME=Formint`), which
   dotenvy rejects — quote them: `SMTP_FROM_NAME="Formint"`.

Only comment lines and space-containing values are rewritten; all other
KEY=VALUE bytes are left untouched.

Usage:
    python3 scripts/fix-env-ascii.py .env
"""
import sys

path = sys.argv[1] if len(sys.argv) > 1 else '.env'

raw = open(path, 'rb').read().decode('utf-8')
lines = raw.split('\n')
out = []
for ln in lines:
    if ln.strip().startswith('#'):
        ln = ln.replace('\u2014', '-').replace('\u2500', '-')
    else:
        s = ln.strip()
        if s and '=' in s and not s.startswith('#'):
            key, _, val = s.partition('=')
            val = val.strip()
            if (
                val
                and any(c.isspace() for c in val)
                and not (val.startswith('"') or val.startswith("'"))
            ):
                ln = f'{key}="{val}"'
    out.append(ln)
new = '\n'.join(out)
open(path, 'w').write(new)

bad_ascii = [i for i, l in enumerate(new.split('\n'), 1) if any(ord(c) > 127 for c in l)]
bad_unquoted = [
    i
    for i, l in enumerate(new.split('\n'), 1)
    if l.strip()
    and not l.strip().startswith('#')
    and '=' in l
    and any(c.isspace() for c in l.split('=', 1)[1])
    and not l.split('=', 1)[1].lstrip().startswith('"')
    and not l.split('=', 1)[1].lstrip().startswith("'")
]
print(f'written {path}')
print(f'  remaining non-ASCII lines:      {bad_ascii}')
print(f'  remaining unquoted-space values: {bad_unquoted}')
