#!/bin/bash
# Live check: home page learning sections at precis-landing + precis
cd /home/structa.cloud

# ── precis-landing :8074 ──
tmux kill-session -t hcheck_lf 2>/dev/null
tmux new-session -d -s hcheck_lf 'cd /home/structa.cloud/projects/precis/landi/backend && PORT=8074 make dev > /tmp/hcheck_lf.log 2>&1'

# ── precis :8079 ──
tmux kill-session -t hcheck_pr 2>/dev/null
tmux new-session -d -s hcheck_pr 'cd /home/structa.cloud/projects/precis/precis-lms/backend && PORT=8079 make dev > /tmp/hcheck_pr.log 2>&1'

sleep 14

echo "=== precis-landing home (full page) ==="
curl -s http://127.0.0.1:8074/ --max-time 12 -o /tmp/lf_home.html && echo "  size: $(wc -c < /tmp/lf_home.html)"
echo "  LEARNING/PREVIEW count: $(grep -o 'LEARNING / PREVIEW' /tmp/lf_home.html | wc -l)"
echo "  PUBLIC CATALOG count: $(grep -o 'PUBLIC CATALOG' /tmp/lf_home.html | wc -l)"
echo "  learning-kicker count: $(grep -o 'learning-kicker' /tmp/lf_home.html | wc -l)"
echo "  featured-courses/section--featured count: $(grep -o 'section--featured-courses' /tmp/lf_home.html | wc -l)"

echo
echo "=== precis-landing home (HTMX fragment) ==="
curl -s http://127.0.0.1:8074/ -H 'HX-Request: true' --max-time 12 -o /tmp/lf_frag.html && echo "  size: $(wc -c < /tmp/lf_frag.html)"
echo "  LEARNING/PREVIEW count: $(grep -o 'LEARNING / PREVIEW' /tmp/lf_frag.html | wc -l)"
echo "  learning-kicker count: $(grep -o 'learning-kicker' /tmp/lf_frag.html | wc -l)"

echo
echo "=== precis home (full page) ==="
curl -s http://127.0.0.1:8079/ --max-time 12 -o /tmp/pr_home.html && echo "  size: $(wc -c < /tmp/pr_home.html)"
echo "  LEARNING count: $(grep -o 'LEARNING' /tmp/pr_home.html | wc -l)"
echo "  learning-kicker count: $(grep -o 'learning-kicker' /tmp/pr_home.html | wc -l)"
echo "  featured-courses count: $(grep -o 'featured-courses' /tmp/pr_home.html | wc -l)"
echo "  section--featured-courses count: $(grep -o 'section--featured-courses' /tmp/pr_home.html | wc -l)"
echo "  PUBLIC CATALOG count: $(grep -o 'PUBLIC CATALOG' /tmp/pr_home.html | wc -l)"
echo "  hero sections: $(grep -o 'class=\"hero' /tmp/pr_home.html | wc -l)"

echo
echo "=== precis home (HTMX fragment) ==="
curl -s http://127.0.0.1:8079/ -H 'HX-Request: true' --max-time 12 -o /tmp/pr_frag.html && echo "  size: $(wc -c < /tmp/pr_frag.html)"
echo "  featured-courses count: $(grep -o 'featured-courses' /tmp/pr_frag.html | wc -l)"
echo "  LEARNING count: $(grep -o 'LEARNING' /tmp/pr_frag.html | wc -l)"

echo
echo "=== first 400 chars of each home (title area) ==="
echo "-- lf --"; head -c 300 /tmp/lf_home.html | tr '\n' ' '; echo
echo "-- pr --"; head -c 300 /tmp/pr_home.html | tr '\n' ' '; echo

tmux kill-session -t hcheck_lf 2>/dev/null
tmux kill-session -t hcheck_pr 2>/dev/null
echo "DONE"
