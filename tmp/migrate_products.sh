#!/usr/bin/env bash
set -e
cd /home/structa.cloud
UV_BIN=$(command -v uv || echo /root/.local/bin/uv)

echo '════════ landing-fusion: makemigrations + migrate ════════'
cd projects/precis/landi/backend
"$UV_BIN" --project .. run --frozen python manage.py makemigrations content 2>&1 | tail -6
"$UV_BIN" --project .. run --frozen python manage.py migrate 2>&1 | tail -4

echo '════════ precis: makemigrations + migrate ════════'
cd /home/structa.cloud/projects/precis/main/backend
"$UV_BIN" --project .. run --frozen python manage.py makemigrations content learning 2>&1 | tail -8
"$UV_BIN" --project .. run --frozen python manage.py migrate 2>&1 | tail -4

echo '════════ ruff both projects ════════'
cd /home/structa.cloud/projects/precis/landi/backend
"$UV_BIN" --project .. run --frozen ruff check apps/content/models/products.py apps/pages/management/commands/seed_pages.py apps/pages/models.py apps/pages/api.py settings.py 2>&1 | tail -3
cd /home/structa.cloud/projects/precis/main/backend
"$UV_BIN" --project .. run --frozen ruff check apps/content/models/products.py apps/content/models/course.py apps/learning/models/courses/info.py apps/learning/api/courses.py apps/pages/products/api.py apps/core/management/commands/setup_wagtail_home.py apps/pages/pages/landing_api.py settings.py 2>&1 | tail -4

echo '════════ manage.py check both ════════'
cd /home/structa.cloud/projects/precis/landi/backend
"$UV_BIN" --project .. run --frozen python manage.py check 2>&1 | tail -3
cd /home/structa.cloud/projects/precis/main/backend
"$UV_BIN" --project .. run --frozen python manage.py check 2>&1 | tail -3
