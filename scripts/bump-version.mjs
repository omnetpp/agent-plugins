#!/usr/bin/env node
// Sets the marketplace version (shared by all plugins) in plugins.json and regenerates the
// manifests. Claude Code keeps an installed plugin until its version changes, so every
// release must bump it. Usage:
//   node scripts/bump-version.mjs <major|minor|patch|X.Y.Z>
import { execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const file = join(root, 'plugins.json');
const arg = process.argv[2];
const data = JSON.parse(readFileSync(file, 'utf8'));
const [major, minor, patch] = data.marketplace.version.split('.').map(Number);

let next;
if (arg === 'major') next = `${major + 1}.0.0`;
else if (arg === 'minor') next = `${major}.${minor + 1}.0`;
else if (arg === 'patch') next = `${major}.${minor}.${patch + 1}`;
else if (/^\d+\.\d+\.\d+$/.test(arg ?? '')) next = arg;
else {
  console.error('usage: node scripts/bump-version.mjs <major|minor|patch|X.Y.Z>');
  process.exit(2);
}

data.marketplace.version = next;
writeFileSync(file, `${JSON.stringify(data, null, 2)}\n`);
console.log(`version ${next}`);
execFileSync(process.execPath, [join(root, 'scripts/gen-manifests.mjs')], { stdio: 'inherit' });
