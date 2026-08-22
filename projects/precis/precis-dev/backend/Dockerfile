FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/precis-main/backend:/app/precis-main/backend/apps \
    PATH=/app/projects/.venv/bin:$PATH \
    DJANGO_SETTINGS_MODULE=settings

WORKDIR /app

RUN apt-get update \
    && apt-get install --no-install-recommends -y build-essential ca-certificates curl gettext git libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv

COPY projects/pyproject.toml projects/uv.lock /app/projects/
COPY libs /app/libs
RUN uv sync --project /app/projects --no-install-project

COPY projects/assets /app/assets
COPY projects/precis/precis-main/backend /app/precis-main/backend
COPY projects/precis/precis-main/templates /app/precis-main/templates
# Compiled design system + favicon (produced by `make css` into
# assets/static/). STATICFILES_DIRS points at BASE_DIR/assets/static, so
# collectstatic needs this tree present in the image.
COPY projects/precis/precis-main/assets /app/precis-main/assets
# Site-level Env overrides (kept in parity with the other Precis sites).
COPY projects/precis/precis-main/Env /app/precis-main/Env
# Project-level config cascade (YAML defaults: site identity, admin, CSS panel,
# static-files reference) — the backend sources env-read defaults from these.
COPY projects/precis/precis-main/configs /app/precis-main/configs

WORKDIR /app/precis-main/backend
RUN mkdir -p assets/static assets/staticfiles assets/media \
    && python manage.py collectstatic --noinput

EXPOSE 8074

CMD ["gunicorn", "wsgi:application", "--bind", "0.0.0.0:8074", "--workers", "2", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]
