import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { describe, expect, it } from 'vitest';

const root = dirname(fileURLToPath(import.meta.url));
const read = (p: string) => readFileSync(join(root, '..', 'pages', p), 'utf8');

/**
 * Contract tests for the create/edit modals added to the Formint Pro
 * "Add … coming soon" pages. Each modal must POST the serializer's writable
 * payload to the collection endpoint, PUT to the detail endpoint on edit,
 * and DELETE by id — mirroring the /api/v1 model controllers
 * (ModelControllerBase in server/formint/controllers.py) the Astro dev
 * proxy forwards to.
 */
describe('Formint Pro create/edit modal contracts', () => {
  it('suppliers modal POSTs the SupplierOut writable fields to /suppliers/', () => {
    const page = read('pos/suppliers/index.astro');
    expect(page).toContain("fetch('/suppliers/', { method: 'POST'");
    for (const key of ['name', 'contact_name', 'phone', 'email', 'address', 'tax_id', 'payment_terms', 'is_active']) {
      expect(page).toMatch(new RegExp(`\\b${key}:\\s*this\\.form\\.${key}\\b`));
    }
    expect(page).toContain("fetch('/suppliers/' + this.editingItem.id + '/', { method: 'PUT'");
    expect(page).toContain("fetch('/suppliers/' + id + '/', { method: 'DELETE'");
  });

  it('roles modal POSTs name/description/permissions/is_active to /roles/', () => {
    const page = read('hr/roles/index.astro');
    expect(page).toContain("fetch('/roles/', { method: 'POST'");
    expect(page).toContain('const p = { name: this.form.name, description: this.form.description, permissions, is_active: this.form.is_active }');
    expect(page).toContain("fetch('/roles/' + this.editingItem.id + '/', { method: 'PUT'");
    expect(page).toContain("fetch('/roles/' + id + '/', { method: 'DELETE'");
  });

  it('schedules modal POSTs EmployeeScheduleOut writable fields to /employee-schedules/', () => {
    const page = read('hr/schedules/index.astro');
    expect(page).toContain("fetch('/employee-schedules/', { method: 'POST'");
    const p = 'const p = { employee: this.form.employee, day_of_week: this.form.day_of_week, start_time: this.form.start_time, end_time: this.form.end_time, status: this.form.status, notes: this.form.notes }';
    expect(page).toContain(p);
    expect(page).toContain("fetch('/employee-schedules/' + this.editingItem.id + '/', { method: 'PUT'");
    expect(page).toContain("fetch('/employee-schedules/' + id + '/', { method: 'DELETE'");
    // list table binds to real serializer fields, with id→name resolution
    expect(page).toContain('empName(item.employee)');
    expect(page).toContain('item.day_of_week');
  });

  it('payroll modal POSTs computed payroll payload (incl. net_pay) to /payroll/', () => {
    const page = read('hr/payroll/index.astro');
    expect(page).toContain("fetch('/payroll/', { method: 'POST'");
    for (const key of ['employee', 'period_start', 'period_end', 'status', 'regular_hours', 'overtime_hours', 'base_salary', 'bonuses', 'deductions', 'net_pay', 'notes']) {
      // accepts both `key: value` and shorthand `key,` object entries
      expect(page).toMatch(new RegExp(`\\b${key}(,|:|\\s*=)`));
    }
    // net pay is auto-computed client side from base + bonuses - deductions
    expect(page).toContain('const net_pay = Math.max(0, Math.round((base + bonuses - deductions) * 100) / 100)');
    expect(page).toContain("fetch('/payroll/' + this.editingItem.id + '/', { method: 'PUT'");
    expect(page).toContain("fetch('/payroll/' + id + '/', { method: 'DELETE'");
    expect(page).toContain('empName(item.employee)');
  });

  it('admin notes modal POSTs NoteOut writable fields to /notes/', () => {
    const page = read('admin/notes/index.astro');
    expect(page).toContain("fetch('/notes/', { method: 'POST'");
    for (const key of ['title', 'content', 'status', 'reference_type', 'reference_id', 'created_by']) {
      expect(page).toMatch(new RegExp(`\\b${key}:`));
    }
    expect(page).toContain("fetch('/notes/' + this.editingItem.id + '/', { method: 'PUT'");
    expect(page).toContain("fetch('/notes/' + id + '/', { method: 'DELETE'");
  });

  it('recipes/ingredients modals POST to /recipes/ and /ingredients/ with model fields', () => {
    const page = read('kitchen/recipes/index.astro');
    // recipe payload
    expect(page).toContain("fetch(base, { method: 'POST'"); // shared create path
    expect(page).toContain("const base = this.kind === 'recipes' ? '/recipes/' : '/ingredients/';");
    expect(page).toContain('p = { product: this.form.product, name: this.form.name, instructions: this.form.instructions, yield_quantity: parseFloat(String(this.form.yield_quantity)) || 1, is_active: this.form.is_active }');
    expect(page).toContain('p = { name: this.form.name, unit: this.form.unit, current_quantity: parseFloat(String(this.form.current_quantity)) || 0, reorder_level: parseFloat(String(this.form.reorder_level)) || 0, reorder_quantity: parseFloat(String(this.form.reorder_quantity)) || 0, cost_per_unit: parseFloat(String(this.form.cost_per_unit)) || 0, is_active: this.form.is_active }');
    expect(page).toContain("fetch('/recipes/')");
    expect(page).toContain("fetch('/ingredients/')");
    expect(page).toContain('prodName(item.product)');
  });

  it('products modal has delete confirmation + edit mode bound to real serializer fields', () => {
    const page = read('pos/products/index.astro');
    // delete confirmation is a real modal, not a toast stub
    expect(page).toContain('<div\n      x-show="deleteTarget"\n      x-transition.opacity\n      class="fixed inset-0 z-50');
    expect(page).toContain('Delete this product?');
    expect(page).toContain("fetch(`${endpoint}${id}/`, { method: 'DELETE' })");
    // edit mode populates form from item incl. serializer key category_id
    expect(page).toContain("category: item.category ?? item.category_id ?? '',");
    // table no longer renders raw item.category_name; resolves via catName
    expect(page).not.toMatch(/item\.category_name/);
    expect(page).toContain('catName(item.category)');
    // PUT to detail endpoint on edit (multi-line fetch)
    expect(page).toContain('fetch(`${endpoint}${this.editingItem.id}/`');
    expect(page).toContain("method: 'PUT'");
  });

  it('inventory modal has delete confirmation + edit mode bound to product_id', () => {
    const page = read('pos/inventory/index.astro');
    expect(page).toContain('Delete this record?');
    expect(page).toContain("fetch(`${endpoint}${id}/`, { method: 'DELETE' })");
    expect(page).toContain("product_id: item.product_id ?? item.product ?? '',");
    // list table resolves product id→name instead of raw item.product_name
    expect(page).toContain('prodName(item.product)');
    expect(page).not.toContain('item.product_name || item.product');
    expect(page).toContain('fetch(`${endpoint}${this.editingItem.id}/`');
    expect(page).toContain("method: 'PUT'");
  });

  it('transactions modal has delete confirmation + edit mode bound to customer_id', () => {
    const page = read('pos/transactions/index.astro');
    expect(page).toContain('Delete this transaction?');
    expect(page).toContain("fetch(`${endpoint}${id}/`, { method: 'DELETE' })");
    expect(page).toContain("customer_id: item.customer_id ?? item.customer ?? '',");
    // table resolves customer id→name instead of raw item.customer_name
    expect(page).toContain('custName(item.customer)');
    expect(page).not.toMatch(/item\.customer_name/);
    expect(page).toContain('fetch(`${endpoint}${this.editingItem.id}/`');
    expect(page).toContain("method: 'PUT'");
  });

  it('crm contacts modal has delete confirmation + table resolves company name', () => {
    const page = read('crm/contacts/index.astro');
    expect(page).toContain('Delete this contact?');
    expect(page).toContain("await fetch('/crm/contacts/' + id, { method: 'DELETE' })");
    expect(page).toContain("fetch('/crm/contacts/' + this.editingItem.id,");
    // table resolves company id→name via companyName helper over /crm/companies/
    expect(page).toContain('companyName(item.company)');
    expect(page).toContain("fetch('/crm/companies')");
    // modal exposes a Company selector and PUT/POST send company_id
    expect(page).toContain('x-model="form.company_id"');
    expect(page).toContain('company_id: this.form.company_id ? parseInt(String(this.form.company_id)) : null');
    // edit mode populates the FK from either serializer key
    expect(page).toContain("company_id: item.company ?? item.company_id ?? ''");
    expect(page).not.toMatch(/item\.company_name/);
  });

  it('crm deals modal binds contact/pipeline/stage FKs and payload sends *_id', () => {
    const page = read('crm/deals/index.astro');
    expect(page).toContain("fetch('/crm/contacts')");
    expect(page).toContain("fetch('/crm/pipelines')");
    expect(page).toContain('x-model="form.contact_id"');
    expect(page).toContain('x-model="form.pipeline_id"');
    expect(page).toContain('x-model="form.stage_id"');
    // table resolves contact/stage id→name (never *_name fields)
    expect(page).toContain('contactName(item.contact)');
    expect(page).toContain('stageName(item.stage)');
    expect(page).not.toMatch(/item\.contact_name/);
    expect(page).not.toMatch(/item\.stage_name/);
    // pipeline change resets a no-longer-valid stage
    expect(page).toContain('onPipelineChange()');
    // payload maps ids to the model FK columns
    expect(page).toContain('pipeline_id: parseInt(String(this.form.pipeline_id))');
    expect(page).toContain('stage_id: this.form.stage_id ? parseInt(String(this.form.stage_id)) : null');
    expect(page).toContain("fetch('/crm/deals/' + this.editingItem.id,");
    expect(page).toContain("await fetch('/crm/deals/' + id, { method: 'DELETE' })");
  });

  it('crm activities + notes resolve contact/deal names and send FK ids', () => {
    const activities = read('crm/activities/index.astro');
    const notes = read('crm/notes/index.astro');
    for (const page of [activities, notes]) {
      expect(page).toContain("fetch('/crm/contacts')");
      expect(page).toContain("fetch('/crm/deals')");
      expect(page).toContain('contactName(item.contact)');
      expect(page).toContain('dealTitle(item.deal)');
      expect(page).not.toMatch(/item\.contact_name/);
      expect(page).not.toMatch(/item\.deal_title/);
      expect(page).toContain('x-model="form.contact_id"');
      expect(page).toContain('x-model="form.deal_id"');
      expect(page).toContain('contact_id:this.form.contact_id?parseInt(String(this.form.contact_id)):null');
      expect(page).toContain('deal_id:this.form.deal_id?parseInt(String(this.form.deal_id)):null');
    }
    expect(activities).toContain("fetch('/crm/activities/'+this.editingItem.id");
    expect(notes).toContain("fetch('/crm/notes/'+this.editingItem.id");
  });

  it('ops/shifts modal enforces unique-open-shift constraint + expected-cash checks', () => {
    const page = read('ops/shifts/index.astro');
    // closing cash + expected cash are required inputs for a closed shift
    expect(page).toContain('Closing Cash ($)</label><input type="number" x-model="form.closing_cash"');
    expect(page).toContain('Expected Cash ($)</label><input type="number" x-model="form.expected_cash"');
    // doSave validates closing cash required when closing, and warns when closing != expected
    expect(page).toContain("'Closing cash is required to close a shift'");
    expect(page).toContain('Math.abs(parseFloat(String(this.form.closing_cash))-expected)>0.005');
    // unique-open-shift: openAdd blocks when a shift is already open, and the
    // server mirrors the guard (409) before the DB constraint fires
    expect(page).toContain("'A shift is already open — close it before opening a new one'");
    expect(page).toContain("'Another shift is already open — only one open shift is allowed'");
    expect(page).toContain('this.openCount>0');
    // auto expected-cash preview: opening float + cash sales since open
    expect(page).toContain('cashSalesBetween');
    expect(page).toContain("(Number(item.opening_cash||0)+cashSales).toFixed(2)");
    expect(page).toContain("sale.payment_method||'').toLowerCase()!=='cash'");
    // delete is blocked for open shifts
    expect(page).toContain('Cannot delete an open shift');
    // edit flow pre-populates expected_cash for existing shifts
    expect(page).toContain("expected_cash:item.expected_cash?Number(item.expected_cash):''");
  });
});
