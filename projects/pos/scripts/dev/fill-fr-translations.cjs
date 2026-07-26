#!/usr/bin/env node
/**
 * scripts/fill-fr-translations.cjs
 *
 * One-shot (and re-runnable) gap-fill for `src/i18n/fr.json`.
 *
 * Reads the current French locale JSON, applies translations from the embedded
 * map for any key that's still missing, and writes the file back. Existing
 * translations are NEVER overwritten — only missing keys are inserted, so the
 * script is safe to re-run after manual edits.
 *
 * The map is sourced from the English reference (src/i18n/en.json) and follows
 * the conventions documented in `docs/i18n-gaps.md`:
 *   - Title Case for headings, sentence case otherwise
 *   - Technical terms (SKU, CRM, POS) kept in Latin script
 *   - Placeholders follow `Entrez le nom…` style
 *
 * Run with:
 *   node scripts/fill-fr-translations.cjs
 *   node scripts/fill-fr-translations.cjs --check   # exit non-zero if any key still missing
 */
'use strict';

const fs = require('fs');
const path = require('path');

const ROOT = process.env.PROJECT_ROOT || process.cwd();
const FR_PATH = path.join(ROOT, 'src', 'i18n', 'fr.json');

/** Flat keypath → French value map. Keys are dot-paths into fr.json. */
const FR = {
  // ── nav (top-level navigation labels) ──
  'nav.customers':         'Clients',
  'nav.suppliers':         'Fournisseurs',
  'nav.kitchen':           'Affichage Cuisine',
  'nav.schedule':          'Planning',
  'nav.payroll':           'Paie',
  'nav.receiptTemplates':  'Modèles de Reçus',
  'nav.taxReports':        'Rapports Fiscaux',
  'nav.roles':             'Rôles',

  // ── customers ──
  'customers.title':            'Gestion des Clients',
  'customers.addCustomer':      'Ajouter un Client',
  'customers.name':             'Nom',
  'customers.phone':            'Téléphone',
  'customers.email':            'E-mail',
  'customers.notes':            'Notes',
  'customers.points':           'points',
  'customers.noCustomers':      'Aucun client pour le moment. Ajoutez votre premier client !',
  'customers.searchPlaceholder':'Rechercher des clients...',

  // ── suppliers ──
  'suppliers.title':            'Gestion des Fournisseurs',
  'suppliers.addSupplier':      'Ajouter un Fournisseur',
  'suppliers.name':             'Nom de l\'entreprise',
  'suppliers.contactName':      'Nom du contact',
  'suppliers.phone':            'Téléphone',
  'suppliers.email':            'E-mail',
  'suppliers.address':          'Adresse',
  'suppliers.taxId':            'Numéro d\'Identification Fiscale',
  'suppliers.paymentTerms':     'Conditions de Paiement',
  'suppliers.noSuppliers':      'Aucun fournisseur pour le moment. Ajoutez votre premier fournisseur !',
  'suppliers.searchPlaceholder':'Rechercher des fournisseurs...',
  'suppliers.sortBy':           'Trier par',
  'suppliers.sortNewest':       'Plus récents',
  'suppliers.sortNameAsc':      'Nom (A→Z)',
  'suppliers.sortNameDesc':     'Nom (Z→A)',

  // ── kitchen ──
  'kitchen.title':              'Affichage Cuisine',
  'kitchen.ticket':             'Ticket',
  'kitchen.allTickets':         'Tous les Tickets',
  'kitchen.pending':            'En attente',
  'kitchen.preparing':          'En préparation',
  'kitchen.ready':              'Prêt',
  'kitchen.delivered':          'Livré',
  'kitchen.startPreparing':     'Commencer la Préparation',
  'kitchen.markReady':          'Marquer Prêt',
  'kitchen.deliver':            'Livrer',
  'kitchen.noTickets':          'Aucun ticket en cuisine.',
  'kitchen.searchPlaceholder':  'Rechercher par ticket ou note...',
  'kitchen.statusFilter':       'Filtrer par statut',

  // ── schedule ──
  'schedule.title':             'Planning des Employés',
  'schedule.addShift':          'Ajouter un Quart',
  'schedule.selectEmployee':    'Sélectionner un employé',
  'schedule.notes':             'Notes',
  'schedule.noShifts':          'Aucun quart planifié.',

  // ── payroll ──
  'payroll.title':              'Paie',
  'payroll.addPayroll':         'Ajouter une Paie',
  'payroll.selectEmployee':     'Sélectionner un employé',
  'payroll.regularHours':       'Heures Régulières',
  'payroll.overtimeHours':      'Heures Supplémentaires',
  'payroll.totalPay':           'Salaire Total',
  'payroll.noPayrolls':         'Aucun bulletin de paie.',

  // ── receiptTemplates ──
  'receiptTemplates.title':           'Modèles de Reçus',
  'receiptTemplates.addTemplate':     'Ajouter un Modèle',
  'receiptTemplates.name':            'Nom du Modèle',
  'receiptTemplates.body':            'Corps du Modèle',
  'receiptTemplates.setAsDefault':    'Définir comme modèle par défaut',
  'receiptTemplates.default':         'Par défaut',
  'receiptTemplates.noTemplates':     'Aucun modèle de reçu.',
  'receiptTemplates.searchPlaceholder':'Rechercher des modèles...',
  'receiptTemplates.sortBy':          'Trier par',
  'receiptTemplates.sortDefaultFirst':'Par défaut en premier',
  'receiptTemplates.sortNameAsc':     'Nom (A→Z)',
  'receiptTemplates.sortNameDesc':    'Nom (Z→A)',
  'receiptTemplates.sortNewest':      'Plus récents',

  // ── taxReports ──
  'taxReports.title':             'Rapports Fiscaux',
  'taxReports.addReport':         'Ajouter un Rapport',
  'taxReports.totalSales':        'Ventes Totales',
  'taxReports.totalTax':          'Taxe Totale',
  'taxReports.transactionCount':  'Nombre de Transactions',
  'taxReports.transactions':      'transactions',
  'taxReports.noReports':         'Aucun rapport fiscal.',
  'taxReports.searchPlaceholder': 'Rechercher par période ou montant...',
  'taxReports.sortBy':            'Trier par',
  'taxReports.sortNewest':        'Période (plus récente)',
  'taxReports.sortOldest':        'Période (plus ancienne)',
  'taxReports.sortSalesDesc':     'Ventes (haute → basse)',
  'taxReports.sortSalesAsc':      'Ventes (basse → haute)',

  // ── roles ──
  'roles.title':             'Rôles Utilisateurs',
  'roles.addRole':           'Ajouter un Rôle',
  'roles.name':              'Nom du Rôle',
  'roles.permissions':       'Permissions (JSON)',
  'roles.noRoles':           'Aucun rôle défini.',
  'roles.searchPlaceholder': 'Rechercher des rôles...',
  'roles.sortBy':            'Trier par',
  'roles.sortNewest':        'Plus récents',
  'roles.sortNameAsc':       'Nom (A→Z)',
  'roles.sortNameDesc':      'Nom (Z→A)',
};

/** Set obj[parts[0]][parts[1]]...[parts[n]] = value, creating intermediate objects. */
function setPath(obj, key, value) {
  const parts = key.split('.');
  let cur = obj;
  for (let i = 0; i < parts.length - 1; i++) {
    if (!cur[parts[i]] || typeof cur[parts[i]] !== 'object') cur[parts[i]] = {};
    cur = cur[parts[i]];
  }
  cur[parts[parts.length - 1]] = value;
}

function walkFilled(obj, prefix = []) {
  return Object.entries(obj || {}).flatMap(([k, v]) => {
    const path = [...prefix, k];
    if (v && typeof v === 'object' && !Array.isArray(v)) return walkFilled(v, path);
    return [path.join('.')];
  });
}

const fr = JSON.parse(fs.readFileSync(FR_PATH, 'utf8'));
const existing = new Set(walkFilled(fr));

let added = 0;
let skipped = 0;
for (const [key, value] of Object.entries(FR)) {
  if (existing.has(key)) { skipped++; continue; }
  setPath(fr, key, value);
  added++;
}

if (added > 0) {
  fs.writeFileSync(FR_PATH, JSON.stringify(fr, null, 2));
}

console.log(`\u2713 fr.json: added ${added} key(s), skipped ${skipped} (already present)`);

// Refill the set + check for any others still missing
const before = new Set(walkFilled(fr));

if (process.argv.includes('--check')) {
  const en = JSON.parse(fs.readFileSync(path.join(ROOT, 'src', 'i18n', 'en.json'), 'utf8'));
  const enKeys = new Set(walkFilled(en));
  const stillMissing = [...enKeys].filter(k => !before.has(k));
  if (stillMissing.length > 0) {
    console.error(`\u2717 ${stillMissing.length} fr key(s) still missing after fill:`);
    stillMissing.forEach(k => console.error(`    ${k}`));
    process.exit(1);
  }
  console.log('\u2713 All en keys now present in fr.json');
}
