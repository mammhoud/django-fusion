# Loop-CRM backend image — Django + django-fusion on the workspace base.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/app/projects/.venv/bin:$PATH

WORKDIR /app

# The workspace uv project owns the dependency set; copy the minimum to sync.
COPY projects/pyproject.toml projects/uv.lock /app/projects/
COPY libs/django-fusion /app/libs/django-fusion
COPY projects/loop-crm /app/projects/loop-crm

RUN pip install --no-cache-dir uv \
    && cd /app/projects \
    && uv sync --no-install-project

ENV PYTHONPATH=/app/projects/loop-crm/backend:/app/projects/loop-crm/backend/apps

WORKDIR /app/projects/loop-crm/backend

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
