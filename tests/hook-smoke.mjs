#!/usr/bin/env node
// Feeds post-edit hook input (Claude's Write, Codex's apply_patch) to the omnetpp plugin's
// lint hook through the launcher, and checks that a broken NED file is reported to the agent
// (exit 2) and a clean one is not (exit 0). Uses opp_lint from PATH, or the pinned package
// through npx.
import { spawnSync } from 'node:child_process';
import { mkdtempSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { delimiter, dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const launcher = join(root, 'plugins/omnetpp/bin/opp-run.mjs');
const project = join(root, 'tests/hook-smoke/project');

const write = (file) => ({ tool_name: 'Write', tool_input: { file_path: join(project, file) } });
const patch = (file) => ({
  tool_name: 'apply_patch',
  tool_input: { command: `*** Begin Patch\n*** Update File: ${file}\n@@\n-a\n+b\n*** End Patch\n` },
});

const cases = [
  { name: 'Write broken.ned', input: write('broken.ned'), code: 2, stderr: /Unknown type 'UndefinedModuleType'/ },
  { name: 'Write clean.ned', input: write('clean.ned'), code: 0 },
  { name: 'apply_patch broken.ned', input: patch('broken.ned'), code: 2, stderr: /Unknown type/ },
  { name: 'Write a non-NED file', input: write('README.md'), code: 0 },
];

let failed = 0;
for (const c of cases) {
  const input = JSON.stringify({ session_id: 'smoke', cwd: project, hook_event_name: 'PostToolUse', ...c.input });
  const r = spawnSync(process.execPath, [launcher, 'lint', '--agent-hook'], { input, encoding: 'utf8' });
  const ok = r.status === c.code && (!c.stderr || c.stderr.test(r.stderr));
  console.log(`${ok ? 'ok  ' : 'FAIL'} ${c.name}: exit ${r.status}`);
  if (!ok) {
    console.log(r.stderr);
    failed++;
  }
}
// A shell skips a file on PATH that it cannot run, and so must the launcher. Windows has no
// execute permission to test this with.
if (process.platform !== 'win32') {
  const dir = mkdtempSync(join(tmpdir(), 'hook-smoke-'));
  writeFileSync(join(dir, 'opp_lint'), '#!/bin/sh\nexit 0\n', { mode: 0o644 });
  const input = JSON.stringify({ cwd: project, ...write('broken.ned') });
  const env = { ...process.env, PATH: `${dir}${delimiter}${process.env.PATH}` };
  const r = spawnSync(process.execPath, [launcher, 'lint', '--agent-hook'], { input, encoding: 'utf8', env });
  const ok = r.status === 2;
  console.log(`${ok ? 'ok  ' : 'FAIL'} non-executable opp_lint first on PATH: exit ${r.status}`);
  if (!ok) {
    console.log(r.stderr);
    failed++;
  }
}
process.exit(failed ? 1 : 0);
