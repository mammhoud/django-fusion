# docs/Makefile — Docus documentation build, serve, validate, and deploy
.PHONY: help install build build-static serve preview check clean deploy

.DEFAULT_GOAL := help

DocusDir := docus

help: ## Show documentation commands
	@printf '%s\n' \
		'Docus documentation commands:' \
		'  make install       Install Docus dependencies' \
		'  make build         Build the Docus Nuxt server' \
		'  make build-static  Generate an optional static export' \
		'  make serve         Run the Docus development server' \
		'  make preview       Preview the generated server output' \
		'  make check         Validate Docus configuration and locale sources' \
		'  make deploy        Rebuild the Docus + shared-media services' \
		'  make clean         Remove generated Docus output'

install: ## Install Docus dependencies
	cd $(DocusDir) && npm install

build: ## Build the Docus Nuxt server
	cd $(DocusDir) && npm run build

build-static: ## Generate an optional static Docus export
	cd $(DocusDir) && npm run build:static

serve: ## Serve Docus locally at the /docs/ base path
	cd $(DocusDir) && npm run dev

preview: ## Preview the generated Docus server output
	cd $(DocusDir) && npm run preview

check: ## Validate Docus configuration and locale sources
	@test -f $(DocusDir)/nuxt.config.ts
	@test -f $(DocusDir)/app.config.ts
	@test -f $(DocusDir)/ar-content/index.md
	@test -f $(DocusDir)/ar-content/guides/quickstart.md
	@test -f $(DocusDir)/ar-content/guides/deployment.md
	@node --check $(DocusDir)/scripts/prepare-content.mjs
	@grep -q "@nuxtjs/i18n" $(DocusDir)/package.json
	@grep -q "code: 'ar'" $(DocusDir)/nuxt.config.ts
	@echo 'Docus configuration and English/Arabic source checks passed.'

deploy: ## Rebuild the Docus and shared-media services
	docker compose -f ../applications/proxy/docker-compose.nginx.yml build docus shared-media

clean: ## Remove generated Docus output and content
	rm -rf $(DocusDir)/content $(DocusDir)/.nuxt $(DocusDir)/.output $(DocusDir)/dist
