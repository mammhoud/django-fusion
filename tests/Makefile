.PHONY: help all unit integration websites ctc structa vresume scripts vresume-pages
PYTHON ?= ../.venv/bin/python

help:
	@echo "tests targets: all unit integration websites ctc structa vresume scripts vresume-pages"

all:
	cd .. && ./.venv/bin/python -m pytest tests

unit:
	cd .. && ./.venv/bin/python -m pytest tests/unit

integration:
	cd .. && ./.venv/bin/python -m pytest tests/integration

websites: ctc structa vresume

ctc:
	cd ../ctc-research && ../.venv/bin/python -m pytest

structa:
	cd ../lms-demo && ../.venv/bin/python -m pytest


vresume:
	cd .. && ./.venv/bin/python manage.py --site=vresume check

scripts:
	$(MAKE) -C scripts $(filter-out $@,$(MAKECMDGOALS))

vresume-pages:
	$(MAKE) -C scripts vresume-pages

# Delegated subtargets are consumed by nested Makefiles.
.PHONY: list health containers production production-simple domains
list health containers production production-simple domains:
	@:
