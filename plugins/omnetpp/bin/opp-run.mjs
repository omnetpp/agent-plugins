#!/usr/bin/env node
// Runs an @omnetpp/opp-tools command for the agent harness: opp-run.mjs <tool> [args...],
// where <tool> is lint, lsp, ide_mcp or docgen. The opp_<tool> on PATH is used when there is
// one, so a global install or the VS Code extension's shims win. Otherwise the pinned
// package version (opp-tools.json) is run through npx. Stdio is inherited and the exit
// code is passed through, because the harness talks LSP/MCP over stdio and reads the lint
// hook's exit code.
import { spawn } from 'node:child_process';
import { accessSync, constants, existsSync, readFileSync, statSync } from 'node:fs';
import { delimiter, dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const TOOLS = ['lint', 'lsp', 'ide_mcp', 'docgen'];
// A PATH entry that cannot be started, or that exits with 127 (a stale shim, e.g. left behind
// by an updated VS Code extension), is treated as missing.
const NOT_FOUND = 127;
const isWindows = process.platform === 'win32';

const [tool, ...rawArgs] = process.argv.slice(2);
if (!TOOLS.includes(tool)) {
  console.error(`usage: opp-run.mjs <${TOOLS.join('|')}> [args...]`);
  process.exit(1);
}
const command = `opp_${tool}`;
// A harness that does not know a ${VAR} leaves it unexpanded; pass nothing rather than a
// literal "${CLAUDE_PROJECT_DIR}" path.
const args = rawArgs.filter((a) => !/^\$\{[A-Za-z_][A-Za-z0-9_]*\}$/.test(a));

const nodeMajor = Number(process.versions.node.split('.')[0]);
if (nodeMajor < 18) {
  console.error(`${command}: @omnetpp/opp-tools needs Node.js 18 or newer; this is ${process.version}.`);
  process.exit(1);
}

const pin = JSON.parse(readFileSync(join(dirname(fileURLToPath(import.meta.url)), 'opp-tools.json'), 'utf8'));

// Like a shell, the search skips a file that it cannot run and goes on.
function isRunnable(file) {
  try {
    if (!statSync(file).isFile()) return false;
    if (!isWindows) accessSync(file, constants.X_OK);
    return true;
  } catch {
    return false;
  }
}

function findOnPath(name) {
  const exts = isWindows ? (process.env.PATHEXT ?? '.EXE;.CMD;.BAT').split(';') : [''];
  for (const dir of (process.env.PATH ?? '').split(delimiter)) {
    if (!dir) continue;
    for (const ext of exts) {
      const file = join(dir, name + ext.toLowerCase());
      if (isRunnable(file)) return file;
    }
  }
  return null;
}

// Windows refuses to spawn .cmd/.bat files directly (npm's shims are .cmd), so they go
// through cmd.exe with each argument quoted. cmd.exe expands %VAR% also inside quotes; a %
// outside the quotes and escaped with ^ ends any variable name before it can match one.
function spawnTool(file, fileArgs, env) {
  if (isWindows && /\.(cmd|bat)$/i.test(file)) {
    const quote = (s) => `"${String(s).replace(/"/g, '""').replace(/%/g, '"^%"')}"`;
    const line = [file, ...fileArgs].map(quote).join(' ');
    return spawn(process.env.ComSpec ?? 'cmd.exe', ['/d', '/s', '/c', `"${line}"`], {
      stdio: 'inherit',
      env,
      windowsVerbatimArguments: true,
    });
  }
  return spawn(file, fileArgs, { stdio: 'inherit', env });
}

function run(file, fileArgs, env = process.env) {
  return new Promise((resolve) => {
    const child = spawnTool(file, fileArgs, env);
    const forward = (sig) => child.kill(sig);
    process.on('SIGINT', forward);
    process.on('SIGTERM', forward);
    child.on('error', (err) => resolve({ code: NOT_FOUND, err }));
    child.on('exit', (code, signal) => {
      process.off('SIGINT', forward);
      process.off('SIGTERM', forward);
      resolve({ code: code ?? 1, signal });
    });
  });
}

function missing(detail) {
  console.error(
    `${command}: ${detail}. Install the OMNeT++ command-line tools with ` +
      `"npm install -g ${pin.package}" (needs Node.js 18 or newer).`,
  );
  process.exit(1);
}

const onPath = findOnPath(command);
if (onPath) {
  const result = await run(onPath, args);
  if (result.code !== NOT_FOUND) {
    if (result.signal) process.kill(process.pid, result.signal);
    process.exit(result.code);
  }
}

const npx = findOnPath('npx');
if (!npx) missing(onPath ? `${onPath} does not work and npx was not found` : 'not found, and npx was not found');

// Quiet npm, so that nothing but the tool's own output reaches the harness (stdout carries
// the LSP/MCP protocol, stderr the lint hook's report).
const env = {
  ...process.env,
  npm_config_loglevel: 'error',
  npm_config_update_notifier: 'false',
  npm_config_fund: 'false',
  npm_config_audit: 'false',
};
const result = await run(npx, ['--yes', '-p', `${pin.package}@${pin.version}`, command, ...args], env);
if (result.code === NOT_FOUND) missing(`could not run it through npx`);
if (result.signal) process.kill(process.pid, result.signal);
process.exit(result.code);
