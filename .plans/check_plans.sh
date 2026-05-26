#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

expected=(DEPLOY_CHECKLIST.md PROMPTS.md SPECIFICATION.md PLANS_VERIFICATION.md)
missing=()
for f in "${expected[@]}"; do
  if [[ ! -f "$ROOT_DIR/$f" ]]; then
    missing+=("$f")
  fi
done

if (( ${#missing[@]} > 0 )); then
  echo "Missing plan files: ${missing[*]}"
  exit 2
fi

echo "All plan files present in $ROOT_DIR"

for f in "${expected[@]}"; do
  echo "---- $f ----"
  head -n 3 "$ROOT_DIR/$f" || true
done

echo "Basic validation complete."
exit 0
