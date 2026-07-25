// Page Object Model — ProductManager Page
// Path: projects/pos/pos-full/src/pages/ProductManager.tsx

import { Page, Locator } from '@playwright/test';

export class ProductManagerPage {
  readonly page: Page;
  readonly title: Locator;
  readonly searchInput: Locator;
  readonly categoryFilter: Locator;
  readonly sortSelect: Locator;
  readonly addButton: Locator;
  readonly totalProductsStat: Locator;
  readonly filteredCountStat: Locator;
  // Product grid
  readonly productCards: Locator;
  readonly editButtons: Locator;
  readonly deleteButtons: Locator;
  // Modal
  readonly modal: Locator;
  readonly nameInput: Locator;
  readonly priceInput: Locator;
  readonly unitInput: Locator;
  readonly borderColorInput: Locator;
  readonly submitButton: Locator;
  readonly cancelButton: Locator;
  // Status
  readonly statusToast: Locator;

  constructor(page: Page) {
    this.page = page;
    this.title = page.locator('h2').first();
    this.searchInput = page.getByTestId('pm-search-input');
    this.categoryFilter = page.getByTestId('pm-category-filter');
    this.sortSelect = page.getByLabel(/sort/i);
    this.addButton = page.getByTestId('pm-add-button');
    this.totalProductsStat = page.locator('text=/total products/i').locator('..');
    this.filteredCountStat = page.locator('text=/visible/i').locator('..');
    this.productCards = page.locator('.card--glass').filter({ has: page.locator('h3') });
    this.editButtons = page.getByTitle(/edit/i);
    this.deleteButtons = page.getByTitle(/delete/i);
    this.modal = page.getByTestId('pm-modal');
    this.nameInput = page.getByTestId('pm-name-input');
    this.priceInput = page.getByTestId('pm-price-input');
    this.unitInput = page.getByTestId('pm-unit-input');
    this.borderColorInput = page.locator('[data-testid="pm-modal"]').locator('input[type="color"], input[placeholder*="#"]');
    this.submitButton = page.getByTestId('pm-submit');
    this.cancelButton = page.getByRole('button', { name: /cancel/i });
    this.statusToast = page.locator('[role="status"]');
  }

  async goto() { await this.page.goto('/products'); }
  async search(query: string) { await this.searchInput.fill(query); }
  async filterByCategory(category: string) { await this.categoryFilter.selectOption(category); }
  async clickAdd() { await this.addButton.click(); }
  async clickEdit(name: string) {
    const card = this.productCards.filter({ hasText: name });
    await card.getByTitle(/edit/i).click();
  }
  async clickDelete(name: string) {
    const card = this.productCards.filter({ hasText: name });
    await card.getByTitle(/delete/i).click();
  }
  async fillForm(data: { name: string; price?: number; unit?: string; borderColor?: string }) {
    await this.nameInput.fill(data.name);
    if (data.price !== undefined) await this.priceInput.fill(String(data.price));
    if (data.unit) await this.unitInput.fill(data.unit);
    if (data.borderColor) await this.borderColorInput.fill(data.borderColor);
  }
  async submit() { await this.submitButton.click(); }
  async cancel() { await this.cancelButton.click(); }
  async confirmDelete() { this.page.once('dialog', d => d.accept()); }
}
