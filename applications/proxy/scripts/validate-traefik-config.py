#!/usr/bin/env python3
"""Validate Traefik dynamic YAML configuration files."""

import pathlib
import sys

import yaml


PROXY_DIR = pathlib.Path(__file__).resolve().parents[1]


def main() -> int:
    dynamic_dir = PROXY_DIR / "traefik" / "dynamic"
    files = [
        PROXY_DIR / "traefik" / "dynamic.yml",
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
