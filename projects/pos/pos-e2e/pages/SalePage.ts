import { Page } from '@playwright/test';
import { BasePage } from './BasePage';

/**
 * Sale Page (Point of Sale) — the primary transaction interface.
 *
 * Contains:
 * - Product grid / search
 * - Cart / order summary
 * - Payment buttons
 * - Customer selection
 */
export class SalePage extends BasePage {
  readonly productGrid;
  readonly productSearch;
  readonly cartItems;
  readonly cartTotal;
  readonly checkoutButton;
  readonly paymentMethods;

  constructor(page: Page) {
    super(page);

    this.productGrid = page.locator('.product-grid, [data-testid="product-grid"]');
    this.productSearch = page.locator('input[placeholder*="search" i], input[placeholder*="product" i], [data-testid="product-search"]');
    this.cartItems = page.locator('.cart-item, [data-testid="cart-item"]');
    this.cartTotal = page.locator('[data-testid="cart-total"], .cart-total');
    this.checkoutButton = page.locator('button:has-text("Checkout"), button:has-text("Pay"), [data-testid="checkout-btn"]');
    this.paymentMethods = page.locator('[data-testid="payment-methods"], .payment-methods');
  }

  async goto(): Promise<void> {
    await super.goto('/sale');
    await this.waitForLoad();
  }

  /** Search for a product by name */
  async searchProduct(query: string): Promise<void> {
    await this.productSearch.fill(query);
    await this.page.keyboard.press('Enter');
    await this.page.waitForTimeout(500);
  }

  /** Add the nth product to cart */
  async addProductToCart(index: number = 0): Promise<void> {
    await this.productGrid.locator('button, .add-to-cart').nth(index).click();
  }

  /** Get number of items in cart */
  async getCartItemCount(): Promise<number> {
    return this.cartItems.count();
  }

  /** Click checkout */
  async checkout(): Promise<void> {
    await this.checkoutButton.click();
  }
}
