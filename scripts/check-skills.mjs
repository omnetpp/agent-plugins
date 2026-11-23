#!/usr/bin/env node
// Checks the published skills against the rules in AGENTS.md. Exit 1 on any finding.
// - plugins.json and plugins/ list the same plugins; every skill folder has a SKILL.md.
// - SKILL.md frontmatter: name equals the folder name; the description says when to use it.
// - A skill names only skills of its own plugin or of the plugins it depends on. A skill of a
//   plugin that depends on it may appear only as an example or optional pointer, on a line
//   with "e.g." or "if installed". Retired skill names may not appear at all.
// - No private paths or names in anything that is published.
import { readdirSync, readFileSync, statSync } from 'node:fs';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const { plugins } = JSON.parse(readFileSync(join(root, 'plugins.json'), 'utf8'));

// Skills that left the repository or were renamed; a mention would point nowhere.
const RETIRED = [
  'omnetpp-release-engineering', 'oppenv-dev', 'rst-editing', 'asd-ste100', 'dev-working-rules',
  'generic-protocol-test-authoring', 'inet-protocol-conformance-review',
  'omnetpp-modeling', 'omnetpp-sim-debugging', 'omnetpp-coding-conventions',
  'omnetpp-fingerprint-testing', 'omnetpp-git-workflow', 'omnetpp-branch-cleanup',
  'omnetpp-branch-rebase',
];
const PRIVATE = [/\/home\/[a-z]/, /~\/(w|projects)\//, /\bai-logs\b/, /\bai-plans\b/, /\brhornig\b/i, /\bandras\b/i];
const OPTIONAL_POINTER = /\be\.g\.|if installed/i;
const WHEN_TO_USE = /\bUse\s+(when|at|before|for|together)\b/;

const findings = [];
const report = (file, line, msg) => findings.push(`${relative(root, file)}${line ? `:${line}` : ''}: ${msg}`);

const walk = (dir) =>
  readdirSync(dir).flatMap((e) => {
    const p = join(dir, e);
    return statSync(p).isDirectory() ? walk(p) : [p];
  });
const isText = (f) => /\.(md|json|mjs|js|py|sh|ya?ml|txt|ned|msg|ini)$/.test(f);
const tokenRe = (name) => new RegExp(`(?<![\\w-])${name}(?![\\w-])`);

function frontmatter(file) {
  const lines = readFileSync(file, 'utf8').split('\n');
  if (lines[0] !== '---') return null;
  const end = lines.indexOf('---', 1);
  const fm = {};
  let key = null;
  for (const l of lines.slice(1, end)) {
    const m = l.match(/^([A-Za-z][\w-]*):\s*(.*)$/);
    if (m) {
      key = m[1];
      fm[key] = m[2].replace(/^[>|]-?$/, '');
    } else if (key) fm[key] += ` ${l.trim()}`;
  }
  return fm;
}

function checkSkill(file) {
  const fm = frontmatter(file);
  if (!fm) return report(file, 0, 'no frontmatter');
  const folder = dirname(file).split('/').pop();
  if (fm.name !== folder) report(file, 0, `name "${fm.name}" differs from the folder name "${folder}"`);
  if (!fm.description?.trim()) report(file, 0, 'no description');
  else if (!WHEN_TO_USE.test(fm.description)) report(file, 0, 'the description does not say when to use the skill ("Use when ...")');
}

// Plugins and their skills.
const dirs = readdirSync(join(root, 'plugins')).filter((d) => statSync(join(root, 'plugins', d)).isDirectory());
const declared = plugins.map((p) => p.name);
for (const d of dirs) if (!declared.includes(d)) report(join(root, 'plugins', d), 0, 'plugin folder not in plugins.json');
for (const n of declared) if (!dirs.includes(n)) report(join(root, 'plugins.json'), 0, `plugin "${n}" has no folder`);

const owner = new Map();
for (const p of plugins) {
  const skillsDir = join(root, 'plugins', p.name, 'skills');
  for (const s of readdirSync(skillsDir)) {
    const file = join(skillsDir, s, 'SKILL.md');
    try {
      statSync(file);
    } catch {
      report(join(skillsDir, s), 0, 'skill folder without SKILL.md');
      continue;
    }
    owner.set(s, p.name);
    checkSkill(file);
  }
}

const deps = new Map(plugins.map((p) => [p.name, p.dependencies]));
const closure = (name, seen = new Set()) => {
  for (const d of deps.get(name) ?? []) if (!seen.has(d)) closure(d, seen.add(d));
  return seen;
};

// Cross-references and retired names, in every text file of each plugin's skills.
for (const p of plugins) {
  const reachable = closure(p.name).add(p.name);
  for (const file of walk(join(root, 'plugins', p.name, 'skills')).filter(isText)) {
    readFileSync(file, 'utf8').split('\n').forEach((line, i) => {
      for (const [skill, plugin] of owner) {
        if (reachable.has(plugin) || !tokenRe(skill).test(line)) continue;
        const downward = closure(plugin).has(p.name);
        if (!downward) report(file, i + 1, `names ${skill} (plugin ${plugin}), which ${p.name} does not depend on`);
        else if (!OPTIONAL_POINTER.test(line))
          report(file, i + 1, `names ${skill} of the dependent plugin ${plugin}; write it as an example ("e.g.") or "if installed"`);
      }
      for (const r of RETIRED) if (tokenRe(r).test(line)) report(file, i + 1, `names the retired skill ${r}`);
    });
  }
}

// Project stub skills: frontmatter only (they belong to other repositories).
for (const s of readdirSync(join(root, 'project-stubs'))) {
  const file = join(root, 'project-stubs', s, 'SKILL.md');
  try {
    statSync(file);
    checkSkill(file);
  } catch {}
}

// Private content in everything that is published.
const published = ['plugins', 'project-stubs'].flatMap((d) => walk(join(root, d))).concat(
  ['README.md', 'AGENTS.md', 'plugins.json'].map((f) => join(root, f)),
);
for (const file of published.filter(isText)) {
  readFileSync(file, 'utf8').split('\n').forEach((line, i) => {
    for (const re of PRIVATE) if (re.test(line)) report(file, i + 1, `private path or name (${re})`);
  });
}

for (const f of findings) console.error(f);
console.log(`${owner.size} skills in ${plugins.length} plugins: ${findings.length ? `${findings.length} finding(s)` : 'ok'}`);
process.exit(findings.length ? 1 : 0);
