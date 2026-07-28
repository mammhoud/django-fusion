.PHONY: help build main-assets production watch clean collectstatic build-collect

help:
	@echo "vResume assets are built by the workspace-level assets package."
	@echo "  make build       Build vResume production assets"
	@echo "  make production  Alias for build"
	@echo "  make watch       Run workspace webpack watch for vResume"
	@echo "  make clean       Remove vResume bundles"

build main-assets:
	@cd ../.. && $(MAKE) -C assets PROJECT_PATH=vresume build-vresume

production: build

watch:
	@cd ../.. && PROJECT_PATH=vresume npm --prefix assets run watch

collectstatic:
	@cd ../.. && $(MAKE) -C assets PROJECT_PATH=vresume DJANGO_SITE=vresume collectstatic-site

build-collect: build collectstatic

clean:
	@cd ../.. && $(MAKE) -C assets PROJECT_PATH=vresume clean-site
