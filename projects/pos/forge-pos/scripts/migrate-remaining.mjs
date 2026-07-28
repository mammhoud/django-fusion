/**
 * migrate-remaining.mjs
 *
 * Migrates the remaining ~32 card bg-base-100 patterns that the v1 script
 * couldn't handle (multi-line motion.div openings).
 *
 * Strategy: read each file, find lines containing card bg-base-100,
 * determine the opening/closing tag boundaries, and replace.
 */

import { readFileSync, writeFileSync } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');

const FILES = [
  'src/pages/Analytics.tsx',
  'src/pages/Transactions.tsx',
  'src/pages/Recipes.tsx',
  'src/pages/ProductManager.tsx',
  'src/pages/Customers.tsx',
  'src/components/DatePicker.tsx',
];

function parseClasses(classStr) {
  const parts = classStr.trim().split(/\s+/);
  const props = {};
  const extras = [];
  const base = new Set(['card', 'bg-base-100', 'shadow-sm', 'rounded-xl']);
  let i = 0;
  while (i < parts.length) {
    const p = parts[i];
    if (base.has(p)) { i++; continue; }
    if (p.startsWith('shadow-') && p !== 'shadow-sm') { props.shadow = p.slice(7); i++; continue; }
    if (p === 'rounded-2xl') { props.radius = '2xl'; i++; continue; }
    if (p === 'rounded-lg') { props.radius = 'lg'; i++; continue; }
    if (p === 'rounded-xl') { i++; continue; }
    if (p === 'p-3') { props.padding = 'sm'; i++; continue; }
    if (p === 'p-4') { props.padding = 'md'; i++; continue; }
    if (p === 'p-5') { props.padding = 'lg'; i++; continue; }
    if (p === 'p-6') { props.padding = 'xl'; i++; continue; }
    if (p === 'p-8') { props.padding = '2xl'; i++; continue; }
    if (p === 'text-center') { props.center = true; i++; continue; }
    if (p === 'hover:-translate-y-0.5') { props.hover = true; while (i < parts.length && ['hover:shadow-lg','transition-all'].includes(parts[i]) || parts[i]?.startsWith('duration-')) i++; continue; }
    if (p === 'hover:shadow-lg' && !props.hover) { props.hover = true; i++; continue; }
    if (p === 'transition-colors' || p === 'transition-shadow') { props.transitional = true; i++; continue; }
    if (p === 'transition-all' && !props.hover) { props.transitional = true; i++; continue; }
    if (p.startsWith('duration-')) { i++; continue; }
    if (p.startsWith('space-y-')) { props.spaceY = p.slice(8); i++; continue; }
    if (p === 'border' && i+1 < parts.length && (parts[i+1]==='border-base-200'||parts[i+1]==='border-base-300')) { props.border = parts[i+1].slice(12); i+=2; continue; }
    extras.push(p); i++;
  }
  return { props, extras: extras.join(' ') };
}

function buildTag(props, extras, indent) {
  const attrs = [];
  if (props.padding && props.padding !== 'md') attrs.push(`padding="${props.padding}"`);
  if (props.center) attrs.push('center');
  if (props.hover) attrs.push('hover');
  if (props.transitional) attrs.push('transitional');
  if (props.spaceY) attrs.push(`spaceY="${props.spaceY}"`);
  if (props.shadow && props.shadow !== 'sm') attrs.push(`shadow="${props.shadow}"`);
  if (props.radius && props.radius !== 'xl') attrs.push(`radius="${props.radius}"`);
  const extraStr = extras.trim();
  if (extraStr) attrs.push(`className="${extraStr.replace(/"/g, '&quot;')}"`);
  return indent + (attrs.length ? `<Card ${attrs.join(' ')}>` : '<Card>');
}

let totalMigrated = 0;

for (const relPath of FILES) {
  const fullPath = path.resolve(ROOT, relPath);
  let content = readFileSync(fullPath, 'utf-8');
  const lines = content.split('\n');
  const cardRanges = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const cm = line.match(/^(\s*)className="(card bg-base-100(?:[^"]*))"/);
    if (!cm) continue;

    const indent = cm[1];
    const classStr = cm[2];

    // Find where `>` closes the opening tag
    let openEndIdx = i;
    if (!line.trim().endsWith('>')) {
      for (let j = i + 1; j < Math.min(lines.length, i + 6); j++) {
        openEndIdx = j;
        if (lines[j].trim() === '>' || lines[j].trim().endsWith('>')) break;
      }
    }

    // Find the opening <tag (walk backward)
    let openStartIdx = i;
    let tagName = 'div';
    for (let j = i; j >= Math.max(0, i - 15); j--) {
      const tm = lines[j].match(/^(\s*)<(\w+(?:\.\w+)?)\b/);
      if (tm) { tagName = tm[2]; openStartIdx = j; break; }
    }

    // Find closing tag
    let closeIdx = -1;
    for (let j = openEndIdx + 1; j < lines.length; j++) {
      const cl = lines[j].trimEnd();
      const closeMatch = cl.match(/^(\s*)<\/(\w+(?:\.\w+)?)>$/);
      if (closeMatch && closeMatch[1] === indent) { closeIdx = j; break; }
    }

    if (closeIdx === -1) {
      console.warn(`  ⚠️  ${relPath}:${i+1} — no closing tag found for ${tagName}`);
      continue;
    }

    const { props, extras } = parseClasses(classStr);
    cardRanges.push({ openStartIdx, openEndIdx, closeIdx, tagName, indent, props, extras });
  }

  if (cardRanges.length === 0) {
    console.log(`➖ ${relPath}: no patterns found`);
    continue;
  }

  // Apply replacements bottom-up to keep indices stable
  // Instead of modifying the array in place with splice, rebuild the content
  // by replacing ranges from bottom to top
  cardRanges.sort((a, b) => b.openStartIdx - a.openStartIdx);

  let newLines = [...lines];

  for (const range of cardRanges) {
    const { openStartIdx, openEndIdx, closeIdx, indent, props, extras } = range;

    const openTag = buildTag(props, extras, indent);
    const closeTag = `${indent}</Card>`;

    // Replace the opening range [openStartIdx, openEndIdx] with the Card tag
    newLines.splice(openStartIdx, openEndIdx - openStartIdx + 1, openTag);

    // Find the close tag at the new position
    // After the splice, closeIdx has shifted by (openStartIdx - openEndIdx - 1)
    // Actually, since we're going bottom-up and the ranges don't overlap,
    // this should work. But let's recalculate closeIdx.
    // The closeIdx was calculated in the original array. After the bottom-up splice,
    // indices above openStartIdx are unaffected (since we process from bottom).
    
    // Find the closing tag in the current newLines
    const adjustedCloseIdx = closeIdx - (cardRanges.indexOf(range) > 0 ? 
      // The closeIdx might need adjustment if earlier (higher-index) replacements affected it
      0 : 0);
    
    // Actually, since we process bottom-up and each range is independent,
    // the closeIdx for each range is at a higher index than its openStartIdx,
    // and ranges don't overlap in the original. So bottom-up processing means
    // the closeIdx is still valid for non-overlapping ranges.
    
    // But after the first splice (highest index range), the closeIdx of lower ranges
    // might shift because splice changes the array length.
    // Let me just search for the close tag again in the current array.
    const expectedClose = `${indent}</${range.tagName}>`;
    let foundClose = false;
    for (let j = openStartIdx + 1; j < newLines.length; j++) {
      if (newLines[j].trimEnd() === expectedClose) {
        newLines[j] = closeTag;
        foundClose = true;
        break;
      }
      // Also check for just </div> or </motion.div>
      if (newLines[j].trimEnd() === `${indent}</div>` || newLines[j].trimEnd() === `${indent}</motion.div>`) {
        newLines[j] = closeTag;
        foundClose = true;
        break;
      }
    }
    if (!foundClose) {
      console.warn(`  ⚠️  ${relPath}:${openStartIdx+1} — could not find closing tag`);
    }
  }

  writeFileSync(fullPath, newLines.join('\n') + '\n');
  console.log(`✅ ${relPath}: ${cardRanges.length} cards migrated`);
  totalMigrated += cardRanges.length;
}

console.log(`\n=== Done: ${totalMigrated} cards migrated ===`);
