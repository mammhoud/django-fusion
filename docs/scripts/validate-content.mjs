import { readdir, readFile, stat } from 'node:fs/promises';
import path from 'node:path';

const contentRoot = path.resolve(new URL('../content/en/', import.meta.url).pathname);
const arContentRoot = path.resolve(new URL('../content/ar/', import.meta.url).pathname);

const NAV_REQUIRED_PREFIXES = [
  'guides/', 'README.md', 'ARCHITECTURE.md', 'COMMANDS.md', 'REFERENCE.md',
  'overview.md', 'project-structure.md', 'recommendations.md',
  'precis/README.md', 'pos/README.md', 'syntara/README.md',
  'loop-crm/README.md', 'libs/README.md', 'shared/README.md',
  'dev/README.md', 'features/README.md', 'ai/README.md',
  'publish/README.md', 'tests/README.md', 'startup/README.md',
  'changelogs/README.md', 'audit/README.md', 'design/README.md'
];

// Paths to EXCLUDE from navigation requirement (deep sub-pages)
const NAV_EXCLUDE_PREFIXES = [
  'guides/auth/'
];

const arGuideMap = {
  'guides/00-project-awareness.md': 'guides/project-awareness.md',
  'guides/01-quickstart.md': 'guides/quickstart.md',
  'guides/02-setup.md': 'guides/setup.md',
  'guides/03-auth.md': 'guides/auth.md',
  'guides/04-dev.md': 'guides/dev.md',
  'guides/05-deploy.md': 'guides/deployment.md',
  'guides/06-customize.md': 'guides/customize.md',
  'guides/07-clone-site.md': 'guides/clone-site.md',
  'guides/08-best-practices.md': 'guides/best-practices.md',
  'guides/09-docus.md': 'guides/docus.md',
  'guides/10-fusion-assets-health.md': 'guides/fusion-assets-health.md',
  'guides/11-tools-dashboard-auth.md': 'guides/tools-dashboard-auth.md',
  'guides/auth/webauthn-passkeys.md': 'guides/webauthn-passkeys.md',
  'guides/config-cascade.md': 'guides/config-cascade.md',
  'guides/fixture-loading.md': 'guides/fixture-loading.md',
};

async function walkDir(directory) {
  const results = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const file = path.join(directory, entry.name);
    if (entry.isDirectory()) results.push(...await walkDir(file));
    else if (/\.mdx?$/i.test(entry.name)) results.push(file);
  }
  return results;
}

const files = await walkDir(contentRoot);
const arFiles = await walkDir(arContentRoot);
const arFileSet = new Set(arFiles.map(f => path.relative(arContentRoot, f).replace(/\\/g, '/')));

const failures = [];

function needsNavCheck(relPath) {
  if (NAV_EXCLUDE_PREFIXES.some(p => relPath.startsWith(p))) return false;
  return NAV_REQUIRED_PREFIXES.some(p => relPath.startsWith(p));
}

for (const file of files) {
  const relPath = path.relative(contentRoot, file);
  const source = await readFile(file, 'utf8');
  const match = source.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n/);
  if (!match) { failures.push(`${file}: missing frontmatter`); continue; }
  const fm = match[1];
  for (const k of ['object:', 'attributes:', 'tags:', 'links:']) if (!fm.includes(k)) failures.push(`${file}: missing ${k}`);
  if (/^\s+href:/m.test(fm)) failures.push(`${file}: use Docus link field 'to', not 'href'`);
  if (needsNavCheck(relPath)) {
    if (!/^navigation:/m.test(fm)) { failures.push(`${file}: missing navigation block`); }
    else {
      const m = fm.match(/^navigation:\r?\n((?:^\s{2,}.*\r?\n)*)/m);
      if (!m) { failures.push(`${file}: navigation block malformed`); }
      else {
        const c = m[1];
        if (!/^\s{2,}title:/m.test(c)) failures.push(`${file}: navigation block missing 'title'`);
        if (!/^\s{2,}icon:/m.test(c)) failures.push(`${file}: navigation block missing 'icon'`);
      }
    }
  }
}

for (const req of [
  'README.md','ARCHITECTURE.md','COMMANDS.md','REFERENCE.md',
  'overview.md','project-structure.md','recommendations.md',
  'guides/README.md','guides/00-project-awareness.md','guides/01-quickstart.md',
  'guides/02-setup.md','guides/03-auth.md','guides/04-dev.md',
  'guides/04-dev.md','guides/05-deploy.md','guides/06-customize.md',
  'guides/07-clone-site.md','guides/08-best-practices.md',
  'guides/09-docus.md','guides/10-fusion-assets-health.md',
  'guides/11-tools-dashboard-auth.md',
  'guides/auth/README.md','guides/auth/adapter.md','guides/auth/social-login.md',
  'guides/auth/style-audit.md','guides/auth/templates.md','guides/auth/testing.md',
  'guides/auth/webauthn-passkeys.md','guides/config-cascade.md','guides/fixture-loading.md',
  'precis/README.md','precis/client/ctc-research/README.md',
  'precis/client/ctc-research/content-strategy.md','precis/client/ctc-research/publishing-and-production.md',
  'syntara/README.md','syntara/configuration.md','syntara/erd.md',
  'syntara/features.md','syntara/infrastructure.md','syntara/use-cases.md',
  'loop-crm/README.md','loop-crm/design-system.md','loop-crm/setup-and-build.md',
  'pos/README.md',
  'libs/README.md','libs/django-fusion.md',
  'shared/README.md','shared/configuration.md','shared/shared-methods.md',
  'shared/use-cases.md',
  'startup/README.md',
  'agenda/roles/README.md','agenda/roles/mahmoud-gm.md','agenda/roles/moustafa-pm.md',
  'agenda/roles/yahia-frontend.md','agenda/roles/asmaa-data.md',
  'agenda/diagrams/README.md','agenda/diagrams/api-request-flows.md',
  'agenda/diagrams/blinko-surrealdb.md','agenda/diagrams/django-loop-crm-er.md',
  'agenda/diagrams/rust-sqlite-er.md',
  'agenda/anytype-extensibility.md',
  'agenda/case-studies/INDEX.md','agenda/case-studies/api-token-management.md',
  'agenda/case-studies/ceptor-ai.md','agenda/case-studies/data-token-sync-tagging.md',
  'agenda/case-studies/django-bolt-fusion.md','agenda/case-studies/pos-multi-terminal-sync.md',
  'agenda/case-studies/pos-offline-queue.md','agenda/case-studies/pos-qr-menu.md',
  'agenda/case-studies/stripe-billing.md',
  'agenda/feature-tracking/precis-landing.md','agenda/feature-tracking/ctc-research.md',
  'agenda/feature-tracking/loop-crm.md','agenda/feature-tracking/django-fusion.md',
  'agenda/feature-tracking/portfolio.md','agenda/feature-tracking/infrastructure.md',
  'agenda/feature-tracking/precis-main.md','agenda/feature-tracking/syntara.md',
  'agenda/feature-tracking/formint-pos.md'
]) {
  let ap = req;
  if (arGuideMap[req]) ap = arGuideMap[req];
  const ex = arFileSet.has(ap) || arFileSet.has(ap.replace(/\.md$/,'/index.md'));
  let wl = false;
  for (const p of ['ai/','dev/','features/','plans/','changelogs/','audit/','design/','tests/','publish/']) if (req.startsWith(p)) { wl = true; break; }
  if (!ex && !wl) failures.push(`MISSING AR MIRROR: ${req} → content/ar/${ap}`);
}

if (failures.length) { console.error(failures.join('\n')); process.exitCode = 1; }
else console.log(`Validated ${files.length} generated English Docus documents. AR parity check passed.`);
