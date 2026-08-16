.PHONY: help all core unit integration websites ctc structa vresume scripts vresume-pages
PYTHON ?= ../.venv/bin/python

help:
	@echo "tests targets: all core unit integration websites ctc structa vresume scripts vresume-pages"

all:
	cd .. && ./.venv/bin/python -m pytest tests

core:
	cd .. && ./.venv/bin/python -m pytest tests/core

unit:
	cd .. && ./.venv/bin/python -m pytest tests/unit

integration:
	cd .. && ./.venv/bin/python -m pytest tests/integration

websites: ctc structa vresume

ctc:
	cd .. && ./.venv/bin/python -m pytest $(shell if [ -d tests/websites/precis-ctc ]; then echo tests/websites/precis-ctc; elif [ -d projects/precis-ctc ]; then echo projects/precis-ctc; else echo tests/unit; fi)

structa:
	cd .. && ./.venv/bin/python -m pytest $(shell if [ -d tests/websites/structa ]; then echo tests/websites/structa; elif [ -d projects/lms ]; then echo projects/lms; else echo tests/unit; fi)

vresume:
	cd .. && ./.venv/bin/python -m pytest tests/websites/vresume

scripts:
	$(MAKE) -C scripts $(filter-out $@,$(MAKECMDGOALS))

vresume-pages:
	$(MAKE) -C scripts vresume-pages

# Delegated subtargets are consumed by nested Makefiles.
.PHONY: list health containers production production-simple domains
list health containers production production-simple domains:
	@:
