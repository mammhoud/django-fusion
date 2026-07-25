// Page Object Model — Customers Page
// Path: projects/pos/pos-full/src/pages/Customers.tsx

import { Page, Locator } from '@playwright/test';

export class CustomersPage {
  readonly page: Page;
  readonly title: Locator;
  readonly addButton: Locator;
  readonly searchInput: Locator;
  readonly clearSearchButton: Locator;
  readonly countDisplay: Locator;
  readonly customerCards: Locator;
  readonly editButtons: Locator;
  readonly deleteButtons: Locator;
  // Form modal
  readonly formModal: Locator;
  readonly nameInput: Locator;
  readonly phoneInput: Locator;
  readonly emailInput: Locator;
  readonly notesInput: Locator;
  readonly submitButton: Locator;
  readonly cancelButton: Locator;
  // Status toast
  readonly statusToast: Locator;

  constructor(page: Page) {
    this.page = page;
    this.title = page.locator('h1');
    this.addButton = page.getByRole('button', { name: /add customer/i });
    this.searchInput = page.getByPlaceholder(/search customers/i);
    this.clearSearchButton = page.getByLabel(/clear/i);
    this.countDisplay = page.locator('text=/\\d+ \\/ \\d+/');
    this.customerCards = page.locator('.card--glass');
    this.editButtons = page.getByTitle(/edit/i);
    this.deleteButtons = page.getByTitle(/delete/i);
    this.formModal = page.locator('form');
    this.nameInput = page.getByPlaceholder(/name/i);
    this.phoneInput = page.getByPlaceholder(/phone/i);
    this.emailInput = page.getByPlaceholder(/email/i);
    this.notesInput = page.getByPlaceholder(/notes/i);
    this.submitButton = page.getByRole('button', { name: /save|update/i });
    this.cancelButton = page.getByRole('button', { name: /cancel/i });
    this.statusToast = page.locator('[role="status"]');
  }

  async goto() { await this.page.goto('/customers'); }
  async search(query: string) { await this.searchInput.fill(query); }
  async clearSearch() { if (await this.clearSearchButton.isVisible()) await this.clearSearchButton.click(); }
  async clickAdd() { await this.addButton.click(); }
  async clickEdit(name: string) {
    const card = this.customerCards.filter({ hasText: name });
    await card.locator('button').first().click();
  }
  async clickDelete(name: string) {
    const card = this.customerCards.filter({ hasText: name });
    await card.getByTitle(/delete/i).click();
  }
  async fillForm(data: { name: string; phone?: string; email?: string; notes?: string }) {
    await this.nameInput.fill(data.name);
    if (data.phone) await this.phoneInput.fill(data.phone);
    if (data.email) await this.emailInput.fill(data.email);
    if (data.notes) await this.notesInput.fill(data.notes);
  }
  async submit() { await this.submitButton.click(); }
  async cancel() { await this.cancelButton.click(); }
  async confirmDelete() { this.page.once('dialog', d => d.accept()); }
  async getCustomerCount(): Promise<number> {
    const text = await this.customerCards.count();
    return text;
  }
}
