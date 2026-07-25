// Page Object Model — Suppliers Page
// Path: projects/pos/pos-full/src/pages/Suppliers.tsx

import { Page, Locator } from '@playwright/test';

export class SuppliersPage {
  readonly page: Page;
  readonly title: Locator;
  readonly addButton: Locator;
  readonly searchInput: Locator;
  readonly clearSearchButton: Locator;
  readonly sortSelect: Locator;
  readonly supplierCards: Locator;
  readonly editButtons: Locator;
  readonly deleteButtons: Locator;
  // Form modal
  readonly formModal: Locator;
  readonly nameInput: Locator;
  readonly contactNameInput: Locator;
  readonly phoneInput: Locator;
  readonly emailInput: Locator;
  readonly addressInput: Locator;
  readonly taxIdInput: Locator;
  readonly paymentTermsInput: Locator;
  readonly submitButton: Locator;
  readonly cancelButton: Locator;
  readonly statusToast: Locator;

  constructor(page: Page) {
    this.page = page;
    this.title = page.locator('h1');
    this.addButton = page.getByRole('button', { name: /add supplier/i });
    this.searchInput = page.getByPlaceholder(/search suppliers/i);
    this.clearSearchButton = page.getByLabel(/clear/i);
    this.sortSelect = page.getByLabel(/sort/i);
    this.supplierCards = page.locator('.card--glass');
    this.editButtons = page.getByTitle(/edit/i);
    this.deleteButtons = page.getByTitle(/delete/i);
    this.formModal = page.locator('form');
    this.nameInput = page.getByPlaceholder(/supplier.*name|name.*supplier/i);
    this.contactNameInput = page.getByPlaceholder(/contact name/i);
    this.phoneInput = page.getByPlaceholder(/supplier.*phone|phone.*supplier/i);
    this.emailInput = page.getByPlaceholder(/supplier.*email|email.*supplier/i);
    this.addressInput = page.getByPlaceholder(/address/i);
    this.taxIdInput = page.getByPlaceholder(/tax.*id/i);
    this.paymentTermsInput = page.getByPlaceholder(/payment terms/i);
    this.submitButton = page.getByRole('button', { name: /save|update/i });
    this.cancelButton = page.getByRole('button', { name: /cancel/i });
    this.statusToast = page.locator('[role="status"]');
  }

  async goto() { await this.page.goto('/suppliers'); }
  async search(query: string) { await this.searchInput.fill(query); }
  async clearSearch() { if (await this.clearSearchButton.isVisible()) await this.clearSearchButton.click(); }
  async clickAdd() { await this.addButton.click(); }
  async clickEdit(name: string) {
    const card = this.supplierCards.filter({ hasText: name });
    await card.getByTitle(/edit/i).click();
  }
  async clickDelete(name: string) {
    const card = this.supplierCards.filter({ hasText: name });
    await card.getByTitle(/delete/i).click();
  }
  async fillForm(data: { name: string; contactName?: string; phone?: string; email?: string; address?: string; taxId?: string; paymentTerms?: string }) {
    await this.nameInput.fill(data.name);
    if (data.contactName) await this.contactNameInput.fill(data.contactName);
    if (data.phone) await this.phoneInput.fill(data.phone);
    if (data.email) await this.emailInput.fill(data.email);
    if (data.address) await this.addressInput.fill(data.address);
    if (data.taxId) await this.taxIdInput.fill(data.taxId);
    if (data.paymentTerms) await this.paymentTermsInput.fill(data.paymentTerms);
  }
  async submit() { await this.submitButton.click(); }
  async cancel() { await this.cancelButton.click(); }
  async confirmDelete() { this.page.once('dialog', d => d.accept()); }
}
