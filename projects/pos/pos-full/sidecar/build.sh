#!/usr/bin/env bash
# =============================================================================
# POS Sidecar Build Script
# =============================================================================
# Packages the Python/Sanic server into a single executable with PyInstaller,
# then copies it into src-tauri/binaries/ with the Tauri-required target-triple
# suffix so Tauri's ExternalBin mechanism can bundle it.
#
# Prerequisites (run once):
#   pip install pyinstaller
#   pip install -r sidecar/requirements.txt
#
# Usage:
#   From the POS repo root:
#     bash sidecar/build.sh
#
#   Cross-compile target (optional):
#     TAURI_TARGET_TRIPLE=x86_64-unknown-linux-gnu bash sidecar/build.sh
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BINARIES_DIR="$REPO_ROOT/src-tauri/binaries"

# ---- Detect target triple ---------------------------------------------------
# Use the env var Tauri sets during `tauri build`, or fall back to rustc output.
if [[ -n "${TAURI_TARGET_TRIPLE:-}" ]]; then
    TARGET="$TAURI_TARGET_TRIPLE"
else
    TARGET=$(rustc -Vv 2>/dev/null | grep 'host:' | awk '{print $2}')
    if [[ -z "$TARGET" ]]; then
        echo "[build.sh] WARNING: rustc not found; defaulting target triple to x86_64-unknown-linux-gnu"
        TARGET="x86_64-unknown-linux-gnu"
    fi
fi

BINARY_NAME="pos-sidecar"
OUTPUT_NAME="${BINARY_NAME}-${TARGET}"

echo ""
echo "============================================"
echo " POS Sidecar Build"
echo " Target  : $TARGET"
echo " Output  : $BINARIES_DIR/$OUTPUT_NAME"
echo "============================================"
echo ""

# ---- Ensure venv/deps -------------------------------------------------------
cd "$SCRIPT_DIR"

if [[ ! -d ".venv" ]]; then
    echo "[build.sh] Creating virtual environment…"
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
pip install --quiet pyinstaller

# ---- Run PyInstaller --------------------------------------------------------
echo "[build.sh] Running PyInstaller…"
pyinstaller \
    --onefile \
    --name "$BINARY_NAME" \
    --distpath "$SCRIPT_DIR/dist" \
    --workpath "$SCRIPT_DIR/build" \
    --specpath "$SCRIPT_DIR" \
    --hidden-import sanic \
    --hidden-import sanic.routing \
    --hidden-import django \
    --hidden-import django.db.backends.sqlite3 \
    --hidden-import asgiref \
    --hidden-import asgiref.sync \
    --add-data "posapp:posapp" \
    server.py

deactivate

# ---- Copy to src-tauri/binaries with triple suffix -------------------------
mkdir -p "$BINARIES_DIR"

SRC="$SCRIPT_DIR/dist/$BINARY_NAME"

# On Windows PyInstaller appends .exe
if [[ "$TARGET" == *"windows"* ]]; then
    SRC="${SRC}.exe"
    OUTPUT_NAME="${OUTPUT_NAME}.exe"
fi

if [[ ! -f "$SRC" ]]; then
    echo "[build.sh] ERROR: PyInstaller output not found at $SRC"
    exit 1
fi

cp "$SRC" "$BINARIES_DIR/$OUTPUT_NAME"
chmod +x "$BINARIES_DIR/$OUTPUT_NAME"

echo ""
echo "[build.sh] ✓ Sidecar binary ready: src-tauri/binaries/$OUTPUT_NAME"
echo ""
echo "Next steps:"
echo "  pnpm tauri build    # bundles the binary into the Tauri app"
echo ""
