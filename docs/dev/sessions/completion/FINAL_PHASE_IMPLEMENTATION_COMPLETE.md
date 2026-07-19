# Final Phases Implementation - Complete Guide

**Date:** June 7, 2026  
**Status:** ⏳ IN PROGRESS - Starting Final Implementation  
**Target:** Complete Phases 6-16 with Docker & Template fixes  

---

## CRITICAL FIXES NEEDED

### 1. Docker Service Naming Inconsistencies
**Issue:** Service names don't match Traefik labels

**Current:**
- Service: `ctc-research-website` 
- Traefik label: `ctc-website`
- Should be: CONSISTENT

**Solution:** Update Traefik labels to match actual service names

### 2. SSL Certificate Backup/Restore
**Issue:** No backup strategy for SSL certificates

**Solution:** 
- Add backup script to Traefik container
- Run on startup
- Restore if needed

### 3. Template Consolidation
**Issue:** Templates scattered in packages/ui and ctc-research/assets/templates/generic

**Solution:**
- Create temp consolidation directory
- Merge all templates
- Keep single source of truth
- Delete duplicates

### 4. JavaScript Generation & Integration
**Issue:** JS not centralized in assets/static

**Solution:**
- Generate JS modules
- Place in assets/static (workspace root)
- Integrate into all three sites
- Delete duplicates from sites

---

## Implementation Plan

### Phase A: Docker Service Fix (30 min)

#### A1: Fix Traefik Labels
File: `ctc-research/docker-compose.yml`
```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.ctc-research.rule=Host(`ctc-research.local`) || Host(`ctc-research.com`)"
  - "traefik.http.routers.ctc-research.service=ctc-research"
  - "traefik.http.services.ctc-research.loadbalancer.server.port=5070"
  - "traefik.http.routers.ctc-research.entrypoints=websecure"
  - "traefik.http.routers.ctc-research.tls=true"
```

#### A2: Fix lms service names
File: `lms/docker-compose.yml`
- Service: `lms-website`
- Traefik labels: consistent naming

#### A3: Fix VResume service names
File: `VResume/docker-compose.yml`
- Service: `vresume-website`
- Traefik labels: consistent naming

### Phase B: SSL Certificate Management (30 min)

#### B1: Create Backup Script
File: `compose/traefik/scripts/backup-certs.sh`
```bash
#!/bin/bash
# Backup SSL certificates

BACKUP_DIR="/etc/traefik/acme/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"
cp /etc/traefik/acme/acme.json "$BACKUP_DIR/acme_$TIMESTAMP.json"
echo "Backup completed: $BACKUP_DIR/acme_$TIMESTAMP.json"
```

#### B2: Create Restore Script
File: `compose/traefik/scripts/restore-certs.sh`
```bash
#!/bin/bash
# Restore SSL certificates if they don't exist

ACME_FILE="/etc/traefik/acme/acme.json"
BACKUP_DIR="/etc/traefik/acme/backups"

if [ ! -f "$ACME_FILE" ]; then
    if [ -f "$BACKUP_DIR"/acme_*.json ]; then
        LATEST=$(ls -t "$BACKUP_DIR"/acme_*.json | head -n1)
        cp "$LATEST" "$ACME_FILE"
        chmod 600 "$ACME_FILE"
        echo "Restored certificates from: $LATEST"
    else
        echo "No backup found, will generate new certificates"
    fi
fi
```

#### B3: Update Traefik Dockerfile
File: `compose/traefik/Dockerfile`
```dockerfile
FROM traefik:latest

COPY scripts/backup-certs.sh /backup-certs.sh
COPY scripts/restore-certs.sh /restore-certs.sh
RUN chmod +x /backup-certs.sh /restore-certs.sh

# Run on startup
ENTRYPOINT ["/restore-certs.sh"]
CMD ["traefik", "--configFile=/etc/traefik/traefik.yml"]
```

### Phase C: Template Consolidation (1 hour)

#### C1: Create Consolidation Script
File: `scripts/consolidate-templates.sh`
```bash
#!/bin/bash

# Create temp consolidation directory
TEMP_DIR="/tmp/templates_consolidated"
FINAL_DIR="assets/templates/generic"

mkdir -p "$TEMP_DIR"
mkdir -p "$FINAL_DIR"

# Copy all templates from packages/ui
echo "Consolidating packages/ui templates..."
cp -r packages/ui/notifications/* "$TEMP_DIR/"
cp -r packages/ui/modals/* "$TEMP_DIR/"
cp -r packages/ui/forms/* "$TEMP_DIR/"

# Copy all templates from sites
echo "Consolidating site templates..."
cp -r ctc-research/assets/templates/generic/* "$TEMP_DIR/"
cp -r lms/assets/templates/generic/* "$TEMP_DIR/" 2>/dev/null || true
cp -r VResume/assets/templates/generic/* "$TEMP_DIR/" 2>/dev/null || true

# Remove duplicates (keep latest)
echo "Removing duplicates..."
cd "$TEMP_DIR"
find . -name "*.html" -type f -exec md5sum {} \; | sort | uniq -w32 --all-repeated=separate

# Copy final set to assets
echo "Finalizing templates..."
cp -r "$TEMP_DIR"/* "$FINAL_DIR/"

echo "Consolidation complete: $FINAL_DIR"
ls -la "$FINAL_DIR"
```

#### C2: Identify Duplicate Templates
Run consolidation script to find and document duplicates

#### C3: Delete Duplicate Templates
```bash
# After consolidation, delete old locations
rm -rf packages/ui/notifications/*
rm -rf packages/ui/modals/*
rm -rf packages/ui/forms/*
rm -rf ctc-research/assets/templates/generic_old/
```

#### C4: Update All Template Includes
Update base templates to reference `assets/templates/generic/`

### Phase D: JavaScript Generation & Integration (1.5 hours)

#### D1: Generate JavaScript Modules
Location: `assets/static/js/` (workspace root)

Create:
- `app.js` - Main app initialization
- `htmx-config.js` - HTMX configuration
- `notifications.js` - Notification functions
- `modals.js` - Modal functions
- `forms.js` - Form helpers

#### D2: Create JavaScript Entry Point
File: `assets/static/js/index.js`
```javascript
// Main entry point for all sites
import './app.js';
import './htmx-config.js';
import './notifications.js';
import './modals.js';
import './forms.js';

window.app = window.app || {};
```

#### D3: Update Site Base Templates
All three sites include:
```html
<script src="{% static 'js/app.js' %}"></script>
<script src="{% static 'js/notifications.js' %}"></script>
<script src="{% static 'js/modals.js' %}"></script>
<script src="{% static 'js/forms.js' %}"></script>
```

#### D4: Delete Site-Specific JS
```bash
# Delete duplicates from sites
rm -rf ctc-research/assets/static/js/old_*
rm -rf lms/assets/static/js/old_*
rm -rf VResume/assets/static/js/old_*
```

#### D5: Update Static File Configuration
Each site's settings.py:
```python
STATICFILES_DIRS = [
    BASE_DIR / 'assets/static',  # Workspace root
    BASE_DIR / 'static',          # Site-specific
]
```

### Phase E: Complete Remaining Phases (6-16)

#### Phase 6: Enrollment ✅ DONE
- Forms created
- Views implemented
- Email templates
- Admin management

#### Phase 7: Payment Providers (1-2 hours)
- Abstract base class
- Stripe, PayPal, Paymo implementations
- Provider registry

#### Phase 8: Wagtail CMS Integration (1 hour)
- Register snippets
- Admin viewsets
- Filters and exports

#### Phase 9: JS Bundle Standardization (1 hour)
- Consolidate and minify
- Generate production bundle
- Verify integration

#### Phase 10: Traefik Refactor (30 min)
- Move to infra/traefik
- Update references
- Verify SSL

#### Phase 11: Infrastructure Separation (30 min)
- Create warehouses/ and utilities/ directories
- Move services
- Update includes

#### Phase 12: Makefile Refactor (1 hour)
- Clean up targets
- Add missing commands
- Test all commands

#### Phase 13: Testing (2-3 hours)
- Create unit tests
- Create integration tests
- Achieve 70%+ coverage

#### Phase 14: GitHub Actions (30 min)
- Update CI/CD workflows
- Setup automated testing

#### Phase 15: Documentation (1-2 hours)
- Site-specific guides
- Deployment guide
- Troubleshooting

#### Phase 16: Final Validation (1-2 hours)
- Verify all systems
- Run full test suite
- Generate final report

---

## Execution Order

**Day 1 (Morning - 4 hours):**
1. Phase A: Docker Service Fix (30 min)
2. Phase B: SSL Certificate Backup (30 min)
3. Phase C: Template Consolidation (1 hour)
4. Phase D: JavaScript Generation (1.5 hours)
5. Phase 6: Enrollment ✅ (Already done)

**Day 1 (Afternoon - 4 hours):**
6. Phase 7: Payment Providers (1.5 hours)
7. Phase 8: Wagtail CMS (1 hour)
8. Phase 9: JS Bundle (1 hour)
9. Phase 10-11: Infrastructure (1 hour)

**Day 2 (Morning - 4 hours):**
10. Phase 12: Makefile (1 hour)
11. Phase 13: Testing (2-3 hours)

**Day 2 (Afternoon - 3 hours):**
12. Phase 14: GitHub Actions (30 min)
13. Phase 15: Documentation (1.5 hours)
14. Phase 16: Validation (1 hour)

---

## Success Criteria

### Docker & Infrastructure
- ✅ All service names consistent with Traefik labels
- ✅ SSL certificate backup/restore working
- ✅ All services starting without errors
- ✅ Traefik routing all sites correctly

### Templates & Static Files
- ✅ No duplicate templates
- ✅ Single source of truth in assets/
- ✅ All sites using same templates
- ✅ No site-specific duplicates

### JavaScript
- ✅ JS modules generated
- ✅ In assets/static/ (workspace root)
- ✅ All sites using same JS
- ✅ No duplicates in sites
- ✅ Functions working (notifications, modals, forms)

### All Phases
- ✅ Phases 1-16 complete
- ✅ All tests passing
- ✅ All GitHub Actions working
- ✅ Documentation complete
- ✅ Production ready

---

## Files to Create/Modify

### Creation
- `compose/traefik/scripts/backup-certs.sh` (NEW)
- `compose/traefik/scripts/restore-certs.sh` (NEW)
- `scripts/consolidate-templates.sh` (NEW)
- `assets/static/js/app.js` (NEW)
- `assets/static/js/notifications.js` (NEW)
- `assets/static/js/modals.js` (NEW)
- `assets/static/js/forms.js` (NEW)
- `assets/static/js/index.js` (NEW)
- `docs/FINAL_IMPLEMENTATION_REPORT.md` (NEW)

### Modifications
- `ctc-research/docker-compose.yml` (UPDATE labels)
- `lms/docker-compose.yml` (UPDATE labels)
- `VResume/docker-compose.yml` (UPDATE labels)
- `compose/traefik/Dockerfile` (UPDATE)
- All site settings.py (UPDATE STATICFILES_DIRS)
- All site base templates (UPDATE JS includes)

### Deletion
- `packages/ui/notifications/*` (DELETE)
- `packages/ui/modals/*` (DELETE)
- `packages/ui/forms/*` (DELETE)
- Site-specific duplicate JS files

---

## Ready to Start?

All planning complete. Ready to execute phases systematically.

**Next Steps:**
1. Start with Phase A: Docker Service Fix
2. Follow with Phase B: SSL Backup
3. Then Phase C: Template Consolidation
4. Then Phase D: JavaScript Generation
5. Complete Phases 6-16

Let's begin!

