#!/usr/bin/env bash
#
# scripts/dev/capture-screenshots.sh
#
# Boots the Vite dev server in the background, waits for it to serve,
# captures the six POS routes via headless Chromium, then JPG-converts
# the PNGs at the canonical filenames referenced by `docs/PUBLISH.md`.
#
# Requiring tooling (the parent Makefile surfaces install hints on missing):
#   - chromium-browser OR chromium                  (screenshot capture)
#   - convert (ImageMagick)                        (PNG → JPG)
#   - pnpm                                         (boots vite)
#
# Usage:
#   bash scripts/dev/capture-screenshots.sh
#   bash scripts/dev/capture-screenshots.sh --keep    # keeps temporary captures for debugging
#
# Exit codes:
#   0   – success
#   1   – required tool missing
#   2   – vite never became ready in 30 s
#   3   – capture or conversion failed

set -Eeuo pipefail

# ── Paths ────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
RELATED_DIR="${ROOT}/../landing-fusion/backend/assets/static/related/formints"
MIRROR_DIR="${ROOT}/../landing-fusion/frontend/public/static/related/formints"
CAPTURES_DIR="${ROOT}/.tmp-screenshot-captures"
LOG="/tmp/vite-shots.log"

# ── Args ─────────────────────────────────────────────────────────────────
KEEP_CAPTURES=0
for arg in "$@"; do
  case "$arg" in
    --keep) KEEP_CAPTURES=1 ;;
    -h|--help)
      sed -n '2,18p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *) echo "✗ unknown arg: $arg" >&2; exit 3 ;;
  esac
done

cd "${ROOT}"

# ── 1. Tool checks ───────────────────────────────────────────────────────
CHROME_BIN="$(command -v chromium-browser || command -v chromium || true)"
if [ -z "${CHROME_BIN}" ]; then
  echo "✗ chromium(chrome) not found — install: sudo apt-get install -y chromium-browser" >&2
  exit 1
fi
if ! command -v convert >/dev/null 2>&1; then
  echo "✗ ImageMagick (convert) not found — install: sudo apt-get install -y imagemagick" >&2
  exit 1
fi

# ── 2. Route table (3 fields: NAME URL WINDOW) ───────────────────────────
#   - NAME:    internal capture filename (used in $CAPTURES_DIR)
#   - URL:     relative route on localhost
#   - WINDOW:  chromium --window-size W×H (taller captures show more content)
shots=(
  "01_home_overview|http://127.0.0.1:1420/|1440,900"
  "02_home_dashboard|http://127.0.0.1:1420/|1440,1500"
  "03_sale|http://127.0.0.1:1420/sale|1440,900"
  "04_inventory|http://127.0.0.1:1420/inventory|1440,1100"
  "05_reports|http://127.0.0.1:1420/reports|1440,1100"
  "06_settings|http://127.0.0.1:1420/settings|1440,1100"
)

# ── 3. Cleanup trap so a failed run doesn't leave _captures/ behind ─────
cleanup() {
  pkill -f 'vite.*--port 1420' 2>/dev/null || true
  if [ "${KEEP_CAPTURES}" -eq 0 ]; then
    rm -rf "${CAPTURES_DIR}"
  fi
}
trap cleanup EXIT
mkdir -p "${CAPTURES_DIR}"

# ── 4. Boot vite detached ───────────────────────────────────────────────
echo "▸ Booting vite dev server (detached)…"
setsid nohup pnpm exec vite --host 127.0.0.1 --port 1420 > "${LOG}" 2>&1 < /dev/null &

echo "▸ Waiting for vite to be ready (max 30s)…"
READY=0
for i in $(seq 1 30); do
  if curl -fsS -I http://127.0.0.1:1420/ -o /dev/null 2>&1; then
    echo "   ready (${i}s)"
    READY=1
    break
  fi
  sleep 1
done
if [ "${READY}" -eq 0 ]; then
  echo "✗ vite did not become ready in 30s — see ${LOG}" >&2
  exit 2
fi

# ── 5. Capture each route ───────────────────────────────────────────────
echo "▸ Capturing 6 routes via headless Chromium…"
for shot in "${shots[@]}"; do
  NAME="${shot%%|*}"
  REST="${shot#*|}"
  URL="${REST%|*}"
  WIN="${REST##*|}"
  "${CHROME_BIN}" --headless=new --disable-gpu --no-sandbox --hide-scrollbars \
    --window-size="${WIN}" --virtual-time-budget=8000 \
    --screenshot="${CAPTURES_DIR}/${NAME}.png" "${URL}" 2>/dev/null
  printf '   ✓ %-22s  %s\n' "${NAME}" "${URL}"
done

# ── 6. Convert PNG → JPG ───────────────────────────────────────────────
echo "▸ Converting PNG → JPG (q=88, white background)…"
for NAME in 01_home_overview 02_home_dashboard 03_sale 04_inventory 05_reports 06_settings; do
  SRC="${CAPTURES_DIR}/${NAME}.png"
  case "${NAME}" in
    01_home_overview) DEST_NAME="standard-home-overview" ;;
    02_home_dashboard) DEST_NAME="standard-home-dashboard" ;;
    03_sale) DEST_NAME="standard-sale" ;;
    04_inventory) DEST_NAME="standard-inventory" ;;
    05_reports) DEST_NAME="standard-reports" ;;
    06_settings) DEST_NAME="standard-settings" ;;
  esac
  mkdir -p "${RELATED_DIR}" "${MIRROR_DIR}"
  DEST="${RELATED_DIR}/${DEST_NAME}.jpg"
  convert "${SRC}" -quality 88 -background white -alpha remove "${DEST}"
  cp "${DEST}" "${MIRROR_DIR}/${DEST_NAME}.jpg"
  printf '   %-22s → related/formints/%s.jpg\n' "${NAME}.png" "${DEST_NAME}"
done

# ── 7. Done ─────────────────────────────────────────────────────────────
if [ "${KEEP_CAPTURES}" -eq 0 ]; then
  rm -rf "${CAPTURES_DIR}"
fi
echo "── ✓ Done — 6 screenshots written to Landing-Fusion related/formints/ ──"
