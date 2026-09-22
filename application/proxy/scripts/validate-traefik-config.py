#!/usr/bin/env python3
"""Validate Traefik dynamic YAML configuration files."""

import pathlib
import sys

import yaml


PROXY_DIR = pathlib.Path(__file__).resolve().parents[1]
# Dynamic router configs live under configs/ (the compose file mounts that tree
# into the container), not at the repo root — without this the validator globbed
# an empty directory and exited 0, so `make validate` never checked anything.
CONFIG_DIR = PROXY_DIR / "configs"


def main() -> int:
    dynamic_dir = CONFIG_DIR / "traefik" / "dynamic"
    files = [
        CONFIG_DIR / "traefik" / "dynamic.yml",
        dynamic_dir / "certs.yml",
    ]
    files.extend(dynamic_dir.glob("*.yml"))

    ok = True
    for f in files:
        if not f.exists():
            continue
        try:
            with open(f) as fh:
                yaml.safe_load(fh)
            print(f"OK   {f}")
        except Exception as exc:  # pragma: no cover
            print(f"FAIL {f}: {exc}")
            ok = False

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
