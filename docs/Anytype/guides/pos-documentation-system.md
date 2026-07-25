---
# yaml-language-server: $schema=schemas/page.schema.json
Object type:
    - Page
Creation date: "2026-07-24T19:54:39Z"
Created by:
    - mammhoud
id: bafyreidimj67mcbykrsgxpj2qx6sqqjpy7sdoprkznpqg2ghu6txcpawhm
---
# POS Documentation System   
> Import Instruction: Create these custom Types in AnyType (Settings → Content Model → Add Type).   
> Assign each doc to its type, then use Properties + Relations to link them.   

 --- 
## Type: Architecture 🏗️   
**Description:** System architecture, data flow, and high-level design documents
**Layout:** Page
**Properties:**   
- `Status` (Select) → Draft \| Review \| Published   
- `Edition` (Multi-select) → Mini \| Solo \| Full \| Cloud   
- `Version` (Text)   
- `Related Features` (Relation → Feature)   
- `Related Guides` (Relation → Guide)   
   
**Files:** `architecture/\*.md`   
 --- 
## Type: Feature ✨   
**Description:** Feature descriptions, capabilities, and edition-specific implementations
**Layout:** Page
**Properties:**   
- `Status` (Select) → Planned \| In Development \| Complete   
- `Edition` (Multi-select) → Mini \| Solo \| Full \| Cloud   
- `Priority` (Select) → Low \| Medium \| High \| Critical   
- `Tags` (Multi-select)   
- `Depends On` (Relation → Feature)   
- `Implementation` (Relation → Guide)   
   
**Files:** `features/\*.md`   
 --- 
## Type: Guide 📘   
**Description:** Step-by-step guides for setup, development, deployment, customization
**Layout:** Page
**Properties:**   
- `Status` (Select) → Draft \| Review \| Published   
- `Category` (Select) → Setup \| Development \| Deployment \| Theming \| Testing   
- `Target Audience` (Select) → Developer \| Admin \| End User   
- `Prerequisites` (Relation → Guide)   
- `Related Architecture` (Relation → Architecture)   
   
**Files:** `guides/\*.md`   
 --- 
## Type: Reference 📚   
**Description:** API endpoints, command references, configuration schemas
**Layout:** Page
**Properties:**   
- `Category` (Select) → API \| CLI \| Database \| Config \| i18n   
- `Edition` (Multi-select) → Mini \| Solo \| Full \| Cloud   
- `Version` (Text)   
- `Related Architecture` (Relation → Architecture)   
   
**Files:** `references/\*.md`   
 --- 
## Type: Changelog 📋   
**Description:** Version history, migration notes, breaking changes
**Layout:** Page
**Properties:**   
- `Version` (Text, required)   
- `Date` (Date)   
- `Edition` (Multi-select) → Mini \| Solo \| Full \| Cloud   
- `Type` (Select) → Major \| Minor \| Patch \| Breaking   
- `Related Features` (Relation → Feature)   
   
**Files:** `changelogs/\*.md`   
 --- 
## Type: Diagram 📊   
**Description:** ASCII / Mermaid diagrams for visual understanding
**Layout:** Page
**Properties:**   
- `Type` (Select) → Flow \| Architecture \| Sequence \| Data Model   
- `Edition` (Multi-select) → Mini \| Solo \| Full \| Cloud   
- `Related Docs` (Relation → Architecture \| Reference \| Guide)   
   
**Files:** Embedded within other types or standalone in `diagrams/`   
 --- 
## Type: Task ✅   
**Description:** Implementation tasks, TODOs, enhancement plans
**Layout:** Task
**Properties:**   
- `Status` (Select) → Backlog \| In Progress \| Done \| Blocked   
- `Priority` (Select) → Low \| Medium \| High \| Critical   
- `Edition` (Multi-select) → Mini \| Solo \| Full \| Cloud   
- `Assignee` (Relation → Person)   
- `Depends On` (Relation → Task)   
   
**Files:** `tasks/\*.md`   
 --- 
## Import Checklist   
1. Create all 7 Types above in AnyType Content Model   
2. Create the Tags from `\_tags.md` as Multi-select property options   
3. Import markdown files using AnyType's Markdown import   
4. Assign each file to its Type   
5. Link related objects using Relations   
6. Use Graph View to visualize connections   
[POS Documentation System](pos-documentation-system.md)    
