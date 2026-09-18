# CTC Research — Archive Media Pack

> **Canonical project:** `projects/precis/precis-ctc/`
> **Public site:** `ctc-research.com`
> **Shared runtime root:** `projects/assets/media/ctc-research/`

<!-- AI-generated: review needed -->

## Purpose

The CTC Research backup media is retained in the shared, project-named media
root and exposed through a small content manifest. This keeps the archive usable
by the Precis CTC website without duplicating binaries into the frontend or
loading the historical database dump automatically.

The source-controlled metadata is:

- `backend/assets/fixtures/ctc-research-media.json` — labels, captions, source
  names, enhanced logo paths, and dump-data aliases.
- `backend/apps/core/management/commands/prepare_ctc_media.py` — non-destructive
  file preparation command.
- `projects/assets/media/ctc-research/media/` — restored archive source files
  supplied with the workspace.
- `projects/assets/media/ctc-research/original_images/` — Wagtail-compatible
  image path expected by the curated dump.
- `projects/assets/media/ctc-research/ctc-content/` — clean website copy made
  by the preparation command.

## Media contract

The CTC settings preserve the existing shared-media topology:

```text
MEDIA_ROOT = /app/media                  # container
MEDIA_URL  = /media/
archive    = /app/media/media/            # restored backup source
website    = /app/media/ctc-content/      # prepared web-safe copy
Wagtail    = /app/media/original_images/  # dump-compatible image aliases
```

The host-side tree is mounted into the CTC backend, worker, and scheduler by
`docker-compose.yml`, while the shared proxy reads the same project-named tree.
The public API is:

```text
GET /apis/content/media/
```

It prefers `/media/ctc-content/<slug>.<ext>` after preparation and temporarily
falls back to `/media/media/<original filename>` when only the restored archive
is present. Missing files are omitted, so a clean checkout returns an empty
available set rather than broken image URLs.

The frontend consumes the endpoint on the home and About pages. Wagtail gallery
content remains authoritative; the archive pack is a safe fallback for the
hero/gallery surfaces when the localized gallery block has no usable media.

## Prepare the copy

Run this against a local or explicitly approved staging CTC environment. It
only copies media files and writes a runtime manifest; it does not migrate,
replace, or load database data.

```bash
cd projects/precis/precis-ctc/backend
python manage.py prepare_ctc_media --dry-run
python manage.py prepare_ctc_media
```

The command:

1. Reads supported image and video files from `MEDIA_ROOT/media/`.
2. Excludes `appmap.log` and unsupported office files such as `img-05.pptx`.
3. Writes normalized website filenames to `MEDIA_ROOT/ctc-content/`.
4. Creates aliases under `MEDIA_ROOT/original_images/` for the image names
   referenced by `backend/assets/fixtures/dump-data.json`.
5. Writes `ctc-content/manifest.json`.
6. Leaves the original archive files untouched.

Use `--overwrite` only when an approved media refresh should replace an existing
prepared copy. The existing `load_data` command remains separate; do not use
`load_data --replace` against a shared database without an approved backup and
change window.

## Dump compatibility

The historical dump uses Wagtail paths such as
`original_images/Laurens_van_Kleef.jpeg`, while the restored archive contains
`Laurens van Kleef.jpeg`. The manifest records these aliases and the preparation
command creates them without altering `dump-data.json`. The same mapping is
used for investigator names containing punctuation/spaces and for the duplicate
`img-30_DIg7fju.jpeg` reference.

The dump includes several historical files that are not in the attached media
folder (`0823-DashboardDesign-Dan-Social_Jac1k9K.png`, a generic favicon,
`happy-graduates...png`, and `unnamed.jpeg`). They are reported by the command
as missing and are not invented. Restore them separately if the corresponding
Wagtail records must render their original imagery.

## Enhanced brand treatment

The existing additive CTC variants remain in the site static source and are
listed by the media manifest:

- `assets/static/images/logo-enhanced.svg` — primary CTC Research wordmark.
- `assets/static/images/favicon-enhanced.svg` — compact browser/app mark.
- `assets/static/images/brand/lms-ribbon-enhanced.svg` — learning pathway mark.
- `assets/static/images/brand/crm-isometric-enhanced.svg` — evidence/workflow mark.

The visual direction is a restrained research-instrument system: carbon/navy
ink, clinical blue, signal yellow, and a small evidence-red accent. Use the
wordmark for institutional surfaces, the favicon for small surfaces, and the
learning/evidence marks only as supporting program identifiers. Do not apply
logos to patient imagery or imply endorsement by an archive partner.

## Content and rights review

The manifest provides descriptive working copy, not scientific validation. A
CTC content owner must review before publication:

- identity, affiliation, and spelling for every investigator portrait;
- image rights, consent, licensing, and partner-logo usage;
- whether a visual is illustrative, educational, or actual study material;
- captions, alt text, dates, and research claims;
- video hosting rights and whether the `.mp4` files should be public;
- translations and medical/legal disclaimers.

Until that review is complete, treat the prepared copy as staging content.

## Remarks & Notes

- The archive is deliberately kept under the same `ctc-research` media identity used by Traefik/Nginx; no second website media root is introduced.
- `prepare_ctc_media` is idempotent by default: existing destination files are preserved unless `--overwrite` is supplied.
- The endpoint is fail-soft and does not make the site depend on a restored backup being present during frontend builds.
- The enhanced SVGs are additive variants; original logos and fixture records remain unchanged.
