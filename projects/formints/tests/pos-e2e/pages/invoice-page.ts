// Page Object Model — Invoice Page
// Path: projects/pos/pos-full/src/pages/InvoicePage.tsx

import { Page, Locator } from '@playwright/test';

export class InvoicePage {
  readonly page: Page;
  readonly title: Locator;
  // Customer search
  readonly customerSearch: Locator;
  // Invoice items
  readonly itemRows: Locator;
  readonly itemNameInputs: Locator;
  readonly itemUnitInputs: Locator;
  readonly addItemButton: Locator;
  readonly removeItemButtons: Locator;
  // Actions
  readonly saveButton: Locator;
  readonly downloadPdfButton: Locator;
  readonly sendButton: Locator;
  readonly statusToast: Locator;

  constructor(page: Page) {
    this.page = page;
    this.title = page.locator('h1');
    this.customerSearch = page.getByPlaceholder(/search or type new/i);
    this.itemRows = page.locator('.card--glass, li[class*="invoice-item"]');
    this.itemNameInputs = page.getByPlaceholder(/item name/i);
    this.itemUnitInputs = page.getByPlaceholder('pc');
    this.addItemButton = page.getByRole('button', { name: /add item/i });
    this.removeItemButtons = page.getByLabel(/remove item/i);
    this.saveButton = page.getByRole('button', { name: /save/i });
    this.downloadPdfButton = page.getByRole('button', { name: /pdf|download/i });
    this.sendButton = page.getByRole('button', { name: /send/i });
    this.statusToast = page.locator('[role="status"]');
  }

  async goto() { await this.page.goto('/invoice'); }
  async searchCustomer(query: string) { await this.customerSearch.fill(query); }
  async addItem() { await this.addItemButton.click(); }
  async removeItem(index: number) { await this.removeItemButtons.nth(index).click(); }
  async fillItemName(index: number, name: string) { await this.itemNameInputs.nth(index).fill(name); }
  async save() { await this.saveButton.click(); }
  async downloadPdf() { await this.downloadPdfButton.click(); }
  async getItemCount(): Promise<number> { return this.itemRows.count(); }
}
