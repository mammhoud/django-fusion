FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/precis-main/backend:/app/precis-main/backend/apps:/app/libs/django-fusion/src \
    DJANGO_SETTINGS_MODULE=settings \
    SERVER_ENV=production

WORKDIR /app

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        build-essential ca-certificates curl gettext git libpq-dev \
        && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv \
    && uv sync --project /app/projects --no-install-project

COPY projects/pyproject.toml projects/uv.lock /app/projects/
COPY libs /app/libs
COPY projects/manage.py /app/manage.py
COPY projects/Clients/structa.cloud/backend /app/precis-main/backend
COPY projects/Clients/configs /app/precis-main/configs
COPY projects/assets /app/precis-main/assets

WORKDIR /app/precis-main/backend
RUN mkdir -p assets/static assets/staticfiles assets/media \
    && python manage.py collectstatic --noinput

EXPOSE 8074

CMD ["gunicorn", "wsgi:application", "--bind", "0.0.0.0:8074", "--workers", "2", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]
