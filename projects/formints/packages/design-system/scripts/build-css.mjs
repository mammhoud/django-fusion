#!/usr/bin/env node

/**
 * Build script for @formints/design-system CSS
 * 
 * Combines CSS files into a single output file.
 */

import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const srcDir = join(__dirname, '..', 'src', 'css');
const distDir = join(__dirname, '..', 'dist');

// Ensure dist directory exists
mkdirSync(distDir, { recursive: true });

// CSS files to combine (in order)
const cssFiles = [
  'variables.css',
  'animations.css',
  'bezel.css',
  'motion.css',
];

// Read and combine CSS
let combinedCSS = '/* @formints/design-system — Styles */\n\n';

for (const file of cssFiles) {
  try {
    const content = readFileSync(join(srcDir, file), 'utf-8');
    combinedCSS += `/* ═══════════════════════════════════════════════════════════════════\n   ${file}\n   ═══════════════════════════════════════════════════════════════════ */\n\n`;
    combinedCSS += content + '\n\n';
  } catch (error) {
    console.error(`Error reading ${file}:`, error);
    process.exit(1);
  }
}

// Write combined CSS
const outputPath = join(distDir, 'styles.css');
writeFileSync(outputPath, combinedCSS, 'utf-8');

console.log(`✓ CSS built: ${outputPath}`);
