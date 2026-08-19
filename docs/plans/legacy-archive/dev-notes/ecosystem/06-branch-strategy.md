# Branch Strategy Update Summary

## Overview
This document summarizes the changes made to simplify the branching strategy across both **precis-ctc** and **xellent-site** projects.

## Changes Made

### 1. ✅ Removed `main-dev` Branch
The `main-dev` branch has been removed from the configuration. The project now uses a simplified two-branch workflow:

- **`dev`** - Development and demo environment (active development)
- **`main`** - Production-ready releases (stable code)

### 2. ✅ Configuration Updates

#### Both Projects (`configs/settings/conf.py`)
Updated the `DEMO_BRANCH` field from `"main-dev"` to `"dev"`:

```python
DEMO_BRANCH: str = Field(default="dev", description="Demo branch name")
MAIN_BRANCH: str = Field(default="main", description="Main branch name")
```

**Files Modified:**
- `/root/site/precis-ctc/configs/settings/conf.py` (line 80)
- `/root/site/xellent-site/configs/settings/conf.py` (line 80)

### 3. ✅ Documentation Updates

#### REPOSITORIES.md (Both Projects)
Updated the branching documentation to clearly explain the new strategy:

**Added Section:**
```markdown
### 🌿 Branch Strategy
The repository uses a simplified two-branch workflow:
- **dev**: Development and demo environment (active development)
- **main**: Production-ready releases (stable code)
```

**Files Modified:**
- `/root/site/precis-ctc/REPOSITORIES.md`
- `/root/site/xellent-site/REPOSITORIES.md`

### 4. ✅ Deploy Commands Fixed

Both makefiles were updated with correct CLI syntax for the sync operations:

**Previous (Incorrect):**
```makefile
sync-demo:
	@$(SYNC_PY) --env demo --push --workflow standard
```

**Updated (Correct):**
```makefile
sync-demo:
	@$(SYNC_PY) sync env=demo direction=push workflow=standard
```

**Files Modified:**
- `/root/site/precis-ctc/makefile`
- `/root/site/xellent-site/makefile`

## Branch Mapping

### Environment to Branch Mapping
The sync system now maps environments to branches as follows:

| Environment    | Branch  | Container      | Use Case                    |
|---------------|---------|----------------|----------------------------|
| `development` | `dev`   | `django-demo`  | Local development          |
| `demo`        | `dev`   | `django-demo`  | Demo/staging environment   |
| `production`  | `main`  | `django-main`  | Production releases        |
| `staging`     | `staging` | `django-staging` | Staging environment (optional) |
| `testing`     | `test`  | `django-demo`  | Testing environment        |

## Available Make Commands

### Deployment Commands
- `make deploy` - Full deployment pipeline (syncs to configured environment)
- `make rollback` - Rollback last deployment

### Sync Commands
- `make sync-demo` - Push to demo environment (`dev` branch)
- `make sync-main` - Push to main/production (`main` branch)
- `make push-demo` - Push to demo (alias)
- `make push-main` - Push to main (alias)
- `make pull-demo` - Pull from demo
- `make pull-main` - Pull from main

### Token Management
- `make token-list` - List available GitHub tokens
- `make token-save` - Save token securely
- `make token-test` - Test token validity

## Migration Notes

### If You Have a `main-dev` Branch
If your remote repository still has a `main-dev` branch, you should:

1. **Rename it to `dev`:**
   ```bash
   git branch -m main-dev dev
   git push origin -u dev
   git push origin --delete main-dev
   ```

2. **Or create a new `dev` branch from `main-dev`:**
   ```bash
   git checkout main-dev
   git checkout -b dev
   git push origin -u dev
   ```

### Updating Your Local Environment
After these changes, ensure your local repository is in sync:

```bash
# Fetch latest branches
git fetch origin

# Switch to dev branch
git checkout dev

# Or create it if it doesn't exist
git checkout -b dev origin/dev
```

## Testing the Changes

### Test Sync to Demo
```bash
cd /root/site/precis-ctc
make sync-demo
```

This will sync your changes to the `dev` branch.

### Test Sync to Production
```bash
cd /root/site/precis-ctc
make sync-main
```

This will sync your changes to the `main` branch.

## Summary of Files Changed

### Both Projects (precis-ctc & xellent-site)
1. `configs/settings/conf.py` - Updated DEMO_BRANCH configuration
2. `makefile` - Fixed deploy and sync commands
3. `REPOSITORIES.md` - Updated documentation

### Total Files Modified
- **6 files** across both projects

## Benefits of This Change

✅ **Simpler branching** - Clear dev/main workflow
✅ **Industry standard** - Follows common Git flow patterns
✅ **Easier understanding** - "dev" is more intuitive than "main-dev"
✅ **Consistent naming** - Aligns with standard practices
✅ **Better deploy clarity** - Demo = dev branch, Release = main branch

## Next Steps

1. ✅ Update remote repositories to use `dev` instead of `main-dev`
2. ✅ Update any CI/CD pipelines to reference `dev` branch
3. ✅ Communicate changes to team members
4. ✅ Update any external documentation or wikis

---

**Last Updated:** 2026-02-10
**Modified By:** Branch Strategy Simplification
