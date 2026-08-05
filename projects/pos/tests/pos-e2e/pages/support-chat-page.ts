// Page Object Model — SupportChat Page
// Path: projects/pos/pos-full/src/pages/SupportChat.tsx

import { Page, Locator } from '@playwright/test';

export class SupportChatPage {
  readonly page: Page;
  readonly title: Locator;
  // Chat sections
  readonly chatMessages: Locator;
  readonly messageInput: Locator;
  readonly sendButton: Locator;
  // Tickets
  readonly ticketList: Locator;
  readonly newTicketButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.title = page.locator('h2').first();
    this.chatMessages = page.locator('[class*="chat"], [class*="message"]');
    this.messageInput = page.getByPlaceholder(/type.*message|message/i);
    this.sendButton = page.getByRole('button', { name: /send/i });
    this.ticketList = page.locator('[class*="ticket"]').locator('li');
    this.newTicketButton = page.getByRole('button', { name: /new ticket/i });
  }

  async goto() { await this.page.goto('/support'); }
  async sendMessage(text: string) {
    await this.messageInput.fill(text);
    await this.sendButton.click();
  }
  async clickNewTicket() { await this.newTicketButton.click(); }
}
