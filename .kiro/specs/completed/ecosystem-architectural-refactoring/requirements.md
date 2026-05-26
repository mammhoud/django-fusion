# Requirements Document: Ecosystem-Wide Architectural Refactoring

## Introduction

This specification defines a comprehensive ecosystem-wide architectural refactoring to establish a clean, modular, domain-driven architecture with strict package boundaries, zero duplication, and maximum reusability. The refactoring consolidates the entire codebase across multiple Django projects (ctc-research.com, structa.cloud) and shared packages (django_osoul, django_rseal, django_grep, nawaai) into a unified, scalable architecture.

The refactoring builds upon completed work (finalize-refactor, phase-3-production-deployment, ctc-research-deployment-verification, django-refactoring specs) and the in-progress core-logic-consolidation spec, ensuring all previous improvements are preserved while eliminating remaining duplication and architectural inconsistencies.

---

## Glossary

- **Ecosystem**: The complete codebase including all projects (ctc-research.com, structa.cloud) and shared packages (django_osoul, django_rseal, django_grep, nawaai)
- **Package**: A reusable Python library in venv/libs/ (django_osoul, django_rseal, django_grep, nawaai)
- **Project**: A Django website application (ctc-research.com, structa.cloud)
- **Domain**: A cohesive area of business logic with clear boundaries (accounts, content, LMS/alliance, messaging, cart, forms)
- **Boundary**: A strict separation rule preventing imports between specific packages or layers
- **Duplication**: Identical or highly similar code (≥70% similarity) existing in multiple locations
- **Thin Layer**: A minimal project-level implementation that delegates to shared packages
- **Source of Truth**: The canonical location where logic is defined and maintained
- **Dependency Direction**: The allowed flow of imports between packages (stdlib → nawaai → django_osoul → django_rseal → projects)
- **Spec**: A feature specification document in .kiro/specs/ with requirements, design, and tasks
- **Task**: An actionable work item in a spec's tasks.md file
- **Recovery**: The process of restoring deleted or moved code from git history or backups
- **Rollback**: Reverting incorrect changes to restore a previous working state
- **Fixture**: Test data or database seed data in JSON format
- **Migration**: A Django database schema change tracked in migrations/ directories
- **Template**: A Django/Wagtail HTML template file (must stay in projects, not packages)
- **AST**: Abstract Syntax Tree — a tree representation of source code structure used for static analysis and semantic comparison
- **import-linter**: A Python tool that enforces import contracts between modules, used to prevent boundary violations in CI
- **ContentType**: A Django framework model that tracks installed models by app label and model name; must be updated during app renames
- **PascalCase**: A naming convention where each word starts with a capital letter (e.g., MyClassName)
- **snake_case**: A naming convention where words are separated by underscores and all letters are lowercase (e.g., my_function_name)
- **EARS**: Easy Approach to Requirements Syntax — a structured language for writing requirements using patterns such as WHEN/THE/SHALL (event-driven), THE/SHALL (ubiquitous), and THE/MAY (optional feature)
- **INCOSE**: International Council on Systems Engineering — defines quality rules for requirements including clarity, testability, completeness, and use of positive statements
- **CI**: Continuous Integration — automated process that runs tests and validation checks on every code commit
- **Docker**: A containerisation platform used to build and run the projects in isolated environments
- **uv**: A fast Python package manager used to manage dependencies and lock files across the ecosystem
- **Wagtail**: A Django-based content management system used in both projects for page and content management
- **Celery**: An asynchronous task queue used for background job processing
- **factory_boy**: A Python library for creating test fixtures using factory classes
- **Hypothesis**: A property-based testing library for Python that generates test inputs automatically
- **Unfold**: A Django admin theme library used for admin interface customisation

---

## Requirements

### Requirement 1: Codebase Analysis and Duplication Detection

**User Story:** As a developer, I want a complete inventory of all duplicated logic across the ecosystem, so that I can systematically eliminate redundancy.

#### Acceptance Criteria

1. THE Analysis_System SHALL scan all Python modules in ctc-research.com/apps/, structa.cloud/apps/, and venv/libs/ packages
2. WHEN two modules have ≥70% code similarity, THE Analysis_System SHALL classify them as duplicated
3. FOR ALL duplicated code, THE Analysis_System SHALL record the current location in both projects and the target package location
4. THE Analysis_System SHALL categorize each duplication as extract-to-osoul, extract-to-rseal, extract-to-grep, already-extracted, or project-specific
5. THE Analysis_System SHALL detect tight coupling violations (imports that cross boundary rules)
6. THE Analysis_System SHALL identify misplaced responsibilities (logic in wrong package or layer)
7. THE Duplication_Report SHALL list every duplicated class, function, and module with source locations and similarity percentage
8. THE Duplication_Report SHALL include cross-references to existing specs that may have already addressed the duplication

---

### Requirement 2: Domain-Driven Module Restructuring

**User Story:** As a developer, I want all code organized by domain with clear responsibilities, so that the architecture is intuitive and maintainable.

#### Acceptance Criteria

1. THE Restructure_System SHALL group all business logic by domain (accounts, content, LMS/alliance, messaging, cart, forms)
2. WHEN a module contains logic for multiple domains, THE Restructure_System SHALL split it into domain-specific modules
3. THE Restructure_System SHALL ensure each module has a single, well-defined responsibility
4. THE Restructure_System SHALL eliminate cross-domain leakage (domain A importing from domain B's internals)
5. THE Restructure_System SHALL detect and eliminate circular dependencies between modules
6. FOR ALL modules, THE Restructure_System SHALL enforce standard sub-module layout (admin/, filters/, forms/, managers/, middleware/, models/, services/, views/)
7. THE Restructure_System SHALL ensure all domain logic follows the same organisational pattern across both projects

---

### Requirement 3: Package Consolidation and Boundary Enforcement

**User Story:** As a developer, I want all shared logic in the correct package with strict boundaries, so that dependencies are clear and violations are prevented.

#### Acceptance Criteria

1. THE Package_System SHALL move all foundation logic (models, mixins, utils, contrib) to django_osoul, ensuring zero Wagtail dependencies
2. THE Package_System SHALL move all automation logic (pipelines, services, workflows, email, signals, admin, cache, commands) to django_rseal
3. THE Package_System SHALL move all Wagtail-related components (blocks, snippets, hooks, Wagtail models) to django_rseal
4. THE Package_System SHALL move all testing infrastructure (seeder, test base, fixtures, factories, assertions, pytest plugin) to django_grep
5. THE Package_System SHALL ensure nawaai contains only pure Python AI logic with zero Django imports
6. THE Boundary_Enforcer SHALL prevent django_osoul from importing wagtail, celery, or django_rseal
7. THE Boundary_Enforcer SHALL prevent django_rseal from importing project-specific code
8. THE Boundary_Enforcer SHALL prevent nawaai from importing any Django modules
9. THE Boundary_Enforcer SHALL enforce dependency direction: stdlib → nawaai → django_osoul → django_rseal → projects
10. WHEN a boundary violation is detected, THE Boundary_Enforcer SHALL fail CI with a descriptive error message
11. THE Package_System SHALL update all imports to new locations and delete original files after verification

---

### Requirement 4: Project Simplification and Thin Layer Pattern

**User Story:** As a developer, I want projects to be thin layers that use packages, so that business logic is reusable and not duplicated.

#### Acceptance Criteria

1. THE Project_System SHALL convert all projects to thin layers that delegate to shared packages
2. THE Project_System SHALL remove all duplicated business logic from project-level code
3. WHEN a project needs domain-specific behaviour, THE Project_System SHALL implement it as a minimal subclass or configuration
4. THE Project_System SHALL ensure projects contain only: settings, URLs, project-specific models, templates, static files, and thin service subclasses
5. THE Project_System SHALL move all reusable managers, mixins, forms, filters, and middleware to django_osoul or django_rseal
6. THE Project_System SHALL ensure both projects follow identical structural patterns
7. THE Project_System SHALL document the canonical import path for every shared class in module-level docstrings

---

### Requirement 5: Cross-Project Consistency and Naming Unification

**User Story:** As a developer, I want consistent structure and naming across all projects, so that navigation and maintenance are predictable.

#### Acceptance Criteria

1. THE Consistency_System SHALL enforce identical app structure in both projects (accounts/, content/, lms/alliance/)
2. THE Consistency_System SHALL enforce snake_case naming for all Python modules, functions, and variables
3. THE Consistency_System SHALL enforce PascalCase naming for all classes
4. THE Consistency_System SHALL ensure both projects use the same patterns for services, handlers, managers, and views
5. THE Consistency_System SHALL unify settings structure across both projects (same base settings, same overrides pattern)
6. THE Consistency_System SHALL ensure both projects use the same middleware stack order
7. THE Consistency_System SHALL ensure both projects use the same URL routing patterns
8. THE Consistency_System SHALL maintain separate CHANGELOG.md files for each project and package

---

### Requirement 6: Testing Standardisation with django_grep

**User Story:** As a developer, I want all tests to use django_grep as the unified testing framework, so that test infrastructure is consistent and reusable.

#### Acceptance Criteria

1. THE Test_System SHALL use django_grep as the single source of truth for all test infrastructure
2. THE Test_System SHALL provide unified base test classes in django_grep.tests.base
3. THE Test_System SHALL provide unified factories in django_grep.tests.factories
4. THE Test_System SHALL provide unified fixtures in django_grep.tests.fixtures
5. THE Test_System SHALL provide unified assertions in django_grep.tests.assertions
6. THE Test_System SHALL provide unified mixins in django_grep.tests.mixins
7. THE Test_System SHALL provide Hypothesis strategy helpers (st_email, st_slug, st_uuid) in django_grep.tests.base
8. THE Test_System SHALL register the pytest plugin via django_grep.tests.pytest_plugin
9. WHEN shared package logic is tested, THE Test_System SHALL place tests in the package's tests/ directory
10. WHEN project-specific integration is tested, THE Test_System SHALL place tests in the project's tests/ directory
11. THE Test_System SHALL ensure all tests pass after migration to django_grep infrastructure
12. THE Test_System SHALL remove duplicate or obsolete test files after migration
13. THE Test_System SHALL provide unified health check endpoints in django_grep.health
14. THE Test_System SHALL provide health check views for: basic health, database, static assets, and media files
15. THE Test_System SHALL provide health check URLs that projects include via django_grep.health.urls
16. WHEN a health check target is healthy, THE Test_System SHALL return HTTP 200; WHEN a health check target is unhealthy, THE Test_System SHALL return HTTP 503

---

### Requirement 7: Documentation Organisation and Spec Completion

**User Story:** As a developer, I want all documentation and specs organised and complete, so that the system is fully documented and all planned work is finished.

#### Acceptance Criteria

1. THE Documentation_System SHALL organise all specs in .kiro/specs/ with clear status (completed, in-progress, not-started)
2. THE Documentation_System SHALL ensure every spec has requirements.md, design.md, and tasks.md files
3. THE Documentation_System SHALL verify all completed specs have all tasks marked as done
4. THE Documentation_System SHALL identify incomplete tasks from all specs
5. THE Documentation_System SHALL create a master task list for all incomplete work
6. THE Documentation_System SHALL ensure all package README.md files document public APIs with usage examples
7. THE Documentation_System SHALL create ARCHITECTURE.md documenting the dependency graph and package responsibilities
8. THE Documentation_System SHALL create MIGRATION_GUIDE.md documenting all changed import paths
9. THE Documentation_System SHALL ensure all docstrings reference the canonical import path for shared classes
10. THE Documentation_System SHALL maintain a docs/ directory with architecture diagrams and design decisions

---

### Requirement 8: Code Recovery and Restoration

**User Story:** As a developer, I want all deleted or moved code recovered and reintegrated, so that no functionality is lost.

#### Acceptance Criteria

1. THE Recovery_System SHALL scan git history for deleted files in the last 6 months
2. THE Recovery_System SHALL identify deleted code that is still referenced in the current codebase
3. THE Recovery_System SHALL restore deleted code from git history or backup sources
4. THE Recovery_System SHALL reintegrate restored code into the new architecture
5. THE Recovery_System SHALL verify restored code has test coverage
6. THE Recovery_System SHALL document all recovered code in a RECOVERY_REPORT.md file
7. WHEN code cannot be recovered, THE Recovery_System SHALL document the missing functionality and create tasks to reimplement it

---

### Requirement 9: Task Reprocessing and Rollback Management

**User Story:** As a developer, I want all incomplete tasks identified and executed, and incorrect changes rolled back, so that the system reaches a complete and correct state.

#### Acceptance Criteria

1. THE Task_System SHALL scan all specs for incomplete tasks (marked as [ ] or [-])
2. THE Task_System SHALL create a prioritised execution plan for all incomplete tasks
3. THE Task_System SHALL execute incomplete tasks in dependency order
4. THE Task_System SHALL verify each task's acceptance criteria after execution
5. WHEN a task execution introduces errors, THE Task_System SHALL roll back the changes
6. THE Task_System SHALL document all rollbacks in a ROLLBACK_LOG.md file
7. THE Task_System SHALL re-execute rolled-back tasks with a corrected approach
8. THE Task_System SHALL ensure all tasks are marked complete before finishing

---

### Requirement 10: Dependency Alignment and Version Unification

**User Story:** As a developer, I want unified dependencies across all projects and packages, so that version conflicts are eliminated.

#### Acceptance Criteria

1. THE Dependency_System SHALL scan all pyproject.toml files in projects and packages
2. THE Dependency_System SHALL identify version conflicts for shared dependencies
3. THE Dependency_System SHALL unify dependency versions across all pyproject.toml files
4. THE Dependency_System SHALL remove unused dependencies from all pyproject.toml files
5. THE Dependency_System SHALL ensure all packages declare their dependencies explicitly
6. THE Dependency_System SHALL verify full version compatibility across the ecosystem
7. THE Dependency_System SHALL update uv.lock files after dependency changes
8. THE Dependency_System SHALL run all tests after dependency updates to verify compatibility

---

### Requirement 11: Template Strategy and Project-Level Assets

**User Story:** As a developer, I want templates to remain in projects only, so that packages stay reusable and projects control presentation.

#### Acceptance Criteria

1. THE Template_System SHALL ensure no templates exist in venv/libs/ packages
2. THE Template_System SHALL keep all templates in project-level templates/ directories
3. THE Template_System SHALL ensure both projects maintain consistent template structure
4. THE Template_System SHALL update templates to reference new import paths after refactoring
5. THE Template_System SHALL ensure templatetags are in packages when reusable, and in projects when project-specific
6. THE Template_System SHALL verify all template references resolve correctly after refactoring
7. THE Template_System SHALL ensure static files follow the same pattern (packages for reusable assets, projects for project-specific assets)

---

### Requirement 12: Commit and Branch Reconciliation

**User Story:** As a developer, I want the best improvements from all branches merged, so that no valuable work is lost.

#### Acceptance Criteria

1. THE Reconciliation_System SHALL compare the current main branch with recent feature branches
2. THE Reconciliation_System SHALL identify functionality present in branches but missing in main
3. THE Reconciliation_System SHALL identify improvements in branches that should be merged to main
4. THE Reconciliation_System SHALL analyse structural differences between branches
5. THE Reconciliation_System SHALL merge improvements without breaking the new architecture
6. THE Reconciliation_System SHALL prevent duplication during merge
7. THE Reconciliation_System SHALL run all tests after each merge to verify stability
8. THE Reconciliation_System SHALL document all merged improvements in MERGE_REPORT.md

---

### Requirement 13: Intelligent Merge and Quality Preservation

**User Story:** As a developer, I want merges to preserve quality and architecture, so that the system improves without regression.

#### Acceptance Criteria

1. THE Merge_System SHALL evaluate code quality before and after each merge
2. THE Merge_System SHALL reject merges that introduce duplication
3. THE Merge_System SHALL reject merges that violate boundary rules
4. THE Merge_System SHALL reject merges that reduce test coverage
5. THE Merge_System SHALL ensure merged code follows the new architecture patterns
6. THE Merge_System SHALL run boundary checks after each merge
7. THE Merge_System SHALL run the full test suite after each merge
8. THE Merge_System SHALL document quality metrics before and after each merge

---

### Requirement 14: Implementation Planning and Incremental Execution

**User Story:** As a developer, I want a complete implementation plan executed incrementally, so that the system remains stable throughout refactoring.

#### Acceptance Criteria

1. THE Planning_System SHALL build a complete implementation plan from all specs and requirements
2. THE Planning_System SHALL order tasks by dependency (foundation before automation, packages before projects)
3. THE Planning_System SHALL define validation checkpoints after each major phase
4. THE Planning_System SHALL execute tasks incrementally with validation at each step
5. THE Planning_System SHALL ensure the system remains runnable after each task
6. THE Planning_System SHALL run tests after each task to verify stability
7. THE Planning_System SHALL create rollback points before major changes
8. THE Planning_System SHALL document progress in a PROGRESS_LOG.md file

---

### Requirement 15: README Enhancement and Documentation Quality

**User Story:** As a developer, I want high-quality README files for all projects and packages, so that onboarding and usage are clear.

#### Acceptance Criteria

1. THE Documentation_System SHALL ensure every project has a comprehensive README.md
2. THE Documentation_System SHALL ensure every package has a comprehensive README.md
3. THE README_System SHALL document package purpose, installation, usage, and API reference
4. THE README_System SHALL include code examples for all public APIs
5. THE README_System SHALL document architectural decisions and design patterns
6. THE README_System SHALL link to related packages and dependencies
7. THE README_System SHALL maintain consistent structure across all README files
8. THE README_System SHALL include contribution guidelines and development setup instructions

---

### Requirement 16: Backup and Safety Mechanisms

**User Story:** As a developer, I want automatic backups before major changes, so that recovery is always possible.

#### Acceptance Criteria

1. THE Backup_System SHALL create database backups before major refactoring steps
2. THE Backup_System SHALL create media file backups before major refactoring steps
3. THE Backup_System SHALL create git commits before major refactoring steps
4. THE Backup_System SHALL tag recovery points in git history
5. THE Backup_System SHALL verify backup integrity after creation
6. THE Backup_System SHALL document backup locations in BACKUP_LOG.md
7. THE Backup_System SHALL provide restore procedures for all backup types
8. THE Backup_System SHALL test restore procedures to verify they work

---

### Requirement 17: Final Deliverables and System Validation

**User Story:** As a developer, I want a clean, unified, tested, and documented architecture, so that the system is production-ready and maintainable.

#### Acceptance Criteria

1. THE System SHALL have zero code duplication across projects and packages
2. THE System SHALL have all shared logic in the correct package
3. THE System SHALL have all boundary rules enforced by import-linter
4. THE System SHALL have all tests passing in all packages and projects
5. THE System SHALL have all specs completed with all tasks marked done
6. THE System SHALL have comprehensive documentation for all packages and projects
7. THE System SHALL have both projects running in Docker containers
8. THE System SHALL have all health endpoints returning HTTP 200
9. THE System SHALL have zero import errors or missing module errors
10. THE System SHALL have all migrations applied successfully
11. THE System SHALL have unified dependency versions across the ecosystem
12. THE System SHALL have templates in projects only, not in packages
13. THE System SHALL have consistent naming (snake_case for modules, PascalCase for classes)
14. THE System SHALL have ARCHITECTURE.md, MIGRATION_GUIDE.md, and updated README files
15. THE System SHALL have a COMPLETION_REPORT.md documenting all changes and improvements

---

### Requirement 18: Parser and Serializer Requirements

**User Story:** As a developer, I want all parsers and serializers to have round-trip testing, so that data integrity is guaranteed.

#### Acceptance Criteria

1. THE System SHALL identify all parsers in the codebase
2. THE System SHALL identify all serializers in the codebase
3. FOR ALL parsers, THE System SHALL provide a corresponding pretty printer
4. FOR ALL parsers, THE System SHALL implement a round-trip property test (parse → print → parse)
5. THE System SHALL document the grammar being parsed for each parser
6. THE System SHALL ensure round-trip tests pass for all valid inputs
7. WHEN an invalid input is provided, THE System SHALL ensure parsers return descriptive errors

---

### Requirement 19: Continuous Integration and Automated Validation

**User Story:** As a developer, I want CI to automatically validate architecture rules, so that violations are caught immediately.

#### Acceptance Criteria

1. THE CI_System SHALL run import-linter on every commit
2. THE CI_System SHALL run all tests on every commit
3. THE CI_System SHALL run boundary checks on every commit
4. THE CI_System SHALL fail builds on any boundary violation
5. THE CI_System SHALL fail builds on any test failure
6. THE CI_System SHALL fail builds on any import error
7. THE CI_System SHALL report clear error messages for all failures
8. THE CI_System SHALL complete all validation jobs within 10 minutes

---

### Requirement 20: Migration Safety and Reversibility

**User Story:** As a developer, I want all database migrations to be reversible, so that rollback is always possible.

#### Acceptance Criteria

1. THE Migration_System SHALL ensure all migrations have reverse operations
2. THE Migration_System SHALL test migration reversal (migrate app zero) before merging
3. THE Migration_System SHALL preserve physical table names during app renames
4. THE Migration_System SHALL update ContentType records during app renames
5. THE Migration_System SHALL verify data integrity after migrations
6. THE Migration_System SHALL document migration dependencies
7. THE Migration_System SHALL ensure migrations run in Docker containers without errors

---

## Special Requirements Guidance

### Parser and Serializer Requirements

All parsers and serializers in the ecosystem MUST follow these patterns:

1. **Parser Requirement**: WHEN a valid input is provided, THE Parser SHALL parse it into a structured object
2. **Parser Error Requirement**: WHEN an invalid input is provided, THE Parser SHALL return a descriptive error
3. **Pretty Printer Requirement**: THE Pretty_Printer SHALL format structured objects back into valid input format
4. **Round-Trip Requirement**: FOR ALL valid structured objects, parsing then printing then parsing SHALL produce an equivalent object

**Example Parser Requirements**:

```markdown
### Requirement 21: Parse JSON Configuration Files

**User Story:** As a developer, I want to parse JSON configuration files, so that I can load application settings.

#### Acceptance Criteria

1. WHEN a valid JSON configuration file is provided, THE Config_Parser SHALL parse it into a Configuration object
2. WHEN an invalid JSON configuration file is provided, THE Config_Parser SHALL return a descriptive error with line number
3. THE Config_Pretty_Printer SHALL format Configuration objects back into valid JSON files
4. FOR ALL valid Configuration objects, parsing then printing then parsing SHALL produce an equivalent object (round-trip property)
```

---

## Document Format

This document follows the EARS (Easy Approach to Requirements Syntax) patterns and INCOSE quality rules as specified in the workflow definition.

---

## Cross-References

- **finalize-refactor** spec: Completed — established initial package extraction patterns
- **phase-3-production-deployment** spec: Completed — established Docker deployment infrastructure
- **ctc-research-deployment-verification** spec: Completed — verified ctc-research.com deployment
- **django-refactoring** spec: Completed — established initial Django refactoring patterns
- **core-logic-consolidation-and-app-restructure** spec: In-progress — consolidates core business logic; this spec builds upon and extends that work
- **phase-2-website-sync-completion** spec: Not-started — website sync work is integrated into this spec's Phase 7 and Phase 8

---

## Notes

- This specification builds upon completed specs: finalize-refactor, phase-3-production-deployment, ctc-research-deployment-verification, django-refactoring
- The core-logic-consolidation spec is in progress and should be completed as part of this refactoring
- The phase-2-website-sync spec is not started and should be integrated into this refactoring
- All requirements use EARS patterns for consistency and testability
- All requirements follow INCOSE quality rules (clarity, testability, completeness, positive statements)
- The system is currently running and healthy — all changes must maintain system stability
- Templates must remain in projects, not packages
- All boundary rules must be enforced by import-linter in CI
- All tests must pass after each major phase
- All migrations must be reversible
- All documentation must be comprehensive and up-to-date
