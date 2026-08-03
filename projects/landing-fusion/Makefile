# landing-fusion — project-level orchestration
# Usage: make dev | make build | make check | make install

NODE_BIN := $(shell ls -d $(HOME)/.nvm/versions/node/v22.* 2>/dev/null | sort -V | tail -1)/bin
export PATH := $(NODE_BIN):$(PATH)

.PHONY: install dev build preview check clean

install:
	npm install

dev:
	npm run dev

build:
	npm run build

preview:
	npm run preview

check:
	npm run check

clean:
	rm -rf dist .astro node_modules
