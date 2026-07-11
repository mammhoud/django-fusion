# ============================================================
# Unified Workspace & Coolify Deployment Makefile
# Centralised command delegation for all deployment components
# ============================================================

SHELL := /bin/bash

#   make push-libs     – commit & push each lib submodule separately
#
# The .env file should contain:
#   github=ghp_xxxxxxxxxxxx  (or github_pat_..., or a classic token)
# -----------------------------------------------------------------
.PHONY: push push-libs push-lib pull sync

GITHUB_TOKEN ?=

# Multi-file POSIX-safe lookup. Order preserved by `cat ... | head -n 1`
# so the root .env wins. POSIX-only tools (no `grep -P`), so macOS /bin/sh
# works fine. Accepts `github=`, `GITHUB_TOKEN=`, or `GH_TOKEN=` keys.
_github_token_files := .env core/.env proxy/.env
_github_token := $(or \
	$(GITHUB_TOKEN), \
	$(shell cat $(_github_token_files) 2>/dev/null \
		| grep -E '^(github|GITHUB_TOKEN|GH_TOKEN)=' \
		| head -n 1 \
		| cut -d= -f2- \
		| tr -d "\042\047\040" ))

# Single auth gate. Every push/pull/sync target depends on this so the
# diagnostic lives in exactly one place. Lists the searched paths so the
# user knows where to drop their token.
.PHONY: require-github-token
require-github-token:
ifndef _github_token
	$(error GitHub token not found. Checked: env var GITHUB_TOKEN, then files $(_github_token_files). Set 'github=<token>' (or 'GITHUB_TOKEN=' / 'GH_TOKEN=') in one of those files, or export GITHUB_TOKEN.)
endif

push: require-github-token
	@echo "🚀 Pushing repo to origin..."
	@branch=$$(git branch --show-current); \
	remote_url=$$(git remote get-url origin 2>/dev/null || echo ''); \
	if [ -z "$$remote_url" ]; then \
		echo "❌ No remote 'origin' configured"; \
		exit 1; \
	fi; \
	echo "  Branch: $$branch"; \
	echo "  Remote: $$remote_url"; \
	GIT_ASKPASS=true git -c credential.helper='!printf "protocol=https\nhost=github.com\nusername=x-access-token\npassword=$(_github_token)\n"' \
	  push origin "$$branch" && echo "✅ Push complete" || echo "❌ Push failed"
	@$(MAKE) push-libs

# ── push-libs: commit + push each lib submodule ──
# Libs are now git submodules pointing to their GitHub repos:
#   django-fusion  → https://github.com/mammhoud/django-fusion.git
#   ceptor-ai      → https://github.com/mammhoud/ceptor-ai.git
# This target commits any local changes in each submodule and pushes.
push-libs: require-github-token
	@echo "📦 Pushing each lib submodule to its GitHub repo..."
	@for lib in $(APPLICATIONS_DIR)/libs/*/; do \
		lib_name=$$(basename $$lib); \
		echo ""; \
		echo "── $$lib_name ──"; \
		case "$$lib_name" in \
			django-fusion) lib_url="https://github.com/mammhoud/django-fusion.git" ;; \
			ceptor-ai)     lib_url="https://github.com/mammhoud/ceptor-ai.git" ;; \
			*) echo "  ⏭️  Unknown lib — skipping"; continue ;; \
		esac; \
		cd "$$lib" || continue; \
		git add -A; \
		if git diff --cached --quiet; then \
			echo "  ℹ️  No new changes to commit"; \
		else \
			git commit -m "chore($$lib_name): update from monorepo" 2>&1 || true; \
		fi; \
		git push "https://x-access-token:$(_github_token)@$${lib_url#https://}" HEAD:generic 2>&1 && \
			echo "  🚀 Pushed $$lib_name → $$lib_url" || \
			echo "  ❌ Push failed for $$lib_name"; \
		cd - >/dev/null; \
	done
	@echo ""
	@echo "✅ push-libs complete"

# ── push-lib <name>: push a single lib submodule by name ──
# Usage: make push-lib LIB=django-fusion
push-lib: require-github-token
ifndef LIB
	$(error Usage: make push-lib LIB=<django-fusion|ceptor-ai>)
endif
	@case "$(LIB)" in \
		django-fusion) lib_url="https://github.com/mammhoud/django-fusion.git" ;; \
		ceptor-ai)     lib_url="https://github.com/mammhoud/ceptor-ai.git" ;; \
		*) echo "❌ Unknown lib: $(LIB) (expected: django-fusion or ceptor-ai)"; exit 1 ;; \
	esac; \
	lib="$(APPLICATIONS_DIR)/libs/$(LIB)"; \
	cd "$$lib" || exit 1; \
	git add -A; \
	if git diff --cached --quiet; then \
		echo "  ℹ️  No new changes to commit"; \
	else \
		git commit -m "chore($(LIB)): update from monorepo" 2>&1 || true; \
	fi; \
	git push "https://x-access-token:$(_github_token)@$${lib_url#https://}" HEAD:generic && \
		echo "🚀 $(LIB) pushed to $$lib_url" || \
		echo "❌ Push failed"; \
	cd - >/dev/null

# ── pull: fetch + smart-merge origin into current branch ──
# Strategy matrix (computed from `git rev-list --count`):
#   ahead=0  behind=0  -> nothing to do, exit 0
#   ahead=0  behind>0  -> `git merge --ff-only` (the clean case)
#   ahead>0  behind=0  -> local-only commits, nothing to pull from origin
#   ahead>0  behind>0  -> diverged. Default = rebase local onto origin
#                         (PULL_MODE=merge switches to a merge commit instead).
# Uses the same `_github_token` as `make push`; aborts with a clear error
# if the auth is missing.
#
# --autostash is enabled on rebase so uncommitted local changes can be
# parked automatically; manual `git rebase --continue` / `--abort` is
# required if a real conflict surfaces, and the recipe prints that hint.
#
# Refuses to push back automatically; that's `make push`'s job.
pull: require-github-token
	@branch=$$(git branch --show-current); \
	if [ -z "$$branch" ]; then \
		echo "❌ not on a branch (detached HEAD?)"; exit 1; \
	fi; \
	remote=$$(git remote get-url origin 2>/dev/null || echo ''); \
	if [ -z "$$remote" ]; then \
		echo "❌ no remote 'origin' configured"; exit 1; \
	fi; \
	echo "📥 Fetching origin/$$branch..."; \
	git -c credential.helper='!printf "protocol=https\nhost=github.com\nusername=x-access-token\npassword=$(_github_token)\n"' \
	  fetch origin "$$branch" || { echo "❌ fetch failed"; exit 1; }; \
	ahead=$$(git rev-list --count "origin/$$branch"..HEAD 2>/dev/null || echo 0); \
	behind=$$(git rev-list --count HEAD.."origin/$$branch" 2>/dev/null || echo 0); \
	echo "  Local:  $$branch @ $$(git rev-parse --short HEAD)"; \
	echo "  Remote: origin/$$branch @ $$(git rev-parse --short origin/$$branch)"; \
	echo "  Ahead: $$ahead   Behind: $$behind"; \
	if [ "$$behind" = "0" ]; then \
		if [ "$$ahead" = "0" ]; then \
			echo "✅ already up to date"; exit 0; \
		fi; \
		echo "  ℹ️  local-only commits; nothing to pull from origin"; exit 0; \
	fi; \
	if [ "$$ahead" = "0" ]; then \
		echo "✅ fast-forwarding..."; \
		git merge --ff-only "origin/$$branch" && \
			echo "✅ pull complete (fast-forward)" || \
			echo "❌ pull failed"; \
	else \
		echo "  ⚠️  branches diverged ($$ahead local ahead, $$behind remote ahead)"; \
		mode=$${PULL_MODE:-rebase}; \
		case "$$mode" in \
			rebase) \
				echo "  ↪️  rebasing local onto origin/$$branch (PULL_MODE=rebase, --autostash)..."; \
				git -c rebase.autoStash=true rebase "origin/$$branch" && \
					echo "✅ pull complete (rebase)" || \
					{ echo "❌ rebase failed"; echo "   resolve with: git rebase --continue | git rebase --abort"; exit 1; }; \
				;; \
			merge) \
				echo "  ↪️  merging origin/$$branch into $$branch (PULL_MODE=merge)..."; \
				git merge --no-ff "origin/$$branch" && \
					echo "✅ pull complete (merge)" || \
					{ echo "❌ merge failed"; echo "   resolve with: git merge --continue | git merge --abort"; exit 1; }; \
				;; \
			*) echo "❌ PULL_MODE must be 'rebase' or 'merge' (got: '$$mode')"; exit 1 ;; \
		esac; \
	fi

# ── sync: bidirectional sync of local <-> origin ──
# Default recipe: pull (rebase) then push.
# Override knobs:
#   SYNC_MODE=merge          - merge remote into local instead of rebasing
#   SYNC_SKIP_PUSH=1         - only pull, no push (handy for first-time users)
#   PULL_MODE=rebase|merge   - forwarded to make pull as well
# Reuses $(_github_token) and all of `make push`'s auth machinery.
sync: require-github-token
	@echo "🔄 Syncing local with origin..."; \
	mode=$${SYNC_MODE:-rebase}; \
	if [ "$$mode" = "rebase" ]; then \
		$(MAKE) --no-print-directory pull PULL_MODE=rebase || exit 1; \
	else \
		$(MAKE) --no-print-directory pull PULL_MODE=merge || exit 1; \
	fi; \
	if [ "$$SYNC_SKIP_PUSH" = "1" ]; then \
		echo "  ℹ️  SYNC_SKIP_PUSH=1 — not pushing back to origin"; \
	else \
		echo ""; \
