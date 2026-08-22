# Formint asset registry

`projects/formints/assets/` is the product-level source of truth for assets that
are consumed by more than one Formint edition. It is deliberately below the
Formint product boundary and above individual frontends, so Community,
Standard, Cloud, Pro, and Client can share brand files without copying source
trees.

## Layout

```text
assets/
├── shared/                 # canonical multi-edition assets
│   ├── fonts/              # Outfit + Roboto webfonts
│   ├── icons/              # shared desktop icons + Remix Icon webfont files
│   ├── images/             # shared brand/transaction imagery
│   ├── public/             # web-root files and shared raster app mark (Logo.png)
│   ├── static/             # Django static assets (POS crest)
│   └── styles/fonts/       # @font-face declarations for shared webfonts
└── [edition]/              # only when an asset is not shared
```

Edition-owned style systems remain in each frontend because the React/FlyonUI,
Cloud tactical admin, Pro Astro, and Client Vue surfaces have different build
contracts. Edition-only Tauri platform exports also remain with their owning
shell.

## Delegation rules

| Consumer | Shared source | Wiring |
|---|---|---|
| Community / Standard Astro | `shared/public`, `shared/images`, `shared/fonts`, `shared/styles/fonts` | `publicDir` and `@formints-assets` alias |
| Community / Standard Tauri | `shared/icons`, `shared/public/Logo.png` | bundle icons and tray icon paths |
| Cloud Astro frontend | same shared roots | `publicDir` and `@formints-assets` alias |
| Pro Astro frontend | `shared/fonts`, `shared/images` | `@formints-assets` alias |
| Pro / Cloud / Client Django | `shared/static` | `FORMINT_SHARED_ASSETS` + `STATICFILES_DIRS` |
| Client Vue/Astro | no duplicated shared brand bundle | local favicon and Fontsource packages remain edition-owned |

## Ownership rules

- A file belongs here only when its content and runtime contract are shared.
- Build output, databases, secrets, installer bundles, and generated reports do
  not belong here.
- Frontend source styles stay local when their theme/build semantics differ.
- Django collects shared static files into the edition's normal `STATIC_ROOT`;
  the parent directory is never used as a runtime write directory.
- Change the parent asset contract and the relevant `configs/assets.yml`
  entry together.
