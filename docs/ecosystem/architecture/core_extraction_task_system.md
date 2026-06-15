# Core Code Extraction & Package Consolidation Task System

**Version:** 2.0
**Status:** Ready for Execution
**Date:** April 14, 2026
**Scope:** Extract only core, reusable code from websites into packages without duplication

---

## Executive Overview

This task system focuses on extracting **only core, reusable code** from Django websites into django-osoul and django-rseal packages. Project-specific logic remains in websites. The system eliminates duplication and ensures code fits clear package use cases.

### Core Principles
- **Extract Only Core Code:** Reusable across multiple projects
- **No Duplication:** Eliminate duplicate logic
- **Package-Aligned:** Code fits clear package use cases
- **Website-Specific Stays:** Project logic remains in websites
- **SOLID Principles:** Clean, maintainable code
- **Incremental Validation:** Validate at each step

### What Gets Extracted
- Base models and mixins
- Form base classes and validators
- Middleware and decorators
- Reusable utilities and helpers
- Email templates and sending logic
- Task scheduling and automation
- Testing factories and fixtures

### What Stays in Websites
- Project-specific models
- Project-specific views and templates
- Project-specific business logic
- Project-specific configurations
- Project-specific tests

---

## Phase 1: Analysis & Planning (Week 1)

### Task 1.1: Identify Core vs. Project-Specific Code

**Objective:** Distinguish between reusable core code and project-specific code

**Deliverables:**
- [ ] Core code inventory
- [ ] Project-specific code inventory
- [ ] Duplication analysis
- [ ] Extraction candidates list

**Steps:**

1. **Audit Models**
   ```bash
   # Find all models in websites
   find ctc-research.com structa.cloud -name "models.py" -type f

   # Analyze each model:
   # - Is it reusable across projects? → Core
   # - Is it project-specific? → Stays
   # - Is it duplicated? → Consolidate
   ```

2. **Audit Forms**
   ```bash
   # Find all forms
   find ctc-research.com structa.cloud -name "forms.py" -type f

   # Categorize:
   # - Base form classes → Core (django-osoul)
   # - Project forms → Stays
   # - Duplicated forms → Consolidate
   ```

3. **Audit Views**
   ```bash
   # Find all views
   find ctc-research.com structa.cloud -name "views.py" -type f

   # Categorize:
   # - Base view classes → Core (django-osoul)
   # - Mixins → Core (django-osoul)
   # - Project views → Stays
   ```

4. **Audit Utilities**
   ```bash
   # Find all utilities
   find ctc-research.com structa.cloud -name "utils.py" -type f

   # Categorize:
   # - Reusable helpers → Core (django-osoul)
   # - Project-specific → Stays
   # - Duplicated → Consolidate
   ```

5. **Audit Email Logic**
   ```bash
   # Find email-related code
   grep -r "send_mail\|EmailMessage" ctc-research.com structa.cloud --include="*.py"

   # Categorize:
   # - Email sending logic → Core (django-rseal)
   # - Email templates → Core (django-rseal)
   # - Project-specific emails → Stays
   ```

6. **Audit Task Logic**
   ```bash
   # Find task-related code
   grep -r "@task\|@periodic_task\|celery" ctc-research.com structa.cloud --include="*.py"

   # Categorize:
   # - Task base classes → Core (django-rseal)
   # - Task utilities → Core (django-rseal)
   # - Project tasks → Stays
   ```

**Success Criteria:**
- All code categorized
- Duplication identified
- Extraction candidates clear
- No ambiguous assignments

---

### Task 1.2: Map Duplication

**Objective:** Identify and document all duplicated code

**Deliverables:**
- [ ] Duplication report
- [ ] Consolidation plan
- [ ] Impact analysis
- [ ] Merge strategy

**Steps:**

1. **Find Duplicate Models**
   ```python
   # Compare models across projects
   # Example: User model, Profile model, etc.
   # Document differences and similarities
   ```

2. **Find Duplicate Forms**
   ```python
   # Compare form classes
   # Identify common validation logic
   # Document field definitions
   ```

3. **Find Duplicate Utilities**
   ```python
   # Compare utility functions
   # Identify common patterns
   # Document usage
   ```

4. **Find Duplicate Templates**
   ```bash
   # Find duplicate templates
   find ctc-research.com structa.cloud -name "*.html" -type f | sort

   # Compare content
   # Identify reusable components
   ```

**Success Criteria:**
- All duplicates documented
- Consolidation plan clear
- Impact understood
- Merge strategy defined

---

### Task 1.3: Plan Extraction Strategy

**Objective:** Define how to extract core code without breaking projects

**Deliverables:**
- [ ] Extraction sequence
- [ ] Dependency map
- [ ] Backward compatibility plan
- [ ] Testing strategy

**Steps:**

1. **Define Extraction Order**
   - Extract base models first
   - Extract utilities next
   - Extract forms and validators
   - Extract email logic
   - Extract task logic

2. **Map Dependencies**
   - What depends on what?
   - What needs to be extracted first?
   - What can be extracted in parallel?

3. **Plan Backward Compatibility**
   - Create deprecation shims
   - Maintain old import paths
   - Plan migration timeline

4. **Plan Testing**
   - What tests to run after each extraction?
   - How to verify nothing broke?
   - How to validate functionality?

**Success Criteria:**
- Extraction sequence clear
- Dependencies mapped
- Backward compatibility planned
- Testing strategy defined

---

## Phase 2: Extract Base Models & Utilities (Weeks 2-3)

### Task 2.1: Extract Base Models to django-osoul

**Objective:** Move reusable base models to django-osoul

**Deliverables:**
- [ ] Base models in django-osoul
- [ ] Deprecation shims in websites
- [ ] All imports updated
- [ ] Tests passing

**Steps:**

1. **Identify Reusable Base Models**
   ```python
   # Examples of core models:
   # - BaseModel (with timestamps, UUID, etc.)
   # - TimestampedModel
   # - SluggedModel
   # - PublishableModel
   # - SoftDeleteModel
   ```

2. **Create in django-osoul**
   ```bash
   # Create models in django-osoul
   venv/libs/django-osoul/src/django_osoul/models/base.py
   venv/libs/django-osoul/src/django_osoul/models/mixins.py
   ```

3. **Move Code**
   ```python
   # Move base model definitions
   # Keep project-specific models in websites
   # Example: Move BaseUser, keep ProjectUser
   ```

4. **Create Deprecation Shims**
   ```python
   # In websites, create shims:
   from django_osoul.models import BaseModel
   # Keep old import path working
   ```

5. **Update All Imports**
   ```bash
   # Update imports in websites
   sed -i 's/from \.models import BaseModel/from django_osoul.models import BaseModel/g' \
       ctc-research.com/**/*.py
   ```

6. **Run Tests**
   ```bash
   # Run all tests
   pytest ctc-research.com/tests/ -v
   pytest structa.cloud/tests/ -v
   ```

**Success Criteria:**
- Base models in django-osoul
- Websites still work
- All tests passing
- No circular imports

---

### Task 2.2: Extract Reusable Utilities to django-osoul

**Objective:** Move reusable utility functions to django-osoul

**Deliverables:**
- [ ] Utilities in django-osoul
- [ ] Deprecation shims in websites
- [ ] All imports updated
- [ ] Tests passing

**Steps:**

1. **Identify Reusable Utilities**
   ```python
   # Examples:
   # - String formatting helpers
   # - Date/time utilities
   # - Validation helpers
   # - Slug generation
   # - URL utilities
   # - Permission helpers
   ```

2. **Create in django-osoul**
   ```bash
   venv/libs/django-osoul/src/django_osoul/utils/
   ```

3. **Move Code**
   ```python
   # Move only reusable utilities
   # Keep project-specific utilities in websites
   ```

4. **Create Deprecation Shims**
   ```python
   # In websites, create shims for backward compatibility
   ```

5. **Update All Imports**
   ```bash
   # Update imports across websites
   ```

6. **Run Tests**
   ```bash
   pytest -v
   ```

**Success Criteria:**
- Utilities in django-osoul
- Websites still work
- All tests passing
- No duplication

---

### Task 2.3: Extract Form Base Classes to django-osoul

**Objective:** Move reusable form classes to django-osoul

**Deliverables:**
- [ ] Form base classes in django-osoul
- [ ] Deprecation shims in websites
- [ ] All imports updated
- [ ] Tests passing

**Steps:**

1. **Identify Reusable Form Classes**
   ```python
   # Examples:
   # - BaseForm (with common methods)
   # - BaseModelForm
   # - BaseFormSet
   # - Common validators
   ```

2. **Create in django-osoul**
   ```bash
   venv/libs/django-osoul/src/django_osoul/forms/
   ```

3. **Move Code**
   ```python
   # Move base form classes
   # Keep project-specific forms in websites
   ```

4. **Create Deprecation Shims**
   ```python
   # In websites, create shims
   ```

5. **Update All Imports**
   ```bash
   # Update imports
   ```

6. **Run Tests**
   ```bash
   pytest -v
   ```

**Success Criteria:**
- Form classes in django-osoul
- Websites still work
- All tests passing
- No duplication

---

## Phase 3: Extract Email & Task Logic (Weeks 4-5)

### Task 3.1: Extract Email Logic to django-rseal

**Objective:** Move reusable email logic to django-rseal

**Deliverables:**
- [ ] Email logic in django-rseal
- [ ] Email templates organized
- [ ] Deprecation shims in websites
- [ ] All imports updated
- [ ] Tests passing

**Steps:**

1. **Identify Reusable Email Logic**
   ```python
   # Examples:
   # - Email sending utilities
   # - Email template base classes
   # - Email scheduling logic
   # - Email tracking
   ```

2. **Create in django-rseal**
   ```bash
   venv/libs/django-rseal/src/django_rseal/email/
   ```

3. **Move Code**
   ```python
   # Move email utilities
   # Keep project-specific email logic in websites
   ```

4. **Organize Email Templates**
   ```bash
   # Move reusable email templates to django-rseal
   # Keep project-specific templates in websites
   ```

5. **Create Deprecation Shims**
   ```python
   # In websites, create shims
   ```

6. **Update All Imports**
   ```bash
   # Update imports
   ```

7. **Run Tests**
   ```bash
   pytest -v
   ```

**Success Criteria:**
- Email logic in django-rseal
- Websites still work
- All tests passing
- No duplication

---

### Task 3.2: Extract Task Logic to django-rseal

**Objective:** Move reusable task logic to django-rseal

**Deliverables:**
- [ ] Task logic in django-rseal
- [ ] Task base classes created
- [ ] Deprecation shims in websites
- [ ] All imports updated
- [ ] Tests passing

**Steps:**

1. **Identify Reusable Task Logic**
   ```python
   # Examples:
   # - Task base classes
   # - Task scheduling utilities
   # - Task monitoring
   # - Task error handling
   ```

2. **Create in django-rseal**
   ```bash
   venv/libs/django-rseal/src/django_rseal/tasks/
   ```

3. **Move Code**
   ```python
   # Move task utilities
   # Keep project-specific tasks in websites
   ```

4. **Create Deprecation Shims**
   ```python
   # In websites, create shims
   ```

5. **Update All Imports**
   ```bash
   # Update imports
   ```

6. **Run Tests**
   ```bash
   pytest -v
   ```

**Success Criteria:**
- Task logic in django-rseal
- Websites still work
- All tests passing
- No duplication

---

## Phase 4: Extract Testing Utilities (Week 6)

### Task 4.1: Extract Testing Factories to django-grep

**Objective:** Move reusable test factories to django-grep

**Deliverables:**
- [ ] Factories in django-grep
- [ ] Deprecation shims in websites
- [ ] All imports updated
- [ ] Tests passing

**Steps:**

1. **Identify Reusable Factories**
   ```python
   # Examples:
   # - UserFactory
   # - BaseModelFactory
   # - Common fixtures
   ```

2. **Create in django-grep**
   ```bash
   venv/libs/django-grep/src/django_grep/factories/
   ```

3. **Move Code**
   ```python
   # Move reusable factories
   # Keep project-specific factories in websites
   ```

4. **Create Deprecation Shims**
   ```python
   # In websites, create shims
   ```

5. **Update All Imports**
   ```bash
   # Update imports
   ```

6. **Run Tests**
   ```bash
   pytest -v
   ```

**Success Criteria:**
- Factories in django-grep
- Websites still work
- All tests passing
- No duplication

---

### Task 4.2: Extract Test Fixtures to django-grep

**Objective:** Move reusable test fixtures to django-grep

**Deliverables:**
- [ ] Fixtures in django-grep
- [ ] Deprecation shims in websites
- [ ] All imports updated
- [ ] Tests passing

**Steps:**

1. **Identify Reusable Fixtures**
   ```python
   # Examples:
   # - Common test data
   # - Reusable setup/teardown
   # - Common assertions
   ```

2. **Create in django-grep**
   ```bash
   venv/libs/django-grep/src/django_grep/fixtures/
   ```

3. **Move Code**
   ```python
   # Move reusable fixtures
   # Keep project-specific fixtures in websites
   ```

4. **Create Deprecation Shims**
   ```python
   # In websites, create shims
   ```

5. **Update All Imports**
   ```bash
   # Update imports
   ```

6. **Run Tests**
   ```bash
   pytest -v
   ```

**Success Criteria:**
- Fixtures in django-grep
- Websites still work
- All tests passing
- No duplication

---

## Phase 5: Cleanup & Documentation (Weeks 7-8)

### Task 5.1: Remove Duplication from Websites

**Objective:** Remove duplicate code now that core code is extracted

**Deliverables:**
- [ ] Duplicate code removed
- [ ] All imports updated
- [ ] Tests passing
- [ ] No functionality lost

**Steps:**

1. **Identify Remaining Duplicates**
   ```bash
   # Find duplicate code in websites
   find ctc-research.com structa.cloud -name "*.py" -type f | \
     xargs md5sum | sort | uniq -d -w32
   ```

2. **Remove Duplicates**
   ```python
   # Remove duplicate code
   # Keep only project-specific code
   ```

3. **Update Imports**
   ```bash
   # Update imports to use extracted code
   ```

4. **Run Tests**
   ```bash
   pytest -v
   ```

**Success Criteria:**
- No duplicate code
- All tests passing
- Functionality preserved

---

### Task 5.2: Organize Documentation

**Objective:** Move documentation to docs/ directory

**Deliverables:**
- [ ] All .md files moved to docs/
- [ ] Documentation organized by domain
- [ ] Index created
- [ ] All references updated

**Steps:**

1. **Create docs structure**
   ```bash
   mkdir -p docs/{architecture,guides,api,changelog}
   ```

2. **Move .md files**
   ```bash
   # Move all .md files from base to docs/
   find . -maxdepth 1 -name "*.md" -type f -exec mv {} docs/ \;
   ```

3. **Organize by domain**
   ```bash
   # Organize documentation
   mv docs/UNIFIED_PACKAGE_REORGANIZATION_SPEC.md docs/architecture/
   mv docs/IMPLEMENTATION_GUIDE.md docs/guides/
   ```

4. **Create index**
   ```bash
   # Create docs/README.md with index
   ```

5. **Update all references**
   ```bash
   # Update all links to documentation
   ```

**Success Criteria:**
- All .md files moved
- Documentation organized
- Index complete
- All references updated

---

### Task 5.3: Create Package Documentation

**Objective:** Document extracted code in packages

**Deliverables:**
- [ ] django-osoul documentation
- [ ] django-rseal documentation
- [ ] django-grep documentation
- [ ] API documentation

**Steps:**

1. **Create django-osoul docs**
   ```bash
   # Document base models, utilities, forms
   venv/libs/django-osoul/docs/
   ```

2. **Create django-rseal docs**
   ```bash
   # Document email, tasks, workflows
   venv/libs/django-rseal/docs/
   ```

3. **Create django-grep docs**
   ```bash
   # Document factories, fixtures, assertions
   venv/libs/django-grep/docs/
   ```

4. **Generate API docs**
   ```bash
   # Generate from docstrings
   sphinx-apidoc -o docs/api venv/libs/
   ```

**Success Criteria:**
- All packages documented
- API documentation complete
- Examples provided

---

## Extraction Checklist

### Before Extraction
- [ ] Code categorized (core vs. project-specific)
- [ ] Duplication identified
- [ ] Extraction sequence planned
- [ ] Backward compatibility planned
- [ ] Tests prepared

### During Extraction
- [ ] Code moved to package
- [ ] Deprecation shims created
- [ ] Imports updated
- [ ] Tests run and passing
- [ ] No circular imports

### After Extraction
- [ ] Websites still work
- [ ] All tests passing
- [ ] No duplication
- [ ] Documentation updated
- [ ] Backward compatibility verified

---

## What Gets Extracted: Detailed List

### django-osoul (Base Models & Utilities)

**Models:**
- BaseModel (with timestamps, UUID)
- TimestampedModel
- SluggedModel
- PublishableModel
- SoftDeleteModel

**Utilities:**
- String formatting helpers
- Date/time utilities
- Validation helpers
- URL utilities
- Permission helpers

**Forms:**
- BaseForm
- BaseModelForm
- Common validators

**Middleware:**
- Request/response processing
- Authentication helpers
- Permission checking

**Decorators:**
- Common decorators
- Permission decorators
- Caching decorators

### django-rseal (Email & Tasks)

**Email:**
- Email sending utilities
- Email template base classes
- Email scheduling
- Email tracking

**Tasks:**
- Task base classes
- Task scheduling utilities
- Task monitoring
- Task error handling

**Workflows:**
- Workflow orchestration
- Pipeline utilities

### django-grep (Testing)

**Factories:**
- UserFactory
- BaseModelFactory
- Common fixtures

**Fixtures:**
- Common test data
- Reusable setup/teardown
- Common assertions

---

## What Stays in Websites

### ctc-research.com & structa.cloud

**Models:**
- Project-specific models
- Custom fields
- Project-specific relationships

**Views:**
- Project-specific views
- Project-specific logic
- Project-specific templates

**Forms:**
- Project-specific forms
- Project-specific validation

**Tasks:**
- Project-specific tasks
- Project-specific workflows

**Tests:**
- Project-specific tests
- Project-specific fixtures

---

## Success Criteria

### Code Quality
- [ ] No duplication across projects
- [ ] All tests passing
- [ ] No circular imports
- [ ] Type hints for public APIs
- [ ] Comprehensive docstrings

### Architecture
- [ ] Clear separation of concerns
- [ ] Core code in packages
- [ ] Project code in websites
- [ ] SOLID principles applied
- [ ] Backward compatibility maintained

### Documentation
- [ ] All packages documented
- [ ] API documentation complete
- [ ] Examples provided
- [ ] Migration guide created
- [ ] Changelog maintained

---

## Timeline

### Week 1: Analysis & Planning
- Task 1.1: Identify core vs. project-specific
- Task 1.2: Map duplication
- Task 1.3: Plan extraction strategy

### Weeks 2-3: Extract Base Models & Utilities
- Task 2.1: Extract base models
- Task 2.2: Extract utilities
- Task 2.3: Extract form base classes

### Weeks 4-5: Extract Email & Task Logic
- Task 3.1: Extract email logic
- Task 3.2: Extract task logic

### Week 6: Extract Testing Utilities
- Task 4.1: Extract factories
- Task 4.2: Extract fixtures

### Weeks 7-8: Cleanup & Documentation
- Task 5.1: Remove duplication
- Task 5.2: Organize documentation
- Task 5.3: Create package documentation

---

## Next Steps

1. **Review this task system** with the team
2. **Assign owners** to each task
3. **Create git branches** for each phase
4. **Begin Phase 1** (Analysis & Planning)
5. **Track progress** against timeline
6. **Validate** at each phase completion
7. **Document** all changes
8. **Maintain** backward compatibility

---

**Document Status:** ✅ Complete
**Last Updated:** April 14, 2026
**Ready for Implementation:** Yes
