/**
 * migrate-card-component.mjs — v4
 *
 * Finds all multi-line `<element ... className="card bg-base-100 ..." ... >`
 * patterns and replaces them with `<Card ...>`.
 *
 * Builds a replacement plan first, then applies bottom-up.
 */

import { readFileSync, writeFileSync } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');

const FILES = [
  'src/pages/Sale.tsx',
  'src/pages/Inventory.tsx',
  'src/pages/Analytics.tsx',
  'src/pages/Transactions.tsx',
  'src/pages/ProductManager.tsx',
  'src/pages/Employees.tsx',
  'src/pages/Recipes.tsx',
  'src/pages/Customers.tsx',
  'src/pages/About.tsx',
  'src/pages/Roles.tsx',
  'src/pages/InvoicePage.tsx',
  'src/pages/EmployeeSchedule.tsx',
  'src/pages/Payroll.tsx',
  'src/pages/Suppliers.tsx',
  'src/components/DatePicker.tsx',
  'src/components/DataTable.tsx',
  'src/pages/Settings.tsx',
  'src/pages/Reports.tsx',
];

function parseCardClasses(classStr) {
  const parts = classStr.trim().split(/\s+/);
  const props = {};
  const extras = [];
  const baseProvided = new Set(['card', 'bg-base-100', 'shadow-sm', 'rounded-xl']);
  let i = 0;
  while (i < parts.length) {
    const p = parts[i];
    if (baseProvided.has(p)) { i++; continue; }
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
    if (p === 'transition-colors' || p === 'transition-shadow' || (p === 'transition-all' && !props.hover)) { props.transitional = true; i++; continue; }
    if (p.startsWith('duration-')) { i++; continue; }
    if (p.startsWith('space-y-')) { props.spaceY = p.slice(8); i++; continue; }
    if (p === 'border' && i+1 < parts.length && (parts[i+1]==='border-base-200'||parts[i+1]==='border-base-300')) { props.border = parts[i+1].slice(12); i+=2; continue; }
    extras.push(p); i++;
  }
  return { props, extras: extras.join(' ') };
}

function buildCardTag(props, extras, indent) {
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

function processFile(relativePath) {
  const fullPath = path.resolve(ROOT, relativePath);
  const content = readFileSync(fullPath, 'utf-8');
  const lines = content.split('\n');

  // Build list of replacements: { startIdx, endIdx, replacementLines[] }
  const repls = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const cm = line.match(/^(\s*)className="(card bg-base-100(?:[^"]*))"/);
    if (!cm) continue;

    const indent = cm[1];
    const classStr = cm[2];

    // Find the closing `>` of the opening tag
    let openEndIdx = i;
    // Check lines after i for the `>`
    if (!line.trim().endsWith('>')) {
      for (let j = i + 1; j < Math.min(lines.length, i + 8); j++) {
        openEndIdx = j;
        if (lines[j].trim() === '>' || lines[j].trim().endsWith('>')) break;
      }
    }

    // Find the opening <element tag (walk backward from i)
    let openStartIdx = i;
    let tagName = 'div';
    for (let j = i; j >= Math.max(0, i - 15); j--) {
      const tm = lines[j].match(/^(\s*)<(\w+(?:\.\w+)?)\b/);
      if (tm) { tagName = tm[2]; openStartIdx = j; break; }
    }

    // Find the closing tag </tagName> at same indent
    let closeIdx = -1;
    for (let j = openEndIdx + 1; j < lines.length; j++) {
      const cl = lines[j].trimEnd();
      if (cl === `${indent}</${tagName}>`) { closeIdx = j; break; }
      if (tagName === 'motion.div') {
        if (cl === `${indent}</motion.div>`) { closeIdx = j; break; }
        if (cl.endsWith('</motion.div>')) { closeIdx = j; break; }
      }
    }

    if (closeIdx === -1) {
      console.warn(`  ⚠️  Cannot find closing tag for ${tagName} at line ${i + 1}`);
      continue;
    }

    // Build replacement
    const { props, extras } = parseCardClasses(classStr);
    const cardOpen = buildCardTag(props, extras, indent);
    const cardClose = `${indent}</Card>`;

    // Preserve any animation/event attrs from the original opening tag
    // Look for initial/animate/exit/onClick/onSubmit/onMouseLeave in the tag range
    const preservedAttrs = [];
    for (let j = openStartIdx; j <= openEndIdx; j++) {
      const l = lines[j];
      const anims = l.match(/(\b(initial|animate|exit|layoutId|key|onClick|onSubmit|onMouseLeave|onChange|onFocus)=\{[^}]+\})/g);
      if (anims) preservedAttrs.push(...anims);
    }
    // Don't preserve className and common framer-motion attrs that set initial/animate on the wrapper
    // Actually for Card we keep the opening tag simple — animation attrs go on inner elements

    repls.push({
      startIdx: openStartIdx,
      endIdx: closeIdx,
      openTag: cardOpen,
      closeTag: cardClose,
      preserveAttrs: preservedAttrs,
    });
  }

  if (repls.length === 0) {
    console.log(`➖ ${relativePath}: no card patterns found`);
    return { modified: false, cardsFound: 0 };
  }

  // Apply replacements bottom-up (to keep indices stable)
  let newContent = content;
  repls.sort((a, b) => b.startIdx - a.startIdx); // reverse order

  for (const repl of repls) {
    // Get the original text range from the original content
    // But we need the CURRENT content, which may have been modified by prior replacements
    const currentLines = newContent.split('\n');
    // Re-find the opening tag in the current content
    // Actually, since we process bottom-up, earlier replacements (higher indices) don't affect later ones (lower indices)
    
    const blockStart = repl.startIdx;
    const blockEnd = repl.endIdx;
    
    // Build new lines
    const newLines = [];
    // Preserve any animation/event attributes on the Card tag
    let openLine = repl.openTag;
    if (repl.preserveAttrs.length > 0) {
      // Insert them before the closing >
      openLine = openLine.replace('>', ' ' + repl.preserveAttrs.join(' ') + '>');
    }
    newLines.push(openLine);

    // Lines between opening and closing tags are content (preserved)
    for (let j = blockStart + 1; j < blockEnd; j++) {
      newLines.push(currentLines[j]);
    }

    newLines.push(repl.closeTag);

    // Splice
    currentLines.splice(blockStart, blockEnd - blockStart + 1, ...newLines);
    newContent = currentLines.join('\n');
  }

  writeFileSync(fullPath, newContent + '\n');
  console.log(`✅ ${relativePath}: ${repls.length} cards migrated`);
  return { modified: true, cardsFound: repls.length };
}

console.log('=== Migrating card bg-base-100 → <Card> (v4 — bottom-up) ===\n');
let total = 0, files = 0;
for (const f of FILES) {
  const r = processFile(f);
  if (r.cardsFound > 0) { files++; total += r.cardsFound; }
}
console.log(`\n=== Done: ${total} cards migrated across ${files} files ===`);
