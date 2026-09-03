---
Object type: Feature
Tags: pos, documentation, by-edition, by-component
Status: Published
---
# POS Documentation   
> Import Instruction: Create a Multi-select Property named "Tags" and add these options.   
> Apply to documentation objects for cross-cutting categorization.   

 --- 
## By Edition   
- `#pos-mini` — Lightweight Rust/Tauri desktop app (SQLite, offline-first)   
- `#pos-solo` — Single-branch Django/Robyn app (LAN sync, sidecar)   
- `#pos-full` — Enterprise Django + sidecar (multi-branch, cloud sync)   
- `#pos-cloud` — Cloud-hosted multi-tenant SaaS   
   
## By Component   
- `#frontend` — React/Next.js UI, Tailwind CSS, Framer Motion   
- `#backend` — Django, Rust, ORM, database logic   
- `#sidecar` — Robyn Python server, REST API, websocket   
- `#tauri` — Tauri desktop shell, Rust commands, native APIs   
- `#database` — SQLite, PostgreSQL, migrations, schema   
- `#sync` — Data sync (LAN, cloud, offline queues)   
   
## By Feature Area   
- `#sales` — POS checkout, cart, order management   
- `#inventory` — Stock, ingredients, recipes   
- `#analytics` — Dashboard, reports, charts   
- `#employees` — Staff management, payroll, schedule   
- `#customers` — CRM, loyalty, feedback   
- `#payments` — Payment processing, invoicing   
- `#kitchen` — Kitchen display system, tickets   
- `#auth` — Authentication, roles, permissions   
- `#i18n` — Internationalization, RTL, translations   
   
## By Theme   
- `#theme-default` — Default teal/indigo palette   
- `#theme-corporate` — Blue professional palette   
- `#theme-luxury` — Gold/warm premium palette   
- `#theme-pastel` — Soft candy colors   
- `#theme-perplexity` — Minimal & intelligent   
   
## By Status   
- `#complete` — Fully implemented and tested   
- `#in-progress` — Partially implemented   
- `#planned` — Design complete, not yet built   
- `#needs-review` — Requires verification   
## Related Docs
- → `../architecture/editions.md` — POS editions overview
- → `../features/_index.md` — Feature comparison across editions
- → `../objects/_tags.md` — Full tag definitions
