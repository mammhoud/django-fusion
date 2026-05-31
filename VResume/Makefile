.PHONY: help check migrate collectstatic shell build-assets build-assets-dev runserver

help:
	@echo "vResume workspace commands"
	@echo "  make check             Run Django checks for vresume"
	@echo "  make migrate           Apply migrations for vresume"
	@echo "  make collectstatic     Collect static files for vresume"
	@echo "  make build-assets      Build production frontend bundle"
	@echo "  make build-assets-dev  Build development frontend bundle"
	@echo "  make shell             Open Django shell for vresume"
	@echo "  make runserver         Run vresume locally on port 5072"

check:
	@cd .. && ./.venv/bin/python manage.py --site=vresume check

migrate:
	@cd .. && ./.venv/bin/python manage.py --site=vresume migrate

collectstatic:
	@cd .. && ./.venv/bin/python manage.py --site=vresume collectstatic --noinput

build-assets:
	@cd .. && npm --prefix assets run build:vresume

build-assets-dev:
	@cd .. && PROJECT_PATH=vresume npm --prefix assets run build:dev

shell:
	@cd .. && ./.venv/bin/python manage.py --site=vresume shell

runserver:
	@cd .. && ./.venv/bin/python manage.py --site=vresume runserver 0.0.0.0:5072
