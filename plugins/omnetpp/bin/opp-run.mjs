#!/usr/bin/env node
// Runs an @omnetpp/opp-tools command for the agent harness: opp-run.mjs <tool> [args...],
// where <tool> is lint, lsp, ide_mcp or docgen. The opp_<tool> on PATH is used when there is
// one, so a global install or the VS Code extension's shims win. Otherwise the pinned
// package version (opp-tools.json) is run through npx. Stdio is inherited and the exit
// code is passed through, because the harness talks LSP/MCP over stdio and reads the lint
// hook's exit code.
import { spawn } from 'node:child_process';
import { accessSync, constants, readFileSync, statSync } from 'node:fs';
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

// The lint hook runs after every edit of every file, so an edit that names no .ned, .msg or
// .ini file (case-sensitive, as in opp_lint) ends here, before any tool starts. The hook
// input is read up front for this and handed to the tool unchanged.
const hookInput = tool === 'lint' && args.includes('--agent-hook') ? readStdin() : undefined;
if (hookInput !== undefined && !/\.(ned|msg|ini)\b/.test(hookInput)) process.exit(0);

function readStdin() {
  try {
    return readFileSync(0, 'utf8');
  } catch {
    return '';
  }
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
function spawnTool(file, fileArgs, options) {
  if (isWindows && /\.(cmd|bat)$/i.test(file)) {
    const quote = (s) => `"${String(s).replace(/"/g, '""').replace(/%/g, '"^%"')}"`;
    const line = [file, ...fileArgs].map(quote).join(' ');
    return spawn(process.env.ComSpec ?? 'cmd.exe', ['/d', '/s', '/c', `"${line}"`], {
      ...options,
      windowsVerbatimArguments: true,
    });
  }
  return spawn(file, fileArgs, options);
}

// input: text for the tool's stdin instead of inheriting it. holdStderr: collect stderr and
// return it instead of passing it through, so that a stale shim's complaint can be dropped.
function run(file, fileArgs, { env = process.env, input, holdStderr = false } = {}) {
  return new Promise((resolve) => {
    const stdio = [input === undefined ? 'inherit' : 'pipe', 'inherit', holdStderr ? 'pipe' : 'inherit'];
    const child = spawnTool(file, fileArgs, { stdio, env });
    let stderr = '';
    child.stderr?.on('data', (d) => (stderr += d));
    if (input !== undefined) {
      child.stdin.on('error', () => {});
      child.stdin.end(input);
    }
    const forward = (sig) => child.kill(sig);
    process.on('SIGINT', forward);
    process.on('SIGTERM', forward);
    child.on('error', () => resolve({ code: NOT_FOUND, stderr }));
    child.on('close', (code, signal) => {
      process.off('SIGINT', forward);
      process.off('SIGTERM', forward);
      resolve({ code: code ?? 1, signal, stderr });
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
  // lint is not interactive, so its stderr can wait until it exits; the LSP and MCP servers
  // log to stderr while they run, so theirs passes straight through.
  const result = await run(onPath, args, { input: hookInput, holdStderr: tool === 'lint' });
  if (result.code !== NOT_FOUND) {
    // Writes to a pipe are asynchronous on Windows; exit only once the report is out.
    process.stderr.write(result.stderr, () => {
      if (result.signal) process.kill(process.pid, result.signal);
      process.exit(result.code);
    });
    await new Promise(() => {});
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
const result = await run(npx, ['--yes', '-p', `${pin.package}@${pin.version}`, command, ...args], {
  env,
  input: hookInput,
});
if (result.code === NOT_FOUND) missing(`could not run it through npx`);
if (result.signal) process.kill(process.pid, result.signal);
process.exit(result.code);
