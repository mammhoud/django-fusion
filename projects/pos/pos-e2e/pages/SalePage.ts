// Page Object Model — Sale Page (POS transaction interface)
// Canonical version (merged from SalePage.ts + sale-page.ts)

import { Page, Locator } from '@playwright/test';
import { BasePage } from './BasePage';

/**
 * Sale Page (Point of Sale) — the primary transaction interface.
 *
 * Supports both selectors from the original SalePage.ts (generic CSS)
 * and the detailed getByRole/getByLabel selectors from sale-page.ts.
 *
 * Contains:
 * - Product grid / search
 * - Order type selection (dine-in, takeaway, delivery)
 * - Cart / order summary
 * - Payment buttons
 */
export class SalePage extends BasePage {
  // ── Product grid (generic / data-testid selectors) ──────────
  readonly productGrid: Locator;
  readonly productSearch: Locator;

  // ── Product grid (enhanced role/label selectors) ────────────
  readonly title: Locator;
  readonly dineInButton: Locator;
  readonly takeawayButton: Locator;
  readonly deliveryButton: Locator;
  readonly searchInput: Locator;
  readonly categoryFilter: Locator;
  readonly productCards: Locator;
  readonly addToCartButtons: Locator;

  // ── Cart ────────────────────────────────────────────────────
  readonly cartItems: Locator;
  readonly cartTotal: Locator;
  readonly increaseQtyButtons: Locator;
  readonly decreaseQtyButtons: Locator;
  readonly totalAmount: Locator;

  // ── Checkout / Payment ─────────────────────────────────────
  readonly checkoutButton: Locator;
  readonly paymentMethods: Locator;
  readonly deliveryAddressInput: Locator;
  readonly orderPanelToggle: Locator;

  constructor(page: Page) {
    super(page);

    // Generic CSS selectors (fallback for editions that don't use accessibility selectors)
    this.productGrid = page.locator('.product-grid, [data-testid="product-grid"]');
    this.productSearch = page.locator('input[placeholder*="search" i], input[placeholder*="product" i], [data-testid="product-search"]');
    this.cartTotal = page.locator('[data-testid="cart-total"], .cart-total');
    this.paymentMethods = page.locator('[data-testid="payment-methods"], .payment-methods');

    // Enhanced accessibility selectors
    this.title = page.locator('h1, h2').first();
    this.dineInButton = page.getByRole('button', { name: /dine.?in/i });
    this.takeawayButton = page.getByRole('button', { name: /takeaway/i });
    this.deliveryButton = page.getByRole('button', { name: /delivery/i });
    this.searchInput = page.getByPlaceholder(/search products/i);
    this.categoryFilter = page.getByLabel(/category filter/i);
    this.productCards = page.locator('.card--glass').filter({ has: page.locator('h3') });
    this.addToCartButtons = page.getByLabel(/add to cart/i);

    // Cart selectors (both generic and enhanced)
    this.cartItems = page.locator('.cart-item, [data-testid="cart-item"]');
    this.increaseQtyButtons = page.getByLabel(/increase quantity/i);
    this.decreaseQtyButtons = page.getByLabel(/decrease quantity/i);
    this.totalAmount = page.locator('text=/total amount/i').locator('..');

    // Checkout selectors
    this.checkoutButton = page.locator(
      'button:has-text("Checkout"), button:has-text("Pay"), button:has-text("Place Order"), [data-testid="checkout-btn"]'
    );
    this.deliveryAddressInput = page.getByPlaceholder(/delivery address/i);
    this.orderPanelToggle = page.getByLabel(/show order panel|hide order panel/i);
  }

  async goto(): Promise<void> {
    await super.goto('/sale');
    await this.waitForLoad();
  }

  // ── Order type ──────────────────────────────────────────────

  async selectDineIn(): Promise<void> {
    await this.dineInButton.click();
  }

  async selectTakeaway(): Promise<void> {
    await this.takeawayButton.click();
  }

  async selectDelivery(): Promise<void> {
    await this.deliveryButton.click();
  }

  // ── Product search ──────────────────────────────────────────

  /** Search for a product by name (generic search input) */
  async searchProduct(query: string): Promise<void> {
    await this.productSearch.fill(query);
    await this.page.keyboard.press('Enter');
    await this.page.waitForTimeout(500);
  }

  /** Search for a product via the accessibility search input */
  async searchProductByLabel(query: string): Promise<void> {
    await this.searchInput.fill(query);
  }

  // ── Adding items to cart ────────────────────────────────────

  /** Add the nth product from the generic grid to cart */
  async addProductToCart(index: number = 0): Promise<void> {
    const btn = this.productGrid.locator('button, .add-to-cart').nth(index);
    const btnCount = await this.productGrid.locator('button, .add-to-cart').count();
    if (btnCount > index) {
      await btn.click();
    }
  }

  /** Add a product by name using the enhanced product cards */
  async addProductByName(productName: string): Promise<void> {
    const card = this.productCards.filter({ hasText: productName });
    await card.getByLabel(/add to cart/i).click();
  }

  // ── Cart quantity adjustments ───────────────────────────────

  async increaseQty(index: number): Promise<void> {
    await this.increaseQtyButtons.nth(index).click();
  }

  async decreaseQty(index: number): Promise<void> {
    await this.decreaseQtyButtons.nth(index).click();
  }

  // ── Cart status ─────────────────────────────────────────────

  /** Get number of items in cart */
  async getCartItemCount(): Promise<number> {
    return this.cartItems.count();
  }

  // ── Checkout ────────────────────────────────────────────────

  /** Click checkout */
  async checkout(): Promise<void> {
    await this.checkoutButton.click();
  }
}
