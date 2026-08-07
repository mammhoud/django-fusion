// Page Object Model — Reports Page
// Path: projects/pos/pos-full/src/pages/Reports.tsx

import { Page, Locator } from '@playwright/test';

export class ReportsPage {
  readonly page: Page;
  readonly title: Locator;
  // Tabs
  readonly overviewTab: Locator;
  readonly salesTab: Locator;
  readonly inventoryTab: Locator;
  readonly employeesTab: Locator;
  readonly transactionsTab: Locator;
  readonly productsTab: Locator;
  readonly invoicesTab: Locator;
  readonly dailyComparisonTab: Locator;
  // Export buttons
  readonly exportPdfButton: Locator;
  readonly exportExcelButton: Locator;
  // Content
  readonly reportContent: Locator;
  readonly charts: Locator;

  constructor(page: Page) {
    this.page = page;
    this.title = page.locator('h1');
    this.overviewTab = page.getByRole('button', { name: /overview/i });
    this.salesTab = page.getByRole('button', { name: /sales/i }).first();
    this.inventoryTab = page.getByRole('button', { name: /inventory/i });
    this.employeesTab = page.getByRole('button', { name: /employees/i });
    this.transactionsTab = page.getByRole('button', { name: /transactions/i });
    this.productsTab = page.getByRole('button', { name: /products/i }).first();
    this.invoicesTab = page.getByRole('button', { name: /invoices/i });
    this.dailyComparisonTab = page.getByRole('button', { name: /daily|comparison/i });
    this.exportPdfButton = page.getByRole('button', { name: /pdf/i });
    this.exportExcelButton = page.getByRole('button', { name: /excel|export/i });
    this.reportContent = page.locator('.card--glass');
    this.charts = page.locator('.recharts-wrapper');
  }

  async goto() { await this.page.goto('/reports'); }
  async switchToOverview() { await this.overviewTab.click(); }
  async switchToSales() { await this.salesTab.click(); }
  async switchToInventory() { await this.inventoryTab.click(); }
  async switchToEmployees() { await this.employeesTab.click(); }
  async switchToTransactions() { await this.transactionsTab.click(); }
  async switchToProducts() { await this.productsTab.click(); }
  async switchToInvoices() { await this.invoicesTab.click(); }
  async exportPdf() { await this.exportPdfButton.click(); }
  async exportExcel() { await this.exportExcelButton.click(); }
  async getChartCount(): Promise<number> { return this.charts.count(); }
}
