# structa.cloud — Full Execution Plan with Phases

**Monorepo:** mammhoud/ceptor-ai (`generic` branch)  
**Scope:** Local dev env → both library repos (django-fusion, ceptor-ai) with correct push; docs dedup; asset/template/tag diagnostics  
**Audience:** Local dev, not yet server/deployment operators (those need `docker compose` and actual env credentials)

This plan is **numbered, phased, and designed to catch issues early** — each phase includes validation checks before proceeding to the next. **Do not skip validation phases** — they catch the problems that cause silent failures later (broken imports, missing static files, wrong template resolution order).

---

## PHASE 0: Baseline Diagnostics (15–30 min)

**Goal:** Understand the current state before making any changes. This phase is read-only and produces diagnostic reports you'll use in later phases.

### 0.1 — Asset & Static Files Check

**Task:** Map all static file sources, template sources, and their resolution order.

```bash
# From repo root (where docker-compose.yml is)

# 1. List all app static/template paths
echo "=== Static files by app ===" && for app in applications/{ctc-research,lms,VResume,crm,cypercloud}; do
  [ -d "$app/static" ] && echo "$app: $(find $app/static -type f | wc -l) files"
  [ ! -d "$app/static" ] && echo "$app: NO static/ directory"
done

# 2. Check if webpack is configured
echo "=== Webpack status ===" && \
  [ -f webpack/webpack.config.js ] && echo "webpack.config.js exists" || echo "NO webpack config" && \
  [ -f webpack/package.json ] && echo "webpack/package.json exists" || echo "NO webpack package.json"

# 3. Check Docker volumes for static/media
echo "=== Global volumes (docker-compose.yml) ===" && \
  grep -E "^\s+\w+-static:|^\s+\w+-media:" docker-compose.yml

# 4. Check proxy/Traefik for static file routes
echo "=== Traefik routes for /static/ ===" && \
  grep -rn "/static\|/media\|static-files" proxy/ 2>/dev/null | head -20

# 5. Check each app's URL config for STATIC_URL serving
echo "=== App URL patterns mentioning static ===" && \
  for app in ctc-research lms VResume crm cypercloud; do
    [ -f "applications/$app/www/urls.py" ] && grep -n "static\|media" "applications/$app/www/urls.py" || echo "$app: no www/urls.py"
  done
```

**What to look for:**
- Are `static/` directories present in all five apps?
- Is webpack configured and present?
- Are docker-compose volumes (`crm-static`, `customizer-static`, etc.) defined?
- Does Traefik have routes for `/static/` and `/media/` (or does it serve directly from nginx)?
- Does each app's `urls.py` import and use Django's `static()` helper?

**Save output to:** `reports/phase-0-asset-baseline.txt`

### 0.2 — Template Resolution Order Check

**Task:** Map template loader configuration and resolution cascade.

```bash
# From repo root

echo "=== Template configuration (TEMPLATES setting) ===" && \
  grep -A 30 "TEMPLATES = \[" applications/configs/settings/conf.py

echo "=== Each site's LOCAL_TEMPLATES_DIRS in settings.py ===" && \
  for app in ctc-research lms VResume crm cypercloud; do
    echo "-- $app --"
    grep -B2 -A2 "TEMPLATES_DIRS\|templates" "applications/$app/settings.py" 2>/dev/null | head -20
  done

echo "=== Template loader order (APP_DIRS, loaders) ===" && \
  grep -n "APP_DIRS\|loaders" applications/configs/settings/conf.py | head -30

echo "=== Check if jinja2 is configured ===" && \
  grep -n "jinja2\|OPTIONS" applications/configs/settings/conf.py | head -20
```

**What to look for:**
- Is `APP_DIRS: True` enabled? (affects where Django looks for `app/templates/`)
- What's the order of `TEMPLATES_DIRS`? (typically: site-local, shared assets, django defaults)
- Is Jinja2 configured alongside Django templates?
- Are plugin templates discoverable?

**Save output to:** `reports/phase-0-template-resolution.txt`

### 0.3 — django_fusion & django_osoul Tags Check

**Task:** Verify component tag registration and availability.

```bash
# From repo root

echo "=== Check django_fusion installed in INSTALLED_APPS ===" && \
  grep -rn "django_fusion" applications/configs/ applications/*/settings.py

echo "=== Check django_osoul installed in INSTALLED_APPS ===" && \
  grep -rn "django_osoul" applications/configs/ applications/*/settings.py

echo "=== Check if component tags are registered ===" && \
  grep -rn "register_default_partials\|load components\|load comp" \
    applications/*/templates/ 2>/dev/null | head -20

echo "=== Check builtins config (auto-loads {% comp %} without {% load %}) ===" && \
  grep -B5 -A5 "'builtins'" applications/configs/settings/conf.py

echo "=== Makefile has asset-related targets ===" && \
  grep -n "^static\|^collect\|^webpack\|^build" Makefile | head -20
```

**What to look for:**
- Is `django_fusion` in `INSTALLED_APPS` of the base settings?
- Is it also in each site's `INSTALLED_APPS` (or does it inherit from base)?
- Is `django_osoul` loaded similarly?
- Is the `components` templatetag loaded globally (via `builtins:` in `TEMPLATES` config)?
- Are there build/webpack/collectstatic targets in the root Makefile?

**Save output to:** `reports/phase-0-tags-and-packages.txt`

### 0.4 — Live URL Health Check (read-only)

**Task:** Fetch the two broken URLs mentioned in the request and diagnose what's happening.

```bash
# From any machine with curl/internet access (not inside Docker)

echo "=== ctc-research /auth/register/ ===" && \
  curl -sI https://ctc-research.com/auth/register/ | head -20

echo "=== HTTP body (first 2 KB) ===" && \
  curl -s https://ctc-research.com/auth/register/ | head -c 2000

echo "=== vresume /blog/list/ ===" && \
  curl -sI https://vresume.structa.cloud/blog/list/ | head -20

echo "=== HTTP body (first 2 KB) ===" && \
  curl -s https://vresume.structa.cloud/blog/list/ | head -c 2000

# Check if pages load but assets (CSS/JS) fail
echo "=== Check for 404/500 in page source ===" && \
  curl -s https://ctc-research.com/auth/register/ | grep -i "404\|500\|error" | head -20

# Check if stylesheets load
echo "=== Check stylesheet links in register page ===" && \
  curl -s https://ctc-research.com/auth/register/ | grep -i "link.*css\|<style>\|<link" | head -20
```

**What to look for:**
- Do the pages return 200 OK, or errors (404, 500)?
- Does the HTML load but styling/JS missing?
- Are there broken `<link>` tags pointing to non-existent `/static/` URLs?
- Are assets getting 404 errors vs. being missing entirely from the HTML?

**Save output to:** `reports/phase-0-live-urls.txt`

### 0.5 — Makefile & CI/CD Targets Check

**Task:** Understand the available automation and what exists vs. what's missing.

```bash
# From repo root

echo "=== All Makefile targets (first 100) ===" && \
  make help 2>&1 | head -100

echo "=== Git tags (if any releases exist) ===" && \
  git tag -l | head -20

echo "=== Makefile push/push-libs structure ===" && \
  grep -B3 -A15 "^\.PHONY.*push\|^push:\|^push-libs:" Makefile | head -80

echo "=== Check if .github/workflows/ exists ===" && \
  ls -la .github/workflows/ 2>&1

echo "=== Check submodule status ===" && \
  git submodule status
```

**What to look for:**
- How many Makefile targets are there? (indicates complexity)
- Are `push`, `push-libs`, and `push-lib` present?
- Is there CI in `.github/workflows/`?
- Are both submodules (`django-fusion`, `ceptor-ai`) on the `generic` branch?

**Save output to:** `reports/phase-0-makefile-ci.txt`

---

## PHASE 1: Local Development Environment Setup (30–45 min)

**Goal:** Set up a working local dev environment and confirm the asset/template pipeline works locally before pushing anything.

### 1.1 — Install Dependencies & Initialize Submodules

```bash
# From repo root

# 1. Ensure submodules are initialized
git submodule update --init --recursive

# 2. Verify both libs are on generic branch
cd applications/libs/django-fusion && git branch -a && git checkout generic
cd ../ceptor-ai && git branch -a && git checkout generic
cd ../../../

# 3. Create local .env from example (if not exists)
[ -f .env ] || cp .env.example .env || cp applications/.env.example applications/.env.dev

# 4. Install Python dependencies
cd applications && pip install -e ".[dev,test]"  # or use uv sync if available
cd ..

# 5. Install Node dependencies for webpack (if webpack is used)
if [ -f webpack/package.json ]; then
  cd webpack && npm install && cd ..
fi

# 6. Run Django checks
cd applications && python manage.py check
cd ..
```

**Validate:**
- `git submodule status` shows both libs on `generic` branch with matching commits.
- `python manage.py check` passes with zero errors (some warnings OK).
- If webpack: `npm install` completes without errors.

**Save output to:** `reports/phase-1-env-setup.txt`

### 1.2 — Webpack Build & Static Files Collection

```bash
# From repo root

# 1. Build webpack if it exists
if [ -d webpack ]; then
  cd webpack
  npm run build      # or yarn build, depending on config
  ls -la dist/       # check output
  cd ..
fi

# 2. From Django root, collect static files
cd applications
python manage.py collectstatic --noinput --verbosity=2  # capture output
ls -la applications/www/static/         # check what was collected
cd ..

# 3. Check nginx/Traefik configuration for static serving
echo "=== Traefik static file routes ===" && \
  find proxy -name "*.yml" -o -name "*.yaml" | xargs grep -l "static\|media" 2>/dev/null | while read f; do
    echo "-- $f --"
    cat "$f"
  done
```

**Validate:**
- `webpack/dist/` exists and contains bundles (if webpack is used).
- `applications/www/static/` contains collected assets (CSS, JS, images).
- No errors in `collectstatic` output (404 warnings for missing files are fine; deletion warnings are OK).

**Save output to:** `reports/phase-1-webpack-collectstatic.txt`

### 1.3 — Template Loader Pipeline Test

```bash
# From applications/ directory

# 1. Create a minimal test to verify template resolution
python manage.py shell <<'PYEOF'
from django.template.loader import get_template
from django.conf import settings

print("=== Template Configuration ===")
print(f"TEMPLATES: {settings.TEMPLATES}")
print(f"TEMPLATES_DIRS: {getattr(settings, 'TEMPLATES_DIRS', 'Not set')}")

# Test that component tag is available
try:
    from django_fusion.comp.templatetags import components
    print("\n✅ django_fusion.comp.templatetags.components loaded")
except ImportError as e:
    print(f"\n❌ Failed to import django_fusion tags: {e}")

# Test that django_osoul is available
try:
    from django_osoul.templatetags import osoul_components
    print("✅ django_osoul.templatetags.osoul_components loaded")
except ImportError:
    print("⚠️  django_osoul not available (may be OK if not installed)")

# Test template resolution
for template_name in ["base.html", "index.html", "components/button.html"]:
    try:
        t = get_template(template_name)
        print(f"✅ Found: {template_name} → {t.origin}")
    except Exception as e:
        print(f"⚠️  {template_name}: {e}")

print("\n=== INSTALLED_APPS check ===")
for app in ["django_fusion", "django_osoul"]:
    if app in settings.INSTALLED_APPS:
        print(f"✅ {app} in INSTALLED_APPS")
    else:
        print(f"❌ {app} NOT in INSTALLED_APPS")
PYEOF
```

**Validate:**
- Component tags load without import errors.
- Base templates resolve correctly.
- Both libraries show as installed.

**Save output to:** `reports/phase-1-template-loader-test.txt`

### 1.4 — Django Fusion Component Registration Test

```bash
# From applications/ directory

python manage.py shell <<'PYEOF'
from django_fusion.comp.registry import component_registry, register_default_partials

print("=== Component Registry Check ===")
print(f"Registered components: {len(component_registry._components)}")

# Load default partials
register_default_partials()
print(f"After default partials: {len(component_registry._components)}")

# List first 10 components
for name, comp in list(component_registry._components.items())[:10]:
    print(f"  - {name}: {comp.__class__.__name__}")
PYEOF
```

**Validate:**
- Registry loads without errors.
- At least some default components are registered after `register_default_partials()`.

**Save output to:** `reports/phase-1-component-registry.txt`

### 1.5 — Asset URL Resolution Test (Local)

**Task:** Test that static/media URLs resolve correctly in local dev.

```bash
# From applications/ directory (with local server running, or via shell context)

python manage.py shell <<'PYEOF'
from django.templatetag.static import static
from django.conf import settings

print("=== Static & Media URL Configuration ===")
print(f"STATIC_URL: {settings.STATIC_URL}")
print(f"STATIC_ROOT: {settings.STATIC_ROOT}")
print(f"MEDIA_URL: {settings.MEDIA_URL}")
print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")

# Test static tag
test_file = "css/main.css"
resolved = static(test_file)
print(f"\n✅ static('{test_file}') → {resolved}")

# Check if file exists
import os
full_path = os.path.join(settings.STATIC_ROOT, test_file)
exists = "exists" if os.path.exists(full_path) else "NOT FOUND"
print(f"   On disk at {full_path}: {exists}")
PYEOF
```

**Validate:**
- `STATIC_URL`, `MEDIA_URL`, `STATIC_ROOT` are configured.
- `static()` tag resolves paths without errors.
- At least some collected static files exist on disk.

**Save output to:** `reports/phase-1-asset-url-resolution.txt`

---

## PHASE 2: Docs Deduplication & Consolidation (30–60 min)

**Goal:** Clean up the `docs/` tree per the duplication audit. This is mechanical but requires careful diff review before deleting anything.

### 2.1 — Audit & Diff Phase (READ-ONLY)

```bash
# From repo root

# 1. Re-run the duplication audit to confirm against the working tree
echo "=== Duplication Audit (confirm baseline) ===" && \
  python3 <<'PYEOF'
import os
from collections import defaultdict

topics = {
    "ctc-research": ["ctc-research", "ctc.research"],
    "deployment": ["deploy"],
    "django-fusion": ["django-fusion", "django_fusion"],
}

for root, dirs, files in os.walk("docs"):
    for name in files:
        full = os.path.join(root, name)
        for topic, patterns in topics.items():
            if any(p.lower() in name.lower() for p in patterns):
                print(f"{topic}: {full}")
PYEOF

# 2. For each duplicate pair, diff the content
echo "\n=== Diff: docs/ctc-research.com vs docs/websites/ctc-research ===" && \
  diff -rq docs/ctc-research.com docs/websites/ctc-research 2>&1 | head -50

echo "\n=== Diff: docs/deployment.md vs docs/guides/deployment ===" && \
  diff -q docs/deployment.md docs/guides/deployment 2>&1 | head -20 || echo "(One or both missing)"

echo "\n=== Diff: AUTH_REGISTER_*.md files ===" && \
  wc -l AUTH_REGISTER_COMPLETE_FIX.md AUTH_REGISTER_FIX_SUMMARY.md FINAL_AUTH_REGISTER_SUMMARY.md

# 3. Identify empty directories to delete safely
echo "\n=== Empty directories (safe to remove) ===" && \
  find docs -type d -empty
```

**Validate & Record:**
- Note which duplicate is most recent/complete (use `stat` if needed).
- List files that exist in one location but not the other (indicates which to merge manually).
- Confirm empty directories are truly not needed.

**Save output to:** `reports/phase-2-duplication-audit.txt`

### 2.2 — Consolidation Strategy (per audit findings)

Based on the audit from PHASE 0, here's the merge strategy:

| Source | Target | Action | Notes |
|---|---|---|---|
| `docs/ctc-research.com/` | `docs/websites/ctc-research/` | Diff and merge if any newer files | `ctc-research.com` is 138 KB; `websites/ctc-research/` is 204 KB (target is larger) |
| `docs/deployment.md`, `docs/deployment_flow.md` | `docs/guides/deployment/` | Merge into one canonical deployment doc | 272 KB in guides suggests most complete; dedup the root files |
| `AUTH_REGISTER_*.md` (all 3 root files) | `docs/09-troubleshooting/auth-register.md` (new file per CA-013 plan) | Consolidate into one, append-only structure | Create the file in Phase 3 docs restructure |
| `docs/django-fusion/`, `docs/ceptor-ai/`, `docs/ctc-research/`, `docs/structa-cloud/` | DELETE (empty dirs) | Remove safely — no content lost | 0 KB each |
| `docs/django-fusion.png`, `django-osoul.png`, `structa.cloud.png` | Extract as Mermaid diagrams (Phase 3) or delete from git history | Stage for `git rm` | ~11.7 MB saved from git history |

### 2.3 — Execute Consolidation (with Git History Preservation)

```bash
# From repo root

# 1. Backup original state (create a branch for this phase)
git checkout -b phase-2-docs-consolidation

# 2. Merge content from duplicate to canonical (manual review per topic)

# For ctc-research:
echo "Merging docs/ctc-research.com → docs/websites/ctc-research"
# Manually review and copy any newer files from ctc-research.com to websites/ctc-research
# Example: for each file in docs/ctc-research.com/, check if a newer version should override
# (This is manual because content may have meaningful diffs)

# For deployment:
echo "Consolidating deployment docs"
# Read docs/deployment.md and docs/deployment_flow.md
# Merge their content into docs/guides/deployment/index.md or similar
# Verify that no important detail is lost

# For auth-register (simpler — structured data):
cat AUTH_REGISTER_COMPLETE_FIX.md AUTH_REGISTER_FIX_SUMMARY.md FINAL_AUTH_REGISTER_SUMMARY.md > docs/auth-register-consolidated.md
# Review the consolidated file for duplicates, then manually edit to remove redundancy

# 3. Delete empty directories
git rm -r docs/ctc-research/ docs/structa-cloud/ docs/django-fusion/ docs/ceptor-ai/ 2>&1 | grep -v "not found"

# 4. Stage the PNG/image cleanup (Phase 3 for git history rewrite)
# For now, just flag them:
echo "=== Images to be staged for removal (git history cleanup) ===" && \
  find docs -name "*.png" -o -name "*.jpg" -o -name "*.gif" | grep -E "(django-fusion|django-osoul|structa|django-grep|django-rseal)"

# 5. Create redirect stubs (optional — helps users find the new location)
cat > docs/ctc-research.md <<'EOF'
> This file has moved. See [`docs/websites/ctc-research/`](./websites/ctc-research/) instead.
EOF

cat > docs/deployment.md <<'EOF'
> This file has moved. See [`docs/guides/deployment/`](./guides/deployment/) instead.
EOF

# 6. Commit this consolidation
git add -A
git commit -m "Phase 2: Consolidate duplicate docs

- Merge docs/ctc-research.com → docs/websites/ctc-research/
- Merge docs/deployment*.md → docs/guides/deployment/
- Merge AUTH_REGISTER_*.md → docs/09-troubleshooting/auth-register.md
- Remove empty stub directories (ctc-research/, structa-cloud/, django-fusion/, ceptor-ai/)
- Add redirect stubs for old paths (1-release deprecation)

See PHASE 2 consolidation audit in reports/ for detailed content diffs."

# 7. Push phase-2 branch for review (don't merge to generic yet)
git push origin phase-2-docs-consolidation
```

**Validate:**
- `git diff HEAD~1 --stat` shows deleted empty dirs and consolidated files.
- All content from source files is preserved (grep for critical keywords in the consolidated output).
- Redirect stubs exist at old paths for one release cycle.

**Save output to:** `reports/phase-2-consolidation-commit.txt`

---

## PHASE 3: Docs Restructuring & Numbering (45–90 min)

**Goal:** Apply the `CA-0NN` numbered doc structure from the companion enhancement document. This provides stable IDs and better organization.

### 3.1 — Create New Directory Structure

```bash
# From repo root

# 1. Backup docs/ directory
cp -r docs docs.backup

# 2. Create the new numbered structure
mkdir -p docs/legacy
mkdir -p docs/08-applications
mkdir -p docs/09-troubleshooting

# 3. Create INDEX.md (CA-000)
cat > docs/INDEX.md <<'EOF'
# Documentation Index — structa.cloud (ceptor-ai)

This index maps all documentation files to stable IDs (`CA-0NN`) used in commit messages, cross-references, and AI agent prompts. **Never mark a file as "complete" until it actually exists.**

## Documentation Map

| ID | File | Topic | Status |
|---|---|---|---|
| CA-000 | `docs/INDEX.md` | This index | ✅ Exists |
| CA-001 | `docs/01-getting-started.md` | Getting started & installation | 🟡 TODO |
| CA-002 | `docs/02-architecture.md` | System architecture overview | 🟡 TODO |
| CA-003 | `docs/03-deployment.md` | Deployment & infrastructure | 🟡 Existing (in guides/deployment/) |
| CA-004 | `docs/04-routing.md` | URL routing & viewsets | 🟡 TODO |
| CA-005 | `docs/05-components-and-fragments.md` | Component system & templates | 🟡 TODO |
| CA-006 | `docs/06-django-fusion-integration.md` | django-fusion library usage | 🟡 TODO |
| CA-007 | `docs/07-django-osoul-integration.md` | django-osoul library usage | 🟡 TODO |
| CA-008 | `docs/08-applications/ctc-research.md` | CTC Research site | 🟡 Existing (in websites/ctc-research/) |
| CA-009 | `docs/08-applications/lms.md` | LMS Demo site | 🟡 Existing (in websites/lms/) |
| CA-010 | `docs/08-applications/vresume.md` | VResume site | 🟡 Existing (in websites/vresume/) |
| CA-011 | `docs/08-applications/crm.md` | CRM site | 🟡 Existing (in websites/crm/) |
| CA-012 | `docs/08-applications/cypercloud.md` | Tinker site | 🟡 Existing (in websites/cypercloud/) |
| CA-013 | `docs/09-troubleshooting/auth-register.md` | Auth/register flow troubleshooting | 🟡 TODO (merge 3 root files) |
| CA-014 | `docs/09-troubleshooting/asset-loading.md` | Asset & static file issues | 🟡 TODO (new, from Phase 0–1 diagnostics) |
| CA-015 | `docs/10-configuration.md` | Django settings & environment config | 🟡 TODO |
| CA-016 | `docs/11-proxy-and-tls.md` | Reverse proxy, TLS, Let's Encrypt | 🟡 TODO |

## Notes

- 🟡 **TODO**: File path defined but content not yet created — do not mark complete.
- ✅ **Exists**: File has content and is ready for review.
- 🔄 **In Progress**: Being worked on; link to PR if available.

Use the `CA-NNNN` ID in commit messages, PRs, and cross-references so links don't break if files are renamed.

## Using this index

- When **writing a new doc**, add a row to this table with the next free `CA-0NN` ID.
- When **linking to a doc**, use both the ID and the relative path: `(CA-003 — Deployment)[./03-deployment.md]`.
- **Before marking any row "Exists"**, verify the file contains real content by reading it in full.
EOF

# 4. Move existing docs to numbered names
echo "Moving existing docs to numbered structure..."
mv docs/websites/ctc-research/ docs/08-applications/ctc-research.md.bak  # preserve for manual restructuring

# 5. Create placeholder files for TODO docs (so they're findable, with status banner)
for id in 01 02 04 05 06 07 15 16; do
  cat > "docs/${id}-placeholder.md" <<'EOF'
> 🟡 **TODO**: This file has not been written yet. See `docs/INDEX.md` for status.
>
> To write this file, refer to the companion enhancement document for the specific prompt (`PR-NN`) that defines content expectations.
EOF
done
```

**Validate:**
- `docs/INDEX.md` exists and is complete.
- No **✅ Exists** entries point to missing files.
- Each TODO placeholder explains where to find the prompt.

**Save output to:** `reports/phase-3-structure-setup.txt`

### 3.2 — Update Root README & AGENTS.md with New Doc IDs

```bash
# From repo root

# 1. Update README.md to link to docs/INDEX.md (CA-000) instead of scattered docs
cat > README.md <<'EOF'
# structa.cloud — Multi-site Django Monorepo

Structa Cloud is a Django application monorepo hosting multiple consumer sites (`ctc-research.com`, `lms.com`, `vresume.structa.cloud`) and internal tools (CRM, Tinker), all sharing a common codebase, configuration, and reusable libraries.

## Quick Start

For a developer unfamiliar with this project:
1. Read [`docs/01-getting-started.md`](./docs/01-getting-started.md) (CA-001)
2. Understand the architecture: [`docs/02-architecture.md`](./docs/02-architecture.md) (CA-002)
3. Find your site in [`docs/08-applications/`](./docs/08-applications/) (CA-008–CA-012)

For full documentation, see [`docs/INDEX.md`](./docs/INDEX.md) (CA-000).

## Making changes

- **Add a document?** Update [`docs/INDEX.md`](./docs/INDEX.md) with the next `CA-NNNN` ID.
- **Propose a code change?** Reference the relevant doc ID in your commit message (e.g., "Fixes asset loading (CA-014)").
- **Write an automation prompt?** See [`PROMPTS.md`](./PROMPTS.md) for the prompt index.

## Important Files

- `Makefile` — Main automation dispatcher; `make help` for all targets.
- `docker-compose.yml` — Root orchestrator for all services.
- `applications/` — Per-site Django projects (ctc-research, lms, VResume, crm, cypercloud).
- `applications/libs/` — Reusable libraries (`django-fusion`, `ceptor-ai`) as git submodules.
- `proxy/` — Reverse proxy configuration (Traefik).
- `databases/` — Postgres & Redis.

## Repository URLs

- **Main monorepo:** https://github.com/mammhoud/ceptor-ai (generic branch)
- **django-fusion library:** https://github.com/mammhoud/django-fusion (generic branch)
- **ceptor-ai library:** https://github.com/mammhoud/ceptor-ai (generic branch) [self-reference]

---

**Documentation:** See [docs/INDEX.md](./docs/INDEX.md) (CA-000).  
**Automation prompts:** See [PROMPTS.md](./PROMPTS.md).  
**Agent instructions:** See [AGENTS.md](./AGENTS.md).
EOF

# 2. Update AGENTS.md with doc ID cross-references
# (Search for "See the deployment guide" and update to "(See CA-003 — Deployment)[./docs/03-deployment.md]")
sed -i \
  -e 's|deployment guide|CA-003 (Deployment)|g' \
  -e 's|architecture|CA-002 (Architecture)|g' \
  -e 's|configuration|CA-015 (Configuration)|g' \
  AGENTS.md
# (This is a rough example; do this manually for precision)

# 3. Update PROMPTS.md similarly
# (Add Doc IDs to each prompt entry, e.g., "Doc IDs: CA-006, CA-005")
```

**Validate:**
- `README.md` now links to `docs/INDEX.md` and numbered doc IDs.
- `AGENTS.md` cross-references are updated to use `CA-NNNN` IDs where possible.
- No broken links (test with `grep -rn "docs/.*\.md" README.md AGENTS.md | while read line; do path=$(echo "$line" | awk -F: '{print $NF}' | sed 's/.*\(docs[^ )]*\).*/\1/'); [ -f "$path" ] || echo "BROKEN: $line"; done`).

**Save output to:** `reports/phase-3-root-files-updated.txt`

---

## PHASE 4: Asset Pipeline Diagnostics & Fixes (60–120 min)

**Goal:** Diagnose why `ctc-research.com/auth/register/` and `vresume.structa.cloud/blog/list/` aren't showing assets, then fix the root causes.

### 4.1 — Local Asset Pipeline Test

**Before touching production, confirm assets work locally.**

```bash
# From applications/ directory (with local dev server running or in shell context)

# 1. Start a local dev server in one terminal
python manage.py runserver 0.0.0.0:8000 --settings=ctc_research.settings

# 2. In another terminal, make requests to check asset loading
echo "=== Direct asset requests ===" && \
  curl -sI http://localhost:8000/static/css/main.css && \
  curl -sI http://localhost:8000/auth/register/ 

# 3. Check if {% static %} tag works in templates
python manage.py shell <<'PYEOF'
from django.template.loader import render_to_string
from django.template.context import Context

# Try to render a template that uses {% static %}
try:
    html = render_to_string("auth/register.html")  # adjust template path
    if "http" in html and "static" in html.lower():
        print("✅ {% static %} tags rendered (found http + 'static' in output)")
    else:
        print("⚠️  No static assets found in rendered template")
    
    # Check for broken asset URLs
    import re
    urls = re.findall(r'(href|src)="([^"]+\.(css|js|png|jpg))"', html)
    for attr, url, ext in urls:
        print(f"  {attr}={url}")
except Exception as e:
    print(f"❌ Error rendering template: {e}")
PYEOF

# 4. Check Nginx/Traefik configuration for static routing
echo "=== Traefik rules for static files ===" && \
  grep -rn "PathPrefix.*static\|/static" proxy/traefik/ 2>/dev/null

echo "=== Nginx static config (if using Nginx) ===" && \
  grep -rn "location.*static\|alias.*static" proxy/nginx/ 2>/dev/null
```

**Validate:**
- `/static/css/main.css` returns 200 (or at least not 404/500).
- Template renders with asset URLs populated.
- Traefik/Nginx routes for `/static/` are configured.

**Save output to:** `reports/phase-4-local-asset-pipeline.txt`

### 4.2 — Browser DevTools Check (Against Live URLs)

**For the two broken URLs, use browser DevTools to see what's failing.**

```bash
# This is a manual step — cannot automate browser inspection.
# But here's what to look for:

# 1. Open https://ctc-research.com/auth/register/ in a browser
#    - Open DevTools (F12) → Console tab
#    - Look for 404 errors on CSS/JS files
#    - Note the exact URLs that fail (e.g., /static/css/main.css?v=123)
#    - Check the Network tab: are static requests being made at all?

# 2. Same for https://vresume.structa.cloud/blog/list/

# 3. Document findings:
cat > reports/phase-4-browser-devtools-findings.txt <<'EOF'
=== ctc-research.com/auth/register/ ===
[ Manually fill this in after opening in browser ]

Static files requested:
- ___________
- ___________

404 errors (failed to load):
- ___________

Network tab shows:
- Request to /static/ → Response status: ___
- Headers look correct? (Cache-Control, Content-Type, etc.): ___

=== vresume.structa.cloud/blog/list/ ===
[ Manually fill this in ]

Static files requested:
- ___________

404 errors:
- ___________
EOF
```

### 4.3 — Docker Compose Service Check

**Understand how static files are served in the containerized environment.**

```bash
# From repo root (with compose stack running, or after inspection)

# 1. Check if a dedicated static/media service exists (or if nginx/Traefik serves it)
echo "=== Services in compose stack ===" && \
  docker compose config 2>&1 | grep -E "^\s+\w+:" | head -30

# 2. Check volume mounts for static directories
echo "=== Static/media volumes ===" && \
  docker compose config 2>&1 | grep -E "static|media" | head -40

# 3. Inspect running containers for static file presence
echo "=== Static files in ctc-research container ===" && \
  docker compose exec ctc-research ls -la /app/applications/www/static/ 2>&1 | head -30

# 4. Check if collectstatic has been run in the container
echo "=== Check for Django admin static files (indicates collectstatic) ===" && \
  docker compose exec ctc-research find /app -path "*/admin/css/base.css" -o -path "*/admin/js/*.js" | head -5

# 5. Check Traefik rules for the live domain
echo "=== Traefik dynamic config for ctc-research.com ===" && \
  find proxy/traefik -name "*.yml" -o -name "*.yaml" | xargs grep -l "ctc-research\|auth/register" 2>/dev/null | while read f; do
    echo "-- $f --"
    cat "$f"
  done
```

**Validate:**
- Static files exist in the container at the expected path.
- Traefik has explicit routes for `/static/` or delegates to a static file service.
- Volume mounts for static/media are correctly defined in docker-compose.

**Save output to:** `reports/phase-4-docker-compose-static.txt`

### 4.4 — Django Fixture & URL Configuration Check

```bash
# From applications/ directory

# 1. Check that STATIC_URL, MEDIA_URL, and ROOT_URLCONF are set correctly
python manage.py shell <<'PYEOF'
from django.conf import settings

print("=== Static/Media Configuration ===")
print(f"STATIC_URL: {settings.STATIC_URL}")
print(f"STATIC_ROOT: {settings.STATIC_ROOT}")
print(f"MEDIA_URL: {settings.MEDIA_URL}")
print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
print(f"DEBUG: {settings.DEBUG}")
print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")

# 2. Check if django.contrib.staticfiles app is installed
print(f"\n'django.contrib.staticfiles' in INSTALLED_APPS: {'django.contrib.staticfiles' in settings.INSTALLED_APPS}")

# 3. Verify URL configuration serves static/media
from django.urls import resolve, reverse
try:
    match = resolve("/static/test.css")
    print(f"\n✅ /static/test.css resolves to: {match}")
except Exception as e:
    print(f"\n⚠️  /static/test.css does not resolve: {e}")

try:
    match = resolve("/media/test.jpg")
    print(f"✅ /media/test.jpg resolves to: {match}")
except Exception as e:
    print(f"⚠️  /media/test.jpg does not resolve: {e}")
PYEOF

# 2. Check app urls.py for static/media handlers
for app in ctc-research lms VResume crm cypercloud; do
  echo "-- $app/www/urls.py --"
  grep -n "static\|media" "$app/www/urls.py" 2>/dev/null || echo "  (no static/media URLs)"
done
```

**Validate:**
- `STATIC_URL` is set to `/static/` (or a CDN URL in production).
- `DEBUG=False` in production (which means Django doesn't auto-serve static files — it must be handled by Traefik/Nginx).
- URLs for `/static/` and `/media/` exist (or are handled by a middleware/proxy).

**Save output to:** `reports/phase-4-django-fixture-config.txt`

### 4.5 — Asset Loading Root Cause Analysis

**Based on Phase 0 & Phase 4 diagnostics, compile a root cause report.**

```bash
# Create a consolidated troubleshooting doc
cat > reports/PHASE-4-ASSET-LOADING-ROOT-CAUSE.md <<'EOF'
# Asset Loading Issues — Root Cause Analysis

## Findings

### ctc-research.com/auth/register/

**Live page status:** [from Phase 0.4 curl results]
- HTTP Status: ___
- Page loads: Yes / No
- Assets load: Yes / No

**Root cause (identified in Phase 4):**
1. collectstatic not run in container? → Fix: `make collectstatic`
2. Traefik not routing /static/? → Fix: Check proxy/traefik/dynamic/rules/
3. STATIC_URL wrong in settings? → Fix: Update STATIC_URL in settings
4. {% static %} tag not working? → Fix: Verify django.contrib.staticfiles in INSTALLED_APPS

**Recommended fix:**
[ One of the above, or combination ]

### vresume.structa.cloud/blog/list/

**Live page status:** [similar analysis]

---

## Action Items

- [ ] Run `make collectstatic` in all affected containers
- [ ] Verify Traefik routes for /static/ and /media/
- [ ] Confirm STATIC_ROOT points to a mounted volume (docker compose)
- [ ] Test template rendering with {% static %} tag locally
- [ ] Re-test live URLs after fixes
EOF

cat reports/PHASE-4-ASSET-LOADING-ROOT-CAUSE.md
```

**Validate:**
- Root cause is clearly identified (one or more of the points above).
- Recommended fix(es) are specific and actionable.

**Save output to:** `reports/PHASE-4-ASSET-LOADING-ROOT-CAUSE.md`

### 4.6 — Apply Fixes (if needed)

**Based on Phase 4.5 analysis, apply one or more of these fixes:**

```bash
# Scenario 1: collectstatic not run
# ─────────────────────────────────
cd applications
python manage.py collectstatic --noinput --verbosity=2
cd ..

# Scenario 2: Traefik routes missing for /static/
# ─────────────────────────────────
# Edit proxy/traefik/dynamic/rules/ to add:
# Rule: "Host(`ctc-research.com`) && PathPrefix(`/static/`)"
# Service: static-files (or nginx container)

# Scenario 3: STATIC_URL wrong
# ─────────────────────────────────
# Edit applications/configs/settings/conf.py:
# STATIC_URL = "/static/"  # (correct)
# NOT: STATIC_URL = "https://cdn.example.com/static/"  # (unless actual CDN)

# Scenario 4: django.contrib.staticfiles missing
# ─────────────────────────────────
# Edit applications/configs/settings/conf.py:
# INSTALLED_APPS += [
#     "django.contrib.staticfiles",
# ]

# 4. Commit fixes
git add -A
git commit -m "Phase 4: Fix asset loading pipeline

- [Specific fix: collectstatic | Traefik route | STATIC_URL | INSTALLED_APPS]
- Tested locally: Yes
- Tested live: [after deployment]

Refs: CA-014 (Asset loading)"

# 5. Document the fix in the new CA-014 troubleshooting doc
cat > docs/09-troubleshooting/asset-loading.md <<'EOF'
# Asset Loading Issues (CA-014)

## Problem: CSS/JS files return 404

**Symptoms:**
- Page loads but styling/JavaScript is missing.
- Browser DevTools shows 404 for `/static/css/*.css` or `/static/js/*.js`.

## Root Causes & Solutions

### 1. collectstatic Not Run

**Cause:** Django's `collectstatic` management command copies static files from app directories to a central location. If not run, files aren't found.

**Check:**
```bash
docker compose exec ctc-research ls -la /app/applications/www/static/
# Should show collected files (admin/, css/, js/, etc.)
```

**Fix:**
```bash
cd applications
python manage.py collectstatic --noinput --verbosity=2
cd ..
```

### 2. Traefik Not Routing /static/

**Cause:** Traefik must have an explicit rule routing `/static/` requests to the right container/service.

**Check:**
```bash
grep -rn "PathPrefix.*static" proxy/traefik/
# Should show rules for /static/ and /media/
```

**Fix:**  
Edit `proxy/traefik/dynamic/rules/` to add:
```yaml
http:
  routers:
    static-files:
      rule: "Host(`ctc-research.com`) && PathPrefix(`/static/`)"
      service: django-app
      priority: 1000  # Higher priority = checked first
```

### 3. STATIC_URL Misconfigured

**Check:**
```python
# In applications/configs/settings/conf.py
STATIC_URL = "/static/"  # ✅ Correct
# NOT: STATIC_URL = "https://cdn.example.com/"  # ❌ (unless using a real CDN)
```

**Fix:**  
Ensure `STATIC_URL = "/static/"` and `STATIC_ROOT` points to a mounted volume in docker-compose.

---

See also: CA-015 (Configuration), CA-006 (django-fusion integration), CA-007 (django-osoul integration).
EOF
```

**Validate:**
- Fix is applied and committed.
- Asset loading is confirmed working locally (Phase 4.1).
- Live URL is re-tested after deployment (someone with deploy access).

**Save output to:** `reports/phase-4-fixes-applied.txt`

---

## PHASE 5: django-fusion & django-osoul Component Tag Setup (30–45 min)

**Goal:** Ensure `{% comp %}` (django-fusion) and django-osoul tags are available as default template tags across all apps.

### 5.1 — Verify django_fusion and django_osoul are installed

```bash
cd applications

# 1. Check that the libraries are in INSTALLED_APPS
grep -rn "django_fusion\|django_osoul" configs/settings/

# 2. Check that they're also in each site's LOCAL_APPS (if needed)
for app in ctc-research lms VResume crm cypercloud; do
  grep "django_fusion\|django_osoul" "$app/settings.py" || echo "$app: not explicitly listed (inherits from base)"
done

# 3. Verify imports don't fail
python manage.py shell <<'PYEOF'
try:
    import django_fusion
    print(f"✅ django_fusion version: {getattr(django_fusion, '__version__', 'unknown')}")
except ImportError as e:
    print(f"❌ django_fusion import failed: {e}")

try:
    import django_osoul
    print(f"✅ django_osoul version: {getattr(django_osoul, '__version__', 'unknown')}")
except ImportError as e:
    print(f"⚠️  django_osoul import failed (may be OK): {e}")
PYEOF
```

**Validate:**
- Both libraries import without errors.
- They're in `INSTALLED_APPS` (either base or per-site).

**Save output to:** `reports/phase-5-fusion-osoul-install.txt`

### 5.2 — Make `{% comp %}` Tag Available Globally

**By default, Django requires `{% load components %}` in every template. Make it global.**

```bash
cd applications

# 1. Check current TEMPLATES config
grep -B10 -A10 "'builtins'" configs/settings/conf.py

# 2. If 'builtins' not present, add it:
# Edit configs/settings/conf.py and update TEMPLATES like this:

cat > configs/settings/builtins-patch.py <<'EOF'
# Patch to TEMPLATES in configs/settings/conf.py
# Add this to the TEMPLATES[0]["OPTIONS"] dict:

TEMPLATES[0]["OPTIONS"]["builtins"] = [
    "django_fusion.comp.templatetags.components",
    "django_osoul.templatetags.osoul_components",  # if using django-osoul
]
EOF

# 3. Manually edit configs/settings/conf.py to include the above
#    (Can't do a regex replace safely; requires human review)

# 4. After editing, test that tags are globally available:
python manage.py shell <<'PYEOF'
from django.template.loader import render_to_string
from django.template import Template, Context

# Try rendering without {% load components %}
template_str = '{% comp "button" label="Click me" / %}'
try:
    t = Template(template_str)
    output = t.render(Context({}))
    print(f"✅ {% comp %} works without {% load %}: {output}")
except Exception as e:
    print(f"❌ {% comp %} not available globally: {e}")
    print("   Add 'builtins' to TEMPLATES OPTIONS (see Phase 5.2)")
PYEOF
```

**Validate:**
- `builtins:` is configured in `TEMPLATES[0]["OPTIONS"]`.
- Template renders `{% comp %}` without explicit `{% load %}`.

**Save output to:** `reports/phase-5-comp-tag-global.txt`

### 5.3 — Audit Existing Templates for `{% include %}` → `{% comp %}`

**Replace `{% include %}` with `{% comp %}` where appropriate (mechanical improvement, not required for function).**

```bash
# From applications/ directory

# 1. Find all {% include %} statements
echo "=== {% include %} statements in templates ===" && \
  grep -rn "{% include" */templates --include="*.html" | wc -l

# 2. For each include, decide: should it be a component instead?
#    Rule: if the included file is static (no complex context logic),
#    use {% comp %}; otherwise keep {% include %}

# 3. Mechanical replacement (review before committing):
find . -name "*.html" -type f -exec sed -i \
  -e "s|{% include '\([^']*\)' %}|{% comp '\1' / %}|g" \
  -e "s|{% include \"\([^\"]*\)\" %}|{% comp \"\1\" / %}|g" \
  {} \;

# 4. Manual review: open a few templates and verify replacements make sense
for tmpl in $(find . -name "*.html" | head -10); do
  grep "{% comp" "$tmpl" && echo "  ← $tmpl has {% comp %}"
done

# 5. Test that templates still render
python manage.py test --verbosity=2 2>&1 | grep -i "error\|fail" | head -20
```

**Validate:**
- No template errors after include→comp replacement.
- At least some templates now use `{% comp %}`.

**Save output to:** `reports/phase-5-include-to-comp-audit.txt`

### 5.4 — Document Component Usage in CA-005/CA-006

**Update the component docs (from Phase 3 TODOs) with actual usage examples.**

```bash
# Create docs/05-components-and-fragments.md (CA-005)
cat > docs/05-components-and-fragments.md <<'EOF'
# Components & Fragments (CA-005)

**Applies to:** All sites (ctc-research, lms, VResume, crm, cypercloud)

## Overview

This project uses **django-fusion**'s component system for template rendering. Components provide:
- Composable, reusable template blocks
- Type-safe props validation (via Pydantic)
- HTMX-aware fragment detection for partial page updates
- A registration system for discovering components

## Using Components: `{% comp %}` Tag

### Basic Syntax

```django
{% comp "path/to/component" prop1="value" prop2=variable / %}
```

> Remark: The trailing `/` is required (self-closing tag syntax). This is different from Django's `{% include %}`.

### Example: Button Component

```django
{% comp "components/button" label="Click me" variant="primary" / %}
```

**Produces:**
```html
<button class="btn btn-primary">Click me</button>
```

### Passing Complex Data

```django
{% comp "components/card" title="User Profile" user=current_user items=user_items / %}
```

### Slots (Nested Content)

```django
{% comp "components/panel" title="Sidebar" %}
  <p>This content goes into the default slot.</p>
{% endcomp %}
```

## Component Registration

Components are auto-discovered from:
- `applications/<site>/components/` (site-specific)
- `applications/assets/components/` (shared across all sites)
- Installed apps with a `components/` directory

## Common Components

| Component | Path | Props | Use Case |
|---|---|---|---|
| Button | `components/button` | `label`, `variant`, `disabled` | CTA buttons |
| Card | `components/card` | `title`, `subtitle`, `footer` | Card layouts |
| Form | `components/form` | `action`, `method`, `fields` | Forms |
| Navbar | `components/navbar` | `site_name`, `user`, `menu_items` | Navigation |
| Footer | `components/footer` | `links`, `copyright` | Page footer |

See `docs/06-django-fusion-integration.md` (CA-006) for the full component API reference.
EOF

# Create docs/06-django-fusion-integration.md (CA-006)
cat > docs/06-django-fusion-integration.md <<'EOF'
# django-fusion Integration (CA-006)

**Applies to:** All sites

**Source:** https://github.com/mammhoud/django-fusion (`generic` branch)

**Local path:** `applications/libs/django-fusion/`

## What is django-fusion?

django-fusion is a Django helper library providing:
- **Component system** (`RoutableComponent`, `FragmentComponent`) with template tags
- **Routing helpers** (`Site`, `Application`, `Viewset`) for organizing URLs
- **Form/table mixins** (`FormMixin`, `TableMixin`) for CRUD patterns
- **Cache managers** (`CachedManager`) for model queries
- **Health checks** for deployment monitoring
- **Wagtail integration** for CMS workflows

## Configuration

### 1. Installation

The library is included as a git submodule:

```bash
git submodule update --init applications/libs/django-fusion
```

### 2. Enable in Django Settings

```python
# applications/configs/settings/conf.py

INSTALLED_APPS = [
    # ...
    "django_fusion.comp",           # component system
    "django_fusion.core",           # models, managers, services, middlewares
    "django_fusion.health",         # health checks
    "django_fusion.wagtail",        # Wagtail integration (if using Wagtail)
    "django_fusion.analyzer",       # template/component analyzer
    # ...
]

# Make component tag globally available (no {% load components %} needed)
TEMPLATES[0]["OPTIONS"]["builtins"] = [
    "django_fusion.comp.templatetags.components",
]
```

### 3. Caching

For `CachedManager` to work, configure Redis:

```python
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/0",
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"}
    }
}
```

---

See `docs/05-components-and-fragments.md` (CA-005) for component usage.
EOF
```

**Validate:**
- Both CA-005 and CA-006 docs exist with real content.
- Examples are runnable (not pseudocode).

**Save output to:** `reports/phase-5-component-docs-created.txt`

---

## PHASE 6: Library Updates & Push (45–90 min)

**Goal:** Ensure both `django-fusion` and `ceptor-ai` submodules are up-to-date and pushed to their respective standalone repos. This phase requires `GITHUB_TOKEN`.

### 6.1 — Sync django-fusion

```bash
# From repo root

cd applications/libs/django-fusion

# 1. Verify we're on generic branch
git branch -a
git checkout generic

# 2. Apply any enhancements from django-fusion-enhancements.md
#    (PR-01 through PR-17 prompts from that doc)
#    These should be done in the standalone django-fusion repo
#    and then pulled here as a submodule update.
#    For now, just verify the current state.

git log --oneline -20

# 3. Stage this submodule version for push
cd ../../../

# The version is now pinned to whatever django-fusion is at
# When we `make push-libs`, it will push this version to the django-fusion remote.
```

**Validate:**
- `git -C applications/libs/django-fusion branch` shows we're on `generic`.
- `git log` shows expected commits.

**Save output to:** `reports/phase-6-django-fusion-sync.txt`

### 6.2 — Sync ceptor-ai

```bash
# From repo root

cd applications/libs/ceptor-ai

# 1. Verify we're on generic branch
git branch -a
git checkout generic

# 2. This is a self-reference (ceptor-ai as a submodule of ceptor-ai)
#    Verify it's not in a broken state
git log --oneline -20
git status

# 3. Stage for push
cd ../../../
```

**Validate:**
- `git -C applications/libs/ceptor-ai branch` shows `generic`.
- `git status` shows no divergence from remote.

**Save output to:** `reports/phase-6-ceptor-ai-sync.txt`

### 6.3 — Prepare .env for Push (requires GITHUB_TOKEN)

```bash
# From repo root

# 1. Ensure .env exists and has GITHUB_TOKEN set
if ! grep -q "GITHUB_TOKEN\|github=" .env 2>/dev/null; then
  echo ""
  echo "❌ GITHUB_TOKEN not found in .env"
  echo "   Add one of:"
  echo "     GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  echo "   OR"
  echo "     github=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  echo ""
  exit 1
fi

# 2. Verify submodules are in sync with remotes
git submodule status

# 3. List what will be pushed
echo "=== Changes to push ===" && \
  git diff --stat origin/generic HEAD

echo "=== Submodule changes ===" && \
  git diff --stat HEAD -- applications/libs/
```

**Validate:**
- `GITHUB_TOKEN` is present in `.env` (or `projects/.env` or `proxy/.env`).
- Submodule pointers are correct (not diverged from expected commit).
- No uncommitted changes locally.

**Save output to:** `reports/phase-6-push-readiness.txt`

### 6.4 — Dry Run: Check Push Targets

```bash
# From repo root

# 1. Verify remote URLs match what make push-libs expects
echo "=== Remote URLs ===" && \
  git remote -v && \
  echo "--- Submodule remotes ---" && \
  git -C applications/libs/django-fusion remote -v && \
  git -C applications/libs/ceptor-ai remote -v

# 2. Verify generic branch exists on all remotes
for remote in origin; do
  echo "=== $remote refs/heads/generic ===" && \
    git ls-remote $remote refs/heads/generic | head -5
done

echo "=== django-fusion remote ===" && \
  git -C applications/libs/django-fusion ls-remote origin refs/heads/generic | head -5

echo "=== ceptor-ai remote ===" && \
  git -C applications/libs/ceptor-ai ls-remote origin refs/heads/generic | head -5

# 3. Simulate what make push-libs would do (without actually pushing)
echo "=== Dry-run: git push would update these ===" && \
  git push --dry-run origin generic 2>&1 | head -30
```

**Validate:**
- Remote URLs point to correct GitHub repos (mammhoud/ceptor-ai, mammhoud/django-fusion).
- `generic` branch exists on all remotes.
- Dry-run shows expected changes (not "up to date" unless truly no changes).

**Save output to:** `reports/phase-6-push-dry-run.txt`

### 6.5 — Execute Push (REQUIRES GITHUB_TOKEN)

```bash
# From repo root

# ⚠️  WARNING: This actually pushes to remote repos. 
#    Commit to the phase-X-... branch first before running this.
#    Have a human review Phase 0–5 reports before proceeding.

if [ -z "$GITHUB_TOKEN" ] && ! grep -q "github=" .env 2>/dev/null; then
  echo "❌ GITHUB_TOKEN not set. Cannot push."
  exit 1
fi

echo "🚀 Pushing changes to remote repos..."

# The Makefile's require-github-token will verify .env
make push

# Or, if prefer to run manually:
# git push origin generic && \
# cd applications/libs/django-fusion && git push origin HEAD:generic && cd ../../../ && \
# cd applications/libs/ceptor-ai && git push origin HEAD:generic && cd ../../../
```

**⚠️  STOP BEFORE RUNNING THIS**

Before executing `make push`:

1. ✅ Verify `.env` has `GITHUB_TOKEN` set
2. ✅ Confirm all Phase 0–5 reports are reviewed
3. ✅ Have a maintainer/code-owner visually inspect the commits being pushed
4. ✅ Ensure you are on the correct branch (`generic`, not `main`/`master`)
5. ✅ Run Phase 6.4 dry-run one more time to confirm expected changes

**After pushing:**

```bash
# Verify push succeeded
git ls-remote origin refs/heads/generic | head -1
git -C applications/libs/django-fusion ls-remote origin refs/heads/generic | head -1
git -C applications/libs/ceptor-ai ls-remote origin refs/heads/generic | head -1

# All three should show the same commits you just pushed (or later)
```

**Save output to:** `reports/phase-6-push-executed.txt`

---

## PHASE 7: Deployment & Validation (30–60 min)

**Goal:** Deploy the changes to production and validate everything works end-to-end.

### 7.1 — Pull Changes on Production Server

**Requires SSH/deploy access to production server(s).**

```bash
# On production server, in the structa.cloud/ directory

# 1. Fetch latest from generic branch
git fetch origin generic

# 2. Merge or rebase
git rebase origin/generic

# 3. Update submodules to their latest versions (now pushed in Phase 6)
git submodule update --recursive

# 4. Verify no conflicts
git status
```

**Validate:**
- No merge conflicts.
- Submodules on correct commits.

### 7.2 — Re-collect Static Files

```bash
# On production server, in applications/ directory

# 1. Collect static files
python manage.py collectstatic --noinput --verbosity=2

# 2. Verify assets exist
ls -la applications/www/static/ | head -30

# 3. Check that collectstatic output shows no errors
#    (warnings about missing files for unused apps are OK)
```

**Validate:**
- No errors in collectstatic output.
- Assets are in the expected location.

### 7.3 — Restart Containers

```bash
# On production server, in the structa.cloud/ directory

# 1. Rebuild Docker images (if base images changed)
docker compose -f docker-compose.yml -f compose/docker-compose.prod.yml build

# 2. Restart affected services
docker compose -f docker-compose.yml -f compose/docker-compose.prod.yml restart ctc-research lms VResume crm

# 3. Check logs for errors
docker compose logs ctc-research -n 100 | grep -i "error\|warn" | head -30
```

**Validate:**
- Containers restart without errors.
- No Traceback or ImportError in logs.

### 7.4 — Re-Test Live URLs

```bash
# From any machine with internet access

# 1. Re-check the two previously-broken URLs
curl -sI https://ctc-research.com/auth/register/
curl -s https://ctc-research.com/auth/register/ | grep -i "css\|javascript" | head -10

curl -sI https://vresume.structa.cloud/blog/list/
curl -s https://vresume.structa.cloud/blog/list/ | grep -i "css\|javascript" | head -10

# 2. Check browser (open in DevTools) and verify:
#    - Status: 200 OK
#    - Assets loading: CSS/JS show 200 (not 404/500)
#    - Page styling: visible and correct

# 3. Full smoke test: create an account, post a blog, etc.
```

**Validate:**
- Both URLs return 200 OK.
- Assets load (no 404 errors in DevTools Network tab).
- Styling and JavaScript are visible and functional.

**Save output to:** `reports/phase-7-deployment-validation.txt`

---

## PHASE 8: Documentation Finalization & Archive (15–30 min)

**Goal:** Complete the doc restructuring, archive old reports, and prepare for the next iteration.

### 8.1 — Complete Remaining CA-0NN Docs (Optional)

If time permits, use the prompts from the companion `django-fusion-enhancements.md` §3 to write the TODO docs from Phase 3:

- CA-001: Getting started → Use PR-01 prompt
- CA-002: Architecture → Use PR-02 prompt
- CA-003: Deployment → Update existing guides/deployment/ (already largely exists)
- CA-004: Routing → Use PR-04 prompt
- ... and so on.

### 8.2 — Archive Reports

```bash
# From repo root

# 1. Create reports/ directory if not exists
mkdir -p reports

# 2. Copy all diagnostic outputs into reports/
mv reports/*.txt reports/ 2>/dev/null
mv reports/*.md reports/ 2>/dev/null

# 3. Create an index of all reports
cat > reports/INDEX.md <<'EOF'
# Execution Reports — structa.cloud (ceptor-ai)

Generated during full execution of structa.cloud-execution-plan.md.

## Phase 0: Baseline Diagnostics
- `phase-0-asset-baseline.txt` — Static files, webpack, volumes, routes
- `phase-0-template-resolution.txt` — Template loader config
- `phase-0-tags-and-packages.md` — django_fusion, django_osoul registration
- `phase-0-live-urls.txt` — Live URL health check results
- `phase-0-makefile-ci.txt` — Available Makefile targets, CI presence

## Phase 1: Local Dev Setup
- `phase-1-env-setup.txt` — Dependency installation, Django checks
- `phase-1-webpack-collectstatic.txt` — Webpack build, collectstatic output
- `phase-1-template-loader-test.txt` — Template resolution verification
- `phase-1-component-registry.txt` — django_fusion component registration
- `phase-1-asset-url-resolution.txt` — Static/media URL configuration test

## Phase 2: Docs Deduplication
- `phase-2-duplication-audit.txt` — Before-consolidation audit
- `phase-2-consolidation-commit.txt` — Consolidation commit log

## Phase 3: Docs Restructuring
- `phase-3-structure-setup.txt` — CA-0NN directory setup
- `phase-3-root-files-updated.txt` — README, AGENTS.md updates

## Phase 4: Asset Pipeline Diagnostics & Fixes
- `phase-4-local-asset-pipeline.txt` — Local asset serving test
- `phase-4-browser-devtools-findings.txt` — Browser inspection results
- `phase-4-docker-compose-static.txt` — Container asset check
- `phase-4-django-fixture-config.txt` — Django settings verification
- `PHASE-4-ASSET-LOADING-ROOT-CAUSE.md` — Root cause analysis & fixes
- `phase-4-fixes-applied.txt` — Applied fixes log

## Phase 5: Component Tag Setup
- `phase-5-fusion-osoul-install.txt` — Library installation verification
- `phase-5-comp-tag-global.txt` — Global template tag availability
- `phase-5-include-to-comp-audit.txt` — include→comp replacement audit
- `phase-5-component-docs-created.txt` — CA-005, CA-006 docs creation

## Phase 6: Library Push
- `phase-6-django-fusion-sync.txt` — django-fusion submodule check
- `phase-6-ceptor-ai-sync.txt` — ceptor-ai submodule check
- `phase-6-push-readiness.txt` — Pre-push validation
- `phase-6-push-dry-run.txt` — Dry-run results
- `phase-6-push-executed.txt` — Actual push results

## Phase 7: Deployment & Validation
- `phase-7-deployment-validation.txt` — Live URL validation post-deployment

---

If any phase fails, refer to its report and the companion execution plan for troubleshooting.
EOF

# 4. Commit the reports directory
git add reports/
git commit -m "Phase 8: Archive execution reports

All diagnostic and execution logs from structa.cloud-execution-plan.md.

This aids in debugging if issues are discovered post-deployment."
```

### 8.3 — Update CHANGELOG.md

```bash
# From repo root

cat >> CHANGELOG.md <<'EOF'

## [Unreleased] — structa.cloud Full Execution (2024)

### Added
- Numbered documentation structure (CA-0NN) for stable cross-references
- Asset loading diagnostics (Phase 4) and root-cause analysis
- Component tag documentation (CA-005, CA-006)
- Troubleshooting guide for asset loading (CA-014)

### Fixed
- docs/ duplication: consolidated ctc-research, deployment, auth-register docs
- Removed empty stub directories from docs/
- Asset pipeline issues: [specific fix from Phase 4.6]

### Changed
- Relocated docs from multiple locations to canonical CA-0NN structure
- README.md now links to docs/INDEX.md (CA-000)
- AGENTS.md cross-references use CA-NNNN IDs
- {% comp %} tag now globally available without {% load %}

### Infrastructure
- Added .github/workflows/ for CI (if added in Phase 1)
- Submodules (django-fusion, ceptor-ai) now on generic branch with push verification

---
EOF

git add CHANGELOG.md
git commit -m "Phase 8: Update CHANGELOG for full execution cycle"
```

### 8.4 — Create Final Summary Report

```bash
cat > reports/EXECUTION-SUMMARY.md <<'EOF'
# Full Execution Summary — structa.cloud (ceptor-ai)

**Date:** [execution date]
**Branch:** generic
**Duration:** [total time across all phases]

## Phases Completed

- ✅ Phase 0: Baseline Diagnostics
- ✅ Phase 1: Local Dev Setup
- ✅ Phase 2: Docs Deduplication
- ✅ Phase 3: Docs Restructuring
- ✅ Phase 4: Asset Pipeline Diagnostics & Fixes
- ✅ Phase 5: Component Tag Setup
- ✅ Phase 6: Library Push
- ✅ Phase 7: Deployment & Validation
- ✅ Phase 8: Documentation Finalization

## Key Achievements

1. **Docs cleaned up**: 22 MB → ~15 MB (removed 4 large PNGs, consolidated duplicates)
2. **Asset pipeline fixed**: ctc-research.com/auth/register/ and vresume.structa.cloud/blog/list/ now load assets correctly
3. **Component tags unified**: {% comp %} now available globally; replaced {% include %} with {% comp %} in [N] templates
4. **Libraries synced**: django-fusion and ceptor-ai both on generic branch, pushed to their standalone repos
5. **Docs structured**: Introduced CA-0NN numbering for stable cross-references

## Issues Resolved

1. Asset loading (404 errors on /static/): [specific root cause from Phase 4.5]
2. Docs duplication: Consolidated into canonical locations per audit
3. Empty doc directories: Removed safely
4. Template tag availability: Made {% comp %} global

## Known Open Items

- [ ] Write remaining CA-0NN docs (CA-001–004, CA-007, etc.) — requires using PR-NN prompts
- [ ] Git history cleanup (remove large PNGs) — optional, for future refactor
- [ ] django-osoul integration — documented but not heavily tested
- [ ] CI workflow setup (.github/workflows/) — not yet created

## To Deploy This Again

1. Pull latest from `generic` branch: `git fetch origin generic && git rebase origin/generic`
2. Update submodules: `git submodule update --recursive`
3. Collect static: `python manage.py collectstatic --noinput`
4. Restart containers: `docker compose restart ctc-research lms VResume crm`
5. Validate live URLs: See Phase 7.4

## Next Steps

1. Have code/docs review of all changes (especially docs/09-troubleshooting/asset-loading.md)
2. Write remaining CA-0NN docs using PR-NN prompts from django-fusion-enhancements.md §3
3. Monitor production for asset loading issues for 1 week
4. Plan Phase 2 of enhancement (library publishing, CI setup, etc.)
EOF

cat reports/EXECUTION-SUMMARY.md
git add reports/EXECUTION-SUMMARY.md
git commit -m "Phase 8: Add execution summary report"
```

---

## FINAL CHECKLIST

Before declaring this execution complete, verify:

- [ ] All Phase 0–7 reports exist in `reports/`
- [ ] No broken links in docs/ (test with: `grep -rn "docs/.*\.md" . | while read line; do path=$(echo "$line" | sed 's/.*\(docs[^ )]*\).*/\1/'); [ -f "$path" ] || echo "BROKEN: $line"; done`)
- [ ] Both submodules (django-fusion, ceptor-ai) on `generic` branch
- [ ] Live URLs (ctc-research.com/auth/register/, vresume.structa.cloud/blog/list/) return 200 and load assets
- [ ] No untracked files in root directory (clean git status)
- [ ] CHANGELOG.md updated with execution summary
- [ ] All commits pushed to `generic` branch via `make push`

---

## Troubleshooting

If any phase fails, consult:
1. The phase's corresponding report file in `reports/`
2. The "Validate:" checklist at the end of each phase section
3. The companion enhancement document for more context on the underlying issue

For asset loading specifically, see `docs/09-troubleshooting/asset-loading.md` (CA-014).

---

**Document version:** 1.0  
**Last updated:** [date]  
**Maintainer:** [your name/team]
