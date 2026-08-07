# LMS Fusion backend

This Django/Wagtail backend is the surviving CMS + LMS backend for the
`lms-fusion` site. The Astro frontend in `../frontend` consumes the additive
landing contract under `/apis/` and `/fragment/` while the existing LMS
`/api/` routes and Wagtail page models remain authoritative.

## Migration safety

The consolidation intentionally does **not** copy `cms-fusion` initial
migrations or rename the existing `lms-fusion` apps. The LMS migration graph
already contains the equivalent Wagtail/content models, so preserving its
history avoids duplicate tables and destructive data changes.

Before applying migrations to an existing database, run:

```bash
cd projects
uv run python lms-fusion/manage.py showmigrations --plan
uv run python lms-fusion/manage.py check
```

The development SQLite database currently has a pre-existing inconsistent
history: `accounts.0001_initial` is recorded as applied before its declared
`wagtailcore.0097_baselogentry_uuid_action_timestamp_indexes` dependency.
Do not use `--fake`, delete the database, or reset migration records blindly.
Back up the database, verify the actual Wagtail schema against migration 0097,
and perform a database-specific repair only after that review. Production
migration startup should remain blocked until the database owner completes
that repair.
