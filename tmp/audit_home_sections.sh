#!/bin/bash
cd /home/structa.cloud

echo "=== 1. Exact marker scan (templates + astro, both projects) ==="
grep -rn "PUBLIC CATALOG\|learning-hero\|LEARNING" \
  projects/landing-fusion/backend/apps --include='*.html' 2>/dev/null | grep -v migrations | head -15
echo "--- precis backend ---"
grep -rn "PUBLIC CATALOG\|learning-hero\|LEARNING\|catalog" \
  projects/precis/backend/apps --include='*.html' 2>/dev/null | grep -v migrations | head -15

echo
echo "=== 2. landing-fusion home partial (page_content.html) learning bits ==="
grep -n "LEARNING\|learning\|catalog\|teaser\|hero" \
  projects/landing-fusion/backend/apps/pages/templates/pages/partials/page_content.html 2>/dev/null | head -12

echo
echo "=== 3. precis home template candidates ==="
find projects/precis/backend/apps -path '*templates*home*' -name '*.html' 2>/dev/null | head -10
find projects/precis/backend -name 'home.html' -o -name 'home*.html' 2>/dev/null | grep -v migrations | head -8

echo
echo "=== 4. landing-fusion index.astro home sections (kicker markers) ==="
grep -noE "tag-marker[^>]*>[^<]*" projects/landing-fusion/frontend/src/pages/index.astro 2>/dev/null | head -12
echo "--- precis index.astro ---"
grep -noE "tag-marker[^>]*>[^<]*" projects/precis/frontend/src/pages/index.astro 2>/dev/null | head -12

echo
echo "=== 5. precis frontend home learning references ==="
grep -rn "learning\|Learning\|catalog\|Catalog" projects/precis/frontend/src/pages/index.astro 2>/dev/null | head -10

echo
echo "DONE"
