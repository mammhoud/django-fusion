import { chromium } from 'playwright';

const baseURL = 'https://ctc-research.com';
const locales = [
  { code: 'en', expectTitle: 'Send us a message', expectLabel: 'Full Name', expectBtn: 'Send Message' },
  { code: 'ar', expectTitle: 'اتصل بنا', expectLabel: 'الاسم الكامل', expectBtn: 'إرسال الرسالة' },
  { code: 'de', expectTitle: 'Kontaktieren Sie uns', expectLabel: 'Vollständiger Name', expectBtn: 'Nachricht senden' },
  { code: 'es', expectTitle: 'Contáctenos', expectLabel: 'Nombre completo', expectBtn: 'Enviar mensaje' },
  { code: 'fr', expectTitle: 'Contactez-nous', expectLabel: 'Nom complet', expectBtn: 'Envoyer le message' },
  { code: 'pt-br', expectTitle: 'Contate-Nos', expectLabel: 'Nome completo', expectBtn: 'Enviar mensagem' },
  { code: 'sv', expectTitle: 'Kontakta oss', expectLabel: 'Namn', expectBtn: 'Skicka meddelande' },
];

const browser = await chromium.launch();
let failures = 0;
for (const t of locales) {
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));
  page.on('requestfailed', (r) => { if (!r.url().includes('favicon')) errors.push(`REQFAIL ${r.url()}`); });
  const url = `${baseURL}/contact/?lang=${t.code}`;
  await page.goto(url, { waitUntil: 'networkidle', timeout: 45000 }).catch(() => {});
  const body = (await page.locator('body').innerText().catch(() => '')).replace(/\n+/g, ' | ');
  // Labels may be CSS-uppercased in innerText — compare case-insensitively.
  const bodyNorm = body.toLowerCase();
  const has = (s) => bodyNorm.includes(s.toLowerCase());
  const checks = {
    title: has(t.expectTitle),
    label: has(t.expectLabel),
    btn: has(t.expectBtn),
  };
  const ok = Object.values(checks).every(Boolean) && errors.length === 0;
  if (!ok) failures++;
  console.log(`${ok ? '✅' : '❌'} ${t.code}: title=${checks.title} label=${checks.label} btn=${checks.btn} errors=${errors.length}${errors.length ? ' :: ' + errors.slice(0, 3).join(' ;; ') : ''}`);
  await page.close();
}
await browser.close();
console.log(failures === 0 ? '\nALL PASS' : `\n${failures} FAILURES`);
process.exit(failures === 0 ? 0 : 1);