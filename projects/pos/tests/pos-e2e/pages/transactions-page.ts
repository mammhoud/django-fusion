// Page Object Model — Transactions Page
// Path: projects/pos/pos-full/src/pages/Transactions.tsx

import { Page, Locator } from '@playwright/test';

export class TransactionsPage {
  readonly page: Page;
  readonly title: Locator;
  // Summary
  readonly allTimeTotal: Locator;
  readonly filteredTotal: Locator;
  readonly filteredCount: Locator;
  // Tabs
  readonly salesTab: Locator;
  readonly productsTab: Locator;
  // Filters
  readonly searchInput: Locator;
  readonly dateRangePicker: Locator;
  // Sales table
  readonly saleRows: Locator;
  readonly editButtons: Locator;
  readonly deleteButtons: Locator;
  // Product sales table
  readonly totalProductsSold: Locator;
  readonly revenueStat: Locator;
  readonly uniqueProductsStat: Locator;
  readonly statusToast: Locator;

  constructor(page: Page) {
    this.page = page;
    this.title = page.locator('h1, h2').first();
    this.allTimeTotal = page.locator('text=/all time total/i').locator('..');
    this.filteredTotal = page.locator('text=/filtered total/i').locator('..');
    this.filteredCount = page.locator('text=/filtered transactions/i').locator('..');
    this.salesTab = page.getByRole('button', { name: /sales/i }).first();
    this.productsTab = page.getByRole('button', { name: /products/i });
    this.searchInput = page.getByPlaceholder(/search product/i);
    this.dateRangePicker = page.locator('input[type="date"]');
    this.saleRows = page.locator('table').locator('tr');
    this.editButtons = page.getByTitle(/edit/i);
    this.deleteButtons = page.getByTitle(/delete/i);
    this.totalProductsSold = page.locator('text=/total products sold/i').locator('..');
    this.revenueStat = page.locator('text=/revenue/i').locator('..').locator('p');
    this.uniqueProductsStat = page.locator('text=/unique products/i').locator('..').locator('p');
    this.statusToast = page.locator('[role="status"]');
  }

  async goto() { await this.page.goto('/transactions'); }
  async switchToSales() { await this.salesTab.click(); }
  async switchToProducts() { await this.productsTab.click(); }
  async search(query: string) { await this.searchInput.fill(query); }
  async clickEdit(rowIndex: number) { await this.editButtons.nth(rowIndex).click(); }
  async clickDelete(rowIndex: number) { await this.deleteButtons.nth(rowIndex).click(); }
  async confirmDelete() { this.page.once('dialog', d => d.accept()); }
}
