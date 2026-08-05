// Page Object Model — Analytics Page
// Path: projects/pos/pos-full/src/pages/Analytics.tsx

import { Page, Locator } from '@playwright/test';

export class AnalyticsPage {
  readonly page: Page;
  readonly title: Locator;
  // Summary cards
  readonly totalRevenue: Locator;
  readonly growthRate: Locator;
  readonly totalOrders: Locator;
  readonly avgOrderValue: Locator;
  // Charts
  readonly revenueChart: Locator;
  readonly topProductsChart: Locator;
  readonly productDistributionChart: Locator;
  readonly dailyOrdersChart: Locator;
  // Empty state
  readonly emptyState: Locator;
  // Keyboard shortcuts
  readonly shortcutHelpButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.title = page.locator('h1');
    this.totalRevenue = page.locator('.card--glass').filter({ hasText: /total revenue/i }).locator('p').last();
    this.growthRate = page.locator('.card--glass').filter({ hasText: /growth rate/i }).locator('p').last();
    this.totalOrders = page.locator('.card--glass').filter({ hasText: /total orders/i }).locator('p').last();
    this.avgOrderValue = page.locator('.card--glass').filter({ hasText: /avg.*order.*value/i }).locator('p').last();
    this.revenueChart = page.locator('.recharts-wrapper').nth(0);
    this.topProductsChart = page.locator('.recharts-wrapper').nth(1);
    this.productDistributionChart = page.locator('.recharts-wrapper').nth(2);
    this.dailyOrdersChart = page.locator('.recharts-wrapper').nth(3);
    this.emptyState = page.locator('text=/no data/i');
    this.shortcutHelpButton = page.locator('[aria-label*="shortcut"]');
  }

  async goto() { await this.page.goto('/analytics'); }
  async getRevenueValue(): Promise<string> {
    const text = await this.totalRevenue.locator('p').last().textContent();
    return text || '';
  }
  async waitForCharts() { await this.revenueChart.waitFor({ state: 'visible', timeout: 10000 }).catch(() => {}); }
}
