# Blinko Graph Enhancement Plan — Anytype-Aligned

> Status: G1+G2+G3 IMPLEMENTED (2026-09-17) — force layout, tooltips, drawer,
> lane filter rail, orphan toggle, timeline playback with speed control, and
> degree heatmap all live in `app.js`; server payload unchanged. Review record
> in §8. Decision answers in §6.
> Analyzes the supplied Anytype graph-engineering
> document against the **deployed runtime** (`application/tools/planing/runtime`)
> and phases only what fits its architecture: a dependency-free vanilla-JS
> shell, SVG graph, SurrealDB backend, 500-node server cap.

## 1. Where the graph stands today (audited)

| Aspect | Current implementation |
|---|---|
| API | `GET /api/graph` — nodes from notes (title, lane, color, updatedAt, in/out degrees), edges from the stored `note_link` table plus title-matched wiki links (resolved + unresolved), stats block, hard `LIMIT 500` |
| Layout | `graphLayout()` in `app.js` — a **static circular ring**, sorted by lane/title. No physics, no overlap avoidance, no zoom/pan |
| Rendering | Inline SVG; hover spotlight dims non-neighbors; click opens the note via search; keyboard focusable nodes |
| Interaction | No tooltips, no filtering, no orphan toggle, no timeline, no drag |
| Persistence | Edges are first-class rows (`note_link`), not client-computed — closer to Anytype than it looks |

## 2. Document concept → Blinko applicability matrix

| Anytype concept (from doc) | Verdict | Adaptation for the runtime |
|---|---|---|
| D3-force physics, prod params (charge −250, linkDistance 100, alphaDecay 0.05, alphaMin 0.01) | ✅ Adopt | Port params into a **~120-line inline force simulation** (repulsion, springs, centering) — no CDN/dependency, keeps the zero-build shell |
| Web Worker + PixiJS OffscreenCanvas | ⚠️ Adapt, don't copy | 500-node cap makes WebGL overkill. Run the sim in a **Blob-URL module worker** if tick cost shows; render with SVG or Canvas 2D |
| `GraphInspectionLayer` hover tooltip (title, type badge, timestamps, description snippet, spring entrance) | ✅ Adopt | HTML overlay positioned from SVG coords; data already in nodes (`updatedAt`, `laneName`); snippet from first content line |
| Click → side drawer with full metadata + "no metadata yet" fallback | ✅ Adopt | Reuse the new modal system: drawer shows lane, dates, degrees, tags, links, Open-note action |
| `graphDataAdapter` metadata auto-interrogation (`discoverMetadataKeys`) | ⚠️ Adapt | Blinko's equivalents are **lanes + tags**: generate the filter rail from `state.categories`/`state.tags` instead of scanning arbitrary keys |
| Orphan flagging → "Show Unlinked" toggle | ✅ Adopt | Nodes with `incoming + outgoing === 0`; the API already computes both degrees |
| `GraphTimeline` playback from created/updated dates | ✅ Adopt (phase 2) | Slider filters edges/nodes by `updatedAt <= t`; alpha-decay gives free fade-in |
| Cluster grouping heatmap | ✅ Adopt (phase 3) | Degree-weighted radial gradients under nodes; no interface changes needed server-side |
| In-viewport search + metadata filters (FilterState) | ✅ Adopt | Search box + lane/tag/degree toggles; dim non-matches via existing `.is-dim` mechanic |
| Reactive graph updates without viewport reset | ✅ Adopt | Re-render keeps a persistent node-position map keyed by id (pattern already proven by the engine code in the doc) |
| any-sync DAG/CRDT sync | ❌ Out of scope | Belongs to the SurrealDB migration plan's sync story, not the view layer |
| Prompt Reader pipeline ingestion | ⚠️ Equivalent exists | The notes/import/sample pipeline is the data source; the adapter pattern maps 1:1 onto `publicNote → node` which the API already performs |

## 3. Phased plan

### Phase G1 — Force-directed layout + inspection (core Anytype feel)
1. Replace `graphLayout` ring with an inline force simulation using the document's production parameters; deterministic seed so layouts are reproducible.
2. Run simulation in a Blob-URL worker; main thread receives `Float32Array` positions per tick and only re-patches `cx/cy` attributes (no innerHTML rebuilds).
3. Hover tooltip overlay: title, lane badge, updated date, degree; spring entrance per the InspectionLayer spec.
4. Click drawer: full record modal (reuse kanban/calendar modal components + i18n record keys).
5. Zoom/pan on the SVG viewport group; reset control; `prefers-reduced-motion` renders the settled layout with no animation.

### Phase G2 — Filters, orphans, search
6. "Show unlinked" toggle (orphan nodes).
7. Filter rail: lane chips, unresolved-edges toggle, min-degree slider — all dim non-matches, no re-layout.
8. Viewport search bound to existing note search state.

### Phase G3 — Timeline + density
9. Timeline playback slider over `updatedAt` with play/pause and speed (1×/2×/4×).
10. Degree heatmap underlay toggle (radial gradients, transparent → accent).

### Estimate
G1: 2–3 days · G2: 1 day · G3: 1–2 days. All server work is optional; the
existing `/api/graph` payload already carries everything phases G1–G2 need
(G3 needs no changes either — `updatedAt` is present).

## 4. Risks

- SVG re-patching on every tick can jank past ~300 nodes → mitigate with Canvas 2D renderer switch (same data contract) behind a settings toggle.
- Worker + CSP: Blob workers require no extra headers; if a stricter CSP lands later, fall back to main-thread sim with time-sliced ticks.
- Physics parameter feel: keep parameters configurable server-side later via the appearance settings (link to the appearance plan).

## 5. Decision points

1. Renderer end-state: SVG (simpler, crisper text) vs Canvas 2D (scales further)?
2. Should physics params (charge/distance) become user-facing appearance options, or stay tuned constants?
3. Timeline: is it worth promoting `created_at` into the graph payload now, or phase G3 uses `updatedAt` only?

## 6. Decision record (2026-09-17)

1. **SVG renderer stays** — crisp text and simpler code outweigh the >300-node scaling concern while the server caps at 500 nodes; revisit only if the cap rises.
2. **Physics params stay tuned constants** — not user-facing; G1 force layout, when implemented, keeps Anytype's production values internal.
3. **Timeline uses `updatedAt` only** — no server payload change needed; `created_at` promotion deferred with the rest of G3 server work.

## 7. Test coverage (2026-09-17)

Graph playback + orphan toggle are locked in by
`runtime/tests/appearance-and-graph.spec.mjs`, which runs on the dedicated Playwright
config `runtime/playwright.extra.config.mjs` (the file was renamed from
`playwright.appearance.config.mjs` when `tickets.spec.mjs` moved onto the same
isolated server) — isolated server + SurrealDB engine per run, and its own
bootstrap admin pinned in a run-keyed temp file so the tickets suite can share it.
It asserts layout sanity after the force simulation, hover tooltip, click drawer,
playhead scrubbing/playback (via `expect.poll`, no fixed sleeps), and orphan
hiding after creating an unlinked note. Run everything with `npm test` in
`runtime/` (main suite + extra suite): **39/39 green** — 32 on the main config
(`auth-and-categories` 29 + `i18n-parity` 3) and 7 on the extra config
(appearance/graph 2 + tickets 5).

## 8. Implementation review (2026-09-17, re-verified)

<!-- AI-generated: review needed -->
Verified line-by-line against the deployed runtime
(`application/tools/planing/runtime`, container `planing`, rebuilt no-cache and
healthy after this pass). The re-check corrected two entries: one shipped item
was missing from the table (zoom/pan/reset, G1.5) and one planned item was
over-credited (the G2 filter rail was recorded as if it covered the whole item).

| Planned | Shipped | Where |
|---|---|---|
| G1.1 inline force sim (Anytype params) | ✅ `graphSim` + `graphSimStep` — repulsion, springs, **collision**, centering, alpha decay, 300-tick cap; settled positions persist across re-renders via a position map | `app.js` L2111 config, L2239–2282 step |
| G1.2 Blob-URL worker | ✅ `graphWorkerSource()` → `Blob` → `new Worker(URL.createObjectURL(...))` with an `onerror` fallback to the main-thread sim; ticks only re-patch `cx/cy`, no innerHTML rebuild | `app.js` L2117–2206, `patchGraphPositions` |
| G1.3 hover tooltip | ✅ `#graph-tooltip` with lane color dot, title, updated date, degree; timed show/hide class | `app.js` L2383–2402 |
| G1.4 click drawer | ✅ `#graph-drawer` with lane, links/backlinks sections, open action, unresolved-edge chips | `app.js` L2407+ |
| G1.5 zoom/pan + reset + reduced motion | ✅ `graphViewport` (k/x/y) transform on the viewport group, pointer pan/zoom, `⟲ 1:1` reset chip; `prefers-reduced-motion` settles instantly in a bounded loop | `app.js` L2497–2502, 2620–2645; `index.html` L309 |
| G2.6 orphan toggle | ✅ `#graph-orphans` chip-toggle, `state.graphHideOrphans`, filters the node set before layout | `app.js` L2369, 2568–2571 |
| G2.7 filter rail — lane chips | ✅ `#graph-filter` lane chips with dim/active states (`state.graphLaneFilter`), colored swatch per lane | `app.js` L2567–2576 |
| G2.7 filter rail — unresolved-edges toggle | ❌ Not shipped. Unresolved edges are *rendered* (dashed `is-unresolved` class, counted in the stats row) but cannot be filtered out | `app.js` L2542, L2552 |
| G2.7 filter rail — min-degree slider | ❌ Not shipped — no degree control exists | — |
| G2.8 viewport search | ❌ Not shipped as a dedicated input; note search state is the only search path | — |
| G3.9 timeline playback | ✅ `state.graphTimeline` (enabled/current/speed/playing) over **`updatedAt`**; scrub + play/pause, 1×/2×/4× speed chips (`data-speed`, `graphTimelineTick` at time-based steps) | `app.js` L2372–2424, L2395; `index.html` L298–305 |
| G3.10 degree heatmap | ✅ `#graph-heat` toggle, degree-weighted radial `<circle class="graph-heat">` underlay beneath the edges, weight capped at 8 | `app.js` L2529–2535, 2569–2572 |

**Bug found by this re-check and fixed:** `collide: 16` was honoured only by the
worker simulation — the main-thread `graphSimStep` (used by the fallback *and*
by the reduced-motion instant settle) had no collision pass, so two nodes could
reach equilibrium 4.5px apart and stay overlapped. The same separation pass now
runs on both paths. The Playwright layout assertion had been measuring during
settle as well; it now polls the node separation instead of reading it once.

**Remaining gaps (honest list):** unresolved-edges toggle, min-degree slider,
and a dedicated viewport search control are the only unshipped planned controls.
Renderer stayed SVG per decision §6.1; physics params remain internal constants
per §6.2; the timeline reads `updatedAt` only per §6.3. Regressions are locked by
`tests/appearance-and-graph.spec.mjs` (layout sanity, tooltip, drawer, playback
via `expect.poll`, orphan hiding) — **39/39 tests green** across both suites
(verified over consecutive full runs).

## Remarks & Notes
- The 500-node server cap is what makes the O(n²) repulsion acceptable; raise the cap only together with the Canvas 2D renderer decision (§6.1).
- The force simulation exists twice — once as a string built by `graphWorkerSource()` and once as the main-thread `graphSimStep` — and they had already drifted: the worker resolved collisions, the main thread did not. Any physics change has to be applied to both, or the fallback path (and reduced motion) silently renders a different layout than the animated one. The shared `graphForceConfig` object is the only thing keeping the parameters in sync.
- The default physical layout can legitimately place two *linked* nodes closer than the collision radius mid-settle; layout assertions must poll for separation rather than sample one frame, which is how the missing collision pass was finally exposed.
- Timeline playback steps are time-based (`speed` × range/220ms), not frame-based — behavior is CPU-speed independent but ~2–4s per sweep at 1×.
- Hover re-scaling re-patches node radii; Playwright showed click-interception flakes when clicking during a hover transition — tests clear hover before clicking.
