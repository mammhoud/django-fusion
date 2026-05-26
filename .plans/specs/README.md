# Project Specifications

This directory contains all project specifications organized by status.

## Directory Structure

```
.kiro/specs/
├── README.md                    # This file - Master spec index
├── _templates/                  # Spec templates
├── _scripts/                    # Utility scripts
├── _reports/                    # Status reports
├── completed/                   # Fully completed specs
├── in-progress/                 # Partially complete specs
├── pending/                     # Not started specs
└── archive/                     # Obsolete/superseded specs
```

## Spec Categories

### Completed Specs (6)

Specifications that have been fully implemented and verified.

| Spec | Description | Status |
|------|-------------|--------|
| ctc-research-deployment-verification | Deployment verification for ctc-research.com | ✅ Complete |
| ecosystem-architectural-refactoring | Refactoring of ecosystem architecture | ✅ Complete |
| finalize-refactor | Final refactoring tasks | ✅ Complete |
| infrastructure-reorganization-cleanup | Infrastructure reorganization | ✅ Complete |
| package-enhancement-project-organization | Package enhancement and organization | ✅ Complete |
| phase-3-production-deployment | Phase 3 production deployment | ✅ Complete |

### In-Progress Specs (9)

Specifications currently being worked on.

| Spec | Description | Status |
|------|-------------|--------|
| core-logic-consolidation-and-app-restructure | Core logic consolidation | 🔄 In Progress |
| django-forge-relay-refactor | Django Forge relay refactor | 🔄 In Progress |
| django-project-reorganization-email-automation | Email automation reorganization | 🔄 In Progress |
| django-refactoring | Django refactoring | 🔄 In Progress |
| documentation-enhancement-and-spec-consolidation | Documentation enhancement | 🔄 In Progress |
| documentation-enhancement-unified-styling | Unified styling | 🔄 In Progress |
| email-sending-and-docker-enhancement | Email and Docker enhancement | 🔄 In Progress |
| package-reorganization-v2 | Package reorganization v2 | 🔄 In Progress |
| phase-2-website-sync-completion | Website sync completion | 🔄 In Progress |

### Pending Specs (12)

Specifications not yet started.

| Spec | Description | Status |
|------|-------------|--------|
| auth-allauth-enhancement | allauth enhancement | ⏳ Pending |
| blog-lms-wagtail-integration | Blog LMS Wagtail integration | ⏳ Pending |
| ctc-docs-and-core-containers | CTC docs and containers | ⏳ Pending |
| ctc-research-server-and-auth-fix | Server and auth fix | ⏳ Pending |
| ctc-structa-admin-auth-integration | Admin auth integration | ⏳ Pending |
| comprehensive-project-documentation | Comprehensive documentation | ⏳ Pending |
| docs-plugin-enhancement | Docs plugin enhancement | ⏳ Pending |
| fix-get-translation-template-tag | Translation template tag fix | ⏳ Pending |
| fix-wagtailsnippets-assets-email-enhancement | Snippets assets fix | ⏳ Pending |
| project-modernization | Project modernization | ⏳ Pending |
| spec-task-orchestrator | Spec task orchestrator | ⏳ Pending |
| structa-color-update | Structa color update | ⏳ Pending |

## Quick Links

- [Completed Specs](completed/)
- [In-Progress Specs](in-progress/)
- [Pending Specs](pending/)
- [Archive](archive/)
- [Templates](_templates/)
- [Scripts](_scripts/)
- [Reports](_reports/)

## Spec Structure

Each spec should contain:

- `requirements.md` - Functional and non-functional requirements
- `design.md` - Technical design and architecture
- `tasks.md` - Implementation tasks with status markers
- `.config.kiro` - Spec configuration (JSON)

## Support Files

### Templates

- `spec-directory-template/` - Standard spec template
- `documentation-templates/` - Documentation templates

### Scripts

- `organize_specs.py` - Organize specs into categories
- `update_all_reports.sh` - Update all status reports
- `verify_task_completion.py` - Verify task completion

### Reports

- `specs_status.json` - Machine-readable status
- `status_report.md` - Human-readable status
- `specs_pydoc.md` - Pydoc coverage report

---

**Last Updated**: 2026-04-19
**Total Specs**: 27
**Completed**: 6
**In Progress**: 9
**Pending**: 12
