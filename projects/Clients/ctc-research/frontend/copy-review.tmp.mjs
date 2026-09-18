import { chromium } from '@playwright/test';
const browser = await chromium.launch();
const targets = [
  ['home', '/'],
  ['home-ar', '/?lang=ar'],
  ['home-sv', '/?lang=sv'],
  ['about', '/about/'],
  ['about-ar', '/about/?lang=ar'],
  ['courses', '/courses/'],
  ['courses-fr', '/courses/?lang=fr'],
];
for (const [name, url] of targets) {
  const page = await browser.newPage();
  await page.goto('https://ctc-research.com' + url, { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(1500);
  // hero
  const h1 = (await page.locator('h1').first().innerText().catch(()=>'')).replace(/\s+/g,' ').trim();
  const heroIntro = (await page.locator('.hero__intro').first().innerText().catch(()=>'')).replace(/\s+/g,' ').trim().slice(0,90);
  const heroBadge = (await page.locator('.hero__eyebrow').first().innerText().catch(()=>'')).trim();
  const cta1 = (await page.locator('.hero__actions a').first().innerText().catch(()=>'')).replace(/\s+/g,' ').trim().slice(0,40);
  // sliders
  const sliderHeading = (await page.locator('#home-slider-title').innerText().catch(()=>'')).trim();
  const sliderIntro = (await page.locator('.home-slider p.max-w-md').first().innerText().catch(()=>'')).replace(/\s+/g,' ').trim().slice(0,90);
  const courseHeading = (await page.locator('#course-slider-title').innerText().catch(()=>'')).trim();
  const courseIntro = (await page.locator('.course-slider__head .max-w-xl').first().innerText().catch(()=>'')).replace(/\s+/g,' ').trim().slice(0,90);
  // about mission
  const aboutMission = (await page.locator('[data-localized-block="mission"]').first().innerText().catch(()=>'')).replace(/\s+/g,' ').trim().slice(0,120);
  const dir = await page.locator('html').getAttribute('dir');
  console.log(`\n=== ${name} (${dir}) ===`);
  console.log(`H1:    ${h1}`);
  console.log(`Badge: ${heroBadge}`);
  console.log(`Intro: ${heroIntro}`);
  console.log(`CTA1:  ${cta1}`);
  console.log(`Slider:${sliderHeading} | ${sliderIntro}`);
  console.log(`Course:${courseHeading} | ${courseIntro}`);
  if (name.startsWith('about')) console.log(`About: ${aboutMission}`);
  await page.close();
}
await browser.close();
