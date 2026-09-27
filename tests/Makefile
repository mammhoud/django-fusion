.PHONY: help all analyzer fragments library

help:
	@echo "tests targets: all analyzer fragments library"

# Uses the project's uv-managed environment (see ../pyproject.toml).
all:
	cd .. && uv run --extra test pytest

analyzer:
	cd .. && uv run --extra test pytest tests/analyzer

fragments:
	cd .. && uv run --extra test pytest tests/fragments

library:
	cd .. && uv run --extra test pytest tests/*.py
