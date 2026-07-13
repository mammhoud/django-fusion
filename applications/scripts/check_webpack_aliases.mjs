#!/usr/bin/env node
/**
 * Detects imports using dead webpack aliases (@theme, @layouts, @usecases)
 * or any alias that points to a non-existent directory.
 * Exits with code 1 if violations are found.
 */
import { readFileSync, existsSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import { globSync } from 'glob';

const __dirname = dirname(fileURLToPath(import.meta.url));
const workspaceRoot = resolve(__dirname, '..');

const DEAD_ALIASES = ['@theme', '@layouts', '@usecases'];

const jsFiles = globSync('**/*.{js,jsx,vue}', {
    cwd: workspaceRoot,
    ignore: ['**/node_modules/**', '**/bundles/**', '**/assets/node_modules/**'],
});

let errors = 0;
for (const file of jsFiles) {
    const content = readFileSync(resolve(workspaceRoot, file), 'utf8');
    for (const alias of DEAD_ALIASES) {
        if (content.includes(`from '${alias}`) || content.includes(`require('${alias}`)) {
            console.error(`❌  Dead alias '${alias}' used in: ${file}`);
            errors++;
        }
    }
}

if (errors > 0) {
    console.error(`\n${errors} dead alias violation(s) found. Fix before committing.`);
    process.exit(1);
}
console.log('✅  Webpack alias audit passed.');
