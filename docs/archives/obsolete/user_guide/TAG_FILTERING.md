# Tag Filtering & Visibility Guide

For content editors managing portfolio projects and blog posts.

---

## Understanding Tags

Tags are **reusable labels** that organize your projects and posts by technology, category, or topic.

### Key Concepts

| Term | Meaning |
|------|---------|
| **Tag** | A reusable label (e.g., "React", "UI Design") |
| **Active Tag** | A tag that appears in filters and listings |
| **Inactive Tag** | A hidden tag that won't show in listings |
| **Project Tag** | A tag assigned to a single project |
| **Tag Filter** | The interface where visitors select tags to filter projects |

---

## Creating & Managing Tags

### 1. Create a New Tag

**Path**: Wagtail Admin → Snippets → Portfolio Tags

1. Click **"Add portfolio tag"**
2. Fill in the form:
   - **Tag Name**: "React" or "UI Design"
   - **Slug**: Auto-populated (e.g., "react", "ui-design")
   - **Description** (optional): "A JavaScript library for building UIs"
   - **Tag Color**: Pick a color for badge styling
   - **Icon** (optional): Bootstrap icon class (e.g., "bi-code-slash")
   - **Active**: ☑️ Checked (default) means this tag will appear in filters

3. Click **Save**

### 2. Editing Tags

1. Click on the tag name in the tags list
2. Update fields as needed
3. To **hide a tag**: Uncheck the **Active** checkbox
4. Click **Save**

### 3. Deleting Tags

1. Select tag(s) from the list
2. Click **Delete** button at bottom
3. **Warning**: This removes the tag from all projects/posts that use it

---

## Tag Visibility Rules

### What Appears in Listings

✅ **SHOWN** in the filter dropdown:
- Only **active tags** appear
- Only tags assigned to at least one active project

❌ **HIDDEN** from the filter dropdown:
- Inactive tags (unchecked "Active" checkbox)
- Tags with no projects

### What Appears in Project Details

✅ **SHOWN** in project detail modals:
- All tags assigned to the project
- Including inactive tags (if someone previously assigned them)

❌ **HIDDEN**:
- Nothing — all assigned tags show, regardless of active status

---

## How to Use Tags: Scenarios

### Scenario 1: Archiving Old Technology

You have projects tagged with "React 16" but you've moved on to React 18. You want to keep the history but hide it from current listings.

**Solution**:
1. Go to Snippets → Portfolio Tags
2. Find "React 16"
3. Uncheck **Active** checkbox
4. Save

**Result**:
- ✅ Old projects still show "React 16" in detail view (preserves history)
- ❌ "React 16" no longer appears in filter dropdown
- ❌ Visitors can't filter by "React 16" anymore

### Scenario 2: Experimental/WIP Tags

You're working on a new project that uses a prototype framework. You don't want it in listings yet.

**Solution**:
1. Create tag "Prototype Framework"
2. **Leave "Active" UNCHECKED**
3. Assign it to your project
4. Save project

**Result**:
- ✅ Project still has the tag (visible in detail view)
- ❌ Tag doesn't appear in filter dropdown
- ❌ Visitors can't filter by this tag

### Scenario 3: Renaming a Tag

You want to rename "UX/UI" to "User Interface Design".

**Solution**:
1. Create NEW tag "User Interface Design"
2. Manually assign it to all projects that had "UX/UI"
3. Remove "UX/UI" from those projects
4. Delete old "UX/UI" tag

**OR** (Simpler):
1. Edit "UX/UI" tag
2. Change **Tag Name** to "User Interface Design"
3. Change **Slug** to "user-interface-design"
4. Save

**Result**: All projects automatically use the new name

### Scenario 4: Hiding All Inactive Tags

You want to clean up the filter dropdown by hiding tags that aren't used.

**Solution**:
1. Create a new tag "Unused Technologies"
2. Create tags like "Flash", "Silverlight", "JSP" and leave **Active** UNCHECKED
3. Or just delete them entirely

**Better**: Leave them **inactive** — you can reactivate if needed

---

## Best Practices

### ✅ Do's

1. **Use consistent naming**: "React" not "react" and "React 18.0"
2. **Add descriptions**: Help visitors understand what each tag means
3. **Archive instead of delete**: Uncheck Active instead of deleting (preserves history)
4. **Keep tag count reasonable**: 10-20 tags max in filter dropdown
5. **Use color coding**: Different colors for different categories
6. **Review periodically**: Once per quarter, clean up unused tags

### ❌ Don'ts

1. **Don't use spaces in slugs**: Use hyphens ("ui-design" not "ui design")
2. **Don't delete tags**: Archive them instead (uncheck Active)
3. **Don't mix naming conventions**: Pick "React" or "ReactJS" and stick with it
4. **Don't create duplicate tags**: "Python" and "python" are different
5. **Don't remove tags from projects**: It breaks history; archive the tag instead

---

## Filter Behavior for Visitors

### What Visitors See

**On Portfolio/Blog Tab**:

1. **All Active Tags Available**
   - Even if no projects currently have this tag
   - Shows where you work/have worked

2. **Clicking a Tag**
   - Shows only projects with that tag
   - Shows "No projects found" if tag is inactive or no projects match

3. **Multiple Tag Selection**
   - Shows projects with ANY of the selected tags
   - (Example: Select "React" AND "Python" → shows projects using either)

4. **Search + Tags Combined**
   - Both filters apply simultaneously
   - (Example: Search "portfolio" + Tag "React" → searches projects AND filters by React)

### Tag Filter Reset

- **Clear All**: Resets to show all active projects
- **Local Storage**: Selected tags persist in visitor's browser (survives tab switches)
- **URL Parameter**: Current tags are stored in URL (shareable link)

---

## Troubleshooting

### Problem: Tag doesn't appear in filter dropdown

**Possible causes**:
1. ❌ Tag is **inactive** (uncheck Active box)
   - **Fix**: Edit tag and check **Active** box

2. ❌ No projects are using this tag
   - **Fix**: Assign the tag to at least one active project

3. ❌ All projects using the tag are inactive
   - **Fix**: Activate at least one project

**Test**: 
1. Go to Snippets → Portfolio Tags
2. Verify tag has **Active** ☑️ checked
3. Click tag name to see which projects use it
4. Verify at least one project is **Active** (status should be "Live")

### Problem: Project shows wrong tag in listing but correct in detail view

**Explanation**: 
- The tag was **deactivated** after the project was created
- Project still has the tag (correct in detail view)
- But filter no longer shows this tag (correct in listing)

**Solution**:
- Either reactivate the tag or remove it from the project

---

## Tag Colors & Icons

### Choosing Colors

Use the color picker to select tag colors:

| Category | Recommended Color |
|----------|------------------|
| Languages | Blue (#0066FF) |
| Frameworks | Green (#00AA00) |
| Databases | Purple (#7700BB) |
| Tools | Orange (#FF6600) |
| Methodologies | Gray (#666666) |

### Icon Classes

Bootstrap icons are available. Examples:
- `bi-code` — Code/programming
- `bi-brush` — Design
- `bi-database` — Database
- `bi-tools` — Tools
- `bi-rocket` — Launch/deployment

[Browse all Bootstrap icons](https://icons.getbootstrap.com/)

**Format**: Use the icon class name
- ✅ Correct: `bi-code` or `bi-code-slash`
- ❌ Wrong: `code` or `bi-code-icon`

---

## Managing Tags Programmatically

### Admin API

If you have Wagtail admin access, you can bulk update tags:

```python
# In Django shell: python manage.py shell

from pages.portfolio.models import PortfolioTag

# Deactivate all tags with "deprecated" in name
PortfolioTag.objects.filter(name__contains='deprecated').update(is_active=False)

# List all inactive tags
for tag in PortfolioTag.objects.filter(is_active=False):
    print(f"- {tag.name}")
```

### Tag Statistics

```python
# Count projects per tag
from pages.portfolio.models import PortfolioTag, Project

for tag in PortfolioTag.objects.filter(is_active=True):
    count = tag.project_set.filter(is_active=True).count()
    print(f"{tag.name}: {count} projects")
```

---

## FAQ

**Q: Can I restore a deleted tag?**
A: No. Always **deactivate** instead of deleting. Once deleted, the tag and its assignments are gone.

**Q: Can visitors see inactive tags?**
A: No. Inactive tags don't appear in filter dropdowns. But they still show in individual project detail pages if assigned.

**Q: Do tag changes affect SEO?**
A: Minimal. Tag names are in URLs (`?tags=react`) and page metadata, but not a major SEO factor.

**Q: How many tags is too many?**
A: More than 20 tags in the filter dropdown becomes cluttered. Archive unused ones annually.

**Q: Can I sort tags differently?**
A: Currently, tags are sorted alphabetically. Contact your administrator if you need custom ordering.

---

## Next Steps

- [Learn how tags filter projects](../architecture/request_flow.md#tag-filtering)
- [Understand the Wagtail admin](../user_guide/index.md)
- [Manage projects](./portfolio.md)
