// Page Object Model — Settings Page
// Path: projects/pos/pos-full/src/pages/Settings.tsx

import { Page, Locator } from '@playwright/test';

export class SettingsPage {
  readonly page: Page;
  readonly title: Locator;
  // Tabs (Settings has sections, not tabs)
  readonly currencySelect: Locator;
  readonly currencySearch: Locator;
  readonly storeNameInput: Locator;
  readonly receiptFooterInput: Locator;
  // Password section
  readonly newPasswordInput: Locator;
  readonly confirmPasswordInput: Locator;
  readonly changePasswordButton: Locator;
  // Save
  readonly saveButton: Locator;
  readonly statusToast: Locator;

  constructor(page: Page) {
    this.page = page;
    this.title = page.locator('h1');
    this.currencySelect = page.locator('select');
    this.currencySearch = page.getByPlaceholder(/search currency/i);
    this.storeNameInput = page.getByPlaceholder(/store|name/i).first();
    this.receiptFooterInput = page.getByPlaceholder(/receipt footer/i);
    this.newPasswordInput = page.getByPlaceholder('••••••••').first();
    this.confirmPasswordInput = page.getByPlaceholder('••••••••').last();
    this.changePasswordButton = page.getByRole('button', { name: /change password|save password/i });
    this.saveButton = page.getByRole('button', { name: /save/i });
    this.statusToast = page.locator('[role="status"]');
  }

  async goto() { await this.page.goto('/settings'); }
  async selectCurrency(currency: string) { await this.currencySelect.selectOption(currency); }
  async searchCurrency(query: string) { await this.currencySearch.fill(query); }
  async changePassword(newPass: string, confirmPass: string) {
    await this.newPasswordInput.fill(newPass);
    await this.confirmPasswordInput.fill(confirmPass);
    await this.changePasswordButton.click();
  }
  async setStoreName(name: string) { await this.storeNameInput.fill(name); }
  async save() { await this.saveButton.click(); }
}
