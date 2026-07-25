import { Page } from '@playwright/test';
import { BasePage } from './BasePage';

/**
 * Home Page (Dashboard) — the main landing page after login.
 *
 * Contains:
 * - Welcome/fusion greeting
 * - Stat cards (sales, inventory, customers, etc.)
 * - Quick action buttons
 * - Recent activity section
 */
export class HomePage extends BasePage {
  // ── Specific selectors ──────────────────────────────────
  readonly statCards;
  readonly quickActions;
  readonly fusionGreeting;

  constructor(page: Page) {
    super(page);

    this.statCards = page.locator('.stat-card, [data-testid="stat-card"]');
    this.quickActions = page.locator('.quick-action, [data-testid="quick-action"]');
    this.fusionGreeting = page.locator('[data-testid="fusion-greeting"], .fusion-greeting');
  }

  /** Navigate to home/dashboard */
  async goto(): Promise<void> {
    await super.goto('/');
    await this.waitForLoad();
  }

  /** Get count of visible stat cards */
  async getStatCardCount(): Promise<number> {
    return this.statCards.count();
  }

  /** Check if the page renders with FusionPage wrapper */
  async hasFusionWrapper(): Promise<boolean> {
    const html = await this.page.content();
    return html.includes('fusion') || html.includes('FusionPage');
  }
}
