# Formint POS — Mobile App Concept
## Art-Direction Spec (Design Bible)

> Generated with the `imagegen-frontend-mobile` art-direction discipline, grounded
> in the existing Formint brand (copper crest, Outfit type, warm neutrals). This
> document locks the design system so every screen in the concept belongs to one
> product world.

---

## 1. Platform Mode

**iOS-native premium.** Staff will run the app on iPhones at the counter and on
the floor. The concept biases toward:

- clean top areas with a large-type title
- a 4-slot bottom tab bar (Home · Order · Inventory · Reports)
- native-feeling sheets for checkout and payment
- safe-area awareness (status bar region, home indicator, docked sheets)
- restrained chrome — one strong structural move per screen, not nested card stacks

---

## 2. Palette Logic — "warm neutral + copper accent"

Controlled, single-accent, desaturated base. This is a POS: trust + calm + legible
numbers. One accent does all the work — the copper of the crest.

| Token            | Light                               | Dark (variant)                        |
|------------------|-------------------------------------|---------------------------------------|
| Surface          | `#FAF7F2` warm off-white            | `#171412` warm near-black            |
| Surface raised   | `#FFFFFF`                           | `#211D19`                            |
| Hairlines        | `#000000` @ 8%                      | `#FFFFFF` @ 10%                      |
| Text primary     | `#2A211B` warm charcoal             | `#F5EFE8`                            |
| Text secondary   | `#2A211B` @ 58%                     | `#F5EFE8` @ 60%                      |
| **Accent (only)**| `#EA580C` copper (→ `#FB923C` soft) | `#FB923C` copper-light               |
| On-accent        | `#FFFFFF`                           | `#1B0F07`                            |
| Success          | `#2E7D4F` (muted emerald)           | `#6FBF8F`                            |
| Danger           | `#C2402F` (muted brick)             | `#E2725F`                            |

Rules: no secondary accent competing with copper, no purple/blue gradients,
numbers always tabular. Soft surfaces are layered with a faint film-grain texture
(svg noise at ~3% opacity) so nothing reads sterile-flat.

## 3. Typography — Outfit (refined grotesk)

- **Display / big numbers:** Outfit 700, `tracking-tight`, tabular-nums for money.
- **Screen titles:** 26–28 px semibold.
- **Body / labels:** 14–15 px regular; secondary 12 px at 58% opacity.
- **Buttons:** 15 px semibold, one tap target ≥ 44 px.
- Scale rhythm: 40 (hero metric) → 26 (title) → 15 (body) → 12 (label). Never
  below 11 px.

## 4. Structure Bias

Tab-bar-led utility app. Composition logic per screen:

- **Home:** one hero metric ("Today" revenue), one active-orders list, two inline
  quick actions. Nothing else above the fold.
- **Order:** search + category chips + product cards (image-led, fixed 4:3 crops).
- **Checkout:** line-item list → payment sheet (Cash / Card / Mobile) → totals.
- **Inventory:** list-led with low-stock state chips.
- **Reports:** one revenue-by-payment bar block, not fake chart spam.

## 5. Signature Components (chosen 4)

1. **Hero metric card** — Home's "Today" revenue, copper number on raised surface.
2. **Framed product card stack** — Order menu grid, 4:3 image frames, add-on buttons.
3. **Bottom action sheet** — Payment method picker docking from the bottom.
4. **Progress ring block** — reused from the desktop branded loader as the
   checkout "processing payment" state.

## 6. Decorative Assets (chosen 2)

1. **Minimal line-icon cluster** — the crest rings + spark, reduced to a thin
   line motif behind the onboarding wordmark.
2. **Tiny directional arrow system** — chevrons that double as flow affordances
   on buttons and list rows.

## 7. Motion-Implied Language (chosen 2)

1. **Sheet rise energy** — payment sheet docks up with spring overshoot.
2. **Staggered list reveal** — menu/product rows fade up 12 px in sequence.

## 8. Texture / Surface Treatment

Ultra-subtle film grain over the base surface + a soft copper radial glow behind
the hero metric (like the crest's `feDropShadow`). No glassmorphism without purpose.

## 9. Flow (logical progression)

```
Welcome → Sign in → Home(Today)
                    ├── New Order → Menu → Cart → Payment → Receipt
                    ├── Inventory (tab)
                    └── Reports (tab)
```

Screen-by-screen:

1. **Welcome** — crest, "Formint", one line, one CTA. First screen stays calm.
2. **Sign in** — email + 6-digit PIN, Face ID hint, "shift handover" link.
3. **Home / Today** — hero revenue, active orders (staggered list), New Order + Reports quick actions.
4. **New Order — Menu** — search, category chips, image-led product grid.
5. **Cart / Checkout** — order lines with qty steppers, guest/table, totals.
6. **Payment** — sheet with Cash / Card / Mobile, progress ring while processing.
7. **Receipt** — success state, order summary, payment method shown.
8. **Inventory** — stock list, low-stock alerts (state chip logic reused).
9. **Reports** — revenue by payment method (Cash vs Card vs Mobile), clean bars.

## 10. Mockup Frame Discipline

Screens are presented inside a clean, even iPhone-style frame (2.6 mm border,
soft controlled shadow), consistent scale across the set, equal gutters, content
always primary. One dark-mode variant screen (Home) is shown at the end to
demonstrate the palette without breaking the set's coherence.
