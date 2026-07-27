# Legacy Directory Cleanup Plan

> **Last updated:** 2026-07-26 | **Branch:** `generic`  
> **Scope:** Audit, archive, and optionally remove old/duplicate directories now that the Fusion architecture is scaffolded.

---

## 1. Cleanup Candidates

| # | Directory | Reason for Removal | Risk | Suggested Action |
|---|-----------|-------------------|------|------------------|
| 1 | `projects/lms/cms/` | Overlaps with new `lms-fusion/backend/` and legacy `projects/cms/lms-full/` | High — may still be referenced by old build scripts | Archive first, delete after 1 release cycle |
| 2 | `projects/cms/lms-full/` | Replaced by `lms-fusion` | High — contains active LMS data/models in some envs | Archive first, delete after migration verification |
| 3 | `projects/lms/front-end/` | Superseded by `lms-fusion/frontend/` | Medium — Next.js app may still be built by CI | Verify CI references, then archive |
| 4 | `projects/cms/portfolio/anytype/` | Operational/marketing docs not used by the app | Low | Archive to `docs/archive/` or delete |
| 5 | `projects/pos/pos-mini/` / `pos-solo/` / `pos-full/` duplicates | Multiple POS editions may overlap | High — confirm which editions are active | Do not delete; consolidate plans instead |

---

## 2. Pre-Cleanup Checklist

Before removing any directory:

- [ ] Verify the directory is not referenced by `projects/Makefile`, `Makefile`, or CI workflows.
- [ ] Verify no active deployment uses the directory as a Docker build context.
- [ ] Search for imports or template paths that reference the directory.
- [ ] Create a compressed archive under `archives/<date>-<dir-name>.tar.gz`.
- [ ] Update `AGENTS.md` and `README.md` to point to the new canonical paths.

---

## 3. Safe Removal Procedure

```bash
# 1. Create an archive
mkdir -p archives
 tar -czf archives/2026-07-26-projects-lms-cms.tar.gz projects/lms/cms

# 2. Verify nothing references the directory
grep -R "projects/lms/cms" Makefile projects/Makefile .github/ || true
rg "projects/lms/cms" --type py --type js --type ts --type md --type yml || true

# 3. Remove only after verification
git rm -r projects/lms/cms

# 4. Commit with a clear message
git commit -m "chore(cleanup): archive and remove legacy projects/lms/cms"
```

---

## 4. Rollback

If a deleted directory is needed again:

```bash
tar -xzf archives/2026-07-26-projects-lms-cms.tar.gz
```

---

## 5. Legend

| Symbol | Meaning |
|:------:|---------|
| ✅ | Complete |
| 🟡 | In Progress |
| ⬜ | Not Started |
| ❌ | Blocked |
