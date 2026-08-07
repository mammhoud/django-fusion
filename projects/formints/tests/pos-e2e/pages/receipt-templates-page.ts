// Page Object Model — ReceiptTemplates Page
// Path: projects/pos/pos-full/src/pages/ReceiptTemplates.tsx

import { Page, Locator } from '@playwright/test';

export class ReceiptTemplatesPage {
  readonly page: Page;
  readonly title: Locator;
  readonly addButton: Locator;
  readonly searchInput: Locator;
  readonly clearSearchButton: Locator;
  readonly sortSelect: Locator;
  readonly templateCards: Locator;
  readonly editButtons: Locator;
  readonly deleteButtons: Locator;
  // Form
  readonly formModal: Locator;
  readonly nameInput: Locator;
  readonly bodyInput: Locator;
  readonly submitButton: Locator;
  readonly cancelButton: Locator;
  readonly statusToast: Locator;

  constructor(page: Page) {
    this.page = page;
    this.title = page.locator('h1');
    this.addButton = page.getByRole('button', { name: /add template|new template|add/i });
    this.searchInput = page.getByPlaceholder(/search template/i);
    this.clearSearchButton = page.getByLabel(/clear/i);
    this.sortSelect = page.getByLabel(/sort/i);
    this.templateCards = page.locator('.card--glass');
    this.editButtons = page.getByTitle(/edit/i);
    this.deleteButtons = page.getByTitle(/delete/i);
    this.formModal = page.locator('form');
    this.nameInput = page.getByPlaceholder(/template.*name|name.*template/i);
    this.bodyInput = page.getByPlaceholder(/body/i);
    this.submitButton = page.getByRole('button', { name: /save|update/i });
    this.cancelButton = page.getByRole('button', { name: /cancel/i });
    this.statusToast = page.locator('[role="status"]');
  }

  async goto() { await this.page.goto('/receipt-templates'); }
  async search(query: string) { await this.searchInput.fill(query); }
  async clickAdd() { await this.addButton.click(); }
  async clickEdit(name: string) {
    const card = this.templateCards.filter({ hasText: name });
    await card.getByTitle(/edit/i).click();
  }
  async clickDelete(name: string) {
    const card = this.templateCards.filter({ hasText: name });
    await card.getByTitle(/delete/i).click();
  }
  async fillForm(data: { name: string; body: string }) {
    await this.nameInput.fill(data.name);
    await this.bodyInput.fill(data.body);
  }
  async submit() { await this.submitButton.click(); }
  async cancel() { await this.cancelButton.click(); }
  async confirmDelete() { this.page.once('dialog', d => d.accept()); }
}
