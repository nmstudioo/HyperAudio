const { chromium } = require('playwright');
const base = process.argv[2] || 'http://localhost:8765/';
const pages = ['index.html', 'compare.html', 'finder.html', 'archive.html', 'changelog.html', 'docs/index.html'];
const MAX_KB = 1500;
(async () => {
const browser = await chromium.launch();
let bad = 0;
for (const pg of pages) {
const context = await browser.newContext();
const page = await context.newPage();
try {
await page.goto(base + pg, { waitUntil: 'networkidle' });
const size = await page.evaluate(() => {
const resources = performance.getEntriesByType('resource');
const resourceBytes = resources.reduce((sum, r) => sum + (r.transferSize || 0), 0);
const domBytes = document.documentElement.outerHTML.length;
return resourceBytes + domBytes;
});
const kb = Math.round(size / 1024);
if (kb > MAX_KB) {
console.log(`FAIL budget: ${pg} is ${kb} KB (limit ${MAX_KB} KB)`);
bad++;
} else {
console.log(`OK budget: ${pg} is ${kb} KB`);
}
} catch (e) {
console.log(`LOAD FAIL ${pg}: ${e.message}`);
bad++;
}
await context.close();
}
await browser.close();
console.log(bad ? `${bad} page(s) exceeded budget` : 'budget: all pages within limits');
process.exit(bad ? 1 : 0);
})();
