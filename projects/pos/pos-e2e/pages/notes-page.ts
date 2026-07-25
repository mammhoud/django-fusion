// Page Object Model — Notes Page
// Path: projects/pos/pos-full/src/pages/Notes.tsx

import { Page, Locator } from '@playwright/test';

export class NotesPage {
  readonly page: Page;
  readonly title: Locator;
  readonly addButton: Locator;
  readonly searchInput: Locator;
  readonly noteCards: Locator;
  readonly editButtons: Locator;
  readonly deleteButtons: Locator;
  // Form
  readonly formModal: Locator;
  readonly titleInput: Locator;
  readonly contentInput: Locator;
  readonly entityIdInput: Locator;
  readonly submitButton: Locator;
  readonly cancelButton: Locator;
  readonly statusToast: Locator;

  constructor(page: Page) {
    this.page = page;
    this.title = page.locator('h1');
    this.addButton = page.getByRole('button', { name: /add note|new note/i });
    this.searchInput = page.getByPlaceholder(/search notes/i);
    this.noteCards = page.locator('.card--glass');
    this.editButtons = page.getByTitle(/edit/i);
    this.deleteButtons = page.getByTitle(/delete/i);
    this.formModal = page.locator('form');
    this.titleInput = page.getByPlaceholder(/note title/i);
    this.contentInput = page.getByPlaceholder(/write your note/i);
    this.entityIdInput = page.getByPlaceholder(/optional entity/i);
    this.submitButton = page.getByRole('button', { name: /save|update/i });
    this.cancelButton = page.getByRole('button', { name: /cancel/i });
    this.statusToast = page.locator('[role="status"]');
  }

  async goto() { await this.page.goto('/notes'); }
  async search(query: string) { await this.searchInput.fill(query); }
  async clickAdd() { await this.addButton.click(); }
  async clickEdit(title: string) {
    const card = this.noteCards.filter({ hasText: title });
    await card.getByTitle(/edit/i).click();
  }
  async clickDelete(title: string) {
    const card = this.noteCards.filter({ hasText: title });
    await card.getByTitle(/delete/i).click();
  }
  async fillForm(data: { title: string; content: string; entityId?: string }) {
    await this.titleInput.fill(data.title);
    await this.contentInput.fill(data.content);
    if (data.entityId) await this.entityIdInput.fill(data.entityId);
  }
  async submit() { await this.submitButton.click(); }
  async cancel() { await this.cancelButton.click(); }
  async confirmDelete() { this.page.once('dialog', d => d.accept()); }
}
