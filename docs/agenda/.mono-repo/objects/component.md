---
# yaml-language-server: $schema=../schemas/page.schema.json
Object type: Component
Tags: component, ui
Status: Published
---

# Component — Reusable UI & Business Logic

> **Type:** Component 🔧
> **Layout:** Page
> **Description:** Reusable building blocks — buttons, cards, forms, navigation, data displays, and layout primitives from django-fusion and the POS frontend.

---

## Properties

| Property | Type | Options | Description |
|----------|------|---------|-------------|
| `Status` | Select | Stable, Beta, Deprecated, Experimental | Component maturity |
| `Category` | Select | UI, Form, Navigation, Data, Layout, Widget | Component category |
| `Framework` | Select | React, Django, Rust, Tailwind | Implementation framework |
| `Edition` | Relation → Edition | — | Which edition(s) include this |
| `Depends On` | Relation → Component | — | Component dependencies |
| `Related APIs` | Relation → API | — | Related API endpoints |
| `Related Styles` | Relation → Style | — | Design tokens used |
| `Related Features` | Relation → Feature | — | Related features |
| `Tags` | Multi-select | — | Cross-cutting labels |

---

## Component Categories

| Category | Examples |
|----------|----------|
| **UI** | Button, Card, Badge, Modal, Tooltip, Avatar |
| **Form** | Input, Select, Checkbox, DatePicker, FileUpload |
| **Navigation** | Sidebar, Navbar, Breadcrumb, Tabs, Pagination |
| **Data** | Table, List, Chart, Calendar, KanbanBoard |
| **Layout** | Grid, Container, Section, Sidebar, Header |
| **Widget** | Chat, Notifications, SearchBar, CommandPalette |

---

## Usage

A Feature uses a Component, which is styled by a Style and exposes an API.

| Relation | Target |
|----------|--------|
| uses | Component |
| styled by | Style |
| exposes | API |

---

## Related

- → `_object-types.md` — All type definitions
- → `api.md` — API entity
- → `style.md` — Style entity
- → `feature.md` — Feature entity
