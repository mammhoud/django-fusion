# Syntara changelog

All notable Syntara changes are recorded here.

## 2026-08-11 - Active project closeout

### Changed

- Confirmed `projects/syntara/` as the canonical home of the former Cypercloud
  AI chat/customizer runtime.
- Preserved the project-owned chat, template discovery, SSE, and AI provider
  boundaries while keeping shared framework behavior in django-fusion.
- Recorded the current deployment and documentation boundary without claiming
  unfinished provider, MCP, or UI roadmap work as complete.

### Verification

- Use `make check`, `make lint`, and `make test` from `projects/syntara/` for
  the project gate.
- Use the project Docker compose file for deployment checks; do not use the
  retired Cypercloud path as a new source location.

## 2026-07-30 - Cypercloud consolidation

- Continued the migration from the historical Cypercloud name to Syntara.
- Kept local AI/MCP integration stubs behind project-owned boundaries.
