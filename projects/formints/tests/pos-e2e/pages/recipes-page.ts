// Page Object Model — Recipes Page
// Path: projects/pos/pos-full/src/pages/Recipes.tsx

import { Page, Locator } from '@playwright/test';

export class RecipesPage {
  readonly page: Page;
  readonly title: Locator;
  // Summary
  readonly totalRecipesStat: Locator;
  readonly productsUsedStat: Locator;
  readonly avgCostStat: Locator;
  readonly avgProfitStat: Locator;
  // Recipe list
  readonly searchInput: Locator;
  readonly recipeCards: Locator;
  readonly addRecipeButton: Locator;
  readonly editButtons: Locator;
  readonly deleteButtons: Locator;
  // Modal
  readonly formModal: Locator;
  readonly qtyInput: Locator;
  readonly unitInput: Locator;
  readonly submitButton: Locator;
  readonly statusToast: Locator;

  constructor(page: Page) {
    this.page = page;
    this.title = page.locator('h1');
    this.totalRecipesStat = page.locator('text=/total recipes/i').locator('..').locator('p');
    this.productsUsedStat = page.locator('text=/products used/i').locator('..').locator('p');
    this.avgCostStat = page.locator('text=/avg.*cost/i').locator('..').locator('p');
    this.avgProfitStat = page.locator('text=/avg.*profit/i').locator('..').locator('p');
    this.searchInput = page.getByPlaceholder(/search/i);
    this.recipeCards = page.locator('.card--glass');
    this.addRecipeButton = page.getByRole('button', { name: /add recipe|new recipe/i });
    this.editButtons = page.getByTitle(/edit/i);
    this.deleteButtons = page.getByTitle(/delete/i);
    this.formModal = page.locator('[role="dialog"], form');
    this.qtyInput = page.getByPlaceholder(/quantity/i).or(page.getByPlaceholder('qty'));
    this.unitInput = page.getByPlaceholder(/unit/i);
    this.submitButton = page.getByRole('button', { name: /save|add|update/i });
    this.statusToast = page.locator('[role="status"]');
  }

  async goto() { await this.page.goto('/recipes'); }
  async search(query: string) { await this.searchInput.fill(query); }
  async clickAdd() { await this.addRecipeButton.click(); }
  async clickEdit(name: string) {
    const card = this.recipeCards.filter({ hasText: name });
    await card.getByTitle(/edit/i).click();
  }
  async clickDelete(name: string) {
    const card = this.recipeCards.filter({ hasText: name });
    await card.getByTitle(/delete/i).click();
  }
  async submit() { await this.submitButton.click(); }
  async confirmDelete() { this.page.once('dialog', d => d.accept()); }
}
