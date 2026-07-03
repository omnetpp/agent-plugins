# Reusable scripts for INET branch cleanup

Adapt the `AREA` / filter / branch placeholders. All assume INET layout
(`tests/fingerprint/fingerprinttest`, `bin/inet_run_module_tests`, build from toplevel).

## Stale-artifact purge (run before reading any fingerprint result)

```bash
rm -f tests/fingerprint/*.UPDATED tests/fingerprint/*.ERROR tests/fingerprint/*.FAILED
```

## Change-point bracketing walk (preferred — fast)

Verifies each fingerprint change point + its parent. `CSV_GLOB`/`-m AREA`/`-F tyf` per project.

```bash
#!/bin/bash
cd <inet-root> || exit 1; BR=<branch>; LOG=/tmp/walk_cp.log; : > "$LOG"
declare -A want
for c in $(git rev-list --reverse master..$BR); do
  if git show --stat --format="" "$c" -- 'tests/fingerprint/*.csv' | grep -q '\.csv'; then
    want[$(git rev-parse "$c")]=1; want[$(git rev-parse "$c^")]=1
  fi
done
for c in $(git rev-list --reverse master..$BR); do
  full=$(git rev-parse "$c"); [ -n "${want[$full]}" ] || continue
  git checkout -q -f "$c"
  make -j"$(nproc)" MODE=debug >/tmp/b.log 2>&1 || { echo "$(git rev-parse --short $c) BUILD_FAIL" | tee -a "$LOG"; continue; }
  rm -f tests/fingerprint/*.UPDATED tests/fingerprint/*.ERROR tests/fingerprint/*.FAILED
  (cd tests/fingerprint && timeout 400 ./fingerprinttest -d -m AREA -F tyf >/tmp/r.log 2>&1); rc=$?
  if grep -q '^OK$' /tmp/r.log; then st=GREEN
  elif [ $rc -eq 124 ]; then st=TIMEOUT
  elif grep -q 'ERROR (should be PASS)' /tmp/r.log; then st="RED-ERR"
  else st="RED-FP($(grep -oE 'failures=[0-9]+' /tmp/r.log|head -1))"; fi
  echo "$(git rev-parse --short $c) $st  $(git log -1 --format=%s $c|cut -c1-50)" | tee -a "$LOG"
done
git checkout -q -f $BR; echo "DONE" | tee -a "$LOG"
```

(For a full walk, drop the `want[]` filter and iterate all commits.)

## Module tests at key commits (timeout-wrapped; rc is truth: 0=pass, 124=hang)

```bash
for c in <RO-test-sha> <other-key-shas> $(git rev-parse <branch>); do
  git checkout -q -f "$c"; make -j"$(nproc)" MODE=debug >/tmp/b.log 2>&1 || { echo "$c BUILD_FAIL"; continue; }
  (cd tests/module && timeout 200 inet_run_module_tests -f AREA >/tmp/m.log 2>&1); rc=$?
  echo "$(git rev-parse --short $c) rc=$rc $(grep -oE '[0-9]+ PASS' /tmp/m.log|tail -1)"
done
git checkout -q -f <branch>
```
Find the hanging test via `tests/module/work/<testname>/test.out` (multi-GB = infinite loop).

## Scripted rebase (interactive machinery without `-i` prompts)

`seq.py` rewrites the rebase todo (reorder lines, set `edit`/`fixup`); then drive it:
```bash
GIT_SEQUENCE_EDITOR="python3 /tmp/seq.py" GIT_EDITOR=true git rebase -i master
```
`seq.py` skeleton (swap/reorder, mark edits, fixup a commit into an earlier one):
```python
import sys
todo=sys.argv[1]; L=open(todo).read().splitlines(True)
cmd=[l for l in L if l.strip() and not l.startswith('#')]; rest=[l for l in L if l not in cmd]
def i(p): return next(k for k,l in enumerate(cmd) if l.split()[1].startswith(p))
# mark edit:        cmd[i('<sha>')]='edit '+cmd[i('<sha>')].split(' ',1)[1]
# reorder adjacent: a=i('<X>'); b=i('<Y>'); cmd[a],cmd[b]=cmd[b],cmd[a]
# fixup into prev:  ln=cmd.pop(i('<fp-sha>')); cmd.insert(i('<code-sha>')+1,'fixup '+ln.split(' ',1)[1])
open(todo,'w').writelines(cmd+rest)
```
At each `edit` stop: apply the fold/fix, purge stale `.UPDATED`, build, run suite, `cp
<file>.csv.UPDATED <file>.csv`, `git commit --amend -F <msg-with-justification>`, then
`git rebase --continue`. Resolve forward-ripple csv conflicts by re-recording at that commit.

## Reword every subject (message-only, bodies preserved)

`reword.py` reads a commit message on stdin, maps the first line via a dict, prints the new
message. Then:
```bash
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f \
  --msg-filter 'python3 /tmp/reword.py' master..<branch>
git update-ref -d refs/original/refs/heads/<branch>   # remove backup ref
git diff --stat <pre-reword-tag> <branch>             # MUST be empty (message-only)
```
Convention: `Area: category: description` — `Area` ∈ {protocol/module, `test`, `common`, …};
`category` ∈ {`fix`,`refactor`,`feature`,`test`}, omit when obvious ("Implement…", "Add … test").
