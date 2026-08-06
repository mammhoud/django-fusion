// Probe @tabler/icons v3 export shape for sprite generation.
import * as icons from '@tabler/icons';
const names = Object.keys(icons);
console.log('total exports:', names.length);
console.log('first 10:', names.slice(0, 10).join(', '));
// Check known names
for (const n of ['cart', 'shopping-cart', 'chef-hat', 'chart-line', 'burger', 'glass', 'cup', 'x', 'check']) {
  console.log(n, '->', typeof icons[n]);
}
// Inspect one icon object
const sample = icons['cart'] ?? icons['shopping-cart'];
console.log('sample keys:', sample ? Object.keys(sample) : 'N/A');
console.log('sample:', JSON.stringify(sample).slice(0, 300));
// Try the iconNames array
console.log('iconNames type:', typeof icons.iconNames, Array.isArray(icons.iconNames) ? icons.iconNames.length : '');
console.log('has iconNames sample:', Array.isArray(icons.iconNames) ? icons.iconNames.slice(0, 5) : '');
