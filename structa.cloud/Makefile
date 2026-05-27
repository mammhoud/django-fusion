.PHONY: help check run-dev run-gunicorn migrations migrate dbshell showmigrations collectstatic build-assets
PYTHON ?= ../.venv/bin/python
MANAGE ?= $(PYTHON) manage.py

help:
	@echo "structa.cloud: check run-dev run-gunicorn migrations migrate dbshell showmigrations collectstatic build-assets"

check:
	$(MANAGE) check

run-dev:
	$(MANAGE) runserver 0.0.0.0:5071

run-gunicorn:
	$(PYTHON) -m gunicorn www.wsgi:application --bind 0.0.0.0:5071 --workers 2

migrations:
	$(MANAGE) makemigrations

migrate:
	$(MANAGE) migrate

dbshell:
	$(MANAGE) dbshell

showmigrations:
	$(MANAGE) showmigrations

collectstatic:
	$(MANAGE) collectstatic --noinput

build-assets:
	npm run build && $(MAKE) collectstatic
