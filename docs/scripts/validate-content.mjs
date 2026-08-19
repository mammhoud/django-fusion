import { readdir, readFile } from 'node:fs/promises';
import path from 'node:path';

const contentRoot = path.resolve(new URL('../content/en/', import.meta.url).pathname);
const requiredKeys = ['object:', 'attributes:', 'tags:', 'links:'];
const files = [];

async function walk(directory) {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const file = path.join(directory, entry.name);
    if (entry.isDirectory()) await walk(file);
    else if (/\.mdx?$/i.test(entry.name)) files.push(file);
  }
}

await walk(contentRoot);
const failures = [];

for (const file of files) {
  const source = await readFile(file, 'utf8');
  const match = source.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n/);
  if (!match) {
    failures.push(`${file}: missing frontmatter`);
    continue;
  }

  const frontmatter = match[1];
  for (const key of requiredKeys) {
    if (!frontmatter.includes(key)) failures.push(`${file}: missing ${key}`);
  }
  if (/^\s+href:/m.test(frontmatter)) {
    failures.push(`${file}: use Docus link field 'to', not 'href'`);
  }
}

if (failures.length) {
  console.error(failures.join('\n'));
  process.exitCode = 1;
} else {
  console.log(`Validated ${files.length} generated English Docus documents.`);
}
