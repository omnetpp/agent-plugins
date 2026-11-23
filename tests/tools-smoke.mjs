#!/usr/bin/env node
// Starts the omnetpp plugin's language server and MCP server through the launcher, as the
// harness does, and checks one round trip each: LSP initialize, and an MCP list_ned_types
// call that must find the fixture project's networks. The MCP server is started from
// another directory with the project as its argument, plus an unexpanded ${VAR} argument
// that the launcher must drop. Its copy of the project has %OPP_SMOKE_VAR% in its path, a
// variable that is set, which cmd.exe must not expand when the tool is a .cmd shim.
import { spawn } from 'node:child_process';
import { cpSync, mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const launcher = join(root, 'plugins/omnetpp/bin/opp-run.mjs');
const project = join(root, 'tests/project');
const TIMEOUT_MS = 120_000;
const percentProject = join(mkdtempSync(join(tmpdir(), 'tools-smoke-')), 'opp %OPP_SMOKE_VAR% project');
cpSync(project, percentProject, { recursive: true });
const env = { ...process.env, OPP_SMOKE_VAR: 'expanded' };

function session(args, onData, start) {
  return new Promise((resolvePromise) => {
    const child = spawn(process.execPath, [launcher, ...args], { cwd: tmpdir(), env, stdio: ['pipe', 'pipe', 'inherit'] });
    let buf = '';
    const finish = (result) => {
      clearTimeout(timer);
      child.kill();
      resolvePromise(result);
    };
    const timer = setTimeout(() => finish({ ok: false, detail: 'timeout' }), TIMEOUT_MS);
    child.on('exit', (code) => finish({ ok: false, detail: `exited with ${code}` }));
    child.stdout.on('data', (d) => {
      buf += d;
      buf = onData(buf, child, finish);
    });
    start(child);
  });
}

const lsp = await session(
  ['lsp', '--stdio'],
  (buf, _child, finish) => {
    const m = buf.match(/Content-Length: (\d+)\r\n\r\n/);
    if (!m) return buf;
    const start = m.index + m[0].length;
    if (buf.length < start + Number(m[1])) return buf;
    const msg = JSON.parse(buf.slice(start, start + Number(m[1])));
    finish({ ok: Boolean(msg.result?.capabilities), detail: 'initialize answered' });
    return '';
  },
  (child) => {
    const body = JSON.stringify({
      jsonrpc: '2.0',
      id: 1,
      method: 'initialize',
      params: { processId: null, rootUri: pathToFileURL(project).href, capabilities: {} },
    });
    child.stdin.write(`Content-Length: ${Buffer.byteLength(body)}\r\n\r\n${body}`);
  },
);

const send = (child, msg) => child.stdin.write(`${JSON.stringify(msg)}\n`);
const mcp = await session(
  ['ide_mcp', percentProject, '${UNEXPANDED_VAR}'],
  (buf, child, finish) => {
    const lines = buf.split('\n');
    for (const line of lines.slice(0, -1)) {
      const msg = JSON.parse(line);
      if (msg.id === 1) {
        send(child, { jsonrpc: '2.0', method: 'notifications/initialized' });
        send(child, { jsonrpc: '2.0', id: 2, method: 'tools/call', params: { name: 'list_ned_types', arguments: {} } });
      } else if (msg.id === 2) {
        const text = msg.result?.content?.[0]?.text ?? '';
        finish({ ok: text.includes('"Clean"') && text.includes('"Broken"'), detail: 'list_ned_types answered' });
      }
    }
    return lines.at(-1);
  },
  (child) =>
    send(child, {
      jsonrpc: '2.0',
      id: 1,
      method: 'initialize',
      params: { protocolVersion: '2025-06-18', capabilities: {}, clientInfo: { name: 'tools-smoke', version: '0' } },
    }),
);

let failed = 0;
for (const [name, r] of [['LSP', lsp], ['MCP', mcp]]) {
  console.log(`${r.ok ? 'ok  ' : 'FAIL'} ${name}: ${r.detail}`);
  if (!r.ok) failed++;
}
rmSync(dirname(percentProject), { recursive: true, force: true });
process.exit(failed ? 1 : 0);
