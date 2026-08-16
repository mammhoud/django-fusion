#!/usr/bin/env node
/**
 * Convert hardcoded Tailwind color classes (text-slate, bg-white, border-slate, bg-teal)
 * to theme-compatible CSS variable classes (text-base-content, bg-base-100, border-base-300, bg-primary)
 *
 * Run: node scripts/convert-colors.mjs
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');

// Files to process (skip already-converted files and print-specific files)
const FILES = [
  // Pages
  'src/pages/Reports.tsx',
  'src/pages/Inventory.tsx',
  'src/pages/Transactions.tsx',
  'src/pages/Settings.tsx',
  'src/pages/Employees.tsx',
  'src/pages/Recipes.tsx',
  'src/pages/About.tsx',
  'src/pages/ProductManager.tsx',
  'src/pages/TaxReports.tsx',
  'src/pages/Analytics.tsx',
  'src/pages/Suppliers.tsx',
  'src/pages/Customers.tsx',
  'src/pages/Payroll.tsx',
  'src/pages/SupportChat.tsx',
  'src/pages/EmployeeSchedule.tsx',
  'src/pages/Home.tsx',
  'src/pages/Auth.tsx',
  // Components
  'src/components/KeyboardShortcutsModal.tsx',
  'src/components/DatePicker.tsx',
  'src/components/DataTable.tsx',
  'src/components/ConfirmDialog.tsx',
  'src/components/ComparisonTable.tsx',
  'src/components/ProductCard.tsx',
  'src/components/Modal.tsx',
  'src/components/LanguageToggle.tsx',
  'src/components/BackButton.tsx',
  'src/components/Skeleton.tsx',
  'src/components/ChatSupport.tsx',
  'src/components/ThemeToggle.tsx',
  'src/components/PageLayout.tsx',
  'src/components/StatCard.tsx',
];

// Comprehensive replacement patterns ordered from most specific to least specific
const replacements = [
  // ===== TEXT COLORS =====
  // Full dark-mode pairs
  [/text-slate-900 dark:text-white/g, 'text-base-content'],
  [/text-slate-800 dark:text-white/g, 'text-base-content'],
  [/text-slate-700 dark:text-gray-300/g, 'text-base-content/80'],
  [/text-slate-600 dark:text-white\/60/g, 'text-base-content/60'],
  [/text-slate-600 dark:text-white\/70/g, 'text-base-content/70'],
  [/text-slate-600 dark:text-gray-300/g, 'text-base-content/70'],
  [/text-slate-600 dark:text-gray-400/g, 'text-base-content/60'],
  [/text-slate-500 dark:text-gray-400/g, 'text-base-content/50'],
  [/text-slate-500 dark:text-slate-400/g, 'text-base-content/50'],
  [/text-slate-400 dark:text-slate-500/g, 'text-base-content/40'],
  [/text-slate-400 dark:text-white\/60/g, 'text-base-content/40'],
  [/text-slate-300 dark:text-gray-300/g, 'text-base-content/30'],

  // ===== BORDER COLORS =====
  [/border-slate-300 dark:border-white\/10/g, 'border-base-300/50'],
  [/border-slate-200 dark:border-gray-600/g, 'border-base-300/50'],
  [/border-slate-200 dark:border-gray-700/g, 'border-base-300/50'],
  [/border-slate-200 dark:border-white\/20/g, 'border-base-300/30'],
  [/border-slate-200 dark:border-white\/10/g, 'border-base-300/30'],

  // ===== BACKGROUND COLORS =====
  [/bg-white\/60 dark:bg-slate-800\/60/g, 'bg-base-100/60'],
  [/bg-white\/60 dark:bg-white\/10/g, 'bg-base-100/60'],
  [/bg-white\/70 dark:bg-white\/10/g, 'bg-base-100/70'],
  [/bg-white\/70 dark:bg-slate-800\/70/g, 'bg-base-100/70'],
  [/bg-white\/50 dark:bg-white\/5/g, 'bg-base-100/50'],
  [/bg-white\/95 dark:bg-slate-900\/95/g, 'bg-base-100/95'],
  [/bg-white dark:bg-slate-800/g, 'bg-base-100'],
  [/bg-white\/30 dark:bg-white\/5/g, 'bg-base-100/30'],
  [/bg-white\/20 dark:bg-white\/10/g, 'bg-base-100/20'],
  [/bg-slate-200 dark:bg-slate-700/g, 'bg-base-300/50'],
  [/bg-slate-100\/50 dark:bg-slate-800\/30/g, 'bg-base-200/50'],
  [/bg-slate-100 dark:bg-slate-800/g, 'bg-base-200/50'],
  [/bg-slate-100\/50 dark:bg-white\/5/g, 'bg-base-200/50'],
  [/bg-slate-100\/80 dark:bg-white\/5/g, 'bg-base-200/80'],
  [/bg-slate-100 dark:bg-white\/[0-9]+/g, 'bg-base-200/50'],

  // ===== TEAL -> PRIMARY =====
  [/bg-teal-100 dark:bg-teal-900\/30/g, 'bg-primary/10'],
  [/bg-teal-100 dark:bg-teal-900\/20/g, 'bg-primary/10'],
  [/bg-teal-100\/70 dark:bg-teal-900\/20/g, 'bg-primary/10'],
  [/bg-teal-50 dark:bg-teal-500\/10/g, 'bg-primary/5'],
  [/bg-teal-500/g, 'bg-primary'],
  [/text-teal-600 dark:text-teal-400/g, 'text-primary'],
  [/text-teal-700 dark:text-teal-300/g, 'text-primary'],
  [/text-teal-500 dark:text-teal-300/g, 'text-primary'],
  [/text-teal-400 dark:text-teal-300/g, 'text-primary'],
  [/border-teal-300 dark:border-teal-700\/50/g, 'border-primary/30'],
  [/border-teal-500 bg-teal-50 dark:bg-teal-500\/10 text-teal-700 dark:text-teal-300/g, 'border-primary bg-primary/5 text-primary'],

  // ===== HOVER STATES =====
  [/hover:bg-slate-100 dark:hover:bg-white\/5/g, 'hover:bg-base-200/50'],
  [/hover:bg-slate-100 dark:hover:bg-white\/20/g, 'hover:bg-base-200/50'],
  [/hover:bg-slate-200 dark:hover:bg-slate-600/g, 'hover:bg-base-300/80'],
  [/hover:bg-slate-300 dark:hover:bg-slate-600/g, 'hover:bg-base-300/80'],
  [/hover:bg-teal-500\/20 dark:hover:bg-teal-500\/30/g, 'hover:bg-primary/20'],
  [/hover:bg-teal-500\/20/g, 'hover:bg-primary/20'],
  [/hover:bg-teal-500\/5/g, 'hover:bg-primary/5'],
  [/hover:bg-teal-50 dark:hover:bg-primary\/20/g, 'hover:bg-primary/10'],
  [/hover:bg-teal-500/g, 'hover:bg-primary'],
  [/hover:text-teal-600/g, 'hover:text-primary'],
  [/hover:border-teal-400/g, 'hover:border-primary'],
  [/hover:border-teal-300 dark:hover:border-teal-500\/50/g, 'hover:border-primary/50'],

  // ===== STANDALONE COLORS (no dark variant) =====
  // These need careful handling - only replace when NOT part of a dark: variant
  // We'll handle these separately below
];

const standaloneReplacements = [
  // Standalone text-slate-* that aren't followed by "dark:"
  // These are handled by scanning for "text-slate-X" not followed by "dark:"
  [/'text-slate-500'/g, "'text-base-content/50'"],
  [/'text-slate-400'/g, "'text-base-content/40'"],
  [/'text-slate-600'/g, "'text-base-content/60'"],
  [/"text-slate-500"/g, '"text-base-content/50"'],
  [/"text-slate-400"/g, '"text-base-content/40"'],
  [/"text-slate-600"/g, '"text-base-content/60"'],
  [/text-slate-500\)/g, 'text-base-content/50)'],
  [/text-slate-400\)/g, 'text-base-content/40)'],
  [/text-slate-600\)/g, 'text-base-content/60)'],
];

let totalReplacements = 0;
const changedFiles = [];

for (const filePath of FILES) {
  const fullPath = path.resolve(root, filePath);
  if (!fs.existsSync(fullPath)) {
    console.log(`Skipping (not found): ${filePath}`);
    continue;
  }

  let content = fs.readFileSync(fullPath, 'utf8');
  const original = content;
  let fileCount = 0;

  // Apply multi-word dark-mode replacements first
  for (const [pattern, replacement] of replacements) {
    const before = content;
    content = content.replace(pattern, replacement);
    if (content !== before) {
      const matches = (before.match(pattern) || []).length;
      fileCount += matches;
    }
  }

  // Apply standalone replacements (for text-slate-* without dark: variants)
  // But be careful - only replace standalone instances
  for (const [pattern, replacement] of standaloneReplacements) {
    const before = content;
    content = content.replace(pattern, replacement);
    if (content !== before) {
      const matches = (before.match(pattern) || []).length;
      fileCount += matches;
    }
  }

  if (content !== original) {
    fs.writeFileSync(fullPath, content, 'utf8');
    totalReplacements += fileCount;
    changedFiles.push({ file: filePath, count: fileCount });
    console.log(`✓ ${filePath}: ${fileCount} replacements`);
  } else {
    // Still write to confirm no changes
    console.log(`– ${filePath}: no changes`);
  }
}

console.log(`\n✅ Done! ${totalReplacements} total replacements across ${changedFiles.length} files.`);
