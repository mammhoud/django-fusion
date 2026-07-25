// Page Object Model — EmployeeSchedule Page
// Path: projects/pos/pos-full/src/pages/EmployeeSchedule.tsx

import { Page, Locator } from '@playwright/test';

export class EmployeeSchedulePage {
  readonly page: Page;
  readonly title: Locator;
  readonly addButton: Locator;
  readonly scheduleRows: Locator;
  readonly editButtons: Locator;
  readonly deleteButtons: Locator;
  // Form
  readonly formModal: Locator;
  readonly notesInput: Locator;
  readonly submitButton: Locator;
  readonly cancelButton: Locator;
  readonly statusToast: Locator;

  constructor(page: Page) {
    this.page = page;
    this.title = page.locator('h1');
    this.addButton = page.getByRole('button', { name: /add|new/i });
    this.scheduleRows = page.locator('table, .grid').locator('tr, .card--glass');
    this.editButtons = page.getByTitle(/edit/i);
    this.deleteButtons = page.getByTitle(/delete/i);
    this.formModal = page.locator('form');
    this.notesInput = page.getByPlaceholder(/notes/i);
    this.submitButton = page.getByRole('button', { name: /save|update|add/i });
    this.cancelButton = page.getByRole('button', { name: /cancel/i });
    this.statusToast = page.locator('[role="status"]');
  }

  async goto() { await this.page.goto('/schedule'); }
  async clickAdd() { await this.addButton.click(); }
  async clickEdit(rowIndex: number) { await this.editButtons.nth(rowIndex).click(); }
  async clickDelete(rowIndex: number) { await this.deleteButtons.nth(rowIndex).click(); }
  async setNotes(text: string) { await this.notesInput.fill(text); }
  async submit() { await this.submitButton.click(); }
  async cancel() { await this.cancelButton.click(); }
  async confirmDelete() { this.page.once('dialog', d => d.accept()); }
}
