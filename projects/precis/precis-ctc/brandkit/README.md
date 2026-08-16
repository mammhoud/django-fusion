# Precis · Research LMS — Brand Kit

Premium brand-identity deck for Precis (research LMS for medical researchers, biostatisticians, and regulatory staff), built with the **brandkit** art-direction method.

## What's inside

| File | Content |
|------|---------|
| `index.html` | Self-contained 2×3 identity board + full written spec (strategy, mark rationale, palette, typography, voice, do/don't) |

The board is **zero-dependency**: inline SVG logo system, CSS-only presentation, Google Fonts (Fraunces / Inter / IBM Plex Mono). No build step required.

## View it

```bash
# open directly
xdg-open projects/precis/precis-lms/brandkit/index.html

# or serve locally
cd projects/precis/precis-lms && python3 -m http.server 8098 --directory brandkit
# → http://127.0.0.1:8098/
```

## The system at a glance

- **Core metaphor** — the clinical protocol: every course is a protocol, every lesson a controlled step, every certificate an audited result.
- **Logo — "The Protocol Mark"** — open-bowl geometric `P` on an 8u grid; negative-space **crosshair** (precision) + amber **evidence line** with arrowhead (systematic reduction to conclusion).
- **Palette** — clinical ink `#0C1210`, warm paper `#F5F2EB`, clinical teal `#1F8A70` (learning), evidence amber `#C9962E` (certification/conclusions), fog `#7E8A82`.
- **Type** — Fraunces (display/editorial), Inter (UI), IBM Plex Mono (protocol data + system voice).
- **Tagline** — "Evidence you can build on." / Campaign: "Build evidence that matters."
