# Migration Record

## ctc-research → lms-demo Structural Differences

lms-demo is the renamed and re-scoped successor to ctc-research. Both sites coexist in the monorepo.

| Property | ctc-research | lms-demo |
|----------|--------------|----------|
| SITE_ID | 1 | 2 |
| WEBSITE_IDENTIFIER | ctc-research | lms-demo |
| Default port | 5070 | 5071 |
| apps.py | Not present at root | Present at root |
| uv.lock | Workspace-level only | Site-level |
| .env.demo | Present | Not present |
| .env.testing | Present | Not present |

Both sites share `configs.settings` via `from configs.settings import *` and both duplicate the same `SILENCED_SYSTEM_CHECKS` list verbatim. Consolidating that list into `configs/settings.py` is a pending task.

The Webpack `SITE_DIR_MAP` maps `structa`, `structa.cloud`, and `lms` to `lms-demo`, so `npm run build:structa` continues to work against the lms-demo site directory.

## Theme Directory Migration (June 2, 2026)

The `assets/static/js/theme/` directory was deleted as part of a vendor-packages and usecases refactor:

| File | Old Location | New Location |
|------|--------------|--------------|
| vendor-packages.js | theme/vendor-packages.js | projects/vendor-packages.js |
| usecases.js | theme/usecases.js | modules/usecases/index.js |

All three site `app.js` files were updated from:
```javascript
import { initAllUsecases } from '@theme'
```
to:
```javascript
import { initAllUsecases } from '../../../../assets/static/js/modules/index.js'
```

The build passed with 23 pre-existing Vue version warnings and produced 408 bundles totaling 73 MB.

The `@theme`, `@layouts`, and `@usecases` aliases in `main.config.js` were not updated during that migration and still point into the deleted directory. These are stale aliases.
