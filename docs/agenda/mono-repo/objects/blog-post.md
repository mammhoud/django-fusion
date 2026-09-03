---
# yaml-language-server: $schema=../schemas/page.schema.json
Object type: Blog/Post
Tags: blog
Status: Published
---

# Blog/Post — Articles, Tutorials & Announcements

> **Type:** Blog/Post 📝
> **Layout:** Page
> **Description:** Published content — tutorials, case studies, announcements, and technical articles documenting progress and product updates.

---

## Properties

| Property | Type | Options | Description |
|----------|------|---------|-------------|
| `Status` | Select | Draft, Published, Scheduled, Archived | Publication workflow status |
| `Author` | Relation → Person | — | Content creator/author |
| `Published Date` | Date | — | When the post was published |
| `Category` | Select | Announcement, Tutorial, Case Study, Update, Technical | Content category |
| `Tags` | Multi-select | — | Cross-cutting labels |
| `Featured Image` | Media | — | Hero/header image |
| `Excerpt` | Text | — | Short description for previews |
| `Related Features` | Relation → Feature | — | Featured product/capability |
| `Related Guides` | Relation → Guide | — | Related how-to guides |
| `Related Goals` | Relation → Goal | — | Strategic goals this post supports |
| `Related Releases` | Relation → Release | — | Release this post announces |
| `Related Editions` | Relation → Edition | — | Product edition context |

---

## Usage in Knowledge Graph

| Relation | Target |
|----------|--------|
| Author | Person |
| Related Features | Feature |
| Related Guides | Guide |
| Related Goals | Goal |
| Related Releases | Release |
| Related Editions | Edition |

---

## Related

- → `_object-types.md` — All type definitions
- → `_relations.md` — Relations guide
- → `_tags.md` — Tag definitions
- → `../blog/_index.md` — Blog directory
