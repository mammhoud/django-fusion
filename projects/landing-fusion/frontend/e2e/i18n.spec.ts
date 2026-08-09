import { expect, test } from '@playwright/test';
import { BACKEND_URL } from '../playwright.config';

/**
 * Server-side Django i18n — the backend road must render translated content
 * from the language preference, matching the Astro road's client-side
 * switching. These tests hit the Django backend directly (BACKEND_URL :8074)
 * because `/` on :3000 is the static Astro page — the server-rendered
 * Wagtail/PageHandler road lives on the backend origin.
 *
 * The language preference is persisted the same way the in-page switcher
 * does it: `localStorage['fusion-lang']` (drives the client pre-paint
 * lang/dir) plus the `django_language` cookie (drives Django's
 * LocaleMiddleware + the page-translation pipeline on the next request).
 */
test('ar preference renders the home page in RTL with Arabic hero', async ({ page }) => {
  // First visit establishes the origin and the server's default cookie.
  await page.goto(`${BACKEND_URL}/`);

  // Persist Arabic exactly as the switcher would.
  await page.evaluate(() => {
    localStorage.setItem('fusion-lang', 'ar');
    document.cookie = 'django_language=ar; path=/; max-age=31536000; SameSite=Lax';
  });

  const response = await page.goto(`${BACKEND_URL}/`);
  expect(response?.status()).toBe(200);

  // Server-rendered <html> carries lang + dir BEFORE any client script runs.
  const raw = await response!.text();
  expect(raw).toContain('<html lang="ar" dir="rtl"');

  // Client side stays consistent after the pre-paint script.
  await expect(page.locator('html')).toHaveAttribute('lang', 'ar');
  await expect(page.locator('html')).toHaveAttribute('dir', 'rtl');

  // The Arabic road renders the localized hero section (page_content.html)
  // with the translated badge, title/accent, and both CTA labels.
  const hero = page.locator('section.hero-block');
  await expect(hero).toBeVisible();
  await expect(hero.locator('.tag-marker')).toHaveText('structa.cloud · شريك المنتجات الرقمية');
  await expect(hero.locator('h1')).toContainText('منتجات رقمية تنمو مع');
  await expect(hero.locator('.btn-primary')).toHaveText('استكشف المنتجات');
  await expect(hero.locator('.btn-secondary')).toHaveText('اعمل معنا');

  // Navigation labels are translated too (PageTranslation overlay titles).
  await expect(page.locator('nav[aria-label="Mobile"]')).toContainText('الرئيسية');
});

test('ar preference renders /products/ with Arabic hero CTAs and bottom-CTA', async ({ page }) => {
  // First visit establishes the origin and the server's default cookie.
  await page.goto(`${BACKEND_URL}/`);

  // Persist Arabic exactly as the switcher would.
  await page.evaluate(() => {
    localStorage.setItem('fusion-lang', 'ar');
    document.cookie = 'django_language=ar; path=/; max-age=31536000; SameSite=Lax';
  });

  const response = await page.goto(`${BACKEND_URL}/products/`);
  expect(response?.status()).toBe(200);

  // Server-rendered <html> carries lang + dir BEFORE any client script runs.
  const raw = await response!.text();
  expect(raw).toContain('<html lang="ar" dir="rtl"');
  await expect(page.locator('html')).toHaveAttribute('dir', 'rtl');

  // The localized hero renders the translated title and both CTA labels.
  const hero = page.locator('section.hero-block');
  await expect(hero).toBeVisible();
  await expect(hero.locator('h1')).toContainText('منتجات جاهزة للنمو');
  await expect(hero.locator('.btn-primary')).toHaveText('شاهد الإصدارات');
  await expect(hero.locator('.btn-secondary')).toHaveText('تصفح المستودع');

  // The bottom-CTA block (localized_blocks.cta) renders the translated
  // banner with its own button labels.
  const cta = page.locator('section#cta');
  await expect(cta).toBeVisible();
  await expect(cta.locator('h2')).toContainText('مبني في العلن، يُسلَّم كصفحة HTML');
  await expect(cta.getByRole('link', { name: 'عرض على GitHub' })).toBeVisible();
  await expect(cta.getByRole('link', { name: 'تواصل معنا' })).toBeVisible();
});

test('without a language preference the home page stays English', async ({ page }) => {
  const response = await page.goto(`${BACKEND_URL}/`);
  expect(response?.status()).toBe(200);
  expect(await response!.text()).toContain('<html lang="en"');

  await expect(page.getByText('structa.cloud · digital product partner').first()).toBeVisible();
  await expect(page.getByText('Explore products').first()).toBeVisible();
});
