# Spec Archive — Restore Procedures

**Archive created:** 2025
**Task:** 6.2 — Create backups of specs to be deleted
**Spec:** documentation-enhancement-and-spec-consolidation

---

## Archive Location

All archived specs are stored at: `.kiro/specs/_archive/`

The archive directory uses an underscore prefix (`_archive`) to distinguish it from active specs.

---

## Archived Specs

| Spec | Files | Reason for Archival |
|------|-------|---------------------|
| `ctc-research-deployment-verification` | 4 | 100% complete, superseded by ecosystem-architectural-refactoring |
| `django-refactoring` | 13 | All mandatory phases complete, superseded by ecosystem-architectural-refactoring |
| `ecosystem-architectural-refactoring` | 5 | 100% complete, architecture is now the established baseline |
| `finalize-refactor` | 5 | 100% complete, superseded by ecosystem-architectural-refactoring |
| `phase-3-production-deployment` | 4 | 100% complete, one-time deployment event |
| `documentation-enhancement-and-spec-consolidation` | 40 | 100% complete, all 7 phases finished, sign-off approved |

---

## Restore Procedures

### Restore a Single Spec

To restore any archived spec back to the active specs directory:

```bash
cp -r .kiro/specs/_archive/<spec-name> .kiro/specs/<spec-name>
```

**Examples:**

```bash
# Restore ctc-research-deployment-verification
cp -r .kiro/specs/_archive/ctc-research-deployment-verification .kiro/specs/ctc-research-deployment-verification

# Restore django-refactoring
cp -r .kiro/specs/_archive/django-refactoring .kiro/specs/django-refactoring

# Restore ecosystem-architectural-refactoring
cp -r .kiro/specs/_archive/ecosystem-architectural-refactoring .kiro/specs/ecosystem-architectural-refactoring

# Restore finalize-refactor
cp -r .kiro/specs/_archive/finalize-refactor .kiro/specs/finalize-refactor

# Restore phase-3-production-deployment
cp -r .kiro/specs/_archive/phase-3-production-deployment .kiro/specs/phase-3-production-deployment
```

### Restore All Archived Specs

To restore all archived specs at once:

```bash
for spec in ctc-research-deployment-verification django-refactoring ecosystem-architectural-refactoring finalize-refactor phase-3-production-deployment documentation-enhancement-and-spec-consolidation; do
  cp -r .kiro/specs/_archive/$spec .kiro/specs/$spec
done
```

### Verify Restore Completeness

After restoring, verify the file counts match:

```bash
for spec in ctc-research-deployment-verification django-refactoring ecosystem-architectural-refactoring finalize-refactor phase-3-production-deployment documentation-enhancement-and-spec-consolidation; do
  orig=$(find .kiro/specs/$spec -type f | wc -l)
  bak=$(find .kiro/specs/_archive/$spec -type f | wc -l)
  echo "$spec: restored=$orig, archive=$bak, match=$([ $orig -eq $bak ] && echo YES || echo NO)"
done
```

---

## Archived File Inventory

### `ctc-research-deployment-verification` (4 files)

```
.kiro/specs/_archive/ctc-research-deployment-verification/.config.kiro
.kiro/specs/_archive/ctc-research-deployment-verification/design.md
.kiro/specs/_archive/ctc-research-deployment-verification/requirements.md
.kiro/specs/_archive/ctc-research-deployment-verification/tasks.md
```

### `django-refactoring` (13 files)

```
.kiro/specs/_archive/django-refactoring/.config.kiro
.kiro/specs/_archive/django-refactoring/Analysis_completion.md
.kiro/specs/_archive/django-refactoring/architecture-analysis-report.md
.kiro/specs/_archive/django-refactoring/architecture-design.md
.kiro/specs/_archive/django-refactoring/design.md
.kiro/specs/_archive/django-refactoring/email-wagtail-design.md
.kiro/specs/_archive/django-refactoring/enhancement-validation-report.md
.kiro/specs/_archive/django-refactoring/git-analysis-report.md
.kiro/specs/_archive/django-refactoring/package-structure-analysis.md
.kiro/specs/_archive/django-refactoring/requirements.md
.kiro/specs/_archive/django-refactoring/shared-library-design.md
.kiro/specs/_archive/django-refactoring/tasks.md
.kiro/specs/_archive/django-refactoring/test-coverage-analysis.md
```

### `ecosystem-architectural-refactoring` (5 files)

```
.kiro/specs/_archive/ecosystem-architectural-refactoring/.config.kiro
.kiro/specs/_archive/ecosystem-architectural-refactoring/design.md
.kiro/specs/_archive/ecosystem-architectural-refactoring/enhancement-validation-report.md
.kiro/specs/_archive/ecosystem-architectural-refactoring/requirements.md
.kiro/specs/_archive/ecosystem-architectural-refactoring/tasks.md
```

### `finalize-refactor` (5 files)

```
.kiro/specs/_archive/finalize-refactor/.config.kiro
.kiro/specs/_archive/finalize-refactor/design.md
.kiro/specs/_archive/finalize-refactor/enhancement-validation-report.md
.kiro/specs/_archive/finalize-refactor/requirements.md
.kiro/specs/_archive/finalize-refactor/tasks.md
```

### `phase-3-production-deployment` (4 files)

```
.kiro/specs/_archive/phase-3-production-deployment/.config.kiro
.kiro/specs/_archive/phase-3-production-deployment/enhancement-validation-report.md
.kiro/specs/_archive/phase-3-production-deployment/requirements.md
.kiro/specs/_archive/phase-3-production-deployment/tasks.md
```

---

## Integrity Verification

Backup integrity was verified at archive creation time. All file counts matched between originals and backups:

| Spec | Original Files | Backup Files | Match |
|------|---------------|--------------|-------|
| `ctc-research-deployment-verification` | 4 | 4 | ✅ YES |
| `django-refactoring` | 13 | 13 | ✅ YES |
| `ecosystem-architectural-refactoring` | 5 | 5 | ✅ YES |
| `finalize-refactor` | 5 | 5 | ✅ YES |
| `phase-3-production-deployment` | 4 | 4 | ✅ YES |
| `documentation-enhancement-and-spec-consolidation` | 40 | 40 | ✅ YES |

---

## Notes

- The archive directory is intentionally kept alongside active specs for easy access.
- The underscore prefix (`_archive`) ensures it sorts separately from active spec directories.
- These specs were archived as part of the `documentation-enhancement-and-spec-consolidation` spec, Phase 6 (Delete Old Specs).
- Deletion of the originals occurs in task 6.4 after references are updated (task 6.3).
- See `deletion-recommendations.md` in the `documentation-enhancement-and-spec-consolidation` spec for the full rationale behind each deletion.
