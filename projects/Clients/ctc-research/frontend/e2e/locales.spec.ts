import { expect, test } from '@playwright/test';

const LOCALES = ['en', 'sv', 'fr', 'de', 'es', 'ar', 'pt-br'] as const;

test.describe('CTC Research localized About page', () => {
  for (const locale of LOCALES) {
    test(`${locale} returns localized API content and matching document metadata`, async ({ page, request }) => {
      const apiResponse = await request.get(`/apis/pages/about/?lang=${locale}`);
      expect(apiResponse.status(), `${locale} API should return 200`).toBe(200);
      const api = await apiResponse.json();
      expect(api.language).toBe(locale);
      expect(api.title).toBeTruthy();
      expect(api.available_languages).toEqual(expect.arrayContaining([...LOCALES]));

      await page.goto(`/about/?lang=${locale}`, { waitUntil: 'networkidle' });
      await expect(page.locator('html')).toHaveAttribute('lang', locale);
      await expect(page.locator('html')).toHaveAttribute('dir', locale === 'ar' ? 'rtl' : 'ltr');
      if (locale !== 'en') {
        await expect(page.locator('html')).toHaveAttribute('data-localized-ready', locale, { timeout: 60_000 });
      }
      await expect(page.locator('h1').first()).toContainText(api.title, { timeout: 60_000 });
      await expect(page.locator('[data-localized-block="mission"]')).toBeVisible();

      if (locale === 'ar') {
        const firstMission = api.mission_values?.[0]?.text || '';
        await expect(page.locator('body')).toContainText(firstMission);
      }
    });
  }
});

test.describe('CTC Research localized Team page', () => {
  for (const locale of LOCALES) {
    test(`${locale} hydrates header, section title, and member bios`, async ({ page, request }) => {
      const apiResponse = await request.get(`/apis/pages/team/?lang=${locale}`);
      expect(apiResponse.status(), `${locale} team API should return 200`).toBe(200);
      const api = await apiResponse.json();
      expect(api.language).toBe(locale);
      const teamTitle = api.team_title;
      expect(teamTitle).toBeTruthy();
      const members = api.team_members || [];
      expect(members.length).toBeGreaterThanOrEqual(3);

      await page.goto(`/team/?lang=${locale}`, { waitUntil: 'networkidle' });
      await expect(page.locator('html')).toHaveAttribute('lang', locale);
      await expect(page.locator('html')).toHaveAttribute('dir', locale === 'ar' ? 'rtl' : 'ltr');
      await expect(page.locator('html')).toHaveAttribute('data-localized-ready', locale, { timeout: 60_000 });

      // Header + section title hydrate to the localized Wagtail copy.
      await expect(page.locator('.page-header__title').first()).toContainText(teamTitle, { timeout: 60_000 });
      await expect(page.locator('.team__header .page-section__title').first()).toContainText(teamTitle, { timeout: 60_000 });

      // Member cards swap to localized names/roles/bios.
      await expect(page.locator('.team__card').first()).toBeVisible({ timeout: 60_000 });
      if (locale !== 'en') {
        const firstBio = members[0]?.bio;
        if (firstBio) {
          await expect(page.locator('.team__card').first()).toContainText(firstBio, { timeout: 60_000 });
        }
      }
    });
  }
});

test.describe('CTC Research localized Events page', () => {
  for (const locale of LOCALES) {
    test(`${locale} hydrates header and event cards`, async ({ page, request }) => {
      const apiResponse = await request.get(`/apis/pages/events/?lang=${locale}`);
      expect(apiResponse.status(), `${locale} events API should return 200`).toBe(200);
      const api = await apiResponse.json();
      expect(api.language).toBe(locale);
      const heroTitle = api.hero?.title || api.title;
      expect(heroTitle).toBeTruthy();
      const events = api.events || [];
      expect(events.length).toBeGreaterThanOrEqual(1);

      await page.goto(`/events/?lang=${locale}`, { waitUntil: 'networkidle' });
      await expect(page.locator('html')).toHaveAttribute('lang', locale);
      await expect(page.locator('html')).toHaveAttribute('dir', locale === 'ar' ? 'rtl' : 'ltr');
      await expect(page.locator('html')).toHaveAttribute('data-localized-ready', locale, { timeout: 60_000 });

      // Header hydrates to the localized hero title.
      await expect(page.locator('.page-header__title').first()).toContainText(heroTitle, { timeout: 60_000 });

      // First event card shows the localized title + description.
      await expect(page.locator('.fu-event-card').first()).toBeVisible({ timeout: 60_000 });
      if (locale !== 'en') {
        const firstTitle = events[0]?.title;
        if (firstTitle) {
          await expect(page.locator('.fu-event-card').first()).toContainText(firstTitle, { timeout: 60_000 });
        }
      }
    });
  }
});

test.describe('CTC Research site-wide locale sync (courses)', () => {
  for (const locale of ['ar', 'sv', 'de'] as const) {
    test(`${locale} catalog hydrates hero + chrome from the localized payload`, async ({ page, request }) => {
      const apiResponse = await request.get(`/apis/pages/all-courses/?lang=${locale}`);
      expect(apiResponse.status(), `${locale} all-courses API should return 200`).toBe(200);
      const api = await apiResponse.json();
      const heroTitle = api.hero?.title;
      expect(heroTitle).toBeTruthy();

      await page.goto(`/courses/?lang=${locale}`, { waitUntil: 'networkidle' });
      await expect(page.locator('html')).toHaveAttribute('lang', locale);
      await expect(page.locator('html')).toHaveAttribute('dir', locale === 'ar' ? 'rtl' : 'ltr');
      await expect(page.locator('html')).toHaveAttribute('data-localized-ready', locale, { timeout: 60_000 });
      // Hero heading hydrates to the localized Wagtail hero title.
      await expect(page.locator('h1').first()).toContainText(heroTitle, { timeout: 60_000 });
    });

    test(`${locale} course detail keeps chrome translated and content rendered`, async ({ page, request }) => {
      const catalog = await (await request.get('/api/courses/?per_page=50')).json();
      const slug = catalog.data[0].slug;
      await page.goto(`/courses/${slug}/?lang=${locale}`, { waitUntil: 'networkidle' });
      await expect(page.locator('html')).toHaveAttribute('lang', locale);
      await expect(page.locator('html')).toHaveAttribute('dir', locale === 'ar' ? 'rtl' : 'ltr');
      await expect(page.locator('html')).toHaveAttribute('data-localized-ready', locale, { timeout: 60_000 });
      await expect(page.locator('.syllabus-accordion__item').first()).toBeVisible({ timeout: 60_000 });
    });
  }
});
