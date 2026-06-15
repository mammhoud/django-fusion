# Frontend asset delegation for the parent Django website.
.PHONY: help install build watch production purge analyze clean collectstatic build-collect

NPM ?= npm
WORKSPACE_ROOT := $(abspath ../..)
SITE_NAME := $(notdir $(abspath ..))
PROJECT_PATH ?= $(SITE_NAME)
ASSETS_MAKE := $(WORKSPACE_ROOT)/assets

help:
	@echo "$(SITE_NAME) asset targets delegate to $(ASSETS_MAKE)"
	@echo "  make build         Build this project's main assets"
	@echo "  make production    Build this project's production assets"
	@echo "  make watch         Watch this project's assets"
	@echo "  make collectstatic Collect this project's static files"
	@echo "  make clean         Remove this project's bundle artifacts"

install:
	@$(MAKE) -C "$(ASSETS_MAKE)" install

build:
	@PROJECT_PATH=$(PROJECT_PATH) $(MAKE) -C "$(ASSETS_MAKE)" build

watch:
	@PROJECT_PATH=$(PROJECT_PATH) $(MAKE) -C "$(ASSETS_MAKE)" watch

production:
	@PROJECT_PATH=$(PROJECT_PATH) $(MAKE) -C "$(ASSETS_MAKE)" production

purge:
	@PROJECT_PATH=$(PROJECT_PATH) $(MAKE) -C "$(ASSETS_MAKE)" purge

analyze:
	@PROJECT_PATH=$(PROJECT_PATH) $(MAKE) -C "$(ASSETS_MAKE)" analyze

collectstatic:
	@PROJECT_PATH=$(PROJECT_PATH) $(MAKE) -C "$(ASSETS_MAKE)" collectstatic-site

build-collect:
	@PROJECT_PATH=$(PROJECT_PATH) $(MAKE) -C "$(ASSETS_MAKE)" build-collect-site

clean:
	@PROJECT_PATH=$(PROJECT_PATH) $(MAKE) -C "$(ASSETS_MAKE)" clean-site
