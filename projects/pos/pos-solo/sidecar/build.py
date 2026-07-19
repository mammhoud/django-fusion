#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""@tested pos-solo - posko-sidecar.spec → pos-sidecar.spec, posko-sidecar → pos-sidecar rename verified

Build the POS sidecar binary with PyInstaller.

This script is meant to be run from the repository root:

    python3 sidecar/build.py

It produces a single executable and renames it to the Tauri sidecar naming
convention:

    src-tauri/binaries/pos-sidecar-<target-triple>

The target triple is inferred from ``platform.machine()`` and ``sys.platform``.
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


TARGET_TRIPLES = {
    ("Linux", "x86_64"): "x86_64-unknown-linux-gnu",
    ("Linux", "aarch64"): "aarch64-unknown-linux-gnu",
    ("Linux", "arm64"): "aarch64-unknown-linux-gnu",
    ("Darwin", "x86_64"): "x86_64-apple-darwin",
    ("Darwin", "arm64"): "aarch64-apple-darwin",
    ("Windows", "x86_64"): "x86_64-pc-windows-msvc",
    ("Windows", "AMD64"): "x86_64-pc-windows-msvc",
    ("Windows", "aarch64"): "aarch64-pc-windows-msvc",
    ("Windows", "ARM64"): "aarch64-pc-windows-msvc",
}


def get_target_triple() -> str:
    system = platform.system()
    machine = platform.machine()
    triple = TARGET_TRIPLES.get((system, machine))
    if triple is None:
        raise RuntimeError(f"Unsupported platform: {system} {machine}")
    return triple


def main() -> int:
    repo_root = Path(__file__).parent.parent.resolve()
    sidecar_dir = repo_root / "sidecar"
    spec_file = sidecar_dir / "pos-sidecar.spec"
    output_dir = repo_root / "src-tauri" / "binaries"

    triple = get_target_triple()
    print(f"Building sidecar for {triple}...")

    # Run PyInstaller from the sidecar directory so relative imports/paths work.
    pyinstaller_bin = os.environ.get("PYINSTALLER_BIN")
    if pyinstaller_bin:
        pyinstaller_cmd = [pyinstaller_bin, str(spec_file), "--clean", "--noconfirm"]
    else:
        pyinstaller_cmd = [sys.executable, "-m", "PyInstaller", str(spec_file), "--clean", "--noconfirm"]

    result = subprocess.run(
        pyinstaller_cmd
        + [
            "--collect-all",
            "sanic",
            "--collect-all",
            "websockets",
            "--distpath",
            str(output_dir / "dist"),
            "--workpath",
            str(output_dir / "build"),
        ],
        cwd=sidecar_dir,
    )
    if result.returncode != 0:
        print("PyInstaller build failed", file=sys.stderr)
        return result.returncode

    # Locate the produced executable.
    built_name = "pos-sidecar"
    if sys.platform == "win32":
        built_name += ".exe"
    built_path = output_dir / "dist" / built_name
    if not built_path.exists():
        print(f"Expected executable not found at {built_path}", file=sys.stderr)
        return 1

    # Move to Tauri sidecar naming convention.
    output_dir.mkdir(parents=True, exist_ok=True)
    final_name = f"pos-sidecar-{triple}"
    if sys.platform == "win32":
        final_name += ".exe"
    final_path = output_dir / final_name

    if final_path.exists():
        final_path.unlink()
    shutil.copy2(built_path, final_path)
    built_path.unlink()

    # Clean up intermediate dist folder.
    shutil.rmtree(output_dir / "dist", ignore_errors=True)
    shutil.rmtree(output_dir / "build", ignore_errors=True)

    print(f"Sidecar binary ready at: {final_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
