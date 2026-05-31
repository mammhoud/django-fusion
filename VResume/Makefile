.PHONY: help check migrate collectstatic shell build-assets build-assets-dev main-assets assets scripts workspace-script test workspace-test test-pages runserver

help:
	@echo "vResume workspace commands"
	@echo "  make check             Run Django checks for vresume"
	@echo "  make migrate           Apply migrations for vresume"
	@echo "  make collectstatic     Collect static files for vresume"
	@echo "  make build-assets      Build production frontend bundle"
	@echo "  make build-assets-dev  Build development frontend bundle"
	@echo "  make test              Run workspace vresume tests"
	@echo "  make test-pages        Run shell page checks through tests/scripts"
	@echo "  make scripts           Delegate to workspace test scripts"
	@echo "  make shell             Open Django shell for vresume"
	@echo "  make runserver         Run vresume locally on port 5072"

check:
	@cd .. && ./.venv/bin/python manage.py --site=vresume check

migrate:
	@cd .. && ./.venv/bin/python manage.py --site=vresume migrate

collectstatic:
	@cd .. && ./.venv/bin/python manage.py --site=vresume collectstatic --noinput

build-assets main-assets:
	@cd .. && $(MAKE) -C assets PROJECT_PATH=vresume build-vresume

build-assets-dev:
	@cd .. && PROJECT_PATH=vresume npm --prefix assets run build:dev

assets:
	@$(MAKE) -C assets $(filter-out $@,$(MAKECMDGOALS))

scripts workspace-script:
	@cd .. && $(MAKE) scripts $(filter-out $@,$(MAKECMDGOALS))

test workspace-test:
	@cd .. && $(MAKE) -C tests vresume

test-pages:
	@cd .. && $(MAKE) -C tests/scripts vresume-pages

shell:
	@cd .. && ./.venv/bin/python manage.py --site=vresume shell

runserver:
	@cd .. && ./.venv/bin/python manage.py --site=vresume runserver 0.0.0.0:5072

# Delegated subtargets are consumed by nested Makefiles.
.PHONY: list health containers production production-simple domains vresume-pages
list health containers production production-simple domains vresume-pages:
	@:
