import { cp, mkdir, readdir, readFile, rm, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const docusRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const docsRoot = path.resolve(docusRoot, '..');
const contentRoot = path.join(docusRoot, 'content');
const arabicSource = path.join(docusRoot, 'ar-content');
const repositoryUrl = 'https://github.com/mammhoud/structa.cloud';
const repositoryBranch = 'generic';

const ignoredDirectories = new Set(['docus', 'node_modules', '.git', 'site']);
const ignoredFiles = new Set(['index.html', '_sidebar.md', '_navbar.md']);

async function walk(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    if (entry.isDirectory()) {
      if (!ignoredDirectories.has(entry.name)) {
        files.push(...(await walk(path.join(directory, entry.name))));
      }
      continue;
    }
    if (entry.isFile() && /\.mdx?$/i.test(entry.name) && !ignoredFiles.has(entry.name)) {
      files.push(path.join(directory, entry.name));
    }
  }
  return files;
}

function yamlScalar(value) {
  return JSON.stringify(String(value));
}

function routeFor(relative) {
  const normalized = relative.split(path.sep).join('/');
  if (normalized === 'README.md') return '';
  if (normalized.endsWith('/README.md')) return normalized.slice(0, -'/README.md'.length).toLowerCase();
  return normalized.replace(/\.(md|mdx)$/i, '').toLowerCase();
}

function ownerFor(relative) {
  const normalized = relative.split(path.sep).join('/');
  if (normalized.startsWith('projects/precis/precis-ctc/')) return 'precis-ctc';
  if (normalized.startsWith('projects/precis/precis-main/')) return 'precis-main';
  if (normalized.startsWith('projects/precis/precis-landing/')) return 'precis-landing';
  if (normalized.startsWith('projects/formints/')) return 'formints';
  if (normalized.startsWith('projects/syntara/')) return 'syntara';
  if (normalized.startsWith('projects/loop-crm/')) return 'loop-crm';
  if (normalized.startsWith('libs/django-fusion/')) return 'django-fusion';
  if (normalized.startsWith('applications/')) return 'infrastructure';
  if (normalized.startsWith('tests/')) return 'workspace-tests';
  if (normalized.startsWith('precis-ctc/')) return 'precis-ctc';
  if (normalized.startsWith('landing-fusion/')) return 'precis-landing';
  if (normalized.startsWith('precis/')) return 'precis-main';
  if (normalized.startsWith('pos/')) return 'formints';
  if (normalized.startsWith('syntara/')) return 'syntara';
  if (normalized.startsWith('loop-crm/')) return 'loop-crm';
  if (normalized.startsWith('libs/')) return 'django-fusion';
  if (normalized.startsWith('dev/infrastructure/')) return 'infrastructure';
  return 'workspace';
}

function tagsFor(relative) {
  const normalized = relative.split(path.sep).join('/').toLowerCase();
  const tags = ['structa-cloud', 'documentation'];
  const parts = normalized.split('/');
  const section = parts.length > 1 ? parts[0] : 'root';
  if (section !== 'root') tags.push(section.replace(/[^a-z0-9-]/g, '-'));
  for (const tag of ['architecture', 'setup', 'deployment', 'testing', 'api', 'security', 'infrastructure', 'frontend', 'backend', 'docus', 'ai', 'pos', 'precis', 'ctc']) {
    if (normalized.includes(tag)) tags.push(tag);
  }
  return [...new Set(tags)];
}

function metadataFor(relative) {
  const normalized = relative.split(path.sep).join('/');
  const route = routeFor(relative);
  const id = `docs.${route || 'index'}`.replace(/[^a-zA-Z0-9_.-]/g, '.');
  const section = normalized.includes('/') ? normalized.split('/')[0] : 'root';
  const owner = ownerFor(relative);
  const tags = tagsFor(relative);
  const metadata = [
    'object:',
    '  type: "document"',
    `  id: ${yamlScalar(id)}`,
    'attributes:',
    `  source_path: ${yamlScalar(normalized)}`,
    `  canonical_route: ${yamlScalar(`/docs/en/${route}`)}`,
    `  section: ${yamlScalar(section)}`,
    `  owner: ${yamlScalar(owner)}`,
    '  status: "maintained"',
    '  source_of_truth: "repository-markdown"',
    'tags:',
    ...tags.map((tag) => `  - ${yamlScalar(tag)}`),
    'links:',
    '  - label: "Documentation home"',
    '    to: "/docs/en/"',
    '    icon: "i-lucide-house"',
    `  - label: "Source file"\n    to: ${yamlScalar(`${repositoryUrl}/blob/${repositoryBranch}/docs/${normalized}`)}\n    icon: "i-simple-icons-github"\n    target: "_blank"`,
    `  - label: "Owner: ${owner}"\n    to: ${yamlScalar(`/docs/en/${route || ''}`)}\n    icon: "i-lucide-link"`,
  ];
  return `---\n${metadata.join('\n')}\n---\n`;
}

function addMetadata(source, relative) {
  const metadata = metadataFor(relative);
  if (source.startsWith('---\n') || source.startsWith('---\r\n')) {
    const closing = source.indexOf('\n---', 4);
    if (closing !== -1) {
      const end = closing + 4;
      const existing = source.slice(0, end);
      const body = source.slice(end).replace(/^\r?\n/, '');
      // A source document that already owns the graph block is copied exactly;
      // this prevents duplicate object/tags/link keys in generated Docus data.
      if (/^---\r?\n(?:.|\r?\n)*?^object:/m.test(existing)) return source;
      // Existing title/description/navigation frontmatter remains authoritative;
      // add the graph fields so the generated Docus document has one block.
      const graph = metadata.replace(/^---\n/, '').replace(/\n---\n$/, '').trim();
      return `${existing}\n${graph}\n---\n\n${body}`;
    }
  }
  return `${metadata}\n${source}`;
}

await rm(contentRoot, { recursive: true, force: true });
await mkdir(path.join(contentRoot, 'en'), { recursive: true });

for (const sourceFile of await walk(docsRoot)) {
  const relative = path.relative(docsRoot, sourceFile);
  const targetRelative = relative === 'README.md' ? 'index.md' : relative;
  const targetFile = path.join(contentRoot, 'en', targetRelative);
  await mkdir(path.dirname(targetFile), { recursive: true });
  const source = await readFile(sourceFile, 'utf8');
  await writeFile(targetFile, addMetadata(source, relative));
}

await cp(arabicSource, path.join(contentRoot, 'ar'), { recursive: true });
console.log('Prepared Docus content: canonical English Markdown + Arabic translations + graph metadata.');
