// Page Object Model — TaxReports Page
// Path: projects/pos/pos-full/src/pages/TaxReports.tsx

import { Page, Locator } from '@playwright/test';

export class TaxReportsPage {
  readonly page: Page;
  readonly title: Locator;
  readonly addButton: Locator;
  readonly searchInput: Locator;
  readonly clearSearchButton: Locator;
  readonly sortSelect: Locator;
  readonly reportRows: Locator;
  readonly editButtons: Locator;
  readonly deleteButtons: Locator;
  // Form
  readonly formModal: Locator;
  readonly totalSalesInput: Locator;
  readonly totalTaxInput: Locator;
  readonly transactionCountInput: Locator;
  readonly submitButton: Locator;
  readonly cancelButton: Locator;
  readonly statusToast: Locator;

  constructor(page: Page) {
    this.page = page;
    this.title = page.locator('h1');
    this.addButton = page.getByRole('button', { name: /add|new/i });
    this.searchInput = page.getByPlaceholder(/search.*period|search.*report/i);
    this.clearSearchButton = page.getByLabel(/clear/i);
    this.sortSelect = page.getByLabel(/sort/i);
    this.reportRows = page.locator('table, .grid').locator('tr, .card--glass');
    this.editButtons = page.getByTitle(/edit/i);
    this.deleteButtons = page.getByTitle(/delete/i);
    this.formModal = page.locator('form');
    this.totalSalesInput = page.getByPlaceholder(/total sales/i);
    this.totalTaxInput = page.getByPlaceholder(/total tax/i);
    this.transactionCountInput = page.getByPlaceholder(/transaction count/i);
    this.submitButton = page.getByRole('button', { name: /save|update|add/i });
    this.cancelButton = page.getByRole('button', { name: /cancel/i });
    this.statusToast = page.locator('[role="status"]');
  }

  async goto() { await this.page.goto('/tax-reports'); }
  async search(query: string) { await this.searchInput.fill(query); }
  async clickAdd() { await this.addButton.click(); }
  async clickEdit(rowIndex: number) { await this.editButtons.nth(rowIndex).click(); }
  async clickDelete(rowIndex: number) { await this.deleteButtons.nth(rowIndex).click(); }
  async fillForm(data: { totalSales?: number; totalTax?: number; transactionCount?: number }) {
    if (data.totalSales !== undefined) await this.totalSalesInput.fill(String(data.totalSales));
    if (data.totalTax !== undefined) await this.totalTaxInput.fill(String(data.totalTax));
    if (data.transactionCount !== undefined) await this.transactionCountInput.fill(String(data.transactionCount));
  }
  async submit() { await this.submitButton.click(); }
  async cancel() { await this.cancelButton.click(); }
  async confirmDelete() { this.page.once('dialog', d => d.accept()); }
}
