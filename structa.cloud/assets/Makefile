# Frontend asset delegation for the parent Django website.
.PHONY: install build watch production purge analyze clean

NPM ?= npm
NPX ?= npx
ROOT := $(abspath ..)

install:
	@if [ -f "$(ROOT)/package.json" ]; then $(NPM) --prefix "$(ROOT)" install; else echo "No package.json in $(ROOT)"; fi

build:
	@if [ -f "$(ROOT)/package.json" ]; then NODE_ENV=development $(NPM) --prefix "$(ROOT)" run build; else echo "No package.json in $(ROOT)"; fi

watch:
	@if [ -f "$(ROOT)/package.json" ]; then NODE_ENV=development $(NPM) --prefix "$(ROOT)" run dev; else echo "No package.json in $(ROOT)"; fi

production:
	@if [ -f "$(ROOT)/package.json" ]; then NODE_ENV=production $(NPM) --prefix "$(ROOT)" run build; else echo "No package.json in $(ROOT)"; fi

purge:
	@if [ -f "$(ROOT)/purgecss.config.js" ]; then NODE_ENV=production $(NPX) --prefix "$(ROOT)" purgecss --config "$(ROOT)/purgecss.config.js"; else echo "No purgecss.config.js in $(ROOT)"; fi

analyze:
	@if [ -f "$(ROOT)/assets/static/css/master.css" ]; then $(NPX) --prefix "$(ROOT)" cssnano --no-map "$(ROOT)/assets/static/css/master.css" | $(NPX) --prefix "$(ROOT)" cssstats; else echo "No master.css to analyze"; fi

clean:
	@rm -rf bundles staticfiles .cache
	@echo "Frontend artifacts cleaned"
