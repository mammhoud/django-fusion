// Page Object Model — Roles Page
// Path: projects/pos/pos-full/src/pages/Roles.tsx

import { Page, Locator } from '@playwright/test';

export class RolesPage {
  readonly page: Page;
  readonly title: Locator;
  readonly addButton: Locator;
  readonly searchInput: Locator;
  readonly clearSearchButton: Locator;
  readonly sortSelect: Locator;
  readonly roleCards: Locator;
  readonly editButtons: Locator;
  readonly deleteButtons: Locator;
  // Form
  readonly formModal: Locator;
  readonly nameInput: Locator;
  readonly permissionsInput: Locator;
  readonly submitButton: Locator;
  readonly cancelButton: Locator;
  readonly statusToast: Locator;

  constructor(page: Page) {
    this.page = page;
    this.title = page.locator('h1');
    this.addButton = page.getByRole('button', { name: /add role/i });
    this.searchInput = page.getByPlaceholder(/search roles/i);
    this.clearSearchButton = page.getByLabel(/clear/i);
    this.sortSelect = page.getByLabel(/sort/i);
    this.roleCards = page.locator('.card--glass');
    this.editButtons = page.getByTitle(/edit/i);
    this.deleteButtons = page.getByTitle(/delete/i);
    this.formModal = page.locator('form');
    this.nameInput = page.getByPlaceholder(/role.*name/i);
    this.permissionsInput = page.getByPlaceholder(/permissions/i);
    this.submitButton = page.getByRole('button', { name: /save|update/i });
    this.cancelButton = page.getByRole('button', { name: /cancel/i });
    this.statusToast = page.locator('[role="status"]');
  }

  async goto() { await this.page.goto('/roles'); }
  async search(query: string) { await this.searchInput.fill(query); }
  async clickAdd() { await this.addButton.click(); }
  async clickEdit(name: string) {
    const card = this.roleCards.filter({ hasText: name });
    await card.getByTitle(/edit/i).click();
  }
  async clickDelete(name: string) {
    const card = this.roleCards.filter({ hasText: name });
    await card.getByTitle(/delete/i).click();
  }
  async fillForm(data: { name: string; permissions?: string }) {
    await this.nameInput.fill(data.name);
    if (data.permissions) await this.permissionsInput.fill(data.permissions);
  }
  async submit() { await this.submitButton.click(); }
  async cancel() { await this.cancelButton.click(); }
  async confirmDelete() { this.page.once('dialog', d => d.accept()); }
}
