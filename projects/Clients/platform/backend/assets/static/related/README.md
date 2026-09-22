# Related Product Media

Screenshots and screencasts used by the Formints product pages on structa.cloud.

## Naming convention

```text
related/<product-slug>/<edition>-<label>.<ext>
```

- `<edition>` comes first so related media stays easy to scan (`standard`, `pro`).
- Use descriptive kebab-case labels (`checkout`, `operations`, `screencast`).
- Use `jpg`/`png` for still captures and `gif` for animated screencasts.

## Formints media

| File | Description |
|------|-------------|
| `formints/standard-checkout.jpg` | Formints Standard checkout screen |
| `formints/standard-operations.jpg` | Formints Standard data and operations |
| `formints/standard-sale-complete.png` | Completed sale receipt with actions |
| `formints/standard-screencast.gif` | Full Formints Standard screencast |
| `formints/standard-walkthrough.gif` | Animated walkthrough of Standard POS |
| `formints/pro-admin-dashboard.jpg` | Formints Pro admin dashboard |
| `formints/pro-admin-products.jpg` | Formints Pro product administration |
| `formints/pro-admin-customers.jpg` | Formints Pro customer administration |
| `formints/pro-admin-sales.jpg` | Formints Pro sales administration |
| `formints/pro-admin-loyalty.jpg` | Formints Pro loyalty administration |
| `formints/pro-admin-settings.jpg` | Formints Pro settings administration |

The same files are mirrored in the Astro public tree at
`frontend/public/static/related/formints/` so Django and Astro resolve the
same `/static/related/formints/...` URLs.

## Animated media must stay browser-safe

Browsers fail to decode full-length screencasts stored as GIF (too many
frames / decoded pixels) and the gallery falls back to
"Preview unavailable. Open this capture.". Keep `gif` previews **≤ ~150
frames** (a ~12–15 s loop at ~10 fps), **≤ ~5 MB**, width **≤ 720 px**, and
re-encode with an adaptive palette + `disposal=2`. See
`../previews/README.md` for the full guideline (Aug 2026: the two Standard
GIFs were 229/458 frames at 10.4/54 MB and failed to decode; resampled to
115 frames at 5.2/7.3 MB).
