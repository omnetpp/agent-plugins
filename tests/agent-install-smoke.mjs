#!/usr/bin/env node
// Installs the plugins from this checkout into the real agent CLIs (Claude Code, Codex,
// Copilot CLI), each in a throwaway HOME, and checks what the agent then reports: every
// plugin installed and enabled at the plugins.json version, the skills found in the plugin
// folders, and the hook, MCP and LSP servers where the CLI shows them. No login and no model
// call is needed. A missing CLI is skipped, or fails with --require (CI).
//
// Usage: node tests/agent-install-smoke.mjs [--require]
import { spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, mkdtempSync, readdirSync, readFileSync, rmSync } from 'node:fs';
import { join, resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const { marketplace, plugins } = JSON.parse(readFileSync(join(root, 'plugins.json'), 'utf8'));
const version = marketplace.version;
const require = process.argv.includes('--require');

const skillsOf = (dir) =>
  readdirSync(join(dir, 'skills'), { withFileTypes: true })
    .filter((e) => e.isDirectory() && existsSync(join(dir, 'skills', e.name, 'SKILL.md')))
    .map((e) => e.name);
const skills = Object.fromEntries(plugins.map((p) => [p.name, skillsOf(join(root, 'plugins', p.name))]));
const SANDBOXES = join(root, '.agent-install-smoke');
const id = (name) => `${name}@${marketplace.name}`;

// Warnings an agent prints for a layout that is intended.
const KNOWN_WARNINGS = [
  // No root mcp.json on purpose: Codex would read it too and start the MCP server in the
  // plugin folder. Codex and Copilot CLI get the MCP server from a user-level registration.
  /declares the Agent Plugins v1 \$schema, so its MCP servers are read only from "mcp\.json"/,
];

let failed = 0;
function check(label, ok, detail = '') {
  console.log(`${ok ? 'ok  ' : 'FAIL'} ${label}`);
  if (!ok) {
    if (detail) console.log(detail.trimEnd().replace(/^/gm, '    '));
    failed++;
  }
}

function sandbox(agent, extraEnv) {
  // Not under the system temp folder: Codex refuses to set up its helper binaries there.
  mkdirSync(SANDBOXES, { recursive: true });
  const home = mkdtempSync(join(SANDBOXES, `${agent}-`));
  const env = { ...process.env, HOME: home, USERPROFILE: home, XDG_CONFIG_HOME: join(home, '.config'), XDG_DATA_HOME: join(home, '.local/share') };
  for (const k of ['GH_TOKEN', 'GITHUB_TOKEN', 'COPILOT_GITHUB_TOKEN', 'ANTHROPIC_API_KEY', 'OPENAI_API_KEY']) delete env[k];
  Object.assign(env, extraEnv(home));
  for (const v of Object.values(extraEnv(home))) mkdirSync(v, { recursive: true });
  return { home, env };
}

function runner(exe, env, cwd) {
  return (...args) => {
    const r = spawnSync(exe, args, { env, cwd, encoding: 'utf8', input: '', timeout: 180_000 });
    const out = `${r.stdout ?? ''}${r.stderr ?? ''}${r.error ? `\n${r.error.message}` : ''}`;
    return { ok: r.status === 0, out };
  };
}

function step(agent, label, r) {
  const warnings = r.out.split('\n').filter((l) => /\bwarn(ing)?\b/i.test(l) && !KNOWN_WARNINGS.some((k) => k.test(l)));
  check(`${agent}: ${label}`, r.ok && !warnings.length, r.out);
  return r.out;
}

function available(exe) {
  return spawnSync(exe, ['--version'], { encoding: 'utf8' }).status === 0;
}

const AGENTS = [
  {
    label: 'Claude Code',
    exe: 'claude',
    env: (home) => ({ CLAUDE_CONFIG_DIR: join(home, 'claude') }),
    test(run) {
      step(this.label, 'adds the marketplace', run('plugin', 'marketplace', 'add', root));
      // Claude resolves dependencies, so the plugin at the end of the chain brings the rest.
      const last = plugins.at(-1).name;
      step(this.label, `installs ${last} with its dependencies`, run('plugin', 'install', id(last), '--scope', 'user'));
      const list = run('plugin', 'list').out;
      for (const p of plugins) {
        const entry = list.split('❯').find((e) => e.trim().startsWith(id(p.name))) ?? '';
        check(`${this.label}: ${id(p.name)} is installed and enabled at ${version}`, entry.includes(`Version: ${version}`) && /enabled/.test(entry), list);
        const d = run('plugin', 'details', id(p.name)).out;
        check(`${this.label}: ${p.name} has ${skills[p.name].length} skills`, d.includes(`Skills (${skills[p.name].length})`), d);
        if (p.tools) {
          check(`${this.label}: ${p.name} has the hook, the MCP server and the LSP server`,
            /Hooks \(1\)/.test(d) && /MCP servers \(1\)/.test(d) && /LSP servers \(1\)/.test(d), d);
        }
      }
    },
  },
  {
    label: 'Codex',
    exe: 'codex',
    env: (home) => ({ CODEX_HOME: join(home, 'codex') }),
    test(run, env) {
      step(this.label, 'adds the marketplace', run('plugin', 'marketplace', 'add', root));
      for (const p of plugins) step(this.label, `installs ${p.name}`, run('plugin', 'add', id(p.name)));
      const list = run('plugin', 'list').out;
      for (const p of plugins) {
        const row = new RegExp(`^${id(p.name).replace(/[.+]/g, '\\$&')}\\s+installed, enabled\\s+${version.replace(/\./g, '\\.')}\\s`, 'm');
        check(`${this.label}: ${id(p.name)} is installed and enabled at ${version}`, row.test(list), list);
        const cache = join(env.CODEX_HOME, 'plugins/cache', marketplace.name, p.name, version);
        const cached = existsSync(cache) ? skillsOf(cache) : [];
        check(`${this.label}: ${p.name} has ${skills[p.name].length} skills`, cached.length === skills[p.name].length, `in ${cache}: ${cached.join(', ')}`);
        if (p.tools) check(`${this.label}: ${p.name} has the hook`, existsSync(join(cache, 'hooks/hooks.json')), cache);
      }
    },
  },
  {
    label: 'Copilot CLI',
    exe: 'copilot',
    env: () => ({}),
    test(run) {
      step(this.label, 'adds the marketplace', run('plugin', 'marketplace', 'add', root));
      for (const p of plugins) {
        const out = step(this.label, `installs ${p.name}`, run('plugin', 'install', id(p.name)));
        check(`${this.label}: ${p.name} has ${skills[p.name].length} skills`, out.includes(`Installed ${skills[p.name].length} skills`), out);
      }
      const list = run('plugin', 'list').out;
      for (const p of plugins) {
        check(`${this.label}: ${id(p.name)} is installed and enabled at ${version}`, list.includes(`${id(p.name)} (v${version}) (enabled)`), list);
      }
      const skillList = run('skill', 'list').out;
      const missing = Object.values(skills).flat().filter((s) => !new RegExp(`^\\s*${s} - `, 'm').test(skillList));
      check(`${this.label}: every skill is listed`, !missing.length, `missing: ${missing.join(', ')}`);
      const tools = plugins.find((p) => p.tools).name;
      const lsp = run('lsp', 'list').out;
      check(`${this.label}: the LSP server comes from ${tools}`, new RegExp(`omnetpp .*\\[from ${tools}\\]`).test(lsp), lsp);
      const mcp = run('mcp', 'list').out;
      check(`${this.label}: no MCP server comes from the plugins (it is registered at user level)`, !/omnetpp/.test(mcp), mcp);
    },
  },
];

for (const a of AGENTS) {
  if (!available(a.exe)) {
    if (require) check(`${a.label}: ${a.exe} is installed`, false, `${a.exe} not found on PATH`);
    else console.log(`SKIP ${a.label}: ${a.exe} not found`);
    continue;
  }
  const { home, env } = sandbox(a.exe, a.env);
  try {
    console.log(`-- ${a.label} ${runner(a.exe, env, home)('--version').out.trim().split('\n')[0]}`);
    a.test(runner(a.exe, env, home), env);
  } finally {
    rmSync(home, { recursive: true, force: true });
  }
}
rmSync(SANDBOXES, { recursive: true, force: true });
process.exit(failed ? 1 : 0);
