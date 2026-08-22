# Structa Cloud — Brand Logo Enhancement Plan

> Generated: 2026-08-18 · Scope: all projects in the workspace

---

## 1 · Audit Summary

| Project | Logo Files | States Covered | Quality | Key Issues |
|---|---|---|---|---|
| **Loop CRM** | favicon.svg, loop-crm-logo.svg | favicon only | ★★★ | No `Logo.svg` for Astro app; no auth/loading logos |
| **Formint Community** | formint-crest.svg, Logo.svg, Logo.png.placeholder.svg, favicon | BrandLoader only | ★★☆ | `Logo.svg` still shows old POS shield (≠ new crest); placeholder says "FORGE" |
| **Formint Standard** | formint-crest.svg, Logo.svg, bg-texture.svg | BrandLoader only | ★★☆ | Same as Community — `Logo.svg` mismatches new crest |
| **Formint Cloud** | formint-crest.svg, Logo.svg, bg-texture.svg | BrandLoader only | ★★☆ | Same — `Logo.svg` mismatches new crest |
| **Formint Client** | favicon.svg (×2) | favicon only | ★★☆ | No brand crest; favicon uses yellow chevron + green circle |
| **Precis Main** | favicon.svg | favicon only | ★★★ | No logo SVG; favicon is blue tag glyph (different brand palette) |
| **Precis Landing** | favicon.svg | favicon only | ★★★ | Identical to Main — no distinct identity |
| **Precis CTC** | 7 brand SVGs + 6 layout partials | Header/favicon/partial | ★★★★ | Fixed: wagtailadmin base.html; auth templates still reference missing `images/logo.png` |
| **Syntara** | (none found) | — | ☆☆☆ | No logo assets at all |

---

## 2 · Per-Project Enhancement Plan

### 2.1 Loop CRM

**Current:** Recurrence loop mark (blue) + revenue bars (amber). No standalone `Logo.svg`.

**Palette:**
| Token | Hex | Role |
|---|---|---|
| Ink | `#0A0E14` | Background |
| Sky | `#0EA5E9` | Primary accent (loops, signals) |
| Amber | `#F59E0B` | Currency, closed-won |
| Paper | `#E8ECF0` | Text |
| Fog | `#5A6577` | Muted text |

**Variants to generate:**
| Variant | File | Purpose |
|---|---|---|
| `Logo.svg` | `frontend/public/Logo.svg` | App header, email signatures |
| `favicon.svg` | `frontend/public/favicon.svg` | Browser tab (already done) |
| `logo-light.svg` | `frontend/public/logo-light.svg` | Dark-on-light backgrounds |
| `logo-loading.svg` | Inline in `BrandLoader` | Progress ring loader |
| `logo-error.svg` | — | 404 / empty-state fallback |
| `logo-email.svg` | — | Email templates (static, no animation) |

**Design directions:**
1. **Primary mark:** Recurrence arc + revenue bars (current)
2. **Monogram variant:** `L` formed from the arc terminus — for small sizes
3. **Wordmark lockup:** Mark + "LOOP" in Inter 700 + "revenue workspace" in JetBrains Mono
4. **App tile:** Mark on dark rounded rect — for PWA/home screen

---

### 2.2 Formint (Community / Standard / Cloud)

**Current:** Octagonal ring + F-monogram + diamond spark (new crest, in thread). `Logo.svg` still shows old POS shield.

**Palette:**
| Token | Hex | Role |
|---|---|---|
| Ink | `#1A1917` | Background |
| Copper | `#EA580C` | Primary (ring, shield) |
| Orange | `#FB923C` | Secondary (F-mark) |
| Gold | `#F59E0B` | Spark, currency |
| Teal | `#14B8A6` | Form dots, accent |
| Paper | `#F8FAFC` | Text |

**Variants to generate:**
| Variant | File | Purpose |
|---|---|---|
| `Logo.svg` | `assets/public/Logo.svg` | App header, loading, PWA |
| `formint-crest.svg` | `assets/images/formint-crest.svg` | BrandLoader, chrome |
| `Logo.png.placeholder.svg` | `assets/public/Logo.png.placeholder.svg` | Fallback placeholder |
| `favicon.svg` | `frontend/public/favicon.svg` | Browser tab |
| `logo-email.svg` | — | Email templates |
| `logo-login.svg` | — | Auth/login screen variant |
| `logo-loading.svg` | Inline in `BrandLoader` | Progress ring loader |

**Design directions:**
1. **Primary crest:** Octagonal ring + F-mark + diamond spark (current new crest)
2. **Wordmark lockup:** Crest icon + "FORMINT" in Inter 700
3. **Simplified icon:** F-mark only (no ring) — for 16-32px contexts
4. **Login variant:** Crest on dark slate-900 with subtle glow — for auth boot screen
5. **Loading variant:** Crest inside SVG progress ring (already in BrandLoader)
6. **Error state:** Dimmed/desaturated crest for 404 / empty states
7. **Email variant:** Static, no animation, on white background

**All 3 variants (community, standard, cloud) must share identical `Logo.svg` and `formint-crest.svg`.**

---

### 2.3 Formint Client (Mobile POS)

**Current:** Yellow chevron + green circle on dark bg. No crest.

**Palette:**
| Token | Hex | Role |
|---|---|---|
| Dark | `#1A1917` | Background |
| Yellow | `#FFE14D` | Primary (chevron) |
| Green | `#2F6F5B` | Secondary (circle, stem) |

**Variants to generate:**
| Variant | File | Purpose |
|---|---|---|
| `favicon.svg` | `frontend/public/favicon.svg` | Browser tab (current — keep) |
| `Logo.svg` | `frontend/public/Logo.svg` | App splash, header |
| `logo-splash.svg` | — | Tauri startup screen |

**Design directions:**
1. **Current mark is fine** — keep the chevron + circle for the mobile client
2. Consider adding a "Client" wordmark for splash screen
3. The green/teal connects to the parent Formint brand

---

### 2.4 Precis (Main / Landing / CTC)

**Current:** Protocol Mark (P + crosshair + evidence line). Favicon is blue tag glyph (different palette).

**Palette:**
| Token | Hex | Role |
|---|---|---|
| Ink | `#0C1210` | Background |
| Paper | `#F5F2EB` | Text |
| Teal | `#1F8A70` | Primary (crosshair, learning) |
| Amber | `#C9962E` | Secondary (evidence line, certification) |
| Fog | `#7E8A82` | Muted |

**Variants to generate:**
| Variant | File | Purpose |
|---|---|---|
| `precis-protocol-mark.svg` | `assets/static/images/brand/` | Primary mark (done) |
| `precis-logo-lockup.svg` | `assets/static/images/brand/` | Horizontal lockup (done) |
| `favicon.svg` | `frontend/public/favicon.svg` | Browser tab (needs update to match teal palette) |
| `logo-login.svg` | — | Auth screen (Protocol Mark on ink bg) |
| `logo-loading.svg` | — | Loading/splash state |
| `logo-email.svg` | — | Email templates |
| `lms-ribbon.svg` | `assets/static/images/brand/` | LMS brand mark (cleaned) |

**Design directions:**
1. **Primary mark:** Protocol Mark (P + crosshair + evidence line) — DONE
2. **Favicon should match brand** — currently blue tag glyph doesn't match teal/amber palette
3. **Login variant:** Protocol Mark centered on dark ink bg with subtle teal glow
4. **Loading variant:** Protocol Mark with animated evidence line drawing in
5. **404 variant:** Dimmed Protocol Mark with "Page not found" text

---

### 2.5 Pos (Point of Sale)

**Current:** Circular ring + hexagonal shield + receipt lines + diamond spark (enhanced in thread).

**Palette:**
| Token | Hex | Role |
|---|---|---|
| Copper | `#EA580C` | Primary (ring, shield) |
| Orange | `#FB923C` | Secondary |
| Gold | `#F59E0B` | Receipt lines, spark |

**Note:** The Pos crest and Formint crest are now **visually distinct**:
- **Pos:** Circular ring + hexagonal shield + receipt lines
- **Formint:** Octagonal ring + F-monogram + form dots

This distinction is correct and intentional.

---

## 3 · State Coverage Matrix

| State | Loop CRM | Formint | Precis | Pos |
|---|---|---|---|---|
| **App header** | ✅ recurrence mark | ⚠️ Logo.svg mismatch | ✅ Protocol Mark | ✅ crest |
| **Favicon** | ✅ recurrence mark | ⚠️ chevron (client only) | ⚠️ blue tag (wrong palette) | — |
| **Login/Auth** | ❌ none | ⚠️ BrandLoader only | ⚠️ auth templates ref missing logo.png | — |
| **Loading/Splash** | ❌ none | ✅ BrandLoader (crest + ring) | ❌ none | — |
| **Empty state** | ❌ none | ❌ none | ❌ none | — |
| **404/Error** | ❌ none | ❌ none | ⚠️ has 404 page but no branded logo | — |
| **Email** | ❌ none | ❌ none | ❌ none | — |
| **PWA/App tile** | ❌ none | ⚠️ placeholder says "FORGE" | — | — |

Legend: ✅ done · ⚠️ exists but issues · ❌ missing

---

## 4 · Color System by Project

### 4.1 Loop CRM — "Dark Product / Operator"
```
Primary:   #0EA5E9 (Sky Blue)
Secondary: #F59E0B (Amber)
Background:#0A0E14 (Ink)
Surface:   #0F1419 (Panel)
Text:      #E8ECF0 (Paper)
Muted:     #5A6577 (Fog)
Line:      #1A2332
```

### 4.2 Formint — "Dark Product / Operator"
```
Primary:   #EA580C (Copper)
Secondary: #FB923C (Orange)
Accent:    #F59E0B (Gold)
Teal:      #14B8A6 (Form dots)
Background:#1A1917 (Ink)
Surface:   #252220 (Panel)
Text:      #F8FAFC (Paper)
Muted:     #9CA3AF (Fog)
Line:      #33302E
```

### 4.3 Precis — "Dark Nature / Calm System"
```
Primary:   #1F8A70 (Teal)
Secondary: #C9962E (Amber)
Background:#0C1210 (Ink)
Surface:   #101815 (Panel)
Text:      #F5F2EB (Paper)
Muted:     #7E8A82 (Fog)
Line:      #24312A
```

### 4.4 Pos — "Dark Product / Operator" (shares Formint palette)
```
Primary:   #EA580C (Copper)
Secondary: #FB923C (Orange)
Accent:    #F59E0B (Gold)
Background:#1A1917 (Ink)
```

---

## 5 · Implementation Priority

### P0 — Fix existing bugs
1. Fix `Logo.svg` in all 3 Formint variants to match new octagonal crest
2. Fix auth templates still referencing missing `images/logo.png`
3. Remove speculative files (structa-cloud-mark, precis-logo-lockup from thread)

### P1 — Core brand consistency
4. Update Formint `Logo.png.placeholder.svg` to show new crest (not "FORGE")
5. Update Precis favicon to match teal/amber palette (not blue tag)
6. Add `Logo.svg` to Loop CRM for Astro app header

### P2 — State coverage
7. Create login/auth variants for each project
8. Create loading/splash variants (Formint already has BrandLoader)
9. Create 404/error state variants (dimmed/desaturated marks)

### P3 — Polish
10. Create email-safe variants (static, no animation, on white)
11. Create PWA app tile variants
12. Create wordmark lockups for each project

---

## 6 · Logo Generation Specifications

### File format
- SVG for all vector logos (scalable, small file size)
- PNG fallback only where SVG is not supported (Tauri icons)

### Size targets
| Context | Target Size | Notes |
|---|---|---|
| Favicon | 32×32 viewBox | Simple mark only, no text |
| App header | 40-48px height | Mark + optional wordmark |
| Login screen | 120-160px width | Full mark with glow |
| Loading/splash | 80-120px width | Mark inside progress ring |
| Email | 200px width | Static, no animation |
| PWA tile | 512×512 | Mark centered, safe area |

### Animation rules
- **Favicon:** No animation (browser performance)
- **App header:** Optional subtle float/pulse
- **Loading:** Progress ring animation (already implemented in BrandLoader)
- **Login:** Evidence line draw-in (Precis) or ring draw-in (Formint/Loop)
- **Email:** No animation (email clients strip SVG animations)

### Accessibility
- All logo SVGs must include `aria-label` or `role="img"` with `aria-label`
- Loading states must include `role="status"` and `aria-live="polite"`
- Decorative logos must have `alt=""` and `aria-hidden="true"`
