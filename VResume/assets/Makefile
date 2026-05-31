.PHONY: help build production watch clean

help:
	@echo "vResume assets are built by the workspace-level assets package."
	@echo "  make build       Build vResume production assets"
	@echo "  make production  Alias for build"
	@echo "  make watch       Run workspace webpack watch for vResume"
	@echo "  make clean       Remove vResume bundles"

build:
	@cd ../.. && npm --prefix assets run build:vresume

production: build

watch:
	@cd ../.. && PROJECT_PATH=vresume npm --prefix assets run watch

clean:
	@cd ../.. && npm --prefix assets run clean:vresume
