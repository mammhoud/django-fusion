#!/usr/bin/env python
"""
Unified data populator for dual-site workspace.

Usage:
  .venv/bin/python -m tests.data_populator --site root --verbose
  .venv/bin/python -m tests.data_populator --site ctc --verbose
  .venv/bin/python -m tests.data_populator --site structa --verbose
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

SITE_TO_DIR = {
    "root": Path("."),
    "ctc": Path("ctc-research.com"),
    "structa": Path("structa.cloud"),
}


def run(cmd, cwd, verbose=False):
    if verbose:
        print("[RUN]", " ".join(cmd), "(cwd=", cwd, ")")
    return subprocess.run(cmd, cwd=str(cwd), check=False, text=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", choices=["root", "ctc", "structa"], default="root")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    base = SITE_TO_DIR[args.site]
    manage = [str(Path("..") / ".venv" / "bin" / "python"), "manage.py"] if args.site != "root" else [str(Path(".venv/bin/python")), "manage.py"]

    model_fixture = Path("tests/fixtures/models_fixture.json")
    dump_fixture = Path("tests/fixtures/dumped_data_fixture.json")

    missing = [str(p) for p in (model_fixture, dump_fixture) if not p.exists()]
    if missing:
        print("Missing fixture files:", ", ".join(missing))
        return 1

    # migrate + loaddata in deterministic order
    rc = run(manage + ["migrate", "--noinput"], cwd=base, verbose=args.verbose).returncode
    if rc != 0:
        return rc

    rc = run(manage + ["loaddata", str(model_fixture)], cwd=base, verbose=args.verbose).returncode
    if rc != 0:
        return rc

    rc = run(manage + ["loaddata", str(dump_fixture)], cwd=base, verbose=args.verbose).returncode
    return rc


if __name__ == "__main__":
    sys.exit(main())
