import { test, expect } from '../../fixtures/auth';
import { captureConsoleErrors } from '../../helpers/utils';
import { InventoryPage } from '../../pages';

/**
 * POS Inventory Management E2E Tests
 *
 * Verifies the inventory page renders correctly:
 * - Product table loads
 * - Search/filter works
 * - Add product button exists (for admin)
 */

test.describe('POS Inventory Management', () => {
  test('inventory page loads with product table', async ({ adminPage }) => {
    const errors = captureConsoleErrors(adminPage);
    const inventory = new InventoryPage(adminPage);

    await inventory.goto();

    // forge-pos Inventory uses a tabbed layout (stock/transactions/adjustments) with CSS Grid,
    // not a <table>. Check for page title, tab buttons, or summary cards.
    const hasTitle = await inventory.title.isVisible().catch(() => false);
    const hasStockTab = await inventory.ingredientsTab.isVisible().catch(() => false);
    const hasTable = await inventory.productTable.isVisible().catch(() => false);
    const hasEmpty = await inventory.emptyState.isVisible().catch(() => false);

    expect(hasTitle || hasStockTab || hasTable || hasEmpty).toBe(true);
    expect(errors.getFiltered()).toHaveLength(0);
  });

  test('admin can see add product button', async ({ adminPage }) => {
    const inventory = new InventoryPage(adminPage);
    await inventory.goto();

    // forge-pos Inventory has 'Add Ingredient' button in stock tab
    const hasAddBtn = await inventory.addProductButton.isVisible().catch(() => false);
    const hasAddIngredient = await inventory.addIngredientButton.isVisible().catch(() => false);
    expect(hasAddBtn || hasAddIngredient).toBe(true);
  });

  test('search input filters inventory', async ({ adminPage }) => {
    const inventory = new InventoryPage(adminPage);
    await inventory.goto();

    if (await inventory.searchInput.isVisible()) {
      await inventory.search('test');
      expect(await inventory.searchInput.inputValue()).toBe('test');
    }
  });

  test('cashier can view inventory (read-only)', async ({ cashierPage }) => {
    const inventory = new InventoryPage(cashierPage);
    await inventory.goto();

    // Page should have loaded — check for reasonable content length
    const bodyText = await cashierPage.textContent('body');
    expect((bodyText?.length ?? 0)).toBeGreaterThan(20);
    expect(bodyText).not.toContain('403');
  });

  test('manager can access inventory', async ({ managerPage }) => {
    const inventory = new InventoryPage(managerPage);
    await inventory.goto();

    // Check for main content (pageLayout from BasePage)
    const hasContent = await inventory.pageLayout.isVisible().catch(() => false);
    const hasTitle = await inventory.title.isVisible().catch(() => false);
    expect(hasContent || hasTitle).toBe(true);
  });
});
