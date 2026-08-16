#!/usr/bin/env bash
#
# scripts/dev/capture-formint-screenshots.sh
#
# Captures the Formint POS frontend and Unfold admin dashboard screenshots
# into Landing-Fusion's canonical related media directory for the README and product pages.
#
#   Frontend (headless Chromium, no auth):
#     01_frontend_home        → http://127.0.0.1:4321/
#     02_frontend_data        → http://127.0.0.1:4321/data/
#
#   Admin (Selenium + login as admin@formint.local / admin123):
#     03_admin_dashboard      → /admin/
#     04_admin_products       → /admin/pos_full/product/
#     05_admin_customers      → /admin/pos_full/customer/
#     06_admin_sales          → /admin/pos_full/sale/
#     07_admin_loyalty        → /admin/pos_full/clientcategory/
#     08_admin_settings       → /admin/pos_full/usersettings/
#
# Requires: chromium-browser/chromium, chromedriver, python3 + selenium,
#           ImageMagick (convert). Run `make env` first so :4321 + :8767 are up.
#
# Usage:
#   bash scripts/dev/capture-formint-screenshots.sh

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
RELATED_DIR="${ROOT}/../precis/precis-landing/backend/assets/static/related/formints"
MIRROR_DIR="${ROOT}/../precis/precis-landing/frontend/public/static/related/formints"
CAPTURES_DIR="${ROOT}/.tmp-screenshot-captures"
FE_BASE="http://127.0.0.1:4321"
ADMIN_BASE="http://127.0.0.1:8767"
ADMIN_USERNAME="admin"   # Django auth username (formint --ensure-superuser keeps 'admin')
ADMIN_PASSWORD="admin123"

CHROME_BIN="$(command -v chromium-browser || command -v chromium || echo /usr/bin/chromium-browser)"

cleanup() {
  if [ "${KEEP_CAPTURES:-0}" -eq 0 ]; then
    rm -rf "${CAPTURES_DIR}"
  fi
}
trap cleanup EXIT
mkdir -p "${CAPTURES_DIR}"

echo "▸ Frontend is ${FE_BASE}, Admin is ${ADMIN_BASE}"

# ── 1. Frontend captures (public, no auth) ───────────────────────────────
echo "▸ Capturing frontend pages…"
fe_shots=(
  "01_frontend_home|${FE_BASE}/|1440,1200"
  "02_frontend_data|${FE_BASE}/data/|1440,1200"
)
for shot in "${fe_shots[@]}"; do
  NAME="${shot%%|*}"; REST="${shot#*|}"
  URL="${REST%|*}"; WIN="${REST##*|}"
  "${CHROME_BIN}" --headless=new --disable-gpu --no-sandbox --hide-scrollbars \
    --window-size="${WIN}" --virtual-time-budget=10000 \
    --screenshot="${CAPTURES_DIR}/${NAME}.png" "${URL}" 2>/dev/null || true
  [ -f "${CAPTURES_DIR}/${NAME}.png" ] && echo "   ✓ ${NAME}" || echo "   ✗ ${NAME}"
done

# ── 2. Admin captures (Selenium login) — delegate to the standalone script ──
echo "▸ Capturing admin pages (Selenium login)…"
FORMINT_ADMIN_BASE="${ADMIN_BASE}" \
FORMINT_ADMIN_USERNAME="${ADMIN_USERNAME}" \
FORMINT_ADMIN_PASSWORD="${ADMIN_PASSWORD}" \
FORMINT_CAPTURE_DIR="${CAPTURES_DIR}" \
CHROME_BIN="${CHROME_BIN}" \
  python3 "${SCRIPT_DIR}/capture-admin-screens.py"

# ── 3. Convert PNG → JPG into the canonical related directory ─────────────
echo "▸ Converting PNG → JPG (q=88, white bg)…"
mkdir -p "${RELATED_DIR}" "${MIRROR_DIR}"
for mapping in \
  "01_frontend_home|standard-checkout" \
  "02_frontend_data|standard-operations" \
  "03_admin_dashboard|pro-admin-dashboard" \
  "04_admin_products|pro-admin-products" \
  "05_admin_customers|pro-admin-customers" \
  "06_admin_sales|pro-admin-sales" \
  "07_admin_loyalty|pro-admin-loyalty" \
  "08_admin_settings|pro-admin-settings"; do
  name="${mapping%%|*}"
  output="${mapping##*|}"
  convert "${CAPTURES_DIR}/${name}.png" -quality 88 -background white -alpha remove "${RELATED_DIR}/${output}.jpg"
  cp "${RELATED_DIR}/${output}.jpg" "${MIRROR_DIR}/${output}.jpg"
  echo "   ${name}.png → related/formints/${output}.jpg"
done

rm -rf "${CAPTURES_DIR}"
echo "── ✓ Screenshots written to Landing-Fusion related/formints/ ──"
