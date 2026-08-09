# POS Page Data Map — Edition Comparison & Recommendations

> **Last Updated:** 9 August 2026  
> **Editions:** pos-mini, pos-solo, pos-full (historical)  
> **Purpose:** Map each page's data dependencies, actions, form submissions, and identify naming conflicts and enhancement opportunities.

> ⚠️ **Archived reference**: pos-solo and pos-full were merged into
> `formint-pos/` (their React UIs live under `formint-pos/legacy-react/`).
> This document is kept as a historical data-layer analysis.

---

## 1. Edition Overview

| Metric | pos-mini | pos-solo | pos-full |
|--------|:--------:|:--------:|:--------:|
| **Pages** | 23 | 25 | 25 |
| **Data layer** | Rust/Diesel (`invoke()`) | RTK Query + invoke (mixed) | RTK Query + invoke (mixed) |
| **Python sidecar** | ❌ | ✅ (port 8765) | ✅ (port 8766) |
| **Cloud sync** | ❌ | ✅ (child→master) | ✅ (master↔children) |
| **Admin panel** | ❌ | ❌ | ✅ (Unfold) |
| **WebSocket** | ❌ | ✅ /ws/config | ✅ /ws/entities + /ws/nodes |
| **Extra pages** | — | Notes | Notes |

**Key observation:** pos-solo and pos-full have identical page sets. The difference is backend capability (cloud sync, admin panel, WebSocket streams).

---

## 2. Page Inventory by Edition

### 2.1 Pages Present in All Editions (23 pages)

| # | Page | Route | Component |
|---|------|-------|-----------|
| 1 | Home | `/` | `Home.tsx` |
| 2 | Product Manager | `/manager` | `ProductManager.tsx` |
| 3 | Sale | `/sale` | `Sale.tsx` |
| 4 | Analytics | `/analytics` | `Analytics.tsx` |
| 5 | Transactions | `/transactions` | `Transactions.tsx` |
| 6 | Inventory | `/inventory` | `Inventory.tsx` |
| 7 | Employees | `/employees` | `Employees.tsx` |
| 8 | Recipes | `/recipes` | `Recipes.tsx` |
| 9 | Reports | `/reports` | `Reports.tsx` |
| 10 | Settings | `/settings` | `Settings.tsx` |
| 11 | About | `/about` | `About.tsx` |
| 12 | Customers | `/customers` | `Customers.tsx` |
| 13 | Suppliers | `/suppliers` | `Suppliers.tsx` |
| 14 | Kitchen Display | `/kitchen` | `KitchenDisplay.tsx` |
| 15 | Employee Schedule | `/schedule` | `EmployeeSchedule.tsx` |
| 16 | Payroll | `/payroll` | `Payroll.tsx` |
| 17 | Receipt Templates | `/receipt-templates` | `ReceiptTemplates.tsx` |
| 18 | Tax Reports | `/tax-reports` | `TaxReports.tsx` |
| 19 | Roles | `/roles` | `Roles.tsx` |
| 20 | Support Chat | `/support-chat` | `SupportChat.tsx` |
| 21 | Invoice | `/invoice` | `InvoicePage.tsx` |
| 22 | Auth | — (inline) | `Auth.tsx` |

### 2.2 Pages Unique to pos-solo / pos-full

| # | Page | Route | Component | Added |
|---|------|-------|-----------|-------|
| 24 | Notes | `/notes` | `Notes.tsx` | Now |

---

## 3. Detailed Page Data Map

### 3.1 HOME

| Aspect | Detail |
|--------|--------|
| **Route** | `/` |
| **Component** | `Home.tsx` |
| **Data loaded** | `Settings` (restaurant_name, logo) — via `invoke('get_settings')` (mini) or `useGetSettingsQuery` when migrated |
| **Actions** | Navigate to other pages via `handleNavigation(route)` |
| **Form submits** | None — pure navigation dashboard |
| **Data written** | None |
| **API pattern** | `invoke('get_settings')` (all editions) |
| **Naming issues** | `loadingRoute` state vs actual route param — slightly redundant pattern |

### 3.2 PRODUCT MANAGER

| Aspect | Detail |
|--------|--------|
| **Route** | `/manager` |
| **Component** | `ProductManager.tsx` |
| **Data loaded** | `Product[]`, `Category[]`, `Settings` |
| **Actions** | `useGetProductsQuery`, `useAddProductMutation`, `useUpdateProductMutation`, `useDeleteProductMutation` |
| **Form submits** | Add/Edit product form: name, price, sku, category_id, tax_rate, barcode, stock_quantity |
| **Data written** | `Product` entity |
| **API pattern** | RTK Query: `GET/POST/PATCH/DELETE /products` |
| **Conflict** | Product interface differs between `types.ts` (`Product`) and `endpoints/products.ts` (`Product`). `types.ts` has `price: number`, endpoints has `price: number` + `category: Category` relation. **Risk:** Response from API may have nested `category` object while page expects flat `category_id`. |

### 3.3 SALE

| Aspect | Detail |
|--------|--------|
| **Route** | `/sale` |
| **Component** | `Sale.tsx` |
| **Data loaded** | `Product[]`, `Category[]`, `Settings`, `Employee[]`, `DeliveryType[]` |
| **Actions** | `useAddSaleMutation` — creates sale with items |
| **Form submits** | Cart checkout: items, totals, payment method, employee, delivery info |
| **Data written** | `Sale` + `SaleItem` entities |
| **API pattern** | RTK Query: `POST /sales` |
| **Enhance** | No draft cart save/restore — user loses cart on page refresh. Could leverage the Notes feature for cart drafts. |

### 3.4 ANALYTICS

| Aspect | Detail |
|--------|--------|
| **Route** | `/analytics` |
| **Component** | `Analytics.tsx` |
| **Data loaded** | Analytics data — specific data shape depends on edition |
| **Actions** | Read-only display of KPI charts and metrics |
| **Form submits** | None |
| **Data written** | None |
| **API pattern** | `invoke()` or RTK Query |
| **Enhance** | Could use `useGetAnalyticsQuery` from legacy.ts for sidecar editions |

### 3.5 TRANSACTIONS

| Aspect | Detail |
|--------|--------|
| **Route** | `/transactions` |
| **Component** | `Transactions.tsx` |
| **Data loaded** | `Transaction[]` |
| **Actions** | `invoke('delete_transaction', { id })` (still invoke) |
| **Form submits** | Delete confirmation |
| **Data written** | Deletes Transaction |
| **API pattern** | `invoke()` — **should migrate to RTK Query** |
| **Naming conflict** | `types.ts` defines `Transaction` as sale-based with `items[]`, while sidecar `/sales` endpoint returns `Sale` with separate `SaleItem`. The `/transactions` endpoint in `routes/data.py` bridges this gap, but the field `total_amount` vs `total` mismatch exists. |

### 3.6 INVENTORY

| Aspect | Detail |
|--------|--------|
| **Route** | `/inventory` |
| **Component** | `Inventory.tsx` |
| **Data loaded** | `Ingredient[]`, `InventoryTransaction[]`, `InventoryAdjustment[]` |
| **Actions** | `useGetIngredientsQuery`, `useAddIngredientMutation`, `useUpdateIngredientMutation`, `useSoftDeleteIngredientMutation`, `useAddInventoryTransactionMutation` |
| **Form submits** | Add/edit ingredient form, add transaction form |
| **Data written** | `Ingredient`, `InventoryTransaction` |
| **API pattern** | RTK Query: legacy.ts + inventory.ts |
| **Conflict** | **Dual model problem**: The page uses the old `Ingredient` model (name, unit, current_quantity, reorder_level) while the sidecar has `Product` + `InventoryTransaction` (product-based stock). The `ingredients` endpoint path doesn't actually exist on the sidecar — it's mapped through legacy.ts to `/ingredients` which may 404. **Recommendation:** Migrate to product-based inventory or add Ingredient model to sidecar. |

### 3.7 EMPLOYEES

| Aspect | Detail |
|--------|--------|
| **Route** | `/employees` |
| **Component** | `Employees.tsx` |
| **Data loaded** | `Employee[]`, `EmployeeType[]` |
| **Actions** | `useGetEmployeesQuery`, `useAddEmployeeMutation`, `useUpdateEmployeeMutation`, `useSoftDeleteEmployeeMutation`, `useGetEmployeeTypesQuery`, `useAddEmployeeTypeMutation`, `useUpdateEmployeeTypeMutation`, `useSoftDeleteEmployeeTypeMutation` |
| **Form submits** | Add/edit employee form, add/edit employee type form |
| **Data written** | `Employee`, `EmployeeType` |
| **API pattern** | RTK Query: `/employees`, `/employee-types` |
| **Conflict** | **Employee model mismatch**: `types.ts` defines `Employee` with `name`, `phone`, `email`, `employee_type_id`, `salary`. Sidecar `models/pos.py` defines `Employee` with `first_name`, `last_name`, `role`, `hourly_rate`. These are completely different schemas. The RTK Query endpoint will return sidecar fields, but the page expects types.ts fields. **Critical:** `/employees` returns `first_name + last_name` but page displays `name`. |

### 3.8 RECIPES

| Aspect | Detail |
|--------|--------|
| **Route** | `/recipes` |
| **Component** | `Recipes.tsx` |
| **Data loaded** | `Recipe[]`, `RecipeIngredient[]`, `Product[]` |
| **Actions** | `invoke('create_recipe')`, `invoke('update_recipe')`, `invoke('add_recipe_ingredient')`, `invoke('delete_recipe_ingredient')`, `invoke('soft_delete_recipe')` |
| **Form submits** | Add/edit recipe form, add ingredient to recipe form |
| **Data written** | `Recipe`, `RecipeIngredient` |
| **API pattern** | `invoke()` — **should migrate to RTK Query** |
| **Enhance** | The `/recipes` endpoint exists in legacy.ts but the page still uses invoke. Recipe ingredients have no dedicated sidecar model. |

### 3.9 REPORTS

| Aspect | Detail |
|--------|--------|
| **Route** | `/reports` |
| **Component** | `Reports.tsx` |
| **Data loaded** | `Sale[]`, `Settings`, `AnalyticsData`, `Ingredient[]`, `InventoryTransaction[]`, `Recipe[]`, `Product[]`, `Employee[]`, `Transaction[]`, `DeliveryType[]` |
| **Actions** | Read-only — 10 RTK Query hooks |
| **Form submits** | None |
| **Data written** | PDF/CSV/Excel exports (client-side only) |
| **API pattern** | RTK Query: 10 hooks across core, products, sales, legacy endpoints |
| **Enhance** | **Heaviest data page** — loads 10 data sets on mount. Could benefit from lazy loading individual report tabs instead of loading all at once. |

### 3.10 SETTINGS

| Aspect | Detail |
|--------|--------|
| **Route** | `/settings` |
| **Component** | `Settings.tsx` |
| **Data loaded** | `Settings` |
| **Actions** | `invoke('save_settings')`, `invoke('import_database_cmd')`, `invoke('change_password_cmd')` |
| **Form submits** | Settings form (restaurant name, address, phone, email, tax_rate, currency, receipt_footer, logo), Database import, Password change |
| **Data written** | `Settings` |
| **API pattern** | `invoke()` — **should migrate**. RTK Query `useUpdateSettingsMutation` already exists in core.ts. |
| **Naming** | `Settings` type in `types.ts` has optional fields; sidecar `Settings` in `core.ts` endpoint has different shape. Import/export/password are Tauri-specific and can't migrate to HTTP. |

### 3.11 CUSTOMERS

| Aspect | Detail |
|--------|--------|
| **Route** | `/customers` |
| **Component** | `Customers.tsx` |
| **Data loaded** | `Customer[]` (paginated) |
| **Actions** | `useGetCustomersQuery`, `useAddCustomerMutation`, `useUpdateCustomerMutation`, `useDeleteCustomerMutation` |
| **Form submits** | Add/edit customer form (name, phone, email, notes) |
| **Data written** | `Customer` |
| **API pattern** | RTK Query: `/customers` |
| **Conflict** | `types.ts` `Customer` has `name`, `phone`, `email`, `loyalty_points`. Sidecar `models/pos.py` `Customer` has `first_name`, `last_name`, `phone`, `email`, `loyalty_points`. Same `name` vs `first_name`/`last_name` split issue as Employees. |

### 3.12 SUPPLIERS

| Aspect | Detail |
|--------|--------|
| **Route** | `/suppliers` |
| **Component** | `Suppliers.tsx` |
| **Data loaded** | `Supplier[]` |
| **Actions** | `invoke('add_supplier')`, `invoke('update_supplier')`, `invoke('soft_delete_supplier')` |
| **Form submits** | Add/edit supplier form |
| **Data written** | `Supplier` |
| **API pattern** | `invoke()` — **should migrate to RTK Query** (endpoint already exists in suppliers.ts) |

### 3.13 KITCHEN DISPLAY

| Aspect | Detail |
|--------|--------|
| **Route** | `/kitchen` |
| **Component** | `KitchenDisplay.tsx` |
| **Data loaded** | `KitchenTicket[]` |
| **Actions** | `invoke('update_kitchen_ticket', { id, update: { status } })` |
| **Form submits** | Status update (pending→preparing→ready→delivered) |
| **Data written** | `KitchenTicket.status` |
| **API pattern** | `invoke()` — endpoint exists in kitchen.ts as `useUpdateKitchenTicketMutation` |

### 3.14 EMPLOYEE SCHEDULE

| Aspect | Detail |
|--------|--------|
| **Route** | `/schedule` |
| **Component** | `EmployeeSchedule.tsx` |
| **Data loaded** | `EmployeeSchedule[]` |
| **Actions** | `invoke('add_employee_schedule')`, `invoke('delete_employee_schedule')` |
| **Form submits** | Add schedule form (employee, day, start_time, end_time) |
| **Data written** | `EmployeeSchedule` |
| **API pattern** | `invoke()` — endpoint exists in payroll.ts as `useGetEmployeeSchedulesQuery`, `useAddEmployeeScheduleMutation`, `useDeleteEmployeeScheduleMutation` |

### 3.15 PAYROLL

| Aspect | Detail |
|--------|--------|
| **Route** | `/payroll` |
| **Component** | `Payroll.tsx` |
| **Data loaded** | `Payroll[]` |
| **Actions** | `invoke('add_payroll')`, `invoke('delete_payroll')` |
| **Form submits** | Add payroll form |
| **Data written** | `Payroll` |
| **API pattern** | `invoke()` — endpoint exists in payroll.ts as `useGetPayrollRecordsQuery`, `useAddPayrollMutation`, `useDeletePayrollMutation` |

### 3.16 RECEIPT TEMPLATES

| Aspect | Detail |
|--------|--------|
| **Route** | `/receipt-templates` |
| **Component** | `ReceiptTemplates.tsx` |
| **Data loaded** | `ReceiptTemplate[]` |
| **Actions** | `invoke('add_receipt_template')`, `invoke('update_receipt_template')`, `invoke('delete_receipt_template')` |
| **Form submits** | Add/edit template form (name, template_body, is_default) |
| **Data written** | `ReceiptTemplate` |
| **API pattern** | `invoke()` — endpoint exists in receipts.ts |

### 3.17 TAX REPORTS

| Aspect | Detail |
|--------|--------|
| **Route** | `/tax-reports` |
| **Component** | `TaxReports.tsx` |
| **Data loaded** | `TaxReport[]` |
| **Actions** | `invoke('add_tax_report')`, `invoke('delete_tax_report')` |
| **Form submits** | Add report form |
| **Data written** | `TaxReport` |
| **API pattern** | `invoke()` — endpoint exists in payroll.ts |

### 3.18 ROLES

| Aspect | Detail |
|--------|--------|
| **Route** | `/roles` |
| **Component** | `Roles.tsx` |
| **Data loaded** | `Role[]` |
| **Actions** | `invoke('add_role')`, `invoke('update_role')`, `invoke('soft_delete_role')` |
| **Form submits** | Add/edit role form (name, permissions) |
| **Data written** | `Role` |
| **API pattern** | `invoke()` — endpoint exists in roles.ts (recently fixed to use 'Role' tag type) |

### 3.19 SUPPORT CHAT

| Aspect | Detail |
|--------|--------|
| **Route** | `/support-chat` |
| **Component** | `SupportChat.tsx` |
| **Data loaded** | Support tickets / chat messages |
| **Actions** | Submit support message |
| **Form submits** | Support form (name, email, subject, message) |
| **Data written** | `SupportTicket` |
| **API pattern** | Via sidecar or external |

### 3.20 INVOICE

| Aspect | Detail |
|--------|--------|
| **Route** | `/invoice` |
| **Component** | `InvoicePage.tsx` |
| **Data loaded** | Minimal (mostly local state) |
| **Actions** | Build invoice document, export to PDF |
| **Form submits** | Invoice builder form (type, items, customer, design) |
| **Data written** | PDF export (client-side) |
| **API pattern** | Client-side only (jsPDF) |

### 3.21 AUTH

| Aspect | Detail |
|--------|--------|
| **Route** | Inline (not a registered route) |
| **Component** | `Auth.tsx` |
| **Data loaded** | Auth state from AuthContext |
| **Actions** | Login, Register, Password reset |
| **Form submits** | Login form, Registration form, Password reset form |
| **Data written** | Auth token (localStorage + context) |
| **API pattern** | `invoke('check_auth_required')`, `invoke('has_users')`, `invoke('register')`, `invoke('login')` |

### 3.22 NOTES (NEW)

| Aspect | Detail |
|--------|--------|
| **Route** | `/notes` |
| **Component** | `Notes.tsx` |
| **Data loaded** | `Note[]` |
| **Actions** | `useGetNotesQuery`, `useAddNoteMutation`, `useUpdateNoteMutation`, `useDeleteNoteMutation` |
| **Form submits** | Note editor (title, content, status, reference_type, reference_id) |
| **Data written** | `Note` |
| **API pattern** | RTK Query: `/notes` |
| **Status** | ✅ Fully migrated — no invoke calls |

---

## 4. Data Layer Summary by Edition

### 4.1 pos-mini: Data Layer

| Access Pattern | Count | Pages |
|---------------|:-----:|-------|
| `invoke()` calls | All | Every page uses Tauri IPC to Rust/Diesel backend |
| RTK Query | 0 | No HTTP API available (no sidecar) |

**Limitations:** pos-mini has no sidecar. All data goes through Tauri invoke commands to Rust/Diesel. No HTTP REST, no WebSocket, no cloud sync.

### 4.2 pos-solo: Data Layer

| Access Pattern | Count | Pages |
|---------------|:-----:|-------|
| RTK Query (migrated) | 7 | Customers, ProductManager, Sale, Reports, Employees, Inventory, Notes |
| `invoke()` (not migrated) | 11 | Payroll, Settings, Suppliers, TaxReports, About, KitchenDisplay, Roles, EmployeeSchedule, Recipes, Transactions, ReceiptTemplates |
| Mixed | 0 | — |

**11 pages still use `invoke()`** — these need migration to RTK Query for consistency and browser-mode support.

### 4.3 pos-full: Data Layer

Identical to pos-solo (pages are copied). Backend has extra capabilities (cloud sync, admin panel, WebSocket streams).

---

## 5. Naming Conflicts & Issues

### 5.1 Model Schema Mismatches (Critical)

| Page | Frontend Type (`types.ts`) | Backend Model (`models/pos.py`) | Conflict |
|------|---------------------------|--------------------------------|----------|
| **Employees** | `{ name, phone, email, employee_type_id, salary, is_active }` | `{ first_name, last_name, role, hourly_rate, pin_code }` | **Complete mismatch** — name→first_name+last_name, role vs employee_type_id, hourly_rate vs salary |
| **Customers** | `{ name, phone, email, loyalty_points }` | `{ first_name, last_name, phone, email, loyalty_points, total_spent }` | name→first_name+last_name split |
| **Inventory** | `Ingredient { name, unit, current_quantity, reorder_level }` | `Product { name, price, stock_quantity }` + `InventoryTransaction` | Ingredient vs Product — completely different models |
| **Products** | `{ id, name, price, unit, category_id }` | `{ name, sku, price, cost_price, tax_rate, category FK }` | category_id vs nested category object in API response |

### 5.2 Field Name Conflicts

| Field | Frontend (`types.ts`) | Backend API Response | Issue |
|-------|----------------------|---------------------|-------|
| `total_amount` | Sale type, Transaction type | `total` (Sale model field) | `total_amount` vs `total` — Reports.tsx uses both |
| `order_type` | Sale, Transaction | No field — maps to `payment_method` | Handled in routes/data.py mapping |
| `quantity_change` | InventoryTransaction | `quantity` (int) | `quantity_change` in old model, `quantity` in new |
| `note` | InventoryTransaction | `notes` (text) | singular vs plural |
| `transaction_type` values | `'purchase'\|'usage'\|'waste'\|'adjustment'\|'return'` | `'in'\|'out'\|'adjustment'\|'return'\|'transfer_out'\|'transfer_in'\|'waste'\|'restock'` | Different enum values — `purchase`→`in`, `usage`→`out` |

### 5.3 Route Path Conflicts

| Frontend Route | Sidecar Path | Notes |
|---------------|-------------|-------|
| `/inventory` | `/inventory` (InventoryTransaction CRUD) + `/ingredients` (legacy) | Two different models at different paths |
| `/employees` | `/employees` (Employee CRUD) + `/employee-types` | Separate endpoints for types |
| `/transactions` | `/transactions` (in routes/data.py) + `/sales` (main CRUD) | Two paths for sale-based data |
| `/schedule` | `/employee-schedules` | Route `/schedule` maps to path `/employee-schedules` |

### 5.4 Naming Convention Issues

| Convention | Examples | Issue |
|-----------|----------|-------|
| Snake case vs camelCase | `total_amount` (API) vs `totalAmount` (JS) | Frontend types.ts uses both inconsistently |
| Plural endpoints | `/employees`, `/products`, `/sales` | Consistent ✅ |
| Singular params | `?include_inactive=true` vs `?page=1` | Some use snake_case, some use camelCase |
| Primary key names | `id` (all) vs `pk` (Robyn routes) | Robyn uses `:pk`, frontend sends `id` |

---

## 6. Action Classification

### 6.1 Data-Reading Pages (No Writes)

| Page | Data Sources | Type |
|------|-------------|------|
| Home | `Settings` (name, logo) | Dashboard |
| Analytics | Analytics aggregates | Dashboard |
| Reports | 10 data sets | Dashboard |
| Transactions | `Transaction[]` | List view |
| Kitchen Display | `KitchenTicket[]` | Real-time board |

### 6.2 CRUD Pages (Create/Read/Update/Delete)

| Page | Creates | Reads | Updates | Deletes |
|------|:-------:|:-----:|:-------:|:-------:|
| Product Manager | ✅ Products | ✅ Products | ✅ Products | ✅ Products |
| Customers | ✅ Customers | ✅ Customers | ✅ Customers | ✅ Customers |
| Employees | ✅ Employees | ✅ Employees | ✅ Employees | ✅ Employees (soft) |
| Suppliers | ✅ Suppliers | ✅ Suppliers | ✅ Suppliers | ✅ Suppliers (soft) |
| Roles | ✅ Roles | ✅ Roles | ✅ Roles | ✅ Roles (soft) |
| Receipt Templates | ✅ Templates | ✅ Templates | ✅ Templates | ✅ Templates |
| Notes | ✅ Notes | ✅ Notes | ✅ Notes | ✅ Notes |
| Inventory | ✅ Ingredients | ✅ Ingredients | ✅ Ingredients | ✅ Ingredients (soft) |

### 6.3 Action-Only Pages (Single Operation)

| Page | Single Action | Affects |
|------|--------------|---------|
| Sale | `POST /sales` (checkout) | `Sale`, `SaleItem` |
| Kitchen Display | `PATCH status` | `KitchenTicket.status` |
| Employee Schedule | `POST /employee-schedules` | `EmployeeSchedule` |
| Payroll | `POST /payroll` | `Payroll` |
| Tax Reports | `POST /tax-reports` | `TaxReport` |
| Settings | `PATCH /settings` + import/export | `Settings` + database file |

### 6.4 Anomalies

| Page | Issue |
|------|-------|
| **Recipes.tsx** | Single page does 3 different operations: recipe CRUD + ingredient linking + soft delete. Mixes `Recipe` and `RecipeIngredient` models. |
| **Settings.tsx** | Mixes RESTful settings update with Tauri-specific operations (database import/export, password change) that have no HTTP equivalent. |
| **About.tsx** | Sends support email via invoke — no HTTP equivalent. Requires Tauri shell plugin inbox. |

---

## 7. Enhancement Recommendations

### 7.1 Immediate (Low Effort, High Impact)

| # | Recommendation | Affected Pages | Effort | Impact |
|---|---------------|----------------|:------:|:------:|
| 1 | **Fix Employee model mismatch** — add computed `name` property or migrate frontend to `first_name`/`last_name`. **CRITICAL:** Backend returns `first_name`/`last_name` but frontend displays `name` — data is broken when accessed via sidecar. | Employees | Small | **Critical** — broken data |
| 2 | **Fix Customer model mismatch** — same `name`→`first_name`/`last_name` split as Employees | Customers | Small | **Critical** — broken data |
| 3 | **Migrate 11 invoke pages to RTK Query** — Payroll, Settings, Suppliers, TaxReports, About, KitchenDisplay, Roles, EmployeeSchedule, Recipes, Transactions, ReceiptTemplates | 11 pages | Medium | High — enables browser mode |
| 4 | **Add Ingredient model to sidecar** — or migrate Inventory page to Product-based stock | Inventory | Medium | High — fixes 404 on `/ingredients` |

### 7.2 Medium Term

| # | Recommendation | Rationale |
|---|---------------|-----------|
| 5 | **Lazy-load Reports tabs** — load only active tab's data instead of all 10 datasets at mount | Reduces initial load time significantly |
| 6 | **Unify field naming** — decide on snake_case (API) vs camelCase (JS) convention and apply consistently | Reduces mapping complexity |
| 7 | **Add cart draft save/restore to Sale page** — leverage Notes reference system so users can save cart state | UX improvement |
| 8 | **Remove duplicate `total_amount` vs `total` field usage** — pick one and use consistently across types.ts and endpoints | Reduces bugs |

### 7.3 Long Term

| # | Recommendation | Rationale |
|---|---------------|-----------|
| 9 | **Extract shared page patterns** — consolidate CRUD list/detail/edit into reusable components | Reduces code duplication across 24 pages |
| 10 | **Add pagination to all list endpoints** — current implementation loads all records for many entities | Performance for large datasets |
| 11 | **Add real-time WebSocket updates to all entity pages** — currently only sync/nodes have WS | Real-time multi-device consistency |
| 12 | **Separate Tauri-specific operations from RESTful ones** in Settings page | Enables browser-only deployment without Tauri |

---

## 8. Data Model Standardization Plan

### 8.1 Proposed Unified Field Names

| Current (`types.ts`) | Proposed Standard | Example Values |
|---------------------|-------------------|----------------|
| `name` (Person) | `first_name` + `last_name` | Employee, Customer |
| `total_amount` | `total` | Sale, Transaction |
| `quantity_change` | `quantity` | InventoryTransaction |
| `note` | `notes` | All models |
| `order_type` | `order_type` (keep) | Sale, Transaction |
| `transaction_type` | `transaction_type` (unify enum values) | InventoryTransaction |

### 8.2 Enum Value Standardization

| Context | Current Values | Proposed Standard |
|---------|---------------|------------------|
| Inventory tx types | `purchase/usage/waste/adjustment/return` (frontend) vs `in/out/adjustment/return/waste/restock` (backend) | `addition, removal, adjustment, transfer, waste, restock` |
| Sale status | `pending/completed/refunded/cancelled` | Keep — already consistent |
| Employee roles | `cashier/server/manager/admin/kitchen` (backend) vs `Waiter/Cashier/Chef/Manager/Driver/Cleaner` (frontend colors) | Align enum values with UI labels |

---

## 9. Sidecar API Coverage Gap

| Frontend Endpoint File | Paths | Sidecar Status |
|-----------------------|-------|:--------------:|
| `products.ts` | `/products` | ✅ CRUD via `_register_crud` |
| `customers.ts` | `/customers` | ✅ CRUD via `_register_crud` |
| `sales.ts` | `/sales` | ✅ CRUD via `_register_crud` |
| `core.ts` | `/categories`, `/settings`, `/employees`, `/delivery-types` | ✅ Categories/Employees via CRUD, Settings via CRUD |
| `inventory.ts` | `/inventory`, `/reports/inventory/count`, `/reports/inventory/transfer` | ✅ Inventory CRUD + reports routes |
| `suppliers.ts` | `/suppliers`, `/purchase-orders` | ✅ CRUD via `_register_crud` |
| `kitchen.ts` | `/kitchen-tickets`, `/recipes`, `/transactions` | ✅ Kitchen CRUD, transactions via data.py |
| `payroll.ts` | `/payroll`, `/tax-reports`, `/employee-schedules` | ✅ HR models added + CRUD |
| `receipts.ts` | `/receipt-templates` | ⬜ **Missing** — no ReceiptTemplate model on sidecar |
| `analytics.ts` | `/reports/sales`, `/reports/sales/cashback`, `/reports/inventory/count` | ✅ Reports routes |
| `roles.ts` | `/roles` | ⬜ **Missing** — no Role model on sidecar |
| `legacy.ts` | `/ingredients`, `/employee-types`, `/recipes`, `/analytics`, `/transactions` | ✅ EmployeeTypes via HR models, Analytics/Transactions via data.py. ⬜ **Ingredients and Recipes missing** |
| `notes.ts` | `/notes` | ✅ Note model added + CRUD |

**Missing sidecar routes:**
1. `/ingredients` — no Ingredient model (frontend expects it for Inventory page). **Recommendation:** Add Ingredient model to sidecar or create a data-derivation route from `Product` + `InventoryTransaction` (similar to how `routes/data.py` derives `/transactions` from `Sale`).
2. `/recipes` — no Recipe model (frontend expects it for Recipes/Reports pages). **Recommendation:** Create a thin Recipe model (id, product_id, yield_quantity, is_active) or a data-derivation route.
3. `/receipt-templates` — no ReceiptTemplate model
4. `/roles` — no Role model
5. `/inventory-adjustments` — no InventoryAdjustment model

---

## 10. Data Flow Diagram by Edition

```
pos-mini:
  React → invoke() → Rust/Diesel → SQLite
  (no HTTP, no sidecar, fully offline)

pos-solo:
  React → RTK Query → HTTP → Robyn (port 8765) → Django ORM → SQLite
  React → invoke() → Rust/Diesel → SQLite (legacy pages only)
  WebSocket: /ws/config

pos-full:
  React → RTK Query → HTTP → Robyn (port 8766) → Django ORM → SQLite
  React → invoke() → Rust/Diesel → SQLite (legacy pages only)
  WebSocket: /ws/entities, /ws/nodes, /ws/config
  Admin: Django Unfold (port 8000) → Django ORM → SQLite
  Cloud: Sync Engine → External CRM/Cloud
```

---

## 11. Quick Reference: Action→Data Flow per Page

| Page | Read Entities | Write Entities | Form Submit | Export |
|------|:------------:|:--------------:|:-----------:|:------:|
| Home | Settings | — | — | — |
| ProductManager | Product, Category, Settings | Product | ✅ Add/Edit | — |
| Sale | Product, Category, Settings, Employee, DeliveryType | Sale, SaleItem | ✅ Checkout | Receipt |
| Analytics | AnalyticsData | — | — | — |
| Transactions | Transaction | Transaction (delete) | ✅ Delete | — |
| Inventory | Ingredient, InventoryTransaction, Adjustment | Ingredient, InventoryTransaction | ✅ Add/Edit/Transaction | — |
| Employees | Employee, EmployeeType | Employee, EmployeeType | ✅ Add/Edit/Type | — |
| Recipes | Recipe, Product | Recipe, RecipeIngredient | ✅ Add/Edit/Ingredient | — |
| Reports | 10 entities | — | — | ✅ PDF/CSV/Excel |
| Settings | Settings | Settings, DB file | ✅ Settings/Import/Password | — |
| Customers | Customer | Customer | ✅ Add/Edit | — |
| Suppliers | Supplier | Supplier | ✅ Add/Edit | — |
| KitchenDisplay | KitchenTicket | KitchenTicket (status) | ✅ Status update | — |
| EmployeeSchedule | EmployeeSchedule | EmployeeSchedule | ✅ Add | — |
| Payroll | Payroll | Payroll | ✅ Add | — |
| ReceiptTemplates | ReceiptTemplate | ReceiptTemplate | ✅ Add/Edit | — |
| TaxReports | TaxReport | TaxReport | ✅ Add | — |
| Roles | Role | Role | ✅ Add/Edit | — |
| SupportChat | SupportTicket | SupportTicket | ✅ Submit | — |
| Invoice | — | — | ✅ Build | ✅ PDF |
| Notes | Note | Note | ✅ Add/Edit/Draft | — |
