// Page Object Model — Payroll Page
// Path: projects/pos/pos-full/src/pages/Payroll.tsx

import { Page, Locator } from '@playwright/test';

export class PayrollPage {
  readonly page: Page;
  readonly title: Locator;
  readonly addButton: Locator;
  readonly payrollRows: Locator;
  readonly editButtons: Locator;
  readonly deleteButtons: Locator;
  // Form
  readonly formModal: Locator;
  readonly regularHoursInput: Locator;
  readonly overtimeHoursInput: Locator;
  readonly totalPayInput: Locator;
  readonly submitButton: Locator;
  readonly cancelButton: Locator;
  readonly statusToast: Locator;

  constructor(page: Page) {
    this.page = page;
    this.title = page.locator('h1');
    this.addButton = page.getByRole('button', { name: /add payroll|add record/i });
    this.payrollRows = page.locator('table').locator('tr, .card--glass');
    this.editButtons = page.getByTitle(/edit/i);
    this.deleteButtons = page.getByTitle(/delete/i);
    this.formModal = page.locator('form');
    this.regularHoursInput = page.getByPlaceholder(/regular hours/i);
    this.overtimeHoursInput = page.getByPlaceholder(/overtime hours/i);
    this.totalPayInput = page.getByPlaceholder(/total pay/i);
    this.submitButton = page.getByRole('button', { name: /save|update|add/i });
    this.cancelButton = page.getByRole('button', { name: /cancel/i });
    this.statusToast = page.locator('[role="status"]');
  }

  async goto() { await this.page.goto('/payroll'); }
  async clickAdd() { await this.addButton.click(); }
  async clickEdit(rowIndex: number) { await this.editButtons.nth(rowIndex).click(); }
  async clickDelete(rowIndex: number) { await this.deleteButtons.nth(rowIndex).click(); }
  async fillForm(data: { regularHours?: number; overtimeHours?: number; totalPay?: number }) {
    if (data.regularHours !== undefined) await this.regularHoursInput.fill(String(data.regularHours));
    if (data.overtimeHours !== undefined) await this.overtimeHoursInput.fill(String(data.overtimeHours));
    if (data.totalPay !== undefined) await this.totalPayInput.fill(String(data.totalPay));
  }
  async submit() { await this.submitButton.click(); }
  async cancel() { await this.cancelButton.click(); }
  async confirmDelete() { this.page.once('dialog', d => d.accept()); }
}
