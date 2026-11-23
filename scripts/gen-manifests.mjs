#!/usr/bin/env node
// Writes every harness manifest and marketplace catalog from plugins.json, so that the
// plugin identity, version and dependencies are stated once. Usage:
//   node scripts/gen-manifests.mjs          write the files
//   node scripts/gen-manifests.mjs --check  exit 1 if a committed file differs (CI)
// Skills are not listed anywhere: every harness discovers plugins/<name>/skills/ itself.
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const { marketplace: mkt, oppTools, plugins } = JSON.parse(
  readFileSync(join(root, 'plugins.json'), 'utf8'),
);

// Tool wiring of a plugin with "tools": true. Every tool goes through bin/opp-run.mjs (PATH
// first, then the pinned package through npx). Claude, Codex and Cursor all expand the
// ${CLAUDE_*} variables.
const LAUNCHER = '${CLAUDE_PLUGIN_ROOT}/bin/opp-run.mjs';
const NED_FILES = { '.ned': 'ned', '.msg': 'msg', '.ini': 'ini' };
const LINT_HOOK = {
  hooks: {
    PostToolUse: [
      {
        matcher: 'Edit|Write|MultiEdit|apply_patch',
        hooks: [{ type: 'command', command: `node "${LAUNCHER}" lint --agent-hook`, timeout: 120 }],
      },
    ],
  },
};
// The project directory is passed explicitly, so the server does not depend on the
// directory the harness starts it in. Codex starts plugin MCP servers in the plugin
// directory and has no such variable, so it gets no MCP from the plugin (README).
const MCP_SERVERS = {
  omnetpp: { command: 'node', args: [LAUNCHER, 'ide_mcp', '${CLAUDE_PROJECT_DIR}'] },
};

const json = (value) => `${JSON.stringify(value, null, 2)}\n`;
const author = { name: mkt.owner.name, url: mkt.owner.url };
const pluginDir = (p) => `plugins/${p.name}`;

function identity(p) {
  return {
    name: p.name,
    version: mkt.version,
    description: p.description,
    author,
    homepage: mkt.homepage,
    repository: mkt.repository,
    license: mkt.license,
    keywords: p.keywords,
  };
}

function files() {
  const out = {};

  out['.claude-plugin/marketplace.json'] = json({
    name: mkt.name,
    owner: author,
    description: mkt.description,
    plugins: plugins.map((p) => ({
      name: p.name,
      source: `./${pluginDir(p)}`,
      description: p.description,
      category: p.category,
    })),
  });

  out['.agents/plugins/marketplace.json'] = json({
    name: mkt.name,
    interface: { displayName: mkt.displayName },
    plugins: plugins.map((p) => ({
      name: p.name,
      source: { source: 'local', path: `./${pluginDir(p)}` },
      policy: { installation: 'AVAILABLE', authentication: 'ON_INSTALL' },
      category: p.category,
    })),
  });

  out['.cursor-plugin/marketplace.json'] = json({
    name: mkt.name,
    owner: author,
    plugins: plugins.map((p) => ({
      name: p.name,
      source: `./${pluginDir(p)}`,
      description: p.description,
    })),
  });

  for (const p of plugins) {
    const dir = pluginDir(p);
    // Claude Code; Devin and omp read it too. Dependencies resolve within this marketplace.
    out[`${dir}/.claude-plugin/plugin.json`] = json({
      ...identity(p),
      displayName: p.displayName,
      ...(p.dependencies.length ? { dependencies: p.dependencies } : {}),
      // The launcher's npx fallback fetches the pinned opp-tools package.
      ...(p.tools ? { network: { hosts: ['registry.npmjs.org'] } } : {}),
    });
    // Agent Plugins 1.0.0: Codex and Copilot CLI.
    out[`${dir}/plugin.json`] = json({
      $schema: 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json',
      ...identity(p),
    });
    out[`${dir}/.cursor-plugin/plugin.json`] = json({
      ...identity(p),
      skills: './skills/',
      ...(p.tools ? { mcpServers: MCP_SERVERS } : {}),
    });
    if (p.tools) {
      out[`${dir}/bin/opp-tools.json`] = json(oppTools);
      // Claude, Codex and Devin read hooks/hooks.json. Devin also reads a root hooks.json, so
      // a second copy there would run the hook twice.
      out[`${dir}/hooks/hooks.json`] = json(LINT_HOOK);
      out[`${dir}/.lsp.json`] = json({
        omnetpp: { command: 'node', args: [LAUNCHER, 'lsp', '--stdio'], extensionToLanguage: NED_FILES },
      });
      out[`${dir}/.mcp.json`] = json({ mcpServers: MCP_SERVERS });
      // Copilot CLI documents ${PLUGIN_ROOT} only for cwd, so the launcher path is relative.
      out[`${dir}/com.github.copilot/lsp.json`] = json({
        lspServers: {
          omnetpp: {
            command: 'node',
            args: ['bin/opp-run.mjs', 'lsp', '--stdio'],
            cwd: '${PLUGIN_ROOT}',
            fileExtensions: NED_FILES,
          },
        },
      });
    }
    // Antigravity prefers this file over the root plugin.json and rejects keys it does not
    // know, so it gets only the basic identity fields.
    out[`${dir}/.antigravity-plugin/plugin.json`] = json({
      name: p.name,
      version: mkt.version,
      description: p.description,
    });
  }
  return out;
}

const check = process.argv.includes('--check');
let stale = 0;
for (const [rel, content] of Object.entries(files())) {
  const path = join(root, rel);
  const current = existsSync(path) ? readFileSync(path, 'utf8') : null;
  if (current === content) continue;
  if (check) {
    console.error(`out of date: ${rel}`);
    stale++;
  } else {
    mkdirSync(dirname(path), { recursive: true });
    writeFileSync(path, content);
    console.log(`wrote ${rel}`);
  }
}
if (stale) {
  console.error('run: node scripts/gen-manifests.mjs');
  process.exit(1);
}
