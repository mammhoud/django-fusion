// Page Object Model — KitchenDisplay Page
// Path: projects/pos/pos-full/src/pages/KitchenDisplay.tsx

import { Page, Locator } from '@playwright/test';

export class KitchenDisplayPage {
  readonly page: Page;
  readonly title: Locator;
  readonly searchInput: Locator;
  readonly clearSearchButton: Locator;
  readonly statusFilter: Locator;
  readonly ticketCards: Locator;
  readonly statusToast: Locator;

  constructor(page: Page) {
    this.page = page;
    this.title = page.locator('h1');
    this.searchInput = page.getByPlaceholder(/search.*ticket/i);
    this.clearSearchButton = page.getByLabel(/clear/i);
    this.statusFilter = page.getByLabel(/filter by status/i);
    this.ticketCards = page.locator('.card--glass');
    this.statusToast = page.locator('[role="status"]');
  }

  async goto() { await this.page.goto('/kitchen'); }
  async search(query: string) { await this.searchInput.fill(query); }
  async clearSearch() { await this.clearSearchButton.click(); }
  async filterByStatus(status: string) { await this.statusFilter.selectOption(status); }
  async getTicketCount(): Promise<number> { return this.ticketCards.count(); }
}
