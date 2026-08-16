# precis-ctc project

This directory is the standalone CTC Research medical research center — the public
`ctc-research.com` runtime. It owns its backend, Astro frontend, Compose stack, and
`db_ctc` database; it does not share runtime state with `projects/precis/precis-lms/`
(Precis/LMS) or `projects/precis/precis-landing/`.

The medical research catalog and Wagtail page tree are seeded from
`backend/assets/fixtures/dump-data.json` (the archived CTC Research website dump) and
`backend/apps/learning/fixtures/medical_research_catalog.json`.
