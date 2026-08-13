# Product Previews

Screenshots and screencasts for product pages on structa.cloud.

## Naming Convention

```
previews/<product-slug>/<edition>-<label>.<ext>
```

- `<product-slug>`: formints, lms, cms, syntara, vresume
- `<edition>`: standard, pro, cloud, business, solo
- `<label>`: front, back, dashboard, products, walkthrough
- `<ext>`: jpg (screenshot), gif (animated screencast), png (lossless)

## Animated media must stay browser-safe

Full-length screencasts stored as GIF break in browsers: Chrome and other
engines fail to decode very large animations (too many frames / decoded
pixels), which makes the gallery fall back to
"Preview unavailable. Open this capture.".

**Rules for `gif` previews:**

- Keep **≤ ~150 frames** (a ~12–15 s preview at ~10 fps). Sample a long
  recording down to a preview loop instead of shipping the whole capture.
- Keep the total decoded size well under the browser limit
  (`width × height × frames` ≲ 50 MP) and the file **≤ ~5 MB**.
- Cap the width at **720 px**.
- Re-encode with an adaptive palette (128 colors) + `disposal=2`.

> Example fix (Aug 2026): `standard-walkthrough.gif` was a 229-frame
> 10.4 MB recording and `standard-screencast.gif` a 458-frame 54 MB one;
> both failed to decode in browsers. They were resampled to ~115 frames,
> 720 px wide, 5.2 / 7.3 MB — well within every engine's limits.

## Formints Previews

| File | Description |
|------|-------------|
| `standard-front.jpg` | Formints Standard checkout screen |
| `standard-back.jpg` | Formints Standard data & operations |
| `standard-walkthrough.gif` | Animated walkthrough of Standard POS |
| `standard-sale-complete.png` | Completed sale receipt with actions |
| `pro-admin-dashboard.jpg` | Formints Pro admin dashboard |
| `pro-admin-products.jpg` | Formints Pro product administration |
