import { Locator, Page } from '@playwright/test';

/**
 * Base Page Object Model for all POS pages.
 *
 * Every POS page extends this with shared selectors for:
 * - SideNav (always present)
 * - PageLayout wrapper
 * - FusionPage fragment container
 * - Common action buttons
 *
 * ## Pattern
 *
 * ```ts
 * class HomePage extends BasePage {
 *   async goto() { await this.page.goto('/'); }
 *   async getDashboardCards() { return this.page.locator('.stat-card'); }
 * }
 * ```
 */
export class BasePage {
  readonly page: Page;

  // ── Layout selectors ────────────────────────────────────
  readonly sideNav: Locator;
  readonly pageLayout: Locator;
  readonly mainContent: Locator;
  readonly pageTitle: Locator;

  // ── Common UI elements ──────────────────────────────────
  readonly loadingSkeleton: Locator;
  readonly errorState: Locator;
  readonly emptyState: Locator;

  // ── Navigation ──────────────────────────────────────────
  readonly navLinks: Locator;
  readonly mobileMenuButton: Locator;

  constructor(page: Page) {
    this.page = page;

    // Layout
    this.sideNav = page.locator('nav, [data-testid="side-nav"]');
    this.pageLayout = page.locator('[data-testid="page-layout"], main');
    this.mainContent = page.locator('main, .page-content, [data-testid="main-content"]');
    this.pageTitle = page.locator('h1');

    // Common states
    this.loadingSkeleton = page.locator('.skeleton, [data-testid="loading-skeleton"]');
    this.errorState = page.locator('[data-testid="error-state"], .error-state');
    this.emptyState = page.locator('[data-testid="empty-state"], .empty-state');

    // Navigation
    this.navLinks = page.locator('nav a');
    this.mobileMenuButton = page.locator('[data-testid="mobile-menu"], .hamburger, button[aria-label="Open menu"]');
  }

  // ── Common actions ────────────────────────────────────────────

  /** Navigate to a page relative to baseURL */
  async goto(path: string = '/'): Promise<void> {
    await this.page.goto(path, { waitUntil: 'networkidle' });
  }

  /** Wait for the page to finish loading (no skeleton visible) */
  async waitForLoad(): Promise<void> {
    await this.loadingSkeleton.first().waitFor({ state: 'hidden', timeout: 15000 }).catch(() => {});
    await this.page.waitForLoadState('networkidle');
  }

  /** Check if the side navigation is visible */
  async isSideNavVisible(): Promise<boolean> {
    return this.sideNav.first().isVisible();
  }

  /** Get the current page title text */
  async getPageTitle(): Promise<string> {
    return this.pageTitle.first().textContent() ?? '';
  }

  /** Navigate using the side nav to a named page */
  async navigateTo(label: string): Promise<void> {
    await this.navLinks.filter({ hasText: label }).first().click();
    await this.waitForLoad();
  }

  /** Take a screenshot with a descriptive name */
  async screenshot(name: string): Promise<void> {
    await this.page.screenshot({ path: `screenshots/${name}.png`, fullPage: true });
  }
}
