# Structa Cloud Docus

The repository documentation is served with [Docus](https://docus.dev), a
Nuxt Content documentation layer with SSR, full-text search, responsive
navigation, SEO/LLM metadata, and built-in internationalization.

## Local development

```bash
cd docs/docus
npm install
npm run dev
```

The local site uses the `/docs/` base path to match the deployed shared-proxy
route. Open `http://localhost:3000/docs/`.

## Languages

- English: `/docs/en/`
- Arabic: `/docs/ar/`

The English locale is generated from the existing repository Markdown tree so
current documentation remains in one source location. Arabic core onboarding
pages live in `ar-content/` and use Docus/ Nuxt i18n RTL metadata. Additional
Arabic pages can be added by mirroring the English route under `ar-content/`.

## Build

```bash
npm run build          # Nuxt server output for deployment
npm run build:static   # optional static export for isolated hosting
npm run preview
```

`prepare-content.mjs` creates the ignored `content/en/` and `content/ar/`
directories before development and build. The production image runs the Docus
Nuxt server so deep links, search, sitemap, LLM output, and locale switching
remain fully functional.

## Deployment contract

- `media.structa.cloud/docs/` is proxied by shared-proxy Nginx to `docus:3000`.
- `docs.structa.cloud/` is proxied through the same shared-proxy service.
- Traefik keeps the existing `/docs` strip-prefix middleware for the docs host.
- `NUXT_APP_BASE_URL=/docs/` keeps asset and locale links valid on both hosts.

Do not commit generated `content/`, `.nuxt/`, `.output/`, `dist/`, or
`node_modules/`.
