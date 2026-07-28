# CRM assets — delegates to workspace asset scripts
.PHONY: build build-dev watch clean collectstatic

WORKSPACE_ASSETS := $(abspath ../../assets)

build:
	npm --prefix $(WORKSPACE_ASSETS) run build:crm

build-dev:
	npm --prefix $(WORKSPACE_ASSETS) run build:dev:crm

watch:
	npm --prefix $(WORKSPACE_ASSETS) run watch:crm

clean:
	npm --prefix $(WORKSPACE_ASSETS) run clean:crm

collectstatic:
	npm --prefix $(WORKSPACE_ASSETS) run collectstatic:crm
