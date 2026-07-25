import { Page } from '@playwright/test';
import { BasePage } from './BasePage';

/**
 * Inventory Page — manage products, stock levels, and categories.
 */
export class InventoryPage extends BasePage {
  readonly productTable;
  readonly addProductButton;
  readonly stockFilter;
  readonly searchInput;

  constructor(page: Page) {
    super(page);

    this.productTable = page.locator('table, [data-testid="product-table"], .data-table');
    this.addProductButton = page.locator('button:has-text("Add"), button:has-text("New"), [data-testid="add-product-btn"]');
    this.stockFilter = page.locator('[data-testid="stock-filter"], select, .filter-select');
    this.searchInput = page.locator('input[placeholder*="search" i], [data-testid="inventory-search"]');
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
}
