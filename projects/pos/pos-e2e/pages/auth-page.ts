// Page Object Model — Auth Page
// Path: projects/pos/pos-full/src/pages/Auth.tsx

import { Page, Locator } from '@playwright/test';

export class AuthPage {
  readonly page: Page;
  // Login tab
  readonly loginEmailInput: Locator;
  readonly loginPasswordInput: Locator;
  readonly loginShowPasswordButton: Locator;
  readonly loginButton: Locator;
  // Register tab
  readonly registerTab: Locator;
  readonly registerNameInput: Locator;
  readonly registerEmailInput: Locator;
  readonly registerPasswordInput: Locator;
  readonly registerConfirmPasswordInput: Locator;
  readonly registerShowPasswordButton: Locator;
  readonly registerButton: Locator;
  // Verify
  readonly verifyInput: Locator;
  readonly verifyButton: Locator;
  // Errors
  readonly errorMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    // Login
    this.loginEmailInput = page.getByRole('textbox', { name: /email/i });
    this.loginPasswordInput = page.getByLabel(/password/i).or(page.getByPlaceholder(/password/i));
    this.loginShowPasswordButton = page.getByLabel(/show password|hide password/i).first();
    this.loginButton = page.getByRole('button', { name: /sign in|log in/i });
    // Register
    this.registerTab = page.getByRole('button', { name: /create account|register|sign up/i });
    this.registerNameInput = page.getByPlaceholder(/name/i);
    this.registerEmailInput = page.getByPlaceholder('manager@restaurant.com');
    this.registerPasswordInput = page.getByPlaceholder('••••••••').first();
    this.registerConfirmPasswordInput = page.getByPlaceholder('••••••••').last();
    this.registerShowPasswordButton = page.getByLabel(/show password|hide password/i).first();
    this.registerButton = page.getByRole('button', { name: /create account|register|sign up/i }).last();
    // Verify
    this.verifyInput = page.getByPlaceholder('000000');
    this.verifyButton = page.getByRole('button', { name: /verify/i });
    this.errorMessage = page.locator('[class*="error"], .text-red');
  }

  async goto() { await this.page.goto('/auth'); }

  // Login flow
  async login(email: string, password: string) {
    await this.loginEmailInput.fill(email);
    await this.loginPasswordInput.fill(password);
    await this.loginButton.click();
  }
  async toggleLoginPassword() { await this.loginShowPasswordButton.click(); }

  // Register flow
  async switchToRegister() { await this.registerTab.click(); }
  async register(data: { name: string; email: string; password: string; confirmPassword: string }) {
    await this.registerNameInput.fill(data.name);
    await this.registerEmailInput.fill(data.email);
    await this.registerPasswordInput.fill(data.password);
    await this.registerConfirmPasswordInput.fill(data.confirmPassword);
    await this.registerButton.click();
  }

  // Verification
  async verifyCode(code: string) {
    await this.verifyInput.fill(code);
    await this.verifyButton.click();
  }
}
