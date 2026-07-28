# Customizer

> **Related Code**
> * **Domain:** Site (Themeforest-tier customizer)
> * **Paths:**
>   * `applications/customizer/docker-compose.yml`
>   * `applications/customizer/instructions.json` (theme metadata)
> * **Production URL:** https://customizer.structa.cloud
> * **Variant:** `layout/landing/skeleton.html`

## What this site is

The Customizer is the theme-preview/customization surface. It serves the Themeforest submission flow and lets buyers preview a Structa Cloud theme against their own content without standing up a full Wagtail install.

## Site / Application / Viewset tree

```text
CustomizerSite (Site)
├── PreviewApp (Application)
│   ├── ThemePicker (FragmentComponent)  -- /themes/
│   └── LivePreview (RoutableComponent)  -- /preview/<theme_id>/
└── SubmitApp (Application)
    └── CheckoutDelegate (RoutableComponent) -- /submit/
```

## Conventions

1. Theme bundles are prebuilt by the theme factory pipeline (see `theme/_variables.scss` and `theme/_INDEX.md`).
2. Each theme lives under `applications/assets/templates/themes/<theme_id>/skeleton.html` and is reachable from the Customizer via the `themes/` Application.

## See also

* [`prompts.md`](prompts.md) — Customizer-specific prompt catalog.
* [`../architecture/templates_layout.md`](../architecture/templates_layout.md) — layout chain reference.
