// Page Object Model — Inventory Page
// Path: projects/pos/pos-full/src/pages/Inventory.tsx

import { Page, Locator } from '@playwright/test';

export class InventoryPage {
  readonly page: Page;
  readonly title: Locator;
  // Tabs
  readonly ingredientsTab: Locator;
  readonly transactionsTab: Locator;
  readonly adjustmentsTab: Locator;
  // Summary cards
  readonly totalIngredientsStat: Locator;
  readonly stockValueStat: Locator;
  readonly avgCostStat: Locator;
  readonly lowStockStat: Locator;
  // Ingredient list
  readonly searchInput: Locator;
  readonly ingredientRows: Locator;
  readonly addIngredientButton: Locator;
  // Transaction log
  readonly transactionRows: Locator;
  readonly addTransactionButton: Locator;
  // Adjustment form
  readonly adjustmentRows: Locator;
  readonly addAdjustmentButton: Locator;
  readonly quantityInput: Locator;
  readonly submitButton: Locator;
  readonly statusToast: Locator;

  constructor(page: Page) {
    this.page = page;
    this.title = page.locator('h1');
    this.ingredientsTab = page.getByRole('button', { name: /ingredients/i }).first();
    this.transactionsTab = page.getByRole('button', { name: /transactions/i });
    this.adjustmentsTab = page.getByRole('button', { name: /adjustments/i });
    this.totalIngredientsStat = page.locator('text=/total ingredients/i').locator('..').locator('p');
    this.stockValueStat = page.locator('text=/stock value/i').locator('..').locator('p');
    this.avgCostStat = page.locator('text=/avg.? cost/i').locator('..').locator('p');
    this.lowStockStat = page.locator('text=/low stock/i').locator('..').locator('p');
    this.searchInput = page.getByPlaceholder(/search ingredient/i);
    this.ingredientRows = page.locator('table, .grid').locator('tr, .card--glass');
    this.addIngredientButton = page.getByRole('button', { name: /add ingredient/i });
    this.transactionRows = page.locator('table').locator('tr');
    this.addTransactionButton = page.getByRole('button', { name: /add transaction/i });
    this.adjustmentRows = page.locator('table').locator('tr');
    this.addAdjustmentButton = page.getByRole('button', { name: /add adjustment/i });
    this.quantityInput = page.getByPlaceholder(/quantity/i);
    this.submitButton = page.getByRole('button', { name: /save|submit|add/i });
    this.statusToast = page.locator('[role="status"]');
  }

  async goto() { await this.page.goto('/inventory'); }
  async switchToIngredients() { await this.ingredientsTab.click(); }
  async switchToTransactions() { await this.transactionsTab.click(); }
  async switchToAdjustments() { await this.adjustmentsTab.click(); }
  async search(query: string) { await this.searchInput.fill(query); }
  async clickAddIngredient() { await this.addIngredientButton.click(); }
  async clickAddTransaction() { await this.addTransactionButton.click(); }
  async clickAddAdjustment() { await this.addAdjustmentButton.click(); }
}
