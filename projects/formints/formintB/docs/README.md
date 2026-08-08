# Design References — Tactical Telemetry concept boards

Static concept boards for the POS Cloud **Tactical Telemetry** design system
(the `industrial-brutalist-ui` bible: CRT substrate `#0A0A0A`, phosphor
`#EAEAEA`, hazard red `#E61919` as the only accent, exactly one
terminal-green `#4AF626` element per surface, zero border-radius,
monospace telemetry, scanline + grain texture).

They are **self-contained HTML** — no build step, no server, no
dependencies. Open them in any browser.

## How to open

From the `formintB/` project root:

```bash
open docs/mobile_ops_preview.html      # macOS
xdg-open docs/mobile_ops_preview.html  # Linux
start docs\mobile_ops_preview.html     # Windows
```

Or just double-click the files in your file manager. Each board links to
the other via its header `COMPANION SET` link, so you can flip between
the mobile and desktop presentations.

## The boards

| Board | File | Contents |
|-------|------|----------|
| Mobile ops companion | [`mobile_ops_preview.html`](mobile_ops_preview.html) | **6-screen iPhone concept set** (330px mockups with dynamic island, status bar, home indicator): 01 unit registration (`TKN-7F2A-91C4`), 02 branch overview roster (ONLINE / DEGRADED / OFFLINE), 03 sync queue, 04 conflict resolution (`CNF-117` USE REMOTE sheet), 05 WS link-lost error state (hazard `LOST` banner + retry), 06 first-run empty queue (`CHANNEL READY` + START INITIAL SYNC) |
| Desktop sync monitor | [`desktop_monitor_preview.html`](desktop_monitor_preview.html) | **1440 × 900 editorial board**: the brutalist telemetry dashboard in a desktop browser frame (tabs, URL bar, `LIVE / 10S` badge), the `SYNC MONITOR` dashboard mirroring `backend/configs/urls.py` token-for-token, a `[ SPEC SHEET ]` rail with the full token list, and 5 numbered design-bible annotation cards |

Rendered previews live in [`images/`](images/)
(`mobile-ops-preview.png`, `desktop-monitor-preview.png`) — regenerate them
with `node scripts/dev/screenshot-boards.mjs` from the `formintB/` root. The
script captures at 2× DPR, then post-processes with the backend venv's Pillow
(downscale to 1280px wide, 256-color palette) to keep the committed PNGs lean.

## Relationship to the shipped admin

These boards are *concept art*, not the live UI. The design language they
illustrate is implemented in the real admin via the shared SCSS token layer
(`backend/apps/core/static/tactical/scss/`, compiled to
`tactical.css` and wired through `UNFOLD["STYLES"]`) — see the main
[`README.md`](../README.md), section *Admin design system — Tactical
Telemetry*. Regenerate the boards if the design system drifts.
