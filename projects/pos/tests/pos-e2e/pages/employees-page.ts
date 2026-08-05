// Page Object Model — Employees Page
// Path: projects/pos/pos-full/src/pages/Employees.tsx

import { Page, Locator } from '@playwright/test';

export class EmployeesPage {
  readonly page: Page;
  readonly title: Locator;
  readonly employeesTab: Locator;
  readonly typesTab: Locator;
  // Summary cards
  readonly totalEmployeesStat: Locator;
  readonly employeeTypesStat: Locator;
  readonly monthlySalaryStat: Locator;
  readonly avgSalaryStat: Locator;
  // Filters
  readonly searchInput: Locator;
  readonly typeFilterSelect: Locator;
  readonly activeFilterButton: Locator;
  readonly inactiveFilterButton: Locator;
  readonly addEmployeeButton: Locator;
  // Employee cards
  readonly employeeCards: Locator;
  readonly editButtons: Locator;
  readonly deleteButtons: Locator;
  // Form modal
  readonly formModal: Locator;
  readonly nameInput: Locator;
  readonly phoneInput: Locator;
  readonly emailInput: Locator;
  readonly typeSelect: Locator;
  readonly salaryInput: Locator;
  readonly submitButton: Locator;
  readonly cancelButton: Locator;
  // Types tab
  readonly addTypeButton: Locator;
  readonly typeCards: Locator;
  readonly statusToast: Locator;

  constructor(page: Page) {
    this.page = page;
    this.title = page.locator('h1');
    this.employeesTab = page.getByRole('button', { name: /employee list/i });
    this.typesTab = page.getByRole('button', { name: /employee types/i });
    this.totalEmployeesStat = page.locator('text=/total employees/i').locator('..').locator('p');
    this.employeeTypesStat = page.locator('text=/employee types/i').locator('..').locator('p');
    this.monthlySalaryStat = page.locator('text=/monthly salary/i').locator('..').locator('p');
    this.avgSalaryStat = page.locator('text=/avg.? salary/i').locator('..').locator('p');
    this.searchInput = page.getByPlaceholder(/search/i);
    this.typeFilterSelect = page.locator('select').first();
    this.activeFilterButton = page.getByRole('button', { name: /active/i });
    this.inactiveFilterButton = page.getByRole('button', { name: /inactive/i });
    this.addEmployeeButton = page.getByRole('button', { name: /add employee/i });
    this.employeeCards = page.locator('.card--glass').filter({ has: page.locator('h3') });
    this.editButtons = page.getByTitle(/edit/i);
    this.deleteButtons = page.getByTitle(/deactivate/i);
    this.formModal = page.locator('[role="dialog"]').filter({ hasText: /employee/i });
    this.nameInput = page.getByPlaceholder(/enter employee name|full name/i);
    this.phoneInput = page.getByPlaceholder(/03XX/i);
    this.emailInput = page.getByPlaceholder(/email/i).last();
    this.typeSelect = page.locator('select').last();
    this.salaryInput = page.getByPlaceholder('0');
    this.submitButton = page.getByRole('button', { name: /add employee|update/i }).first();
    this.cancelButton = page.getByRole('button', { name: /cancel/i });
    this.addTypeButton = page.getByRole('button', { name: /add type/i });
    this.typeCards = page.locator('.card--glass').filter({ has: page.getByRole('heading', { level: 3 }) });
    this.statusToast = page.locator('[role="status"]');
  }

  async goto() { await this.page.goto('/employees'); }
  async switchToEmployees() { await this.employeesTab.click(); }
  async switchToTypes() { await this.typesTab.click(); }
  async search(query: string) { await this.searchInput.fill(query); }
  async filterByType(typeId: number) { await this.typeFilterSelect.selectOption(String(typeId)); }
  async filterActive() { await this.activeFilterButton.click(); }
  async filterInactive() { await this.inactiveFilterButton.click(); }
  async clickAddEmployee() { await this.addEmployeeButton.click(); }
  async clickAddType() { await this.addTypeButton.click(); }
  async clickEdit(employeeName: string) {
    const card = this.employeeCards.filter({ hasText: employeeName });
    await card.getByTitle(/edit/i).click();
  }
  async clickDelete(employeeName: string) {
    const card = this.employeeCards.filter({ hasText: employeeName });
    await card.getByTitle(/deactivate/i).click();
  }
  async fillEmployeeForm(data: { name: string; phone?: string; email?: string; typeId?: number; salary?: number }) {
    await this.nameInput.fill(data.name);
    if (data.phone) await this.phoneInput.fill(data.phone);
    if (data.email) await this.emailInput.fill(data.email);
    if (data.typeId) await this.typeSelect.selectOption(String(data.typeId));
    if (data.salary !== undefined) await this.salaryInput.fill(String(data.salary));
  }
  async submit() { await this.submitButton.click(); }
  async cancel() { await this.cancelButton.click(); }
  async confirmDialog() { this.page.once('dialog', d => d.accept()); }
}
