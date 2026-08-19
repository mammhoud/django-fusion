# Structa Cloud Docus application

This directory contains the Nuxt/Docus application that serves the authored
repository documentation. The canonical reader-facing implementation guide is
[`../guides/09-docus.md`](../guides/09-docus.md); keep operational detail there
instead of maintaining a second documentation copy in this package README.

## Local development

```bash
cd docs/docus
npm install
npm run prepare-content
npm run validate-content
npm run dev
```

Open `http://localhost:3000/docs/en/`. The application also exposes the Arabic
locale at `/docs/ar/` and uses `/docs/` as its configured base path.

## Build and preview

```bash
npm run build
npm run build:static
npm run preview
```

`prepare-content.mjs` generates the ignored `content/en/` and `content/ar/`
trees before development and build. Do not edit or commit `content/`, `.nuxt/`,
`.output/`, `dist/`, or `node_modules/`.

## Deployment

The production image is built from `docs/Dockerfile`, runs the Docus Nuxt SSR
server on `docus:3000`, and is routed by the shared proxy. See the canonical
[Docus implementation guide](../guides/09-docus.md) for the proxy contract,
metadata model, validation commands, and source-of-truth rules.

## Remarks & Notes

- This README describes the application package; `docs/guides/09-docus.md` is the single published Docus guide.
- A Docus build does not validate product backend health; run the owning project checks separately.
