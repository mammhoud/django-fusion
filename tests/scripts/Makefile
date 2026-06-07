.PHONY: help list health websites containers production production-simple domains populate vresume-pages

PYTHON ?= ../../.venv/bin/python
BASE_URL ?= http://localhost:8000
VERBOSE ?= false
WEBSITE ?= all

help:
	@echo "Workspace script targets:"
	@echo "  make list              List available utility scripts"
	@echo "  make health            Run HTTP health-check script"
	@echo "  make websites          Run website shell test runner (WEBSITE=all|ctc|structa|vresume)"
	@echo "  make containers        Run container shell test runner"
	@echo "  make production        Run production Python checks"
	@echo "  make production-simple Run simple production Python checks"
	@echo "  make domains           Run domain URL Python checks"
	@echo "  make populate          Populate data (WEBSITE=..., add ARGS=--dry-run)"
	@echo "  make vresume-pages     Run VResume page checks (BASE_URL=..., VERBOSE=true|false)"

list:
	@echo "=== deployment/ ===" && find deployment -maxdepth 1 -type f \( -name '*.sh' -o -name '*.py' \) | sort
	@echo "=== validation/ ===" && find validation -maxdepth 1 -type f \( -name '*.sh' -o -name '*.py' \) | sort
	@echo "=== utilities/ ===" && find utilities -maxdepth 1 -type f \( -name '*.sh' -o -name '*.py' \) | sort
	@echo "=== helpers/  ===" && find helpers -maxdepth 1 -type f \( -name '*.sh' -o -name '*.py' \) | sort

health:
	@bash helpers/health-check.sh $(BASE_URL)

websites:
	@bash helpers/run_website_tests.sh $(WEBSITE)

containers:
	@bash helpers/run_container_tests.sh $(WEBSITE)

production:
	@$(PYTHON) validation/test_production.py

production-simple:
	@$(PYTHON) validation/test_production_simple.py

domains:
	@$(PYTHON) validation/test_domain_urls.py

populate:
	@$(PYTHON) utilities/populate_site_data.py --site $(WEBSITE) $(ARGS)

vresume-pages:
	@bash helpers/test_vresume_pages.sh $(BASE_URL) $(VERBOSE)
