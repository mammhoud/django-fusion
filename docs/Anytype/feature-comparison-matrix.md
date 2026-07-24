---
# yaml-language-server: $schema=schemas/page.schema.json
Object type:
    - Page
Creation date: "2026-07-24T19:54:39Z"
Created by:
    - mammhoud
id: bafyreieqtzumb4kurtwsqidavclpzqd5fpa6shonl4bwluzeynhlcio6mm
---
# Feature Comparison Matrix   
**Type:** Feature ✨
**Tags:** `#pos-mini` `#pos-solo` `#pos-full` `#pos-cloud`
**Status:** Published   
 --- 
## Feature Grid   
|                 Feature   <br> |    pos-mini   <br> |     pos-solo   <br> |          pos-full   <br> |   pos-cloud   <br> |
|:-------------------------------|:-------------------|:--------------------|:-------------------------|:-------------------|
|         **Sales (POS)**   <br> |           ✅   <br> |            ✅   <br> |                 ✅   <br> |           ✅   <br> |
|     **Cart + Checkout**   <br> |           ✅   <br> |            ✅   <br> |                 ✅   <br> |           ✅   <br> |
|     **Product Manager**   <br> |           ✅   <br> |            ✅   <br> |                 ✅   <br> |           ✅   <br> |
|          **Categories**   <br> |           ✅   <br> |            ✅   <br> |                 ✅   <br> |           ✅   <br> |
|           **Inventory**   <br> |           ✅   <br> |            ✅   <br> |                 ✅   <br> |           ✅   <br> |
|             **Recipes**   <br> |           ✅   <br> |            ✅   <br> |                 ✅   <br> |           ✅   <br> |
| **Analytics Dashboard**   <br> |           ✅   <br> |            ✅   <br> |                 ✅   <br> |           ✅   <br> |
| **Transaction History**   <br> |           ✅   <br> |            ✅   <br> |                 ✅   <br> |           ✅   <br> |
|            **Invoices**   <br> |           ✅   <br> |            ✅   <br> |                 ✅   <br> |           ✅   <br> |
|             **Reports**   <br> |           ✅   <br> |            ✅   <br> |                 ✅   <br> |           ✅   <br> |
|    **Employee Manager**   <br> |           ✅   <br> |            ✅   <br> |                 ✅   <br> |           ✅   <br> |
|             **Payroll**   <br> |           ✅   <br> |            ✅   <br> |                 ✅   <br> |           ✅   <br> |
|            **Schedule**   <br> |           ✅   <br> |            ✅   <br> |                 ✅   <br> |           ✅   <br> |
|     **Kitchen Display**   <br> |           ✅   <br> |            ✅   <br> |                 ✅   <br> |           ✅   <br> |
|    **Customer Manager**   <br> |           ✅   <br> |            ✅   <br> |                 ✅   <br> |           ✅   <br> |
|    **Supplier Manager**   <br> |           ✅   <br> |            ✅   <br> |                 ✅   <br> |           ✅   <br> |
|   **Receipt Templates**   <br> |           ✅   <br> |            ✅   <br> |                 ✅   <br> |           —   <br> |
|         **Tax Reports**   <br> |           ✅   <br> |            ✅   <br> |                 ✅   <br> |           ✅   <br> |
| **Roles & Permissions**   <br> |    ✅ (Rust)   <br> |   ✅ (Django)   <br> |        ✅ (Django)   <br> |   ✅ (Admin)   <br> |
|                **Auth**   <br> |   ✅ (Local)   <br> |    ✅ (Local)   <br> |         ✅ (Local)   <br> |     ✅ (SSO)   <br> |
|  **i18n (5 languages)**   <br> |           ✅   <br> |            ✅   <br> |                 ✅   <br> |           ✅   <br> |
|        **Theme System**   <br> |     ✅ (Bio)   <br> |      ✅ (Bio)   <br> |           ✅ (Bio)   <br> |           —   <br> |
|         **RTL Support**   <br> |           ✅   <br> |            ✅   <br> |                 ✅   <br> |           ✅   <br> |
|        **Offline Mode**   <br> |    ✅ Always   <br> |    ✅ Partial   <br> |         ✅ Partial   <br> |           ❌   <br> |
|            **LAN Sync**   <br> |           ❌   <br> |     ✅ Branch   <br> |          ✅ Branch   <br> |           ❌   <br> |
|          **Cloud Sync**   <br> |           ❌   <br> |            ❌   <br> |                 ✅   <br> |    ✅ Native   <br> |
|        **Multi-branch**   <br> |           ❌   <br> |       Single   <br> |                 ✅   <br> |           ✅   <br> |
|     **Admin Dashboard**   <br> |           ❌   <br> |    ✅ Sidecar   <br> |   ✅ Sidecar+Cloud   <br> |    ✅ Native   <br> |
|  **Export (PDF/Excel)**   <br> |           ✅   <br> |            ✅   <br> |                 ✅   <br> |           ✅   <br> |
|  **Keyboard Shortcuts**   <br> |           ✅   <br> |            ✅   <br> |                 ✅   <br> |           ✅   <br> |
|        **PDF Receipts**   <br> |           ✅   <br> |            ✅   <br> |                 ✅   <br> |           ✅   <br> |
|      **Print Receipts**   <br> |           ✅   <br> |            ✅   <br> |                 ✅   <br> |           ✅   <br> |

 --- 
## Edition-Specific Strengths   
```
pos-mini ──→ Lightest, fastest, fully offline, no dependencies
pos-solo ──→ Branch sync, sidecar dashboard, Django ORM
pos-full ──→ Cloud sync, enterprise features, admin panel
pos-cloud ─→ Multi-tenant, subscription, web-first

```
 --- 
## Technology Stack   
|    Component   <br> |        pos-mini   <br> |        pos-solo   <br> |        pos-full   <br> |     pos-cloud   <br> |
|:--------------------|:-----------------------|:-----------------------|:-----------------------|:---------------------|
| **Frontend**   <br> |   React 19 + TS   <br> |   React 19 + TS   <br> |   React 19 + TS   <br> |    Next.js 15   <br> |
|  **Desktop**   <br> | Tauri v2 + Rust   <br> |        Tauri v2   <br> |        Tauri v2   <br> |             —   <br> |
|  **Backend**   <br> |    Rust (Tauri)   <br> |  Django + Robyn   <br> |  Django + Robyn   <br> |  Django + DRF   <br> |
| **Database**   <br> |          SQLite   <br> |          SQLite   <br> |          SQLite   <br> |    PostgreSQL   <br> |
|     **Sync**   <br> |               —   <br> |     LAN (Robyn)   <br> |      REST + WSS   <br> |    REST + WSS   <br> |
|    **State**   <br> | Zustand + React   <br> | Zustand + React   <br> | Zustand + React   <br> | Redux + React   <br> |

 --- 
## Related Docs   
- → `architecture/editions-overview.md` — High-level edition comparison   
- → `features/pos-mini.md` — pos-mini feature details   
- → `features/pos-solo.md` — pos-solo feature details   
- → `features/pos-full.md` — pos-full feature details   
[Feature Comparison Matrix](feature-comparison-matrix.md)    
