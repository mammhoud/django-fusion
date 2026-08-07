import puppeteer from 'puppeteer';
(async () => {
  const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox', '--disable-setuid-sandbox'] });
  const page = await browser.newPage();
  await page.goto('http://127.0.0.1:3000/', { waitUntil: 'networkidle0' });
  const h1Info = await page.evaluate(() => {
    const h1 = document.querySelector('h1');
    if (!h1) return null;
    const text = h1.innerText;
    const style = window.getComputedStyle(h1);
    const rect = h1.getBoundingClientRect();
    const parent = h1.parentElement;
    const parentRect = parent ? parent.getBoundingClientRect() : null;
    return {
      text,
      textAlign: style.textAlign,
      marginLeft: style.marginLeft,
      marginRight: style.marginRight,
      rect,
      parentRect
    };
  });
  console.log(JSON.stringify(h1Info, null, 2));
  await browser.close();
})();
