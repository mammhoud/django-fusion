---
# yaml-language-server: $schema=schemas/page.schema.json
Object type:
    - Page
Creation date: "2026-07-24T19:54:39Z"
Created by:
    - mammhoud
id: bafyreidjmy6bqls7iykmucbtgqxjlbedna7ig4m5vjdjlqqztiahdch5h4
---
# POS System   
**Type:** Guide 📘
T**ags: **#`pos-mini `#`pos-solo `#`pos-full `#`pos-cloud
`S**tatus: **Published   
 --- 
## Organization   
```
anytype/
├── _object-types.md      ── Custom type definitions for AnyType import
├── _tags.md               ── Multi-select tag definitions
├── _relations.md          ── Object relation/linking guide
├── architecture/          ── System architecture 🏗️
│   ├── editions-overview.md     — Edition comparison + stack
│   ├── sync-architecture.md     — 3-tier sync model
│   ├── role-system.md           — Role & permission design
│   └── theme-system.md          — Theme variant system
├── features/              ── Feature descriptions ✨
│   ├── comparison-matrix.md     — Full feature grid
│   ├── pos-mini.md              — Rust/Tauri edition
│   ├── pos-solo.md              — Django + Robyn edition
│   └── pos-full.md              — Cloud-enabled edition
├── guides/                ── Step-by-step guides 📘
│   ├── setup.md                 — Setup & quick start
│   ├── development.md           — Development workflow
│   └── theming.md               — Theme customization
├── references/            ── API & config references 📚
│   ├── sidecar-api.md           — Robyn sidecar endpoints
│   ├── tauri-commands.md        — Tauri Rust commands
│   └── i18n-keys.md             — Translation key reference
├── changelogs/            ── Version history 📋
│   └── pos.md                   — POS changelog
└── diagrams/              ── (Future) Mermaid/ASCII diagrams 📊

```
 --- 
## Import to AnyType   
### Step 1: Create Object Types   
Open AnyType → Settings → Content Model → Add Type. Create the 7 types from `\_object-types.md`.   
### Step 2: Create Properties   
For each type, add the properties listed in `\_object-types.md`.
Create a shared "Tags" Multi-select property from `\_tags.md`.   
### Step 3: Import Markdown   
Use AnyType's Markdown import feature for each file.
Assign the correct Type to each document after import.   
### Step 4: Link Objects   
For the `Related Docs` sections, create Object Relations:   
- Open the target document   
- Add the relation property   
- Link back to the source   
   
### Step 5: Graph View   
Open Graph View to see all connections.
Use filters by Type, Tags, or Edition to focus.   
 --- 
## Style Guide   
- **Minimal code** — Show method signatures + `→` return types, not full implementations   
- **ASCII diagrams** — Use box-drawing characters for flow diagrams   
- **Tables** — Compact comparison tables   
- **Related links** — Always end with `→` cross-references   
- **Frontmatter** — Type, Tags, Status, Edition at top   
[POS System](pos-system.md)    
