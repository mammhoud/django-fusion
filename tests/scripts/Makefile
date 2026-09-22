.PHONY: help list health websites containers production production-simple domains populate vresume-pages

PYTHON ?= ../../.venv/bin/python
BASE_URL ?= http://localhost:8000
VERBOSE ?= false
WEBSITE ?= all

help:
	@echo "Workspace script targets:"
	@echo "  make list              List available utility scripts"
	@echo "  make health            Run HTTP health-check script (BASE_URL=...)"
	@echo "  make websites          Run the workspace website pytest suite"
	@echo "  make containers        Run container shell test runner"
	@echo "  make production        Run production Python checks"
	@echo "  make production-simple Run simple production Python checks"
	@echo "  make domains           Run domain URL Python checks"
	@echo "  make populate          Populate data (WEBSITE=..., add ARGS=--dry-run)"
	@echo "  make vresume-pages     Run VResume page checks (BASE_URL=..., VERBOSE=true|false)"

list:
	@echo "=== dev/ ==="
	@find dev -maxdepth 1 -type f \( -name '*.sh' -o -name '*.py' \) | sort
	@echo "=== helpers/ ==="
	@find helpers -maxdepth 1 -type f \( -name '*.sh' -o -name '*.py' \) | sort
	@echo "=== staging/ ==="
	@find staging -maxdepth 1 -type f \( -name '*.sh' -o -name '*.py' \) | sort
	@echo "=== testing/ ==="
	@find testing -maxdepth 1 -type f \( -name '*.sh' -o -name '*.py' \) | sort

health:
	@bash dev/health-check.sh $(BASE_URL)

websites:
	@cd ../.. && uv run python -m pytest tests/websites -q

containers:
	@bash ../../tests/run_containers.sh

production:
	@$(PYTHON) staging/test_production.py

production-simple:
	@$(PYTHON) staging/test_production_simple.py

domains:
	@$(PYTHON) ../../tests/test_domain_urls.py

populate:
	@$(PYTHON) populate_site_data.py --site $(WEBSITE) $(ARGS)

vresume-pages:
	@bash dev/test_vresume_pages.sh $(BASE_URL) $(VERBOSE)
