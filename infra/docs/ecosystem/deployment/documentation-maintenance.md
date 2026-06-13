# Documentation Maintenance Guide

## Overview

This guide defines the process for keeping the project documentation current, accurate, and well-organized. It covers how to update existing content, add new sections, manage navigation, review changes, and handle deprecated documentation.

**Documentation System**: [Docsify](https://docsify.js.org/) — renders markdown files dynamically
**Entry Point**: `docs/index.html`
**Navigation**: `docs/_sidebar.md`
**Root**: `docs/` directory at project root

---

## Table of Contents

1. [Updating Existing Documentation](#updating-existing-documentation)
2. [Adding New Documentation Sections](#adding-new-documentation-sections)
3. [Updating the Sidebar Navigation](#updating-the-sidebar-navigation)
4. [Review Process for Documentation Changes](#review-process-for-documentation-changes)
5. [Handling Deprecated Documentation](#handling-deprecated-documentation)
6. [Documentation Standards](#documentation-standards)
7. [Local Preview](#local-preview)

---

## Updating Existing Documentation

### Simple Content Updates

For minor corrections (typos, outdated values, broken links):

1. Locate the relevant markdown file in `docs/`
2. Edit the file directly
3. Verify the change renders correctly (see [Local Preview](#local-preview))
4. Commit with a descriptive message:

```bash
git add docs/deployment/environment.md
git commit -m "docs: update Redis environment variable defaults"
```

### Updating Code Examples

When updating code examples, always verify the example works with the current stack before committing:

```bash
# Test the example in a local environment
python manage.py shell
# or
docker-compose exec frontend python manage.py shell
```

Update the example in the markdown file, then note the version it applies to if relevant:

```markdown
<!-- Works with Wagtail 6.x+ -->
```python
from wagtail.models import Page
```
```

### Updating Configuration References

When environment variables, Docker settings, or configuration files change:

1. Update `docs/deployment/environment.md` with the new variable
2. Update any other docs that reference the changed configuration
3. Search for references across the docs directory:

```bash
grep -r "OLD_VARIABLE_NAME" docs/
```

4. Update all occurrences before committing

---

## Adding New Documentation Sections

### When to Add a New Section

Add a new top-level section when:
- A new major service or application is introduced
- A new technology is adopted project-wide
- An existing section grows too large to navigate easily

Add a new page within an existing section when:
- A topic is distinct enough to warrant its own page
- A section's README is becoming too long (>300 lines)

### Step-by-Step: Adding a New Page

1. **Create the markdown file** in the appropriate section directory:

```bash
# Example: adding a caching guide to the deployment section
touch docs/deployment/07-caching-setup.md
```

2. **Write the content** following the [Documentation Standards](#documentation-standards) below.

3. **Add the page to `_sidebar.md`** (see [Updating the Sidebar Navigation](#updating-the-sidebar-navigation)).

4. **Add cross-references** from related pages where relevant.

### Step-by-Step: Adding a New Top-Level Section

1. **Create the section directory and README**:

```bash
mkdir docs/security
touch docs/security/README.md
```

2. **Write the section README** with an overview and links to sub-pages.

3. **Add the section to `_sidebar.md`** with its own heading block.

4. **Update `docs/README.md`** to include a link to the new section.

5. **Create initial content pages** — at minimum one substantive page beyond the README.

### Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Section directories | lowercase, hyphenated | `getting-started/` |
| Numbered pages | `NN-descriptive-name.md` | `03-deployment-procedures.md` |
| Unnumbered pages | `descriptive-name.md` | `architecture.md` |
| Section index | `README.md` | `deployment/README.md` |

Use numbered filenames when the reading order matters (e.g., step-by-step guides). Use descriptive names for reference documents that can be read in any order.

---

## Updating the Sidebar Navigation

The `docs/_sidebar.md` file controls all navigation in Docsify. Every new page must be added here to be discoverable.

### Sidebar Structure

```markdown
- **[Home](README.md)**

- **Section Name**
  - [Page Title](section/page.md)
  - [Another Page](section/another-page.md)
```

- Top-level sections use `**bold**` formatting
- Pages are indented with two spaces
- Links use relative paths from the `docs/` root

### Adding a Page to an Existing Section

Locate the section block in `_sidebar.md` and add the new entry in logical order:

```markdown
- **Deployment**
  - [Overview](deployment/README.md)
  - [Deployment Overview](deployment/01-deployment-overview.md)
  - [Build for Production](deployment/02-build-for-production.md)
  - [Deployment Procedures](deployment/03-deployment-procedures.md)
  - [Post-Deployment Verification](deployment/04-post-deployment-verification.md)
  - [Rollback Procedures](deployment/05-rollback-procedures.md)
  - [Troubleshooting](deployment/06-troubleshooting.md)
  - [Caching Setup](deployment/07-caching-setup.md)   ← new entry
```

### Adding a New Top-Level Section

Add a new section block at the appropriate position in `_sidebar.md`. Maintain a logical grouping — developer-facing sections first, operational sections after:

```markdown
- **Security**
  - [Overview](security/README.md)
  - [Authentication](security/01-authentication.md)
  - [Secrets Management](security/02-secrets-management.md)
```

### Placeholder Entries (Coming Soon)

For sections that are planned but not yet ready, use a non-linked placeholder:

```markdown
- **LMS Integration**
  - [Overview](lms/README.md)
```

The placeholder page (`lms/README.md`) should display a "Coming Soon" badge and brief description of planned content.

### Verifying Navigation

After editing `_sidebar.md`, preview locally to confirm:
- All links resolve correctly
- Indentation is consistent (two spaces per level)
- No broken or duplicate entries

---

## Review Process for Documentation Changes

### Minor Changes (No Review Required)

The following can be committed directly without a formal review:
- Fixing typos or grammar
- Updating version numbers or URLs
- Adding missing punctuation or formatting fixes
- Correcting factually wrong values you have direct knowledge of

### Standard Changes (Self-Review)

For content additions or rewrites, review your own changes before committing:

- [ ] Content is accurate and reflects the current state of the system
- [ ] Code examples are tested and working
- [ ] Links are valid (no 404s)
- [ ] Markdown renders correctly in Docsify preview
- [ ] `_sidebar.md` is updated if a new page was added
- [ ] Related pages are updated with cross-references if needed

### Significant Changes (Peer Review)

Request a peer review for:
- New top-level sections
- Major rewrites of existing sections
- Changes to `docs/index.html` or `docs/_sidebar.md` structure
- Documentation that affects security or production procedures

To request a review, open a pull request and tag a team member. Include in the PR description:
- What changed and why
- Which sections were affected
- Whether any pages were deprecated or removed

### Review Checklist for Reviewers

- [ ] Technical accuracy — does the content match how the system actually works?
- [ ] Completeness — are there obvious gaps or missing steps?
- [ ] Clarity — can a new team member follow the instructions?
- [ ] Navigation — is the new content discoverable via `_sidebar.md`?
- [ ] Standards — does the content follow the [Documentation Standards](#documentation-standards)?

---

## Handling Deprecated Documentation

### When Documentation Becomes Deprecated

Documentation is deprecated when:
- A feature, service, or configuration it describes has been removed
- The described approach has been superseded by a better one
- The content is no longer accurate and cannot be easily updated

### Option 1: Update in Place

If the old approach is still partially relevant (e.g., for rollback or historical context), update the page with a deprecation notice at the top:

```markdown
> **Deprecated**: This configuration applies to versions prior to 2.0. For current setup,
> see [New Configuration Guide](new-config.md). This page is retained for rollback reference.
```

Keep the page in `_sidebar.md` but move it to the bottom of its section or add a `(Deprecated)` label:

```markdown
  - [Old Config Guide (Deprecated)](deployment/old-config.md)
```

### Option 2: Archive the Page

For content that is no longer relevant to any current workflow:

1. Move the file to `docs/archive/`:

```bash
mkdir -p docs/archive
git mv docs/deployment/old-guide.md docs/archive/old-guide.md
```

2. Remove the entry from `_sidebar.md`

3. Add a note in the archive file explaining why it was archived:

```markdown
> **Archived**: This guide was relevant to the django-seed era (pre-2024).
> The described setup no longer applies to the current Wagtail + django-unfold stack.
```

4. Commit with a clear message:

```bash
git commit -m "docs: archive django-seed setup guide (superseded by migration-guide.md)"
```

### Option 3: Delete the Page

Delete documentation only when:
- It is factually wrong and cannot be corrected
- It describes a security vulnerability or bad practice
- It has been fully superseded and the archive adds no value

```bash
git rm docs/deployment/obsolete-guide.md
# Remove entry from _sidebar.md
git commit -m "docs: remove obsolete guide (replaced by environment.md)"
```

### Never Delete Without a Trace

Before deleting any documentation, check if it is referenced from other pages:

```bash
grep -r "obsolete-guide" docs/
```

Update or remove all references before deleting the file.

---

## Documentation Standards

### File Format

- All documentation files use Markdown (`.md`)
- Files must be UTF-8 encoded
- Use Unix line endings (`\n`)
- End files with a single newline

### Headings

- Use a single `#` H1 at the top of each file (the page title)
- Use `##` for major sections, `###` for subsections
- Do not skip heading levels

### Code Blocks

Always specify the language for syntax highlighting:

````markdown
```python
# Python code
```

```bash
# Shell commands
```

```yaml
# YAML configuration
```
````

### Links

Use relative links for internal documentation:

```markdown
[Environment Variables](environment.md)           ← same directory
[Architecture Overview](../architecture/README.md) ← parent directory
```

Use absolute URLs for external links:

```markdown
[Docsify Documentation](https://docsify.js.org/)
```

### Tables

Use tables for structured comparisons, configuration references, and option lists:

```markdown
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| DB_NAME  | Yes      | —       | Database name |
```

### Admonitions

Use blockquotes for notes, warnings, and tips:

```markdown
> **Note**: This step is only required in production environments.

> **Warning**: Changing this setting requires a full service restart.

> **Deprecated**: See [new guide](new-guide.md) for current instructions.
```

---

## Local Preview

To preview documentation locally before committing:

### Option 1: Docsify CLI

```bash
# Install docsify-cli globally
npm install -g docsify-cli

# Serve the docs directory
docsify serve docs

# Open http://localhost:3000
```

### Option 2: Docker (using the project's Docsify service)

```bash
# Start only the Docsify service
docker-compose up docsify

# Open http://localhost:3001 (or configured port)
```

### Option 3: Simple HTTP Server

```bash
# Python 3
python -m http.server 3000 --directory docs

# Open http://localhost:3000
```

Note: The Python HTTP server does not support Docsify's client-side routing. Use the Docsify CLI or Docker for full preview fidelity.

---

## Related Documentation

- [Deployment Overview](01-deployment-overview.md) — Service deployment procedures
- [Environment Configuration](environment.md) — Environment variables reference
- [Architecture Overview](architecture.md) — System architecture documentation
- [Migration Guide](migration-guide.md) — Framework migration history
