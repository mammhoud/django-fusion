PYTHON ?= python
MANAGE := $(PYTHON) manage.py

.PHONY: check migrate runserver shell
check:
	$(MANAGE) check
migrate:
	$(MANAGE) migrate
runserver:
	$(MANAGE) runserver 127.0.0.1:5073
shell:
	$(MANAGE) shell
