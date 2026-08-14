import { cp, mkdir, readdir, readFile, rm, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const docusRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const docsRoot = path.resolve(docusRoot, '..');
const contentRoot = path.join(docusRoot, 'content');
const arabicSource = path.join(docusRoot, 'ar-content');

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

await rm(contentRoot, { recursive: true, force: true });
await mkdir(path.join(contentRoot, 'en'), { recursive: true });

for (const sourceFile of await walk(docsRoot)) {
  const relative = path.relative(docsRoot, sourceFile);
  const targetRelative = relative === 'README.md' ? 'index.md' : relative;
  const targetFile = path.join(contentRoot, 'en', targetRelative);
  await mkdir(path.dirname(targetFile), { recursive: true });
  const source = await readFile(sourceFile, 'utf8');
  await writeFile(targetFile, source);
}

await cp(arabicSource, path.join(contentRoot, 'ar'), { recursive: true });
console.log('Prepared Docus content: English source tree + Arabic core guides.');
