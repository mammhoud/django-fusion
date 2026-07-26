import { Page, Locator } from '@playwright/test';
import { BasePage } from './BasePage';

/**
 * Inventory Page — manage products, stock levels, and categories.
 *
 * Covers both the generic product-table layout (forge-pos / pos-mini)
 * and the tabbed ingredients/transactions/adjustments layout (pos-full).
 */
export class InventoryPage extends BasePage {
  readonly productTable: Locator;
  readonly addProductButton: Locator;
  readonly stockFilter: Locator;
  readonly searchInput: Locator;

  // Tabbed layout (pos-full)
  readonly title: Locator;
  readonly ingredientsTab: Locator;
  readonly transactionsTab: Locator;
  readonly adjustmentsTab: Locator;
  readonly ingredientRows: Locator;
  readonly addIngredientButton: Locator;
  readonly transactionRows: Locator;
  readonly addTransactionButton: Locator;
  readonly adjustmentRows: Locator;
  readonly addAdjustmentButton: Locator;
  readonly quantityInput: Locator;
  readonly submitButton: Locator;
  readonly statusToast: Locator;

  constructor(page: Page) {
    super(page);

    // Generic product-table selectors (forge-pos / pos-mini)
    this.productTable = page.locator('table, [data-testid="product-table"], .data-table');
    this.addProductButton = page.locator('button:has-text("Add"), button:has-text("New"), [data-testid="add-product-btn"]');
    this.stockFilter = page.locator('[data-testid="stock-filter"], select, .filter-select');
    this.searchInput = page.locator('input[placeholder*="search" i], [data-testid="inventory-search"]');

    // Tabbed layout selectors (pos-full)
    this.title = page.locator('h1');
    this.ingredientsTab = page.getByRole('button', { name: /ingredients/i }).first();
    this.transactionsTab = page.getByRole('button', { name: /transactions/i });
    this.adjustmentsTab = page.getByRole('button', { name: /adjustments/i });
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

  async goto(): Promise<void> {
    await super.goto('/inventory');
    await this.waitForLoad();
  }

  /** Get number of rows in the product table */
  async getProductCount(): Promise<number> {
    return this.productTable.locator('tbody tr').count();
  }

  /** Search for an inventory item */
  async search(query: string): Promise<void> {
    await this.searchInput.fill(query);
    await this.page.keyboard.press('Enter');
    await this.page.waitForTimeout(500);
  }

  // Tabbed layout helpers

  async switchToIngredients(): Promise<void> {
    await this.ingredientsTab.click();
  }

  async switchToTransactions(): Promise<void> {
    await this.transactionsTab.click();
  }

  async switchToAdjustments(): Promise<void> {
    await this.adjustmentsTab.click();
  }

  async clickAddIngredient(): Promise<void> {
    await this.addIngredientButton.click();
  }

  async clickAddTransaction(): Promise<void> {
    await this.addTransactionButton.click();
  }

  async clickAddAdjustment(): Promise<void> {
    await this.addAdjustmentButton.click();
  }
}
