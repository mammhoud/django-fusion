#!/usr/bin/env node
/**
 * Generate the interactive ERD for the Formint POS database.
 *
 * Reads:
 *   - src-tauri/src/db/schema.rs   (diesel::table! + joinable! definitions)
 *   - src-tauri/src/operations/*.rs (operation module inventory, for the
 *     "operations logic" mapping attached to every entity)
 *
 * Writes:
 *   - docs/erd/erd-data.js    `window.ERD_DATA = {...}` consumed by index.html
 *   - docs/erd/erd.mmd        Mermaid ER diagram source (also inlined in README)
 *
 * Usage: node scripts/generate-erd.mjs
 */
import { readFileSync, writeFileSync, readdirSync, existsSync } from 'node:fs';
import { resolve, dirname, basename } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const SCHEMA_PATH = resolve(ROOT, 'src-tauri/src/db/schema.rs');
const OPERATIONS_DIR = resolve(ROOT, 'src-tauri/src/operations');
const OUT_DIR = resolve(ROOT, 'docs/erd');
const OUT_DATA = resolve(OUT_DIR, 'erd-data.js');
const OUT_MMD = resolve(OUT_DIR, 'erd.mmd');

/* ------------------------------------------------------------------ *
 * 1. Parse schema.rs — tables, columns, primary keys, joinables
 * ------------------------------------------------------------------ */

const schemaSrc = readFileSync(SCHEMA_PATH, 'utf8');

// diesel::table! { name (pk, ...) { col -> Type, ... } }
const TABLE_RE = /diesel::table!\s*\{\s*(\w+)\s*\(([^)]*)\)\s*\{([^}]*)\}\s*\}/g;

/** Map Diesel column types to SQL-ish display types. */
const SQL_TYPE = {
  Integer: 'INTEGER',
  Text: 'TEXT',
  Double: 'REAL',
  Bool: 'BOOLEAN',
  Timestamp: 'DATETIME',
  BigInt: 'INTEGER',
};

function parseType(raw) {
  const s = raw.trim().replace(/,+$/, '');
  const nullable = s.startsWith('Nullable<');
  const inner = nullable ? s.slice('Nullable<'.length, -1) : s;
  return {
    type: SQL_TYPE[inner] ?? inner.toUpperCase(),
    nullable,
  };
}

const entities = [];
for (const m of schemaSrc.matchAll(TABLE_RE)) {
  const name = m[1];
  const pks = m[2].split(',').map((s) => s.trim()).filter(Boolean);
  const columns = [];
  for (const line of m[3].split('\n')) {
    const cm = line.trim().match(/^(\w+)\s*->\s*(.+),?$/);
    if (!cm) continue;
    const { type, nullable } = parseType(cm[2]);
    columns.push({
      name: cm[1],
      type,
      nullable,
      pk: pks.includes(cm[1]),
    });
  }
  entities.push({ name, columns, primaryKeys: pks });
}

// diesel::joinable!(child -> parent (fk_col));
const joinables = [];
for (const m of schemaSrc.matchAll(/diesel::joinable!\((\w+)\s*->\s*(\w+)\s*\((\w+)\)\);/g)) {
  joinables.push({ child: m[1], parent: m[2], column: m[3] });
}

/* ------------------------------------------------------------------ *
 * 2. Operations inventory — module name -> exported functions
 * ------------------------------------------------------------------ */

const operations = {};
for (const f of readdirSync(OPERATIONS_DIR).filter((f) => f.endsWith('.rs'))) {
  const src = readFileSync(resolve(OPERATIONS_DIR, f), 'utf8');
  const funcs = [...src.matchAll(/pub fn (\w+)/g)].map((m) => m[1]);
  operations[basename(f, '.rs')] = funcs;
}

/* ------------------------------------------------------------------ *
 * 3. Hand-authored metadata — domains, operations mapping, logic notes
 * ------------------------------------------------------------------ */

/** Domain grouping used by the viewer and the diagram layout. */
const DOMAIN = {
  auth: 'Auth & Users',
  catalog: 'Catalog',
  sales: 'Sales & Orders',
  inventory: 'Inventory & Recipes',
  hr: 'HR & Payroll',
  finance: 'Finance & Tax',
  crm: 'CRM & Loyalty',
  ops: 'Operations & Sync',
};

/** Entity -> { domain, operations: [module], logic } */
const ENTITY_META = {
  users: {
    domain: 'auth',
    operations: ['auth', 'roles'],
    logic: 'Auth lifecycle: account setup, login/verify, password change & reset, superuser bootstrap. Roles join via user_roles for RBAC.',
  },
  roles: {
    domain: 'auth',
    operations: ['roles', 'permissions'],
    logic: 'RBAC: permission catalog (comma-separated flags in `permissions`), role CRUD with soft delete, assignment to users via user_roles.',
  },
  user_roles: {
    domain: 'auth',
    operations: ['roles'],
    logic: 'Join table between users and roles. `assign_role` / `remove_role` manage membership; `get_user_roles` lists a user\'s roles.',
  },
  user_actions: {
    domain: 'auth',
    operations: ['user_actions'],
    logic: 'Audit log. Every sale / coupon / offer action appends a row via `add_user_action`; queried by entity or globally.',
  },
  currencies: {
    domain: 'finance',
    operations: ['currency'],
    logic: 'Multi-currency support: full CRUD, one row flagged `is_default`. Exchange rates convert sale totals.',
  },
  settings: {
    domain: 'ops',
    operations: ['settings'],
    logic: 'Single-row restaurant configuration (branding, tax %, delivery fees, SMTP, thermal printer). `save_settings` upserts.',
  },
  categories: {
    domain: 'catalog',
    operations: ['categories'],
    logic: 'Product categories: plain CRUD with optional color for UI pills.',
  },
  products: {
    domain: 'catalog',
    operations: ['products'],
    logic: 'Product CRUD. `uploaded` flag drives offline→cloud sync via dump. Optional tax_profile_id selects the tax rate applied at sale.',
  },
  tax_profiles: {
    domain: 'finance',
    operations: ['tax_profile', 'tax'],
    logic: 'Named tax rates. Products and sales reference one profile; `compute_tax` applies rate per sale totals.',
  },
  delivery_types: {
    domain: 'catalog',
    operations: ['delivery_types'],
    logic: 'Delivery channel presets (fee multiplier). Soft delete via is_active.',
  },
  delivery_zones: {
    domain: 'catalog',
    operations: ['delivery_zones'],
    logic: 'Delivery zones with base fee, per-km fee and max distance; soft delete via is_active.',
  },
  sales: {
    domain: 'sales',
    operations: ['sales', 'transactions', 'analytics'],
    logic: 'Atomic insert: sale + sale_items in one transaction, then auto-creates a kitchen ticket with prep time by order type (dine-in 15, takeaway 20, delivery 25 min). `refund_sale` marks status=refunded (once only).',
  },
  sale_items: {
    domain: 'sales',
    operations: ['sales'],
    logic: 'Line items written atomically with the parent sale. `get_sale_with_items` loads sale + lines for receipts/KDS.',
  },
  coupons: {
    domain: 'sales',
    operations: ['coupons'],
    logic: 'Discount codes: kind (percent/flat), min_subtotal gate, `get_active_coupons` feeds the checkout; sales record the applied code.',
  },
  kitchen_tickets: {
    domain: 'sales',
    operations: ['kitchen_tickets', 'sales'],
    logic: 'KDS workflow: status transitions, priority, `count_pending_tickets`, and category resolution for filter pills. Auto-created by add_sale.',
  },
  shifts: {
    domain: 'ops',
    operations: ['shifts'],
    logic: 'Cash drawer lifecycle. `open_shift` refuses a second open shift; `close_shift` computes expected cash from cash sales in the shift window and the cash difference.',
  },
  customers: {
    domain: 'crm',
    operations: ['customers'],
    logic: 'Customer CRUD + loyalty balance. `add_loyalty_transaction` updates loyalty_points atomically with the transaction.',
  },
  loyalty_transactions: {
    domain: 'crm',
    operations: ['customers'],
    logic: 'Points ledger: signed points_change per sale; joined with customer name for the loyalty report.',
  },
  receipt_templates: {
    domain: 'crm',
    operations: ['notes'],
    logic: 'Recipe/kitchen "notes" stored here: templates with steps, per-recipe notes, default + selectable flags.',
  },
  ingredients: {
    domain: 'inventory',
    operations: ['ingredients'],
    logic: 'Stock item CRUD with reorder levels; soft delete via is_active; `uploaded` flag for sync. Stock is mutated by inventory_transactions, never directly.',
  },
  recipe_types: {
    domain: 'inventory',
    operations: ['recipes'],
    logic: 'Recipe classification (e.g. standard, bulk). Referenced by recipes; no standalone CRUD module — seeded and managed via migrations.',
  },
  recipes: {
    domain: 'inventory',
    operations: ['recipes'],
    logic: 'Recipe = product × recipe_type with yield. `create_recipe` inserts recipe + ingredients; soft delete; `uploaded` sync flag.',
  },
  recipe_ingredients: {
    domain: 'inventory',
    operations: ['recipes'],
    logic: 'Bill-of-materials lines: ingredient quantity per recipe, with preparation note and optional unit override.',
  },
  inventory_transactions: {
    domain: 'inventory',
    operations: ['inventory_transactions'],
    logic: 'Stock movements ledger (sale deduction, purchase receipt, adjustment). Rejects negative stock with InsufficientStockError + rollback.',
  },
  inventory_adjustments: {
    domain: 'inventory',
    operations: ['inventory_transactions'],
    logic: 'Manual count corrections storing previous→new quantity and reason. Deleting an adjustment reverses its stock delta.',
  },
  inventory_alerts: {
    domain: 'inventory',
    operations: [],
    logic: 'Low-stock alert records. No standalone operations module — rows are consumed by exports/dump for cloud sync.',
  },
  suppliers: {
    domain: 'inventory',
    operations: ['suppliers'],
    logic: 'Vendor CRUD with tax/payment terms; soft delete via is_active.',
  },
  purchase_orders: {
    domain: 'inventory',
    operations: ['purchase_orders'],
    logic: 'Procurement workflow: PO header (status, totals, expected date) plus items; receiving updates item quantities.',
  },
  purchase_order_items: {
    domain: 'inventory',
    operations: ['purchase_orders'],
    logic: 'PO lines: ingredient, ordered quantity, cost per unit, received quantity for partial receiving.',
  },
  employee_types: {
    domain: 'hr',
    operations: ['employee_types'],
    logic: 'Job-type presets (waiter, chef, …); soft delete via is_active.',
  },
  employees: {
    domain: 'hr',
    operations: ['employees'],
    logic: 'Employee records incl. payroll settings (salary vs hourly, bank details). Soft delete; `uploaded` sync flag.',
  },
  employee_schedules: {
    domain: 'hr',
    operations: ['employee_schedules'],
    logic: 'Shift scheduling: employee × shift window with status and notes.',
  },
  payrolls: {
    domain: 'hr',
    operations: ['payrolls'],
    logic: 'Payslips per period. `generate_payrolls` is idempotent: monthly → salary, hourly → rate × 160h, skips employees already covered.',
  },
  finance_transactions: {
    domain: 'finance',
    operations: ['finance'],
    logic: 'Income/expense ledger with direction + category; powers the finance summary (totals per category, budget vs actual).',
  },
  budgets: {
    domain: 'finance',
    operations: ['finance'],
    logic: 'Period budgets per category (or global); `get_finance_summary` computes spent/remaining/over.',
  },
  tax_reports: {
    domain: 'finance',
    operations: ['tax_reports'],
    logic: 'Periodic tax summaries (total sales, total tax, transaction count).',
  },
  report_metadata: {
    domain: 'finance',
    operations: ['reports'],
    logic: 'Generated report registry: type, format, file path, params, generating user.',
  },
  support_messages: {
    domain: 'ops',
    operations: ['support_messages'],
    logic: 'Support inbox: message CRUD with priority/status workflow.',
  },
  badges: {
    domain: 'crm',
    operations: ['badges'],
    logic: 'Customer reward badges with threshold, icon and tone.',
  },
  sync_queue: {
    domain: 'ops',
    operations: ['sync_queue', 'dispatcher', 'server_reconnect'],
    logic: 'Offline→cloud sync FIFO: `tag_for_sync` enqueues mutations, `dispatch_mutation` fans out, `mark_flushed`/`mark_failed` track retries, `flush_pending_sync` pushes on reconnect.',
  },
};

/** Logical FKs not covered by diesel::joinable! (still real relations). */
const LOGICAL_FKS = [
  { child: 'sale_items', parent: 'sales', column: 'sale_id' },
  { child: 'sales', parent: 'delivery_zones', column: 'delivery_zone_id' },
  { child: 'sales', parent: 'customers', column: 'customer_id' },
  { child: 'sales', parent: 'tax_profiles', column: 'tax_profile_id' },
  { child: 'products', parent: 'tax_profiles', column: 'tax_profile_id' },
  { child: 'receipt_templates', parent: 'recipes', column: 'recipe_id' },
  { child: 'user_actions', parent: 'users', column: 'user_id' },
];

const relations = [
  ...joinables.map((j) => ({ ...j, logical: false })),
  ...LOGICAL_FKS.map((j) => ({ ...j, logical: true })),
];

// Dedupe: the same (child, parent, column) can be declared twice (e.g. a
// joinable! plus a logical FK).
const seen = new Set();
const uniqueRelations = relations.filter((r) => {
  const key = `${r.child}|${r.parent}|${r.column}`;
  if (seen.has(key)) return false;
  seen.add(key);
  return true;
});

/* ------------------------------------------------------------------ *
 * 4. Assemble + emit
 * ------------------------------------------------------------------ */

const tableNames = new Set(entities.map((e) => e.name));

const entityOut = entities.map((e) => {
  const meta = ENTITY_META[e.name] ?? { domain: 'ops', operations: [], logic: '' };
  const fks = uniqueRelations
    .filter((r) => r.child === e.name)
    .map((r) => ({ column: r.column, ref: r.parent, logical: r.logical }));
  return {
    name: e.name,
    domain: meta.domain,
    domainLabel: DOMAIN[meta.domain],
    primaryKeys: e.primaryKeys,
    columns: e.columns,
    foreignKeys: fks,
    operations: (meta.operations ?? []).map((mod) => ({
      file: `operations/${mod}.rs`,
      module: mod,
      functions: operations[mod] ?? [],
    })),
    logic: meta.logic,
    hasOperations: (meta.operations ?? []).length > 0,
  };
});

const data = {
  generated: new Date().toISOString().slice(0, 10),
  source: 'src-tauri/src/db/schema.rs',
  entities: entityOut,
  relations: uniqueRelations.map((r) => ({ child: r.child, parent: r.parent, column: r.column, logical: r.logical })),
  domains: DOMAIN,
  stats: {
    tables: entityOut.length,
    relations: relations.length,
    operationsModules: Object.keys(operations).length,
  },
};

const dataJs = `// Generated by scripts/generate-erd.mjs — do not edit by hand.\n// Source: ${data.source} (${data.generated})\nwindow.ERD_DATA = ${JSON.stringify(data, null, 2)};\n`;

// Mermaid ER diagram
const mmd = [
  'erDiagram',
  ...entityOut.map((e) => {
    const cols = e.columns
      .map((c) => `        ${c.type}${c.nullable ? ' (nullable)' : ''} ${c.name}${c.pk ? ' PK' : ''}`)
      .join('\n');
    return `    ${e.name} {\n${cols}\n    }`;
  }),
  ...uniqueRelations.map((r) => `    ${r.parent} ||--o{ ${r.child} : "${r.column}"`),
].join('\n');

writeFileSync(OUT_DATA, dataJs);
writeFileSync(OUT_MMD, mmd + '\n');

// eslint-disable-next-line no-console
console.log(
  `✓ wrote ${OUT_DATA}\n✓ wrote ${OUT_MMD}\n  ${entityOut.length} entities, ${relations.length} relations, ${Object.keys(operations).length} operations modules`
);