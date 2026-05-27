.PHONY: help all unit integration websites ctc structa
PYTHON ?= ../.venv/bin/python

help:
	@echo "tests targets: all unit integration websites ctc structa"

all:
	$(PYTHON) -m pytest

unit:
	$(PYTHON) -m pytest tests/unit

integration:
	$(PYTHON) -m pytest tests/integration

websites: ctc structa

ctc:
	cd ../ctc-research.com && ../.venv/bin/python -m pytest

structa:
	cd ../structa.cloud && ../.venv/bin/python -m pytest
