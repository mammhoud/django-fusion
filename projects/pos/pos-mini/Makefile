# POS Mini Makefile — Rust/Diesel only, no sidecar
#
# Targets:
#   make setup    Install Rust dependencies
#   make dev      Development mode (hot reload)
#   make build    Production build
#   make clean    Clean build artifacts
#   make test     Run Rust tests

.PHONY: setup dev build clean test

CARGO = cargo
TAURI_DIR = src-tauri

setup:
	@echo "── Installing Rust dependencies ──"
	cd $(TAURI_DIR) && $(CARGO) fetch
	@echo "Done. Run 'make dev' to start."

dev:
	@echo "── Starting POS Mini (dev mode) ──"
	cd $(TAURI_DIR) && $(CARGO) tauri dev

build:
	@echo "── Building POS Mini ──"
	cd $(TAURI_DIR) && $(CARGO) tauri build

clean:
	@echo "── Cleaning build artifacts ──"
	cd $(TAURI_DIR) && $(CARGO) clean
	rm -f restaurant.db

test:
	@echo "── Running Rust tests ──"
	cd $(TAURI_DIR) && $(CARGO) test

db-reset:
	@echo "── Resetting database ──"
	rm -f restaurant.db
	@echo "Database reset. Run 'make dev' to recreate."
