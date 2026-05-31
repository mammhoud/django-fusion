#!/usr/bin/env python
"""Compatibility wrapper for the workspace site data populator.

Use ``tests/scripts/populate_site_data.py`` directly or run through Make/npm:

  .venv/bin/python tests/scripts/populate_site_data.py --site ctc --dry-run
  make -C tests/scripts populate WEBSITE=vresume ARGS="--dry-run"
  npm --prefix assets run populate -- --site all --dry-run
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path


if __name__ == "__main__":
    script = Path(__file__).resolve().parent / "scripts" / "populate_site_data.py"
    sys.argv[0] = str(script)
    runpy.run_path(str(script), run_name="__main__")
