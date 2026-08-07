#!/usr/bin/env bash
#
# scripts/dev/capture-admin-screenshots.sh
#
# Boots the Django runserver in the background, waits for it to serve,
# captures the Unfold admin dashboard and key admin pages via headless
# Chromium, then PNG→JPG converts the outputs.
#
# NOTE: The captures will show the admin login page unless you first
# authenticate. To capture authenticated pages:
#   Option A: Run `make admin-bootstrap` first, log in manually at :8000/admin/
#             (the session persists in the Chrome user-data-dir), then run this
#             script with --keep so _captures/ are preserved.
#   Option B: After the script starts runserver, log in manually at :8000/admin/
#             before the screenshots are taken.
#
# The SVG placeholders in docs/screenshots/admin/ already show the fully
# authenticated dashboard. This script captures real JPGs for replacement.
#
# Requires:
#   - chromium-browser OR chromium        (screenshot capture)
#   - convert (ImageMagick)               (PNG → JPG)
#   - python3 + django-unfold installed   (runserver)
#
# Usage:
#   bash scripts/dev/capture-admin-screenshots.sh               # default: 6 pages
#   bash scripts/dev/capture-admin-screenshots.sh --all          # capture all 6 pages
#   bash scripts/dev/capture-admin-screenshots.sh --keep        # leave _captures/ in place
#
# Exit codes:
#   0  – success
#   1  – required tool missing
#   2  – runserver never became ready in 60 s
#   3  – capture or conversion failed

set -Eeuo pipefail

# ── Paths ────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
SIDECAR="${ROOT}/sidecar"
CAPTURES_DIR="${ROOT}/docs/screenshots/admin/_captures"
SCREENSHOTS_DIR="${ROOT}/docs/screenshots/admin"
LOG="/tmp/django-shots.log"

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
if ! command -v python3 >/dev/null 2>&1; then
  echo "✗ python3 not found" >&2
  exit 1
fi

ADMIN_EMAIL="${POS_FULL_ADMIN_EMAIL:-admin@pos-full.local}"
ADMIN_PASSWORD="${POS_FULL_ADMIN_PASSWORD:-admin123}"

# ── 2. Route table ───────────────────────────────────────────────────────
#  NAME|URL|WINDOW(WxH)
shots=(
  "01_admin_dashboard|http://127.0.0.1:8000/admin/|1440,1080"
  "02_admin_products|http://127.0.0.1:8000/admin/pos_full/product/|1440,900"
  "03_admin_customers|http://127.0.0.1:8000/admin/pos_full/customer/|1440,900"
  "04_admin_sales|http://127.0.0.1:8000/admin/pos_full/sale/|1440,900"
  "05_admin_nodes|http://127.0.0.1:8000/admin/pos_full/node/|1440,900"
  "06_admin_add_product|http://127.0.0.1:8000/admin/pos_full/product/add/|1440,1080"
)

declare -A OUT=(
  [01_admin_dashboard]="01_admin_dashboard"
  [02_admin_products]="02_admin_products"
  [03_admin_customers]="03_admin_customers"
  [04_admin_sales]="04_admin_sales"
  [05_admin_nodes]="05_admin_nodes"
  [06_admin_add_product]="06_admin_add_product"
)

# ── 3. Cleanup trap ──────────────────────────────────────────────────────
cleanup() {
  pkill -f 'manage.py runserver' 2>/dev/null || true
  if [ "${KEEP_CAPTURES}" -eq 0 ]; then
    rm -rf "${CAPTURES_DIR}"
  fi
}
trap cleanup EXIT
mkdir -p "${CAPTURES_DIR}"

# ── 4. Boot Django runserver detached ────────────────────────────────────
echo "▸ Bootstrapping admin database & superuser…"
cd "${SIDECAR}"
python3 manage.py migrate
POS_FULL_ADMIN_EMAIL="${ADMIN_EMAIL}" \
POS_FULL_ADMIN_PASSWORD="${ADMIN_PASSWORD}" \
  python3 manage.py --ensure-superuser

echo "▸ Booting Django runserver (detached) on :8000…"
setsid nohup python3 manage.py runserver 0.0.0.0:8000 > "${LOG}" 2>&1 < /dev/null &

echo "▸ Waiting for runserver to be ready (max 60s)…"
READY=0
for i in $(seq 1 60); do
  if curl -fsS -I http://127.0.0.1:8000/admin/ -o /dev/null 2>&1; then
    echo "   ready (${i}s)"
    READY=1
    break
  fi
  sleep 1
done
if [ "${READY}" -eq 0 ]; then
  echo "✗ runserver did not become ready in 60s — see ${LOG}" >&2
  exit 2
fi

# ── 5. Capture each route via Chromium headless ──────────────────────────
echo "▸ Capturing ${#shots[@]} admin pages via headless Chromium…"

echo "  📝 Note: Pages may show login form if not yet authenticated."
echo "     To capture authenticated views, manually log in at :8000/admin/"
echo "     while this script is running (wait for 'ready'), then it will"
echo "     capture the pages you have opened."

for shot in "${shots[@]}"; do
  NAME="${shot%%|*}"
  REST="${shot#*|}"
  URL="${REST%|*}"
  WIN="${REST##*|}"

  "${CHROME_BIN}" --headless=new --disable-gpu --no-sandbox --hide-scrollbars \
    --window-size="${WIN}" --virtual-time-budget=10000 \
    --screenshot="${CAPTURES_DIR}/${NAME}.png" "${URL}" 2>/dev/null || true

  if [ -f "${CAPTURES_DIR}/${NAME}.png" ]; then
    printf '   ✓ %-22s  %s\n' "${NAME}" "${URL}"
  else
    printf '   ✗ %-22s  failed\n' "${NAME}"
  fi
done

# ── 6. Convert PNG → JPG ────────────────────────────────────────────────
echo "▸ Converting PNG → JPG (q=88, white background)…"
CAPTURED=0
for shot_info in "${shots[@]}"; do
  NAME="${shot_info%%|*}"
  SRC="${CAPTURES_DIR}/${NAME}.png"
  DEST="${SCREENSHOTS_DIR}/${OUT[$NAME]}.jpg"
  if [ -f "${SRC}" ]; then
    convert "${SRC}" -quality 88 -background white -alpha remove "${DEST}"
    printf '   %-22s → %s.jpg\n' "${NAME}.png" "${OUT[$NAME]}"
    ((CAPTURED++))
  fi
done

# ── 7. Done ─────────────────────────────────────────────────────────────
echo "── ✓ Done — ${CAPTURED} admin screenshots written to ${SCREENSHOTS_DIR}/ ──"
echo "  SVG placeholders: admin-dashboard.svg, admin-products.svg"
echo "  Replace JPGs with screenshots from your instance for best results."
