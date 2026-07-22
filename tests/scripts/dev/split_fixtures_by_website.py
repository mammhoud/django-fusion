#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
src=ROOT/'tests'/'fixtures'/'dumped_data_fixture.json'
out=ROOT/'tests'/'fixtures'/'websites'
out.mkdir(parents=True,exist_ok=True)
if not src.exists():
    raise SystemExit('source fixture not found')
objs=json.loads(src.read_text())
by={}
for o in objs:
    model=o.get('model','unknown')
    app=model.split('.')[0]
    site='shared'
    if 'ctc' in app:
        site='ctc-research.com'
    elif 'structa' in app:
        site='structa.cloud'
    by.setdefault(site,[]).append(o)
for site,items in by.items():
    sdir=out/site
    sdir.mkdir(parents=True,exist_ok=True)
    per={}
    for i in items:
        per.setdefault(i.get('model','unknown').replace('.','_'),[]).append(i)
    for name,val in per.items():
        (sdir/f'{name}.json').write_text(json.dumps(val,indent=2))
print('created',sum(len(v) for v in by.values()),'records')
