// Page Object Model — About Page
// Path: projects/pos/pos-full/src/pages/About.tsx

import { Page, Locator } from '@playwright/test';

export class AboutPage {
  readonly page: Page;
  readonly title: Locator;
  // Contact form
  readonly nameInput: Locator;
  readonly emailInput: Locator;
  readonly subjectInput: Locator;
  readonly messageInput: Locator;
  readonly submitButton: Locator;
  // Version info
  readonly versionInfo: Locator;

  constructor(page: Page) {
    this.page = page;
    this.title = page.locator('h2').first();
    this.nameInput = page.getByPlaceholder(/name/i);
    this.emailInput = page.getByPlaceholder(/email/i);
    this.subjectInput = page.getByPlaceholder(/subject/i);
    this.messageInput = page.getByPlaceholder(/message/i);
    this.submitButton = page.getByRole('button', { name: /send|submit/i });
    this.versionInfo = page.locator('text=/version/i');
  }

  async goto() { await this.page.goto('/about'); }
  async fillContactForm(data: { name: string; email: string; subject: string; message: string }) {
    await this.nameInput.fill(data.name);
    await this.emailInput.fill(data.email);
    await this.subjectInput.fill(data.subject);
    await this.messageInput.fill(data.message);
  }
  async submit() { await this.submitButton.click(); }
}
