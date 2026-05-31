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
	@find . -maxdepth 1 -type f \( -name '*.sh' -o -name '*.py' \) -printf '%f\n' | sort

health:
	@./health-check.sh $(BASE_URL)

websites:
	@./run_website_tests.sh $(WEBSITE)

containers:
	@./run_container_tests.sh $(WEBSITE)

production:
	@$(PYTHON) test_production.py

production-simple:
	@$(PYTHON) test_production_simple.py

domains:
	@$(PYTHON) test_domain_urls.py

populate:
	@$(PYTHON) populate_site_data.py --site $(WEBSITE) $(ARGS)

vresume-pages:
	@./test_vresume_pages.sh $(BASE_URL) $(VERBOSE)
