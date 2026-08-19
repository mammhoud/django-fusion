# CTC Research — Enhancement Register

> **Status:** Active publish checklist
> **Canonical project:** `projects/precis/precis-ctc/`
> **Related plan:** [`../../../docs/plans/repository/ctc-research-publish-2026-08-18.md`](../../../docs/plans/repository/ctc-research-publish-2026-08-18.md)

<!-- AI-generated: review needed -->

## 1. Completed in this publish pass

### Medical-first presentation

- Replaced the Hero “View Source” panel with a medical evidence/media gallery.
- Replaced the product detail “Models & snippets” code section with the same gallery pattern.
- Added `MediaGallery.astro` with responsive cards, captions, source labels, and a native lightbox.
- Removed the unused public `CodeBlock.astro` component.
- Removed inline code styling from render-mode and fragment fallback notes.
- Kept developer/admin/example templates separate from public medical content.

### Runtime interpolation and interaction fixes

- Fixed Alpine data interpolation in `BackToTop.astro`, `Modal.astro`, and `ShareButtons.astro`.
- Fixed `ContactForm.astro` so the backend endpoint is injected into the Alpine state instead of being emitted literally as `{contactEndpoint}`.
- Added the `Window.__FUSION_AUTH` type declaration used by `LoginModal.astro`.
- Frontend check is currently clean: 0 errors, 0 warnings, 0 hints.

### Shared assets and proxy mapping

- Runtime CTC media is now under `projects/assets/media/ctc-research/`.
- Webpack output is configured for `projects/assets/bundles/ctc-research/`.
- Django settings register the shared media and bundle paths.
- CTC Compose binds shared media into `/app/media`; the shared proxy mounts the same tree read-only.
- The restored archive is described by `backend/assets/fixtures/ctc-research-media.json`; `prepare_ctc_media` creates a normalized `ctc-content/` website copy and dump-compatible `original_images/` aliases without loading database data.
- The additive `/apis/content/media/` contract feeds archive imagery to the home/About fallback gallery while preserving Wagtail gallery precedence.
- Nginx and Traefik use the public identity `ctc-research` for `/media/`, `/static/bundles/`, and site static routes.
- Compose config validation and the asset-pipeline verification script pass.

### Redeploy workflow

- `cd projects/precis/precis-ctc && make redeploy` checks backend/frontend, builds backend/worker/frontend images, and recreates backend, worker, scheduler, and frontend.
- `cd projects && make redeploy-with-stack WEBSITE=precis-ctc` delegates to the full CTC stack target.
- Existing `make redeploy WEBSITE=precis-ctc` remains the dispatcher’s web-service deployment path; use `redeploy-with-stack` for all attached containers.

### Locales

- Added target data modules for Spanish, Swedish, and Brazilian Portuguese.
- The generator now preserves multiline and plural PO entries, applies exact and recurring-pattern translations, and compiles `.mo` files without requiring a system `msgfmt` binary.
- Generated catalogs contain the complete 3,438-entry reference set; the generator reports 1,958–2,239 English fallbacks per locale for qualified linguistic review.

## 2. P0 publish blockers

| Item | Verification | Owner |
|---|---|---|
| Production media is present and licensed | Review `projects/assets/media/ctc-research/`; confirm source, consent, and usage rights | CTC content owner |
| Course catalog is complete | Review the seeded medical rich-text descriptions, 12 modules, 24 lessons, outcomes, and disclaimers; localized UI catalogs are separate from course-copy translation | LMS/content owner |
| Runtime environment is populated | Set database, Redis, host, email, and domain variables in deployment secret store | Operations |
| SMTP delivery works | Use the approved test procedure; never commit credentials or send unsolicited mail | Operations |
| Legal and medical copy review | Privacy, consent, research claims, and educational disclaimers | Legal/clinical reviewer |
| Proxy volume permissions | Confirm shared-proxy can read media and collected static files after deployment | Operations |

## 3. P1 content enhancements

1. Add publication cards with DOI/PMID, abstract, authors, journal, date, and review status.
2. Add project pages with research question, protocol stage, cohort description, outcome measures, and linked evidence.
3. Add investigator profiles with affiliation, expertise, ORCID, publications, and contact policy.
4. Add event registration state, timezone, speaker bios, agenda, recording, and abstract links.
5. Review and promote the seeded course modules and lessons as editor-managed content instead of flat course cards.
6. Add captions and alt text for every gallery item; include “illustrative” labels where a visual is not study data.
7. Add locale-aware metadata, canonical URLs, `hreflang`, OpenGraph images, and structured data for articles/events/courses.
8. Add review workflows for scientific copy, translation, legal copy, and image rights.

## 4. P2 product and platform enhancements

- Add a research publication search/filter road with server-side pagination.
- Add evidence-type facets: trial, cohort, systematic review, protocol, dataset, educational resource.
- Add accessible chart components for aggregate metrics; never expose identifiable patient data.
- Add audit events for content publication, translation review, image replacement, and course release.
- Add screenshot/browser smoke coverage for locale switching, gallery lightbox, course enrollment, and contact submission.
- Add Nx targets only if the repository’s root Nx installation is made authoritative; do not create a second package-manager workflow.

## Remarks & Notes

- “No code blocks” applies to public HTML components for the CTC medical experience. Developer documentation and admin diagnostics may still use code blocks.
- Do not treat generated locale coverage as human editorial approval. The generator intentionally reports English fallbacks.
- Any content involving patients, clinical claims, identifiable images, or trial outcomes requires explicit review before publication.
