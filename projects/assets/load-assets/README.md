# Load Assets (shared)

Canonical shared location for loadable content used by data-loading and
asset-population flows across products (`load-dumps`, fixture loaders,
`data_populator`, webpack-driven content builds).

## Why a shared directory

Each product owns its own `assets/` tree (source SCSS, JS, images, locale,
fixtures) under `projects/<product>/`. Content that is loaded or generated
from more than one product — JSON dump fixtures, seed data, shared content
images — belongs here instead, so products never duplicate or fork the
same loadable assets. This mirrors the rule for the monorepo-level
`projects/assets/` shared tree in the root `AGENTS.md`.

## Directory structure

```text
projects/assets/load-assets/
├── README.md                 # This file
├── dumps/                    # JSON dump fixtures loaded by load-dumps
├── seeds/                    # Shared seed/content fixtures
└── images/                   # Content images referenced by seed data
```

Add product-specific loadable assets under a product-named subdirectory
(e.g. `dumps/precis-lms/`) so the tree stays organized.

## Webpack wiring

The shared path is exported by `projects/webpack/paths.js`:

```js
const { loadAssetsDir } = require('../../webpack/paths');
```

`resolvePaths()` resolves per-project `assets/` trees; `loadAssetsDir`
resolves the monorepo-shared `projects/assets/load-assets/` directory so
webpack configs and asset pipelines can reference it consistently.

## Naming conventions

- Dumps: `{product}-{env}-{purpose}.json` — e.g. `precis-lms-prod-pages.json`
- Seeds: `{product}-{entity}.json` — e.g. `loop-crm-products.json`
- Images: `{product}-{subject}-{description}.{ext}`
