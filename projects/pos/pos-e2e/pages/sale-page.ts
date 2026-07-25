// Page Object Model — Sale Page (POS main screen)
// Path: projects/pos/pos-full/src/pages/Sale.tsx

import { Page, Locator } from '@playwright/test';

export class SalePage {
  readonly page: Page;
  readonly title: Locator;
  // Order type
  readonly dineInButton: Locator;
  readonly takeawayButton: Locator;
  readonly deliveryButton: Locator;
  // Product grid
  readonly searchInput: Locator;
  readonly categoryFilter: Locator;
  readonly productCards: Locator;
  readonly addToCartButtons: Locator;
  // Cart
  readonly cartItems: Locator;
  readonly increaseQtyButtons: Locator;
  readonly decreaseQtyButtons: Locator;
  readonly totalAmount: Locator;
  // Checkout
  readonly deliveryAddressInput: Locator;
  readonly checkoutButton: Locator;
  readonly orderPanelToggle: Locator;

  constructor(page: Page) {
    this.page = page;
    this.title = page.locator('h1, h2').first();
    this.dineInButton = page.getByRole('button', { name: /dine.?in/i });
    this.takeawayButton = page.getByRole('button', { name: /takeaway/i });
    this.deliveryButton = page.getByRole('button', { name: /delivery/i });
    this.searchInput = page.getByPlaceholder(/search products/i);
    this.categoryFilter = page.getByLabel(/category filter/i);
    this.productCards = page.locator('.card--glass').filter({ has: page.locator('h3') });
    this.addToCartButtons = page.getByLabel(/add to cart/i);
    this.cartItems = page.locator('[class*="cart"]').locator('li, .cart-item');
    this.increaseQtyButtons = page.getByLabel(/increase quantity/i);
    this.decreaseQtyButtons = page.getByLabel(/decrease quantity/i);
    this.totalAmount = page.locator('text=/total amount/i').locator('..');
    this.deliveryAddressInput = page.getByPlaceholder(/delivery address/i);
    this.checkoutButton = page.getByRole('button', { name: /checkout|place order|pay/i });
    this.orderPanelToggle = page.getByLabel(/show order panel|hide order panel/i);
  }

  async goto() { await this.page.goto('/sale'); }
  async selectDineIn() { await this.dineInButton.click(); }
  async selectTakeaway() { await this.takeawayButton.click(); }
  async selectDelivery() { await this.deliveryButton.click(); }
  async searchProduct(query: string) { await this.searchInput.fill(query); }
  async addProductToCart(productName: string) {
    const card = this.productCards.filter({ hasText: productName });
    await card.getByLabel(/add to cart/i).click();
  }
  async increaseQty(index: number) { await this.increaseQtyButtons.nth(index).click(); }
  async decreaseQty(index: number) { await this.decreaseQtyButtons.nth(index).click(); }
  async checkout() { await this.checkoutButton.click(); }
  async getCartItemCount(): Promise<number> { return this.cartItems.count(); }
}
