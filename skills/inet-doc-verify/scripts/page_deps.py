#!/usr/bin/env python3
"""List the commits that can invalidate a showcase/tutorial page.

Usage: page_deps.py PAGE_DIR... [--since REV] [--until REV] [--inet-root R]
                    [--max-indirect N] [--json]

--since defaults to the page's ".. verified-commit:" comment, else to the tag
v<version>.0 of its "Verified with INET version" line.

Output per page (Markdown):
  1. commits touching the page directory itself (someone edited the showcase)
  2. commits that changed this page's rows in tests/fingerprint/*.csv (the
     simulation's behavior changed and the baseline was re-recorded)
  3. DIRECT commits: files implementing the NED types the page names
     (:ned: roles, :par: declarers, the page's own NED submodule types,
     ini typename values)
  4. INDIRECT commits: directories of every type reachable from those through
     submodules / extends / like-defaults (compound modules pull in a lot)
The lists are the input to the diff-driven review; empty lists 1-3 mean the
page has nothing to re-read.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nedindex import NedIndex, parse_rst, parse_ini  # noqa: E402


def git(root, *args):
    return subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True)


def rel(root, p):
    try:
        return str(Path(p).resolve().relative_to(Path(root).resolve()))
    except ValueError:
        return str(p)


def resolve_since(root, rst):
    page = parse_rst(rst)
    if page['verified_commit']:
        return page['verified_commit'], 'verified-commit comment'
    if page['stamp']:
        tags = git(root, 'tag', '-l', f'v{page["stamp"]}*', '--sort=version:refname').stdout.split()
        if tags:
            return tags[-1], f'latest tag for "Verified with INET version: {page["stamp"]}"'
    return None, None


def direct_types(index, page_dir, rst):
    page = parse_rst(rst)
    names, why = set(), {}

    def add(n, reason):
        n = n.split('.')[-1]
        if index.has_type(n) and n in index.types:
            names.add(n)
            why.setdefault(n, reason)

    for r in page['roles']:
        if r['role'] == 'ned':
            add(r['target'], f':ned: role, line {r["line"]}')
        elif r['role'] == 'par':
            pname = r['target'].split('.')[-1]
            if re.fullmatch(r'\w+', pname):
                for t in index.types_declaring(pname):
                    add(t.name, f':par:`{pname}` line {r["line"]}')
    for ned in page_dir.rglob('*.ned'):
        for t in index.types.values():
            if Path(t.file).resolve() == ned.resolve():
                for u in t.uses:
                    add(u, f'used by {ned.name}')
    for ini in page_dir.rglob('*.ini'):
        if 'results' in ini.parts:
            continue
        entries, _ = parse_ini(ini)
        for e in entries:
            if e['kind'] == 'typename':
                v = e['value'].strip().strip('"')
                if v and '$' not in v:
                    add(v, f'typename in {ini.name}:{e["line"]}')
    return names, why


def closure(index, start):
    seen, stack = set(start), list(start)
    while stack:
        t = index.types.get(stack.pop())
        if not t:
            continue
        for u in t.uses:
            if u in index.types and u not in seen:
                seen.add(u)
                stack.append(u)
    return seen - set(start)


def commits(root, rng, paths, with_files=False):
    if not paths:
        return []
    r = git(root, 'log', '--format=%h%x00%ad%x00%s', '--date=short', rng, '--', *paths)
    out = []
    for line in r.stdout.splitlines():
        h, d, s = line.split('\0')
        c = {'sha': h, 'date': d, 'subject': s}
        if with_files:
            f = git(root, 'show', '--format=', '--name-only', h, '--', *paths)
            c['files'] = f.stdout.split()
        out.append(c)
    return out


def fingerprint_commits(root, rng, page_rel):
    """Commits whose diff of the fingerprint CSVs adds/removes rows naming this page's directory."""
    csvs = [str(p) for p in (root / 'tests' / 'fingerprint').glob('*.csv')]
    r = git(root, 'log', '--format=%h%x00%ad%x00%s', '--date=short', '-p', rng, '--', *csvs)
    out, cur = [], None
    for line in r.stdout.splitlines():
        if '\0' in line:
            h, d, s = line.split('\0')
            cur = {'sha': h, 'date': d, 'subject': s, 'rows': 0}
        elif cur and line[:1] in '+-' and line[:3] not in ('+++', '---') and ('/' + page_rel + '/' in line or '/' + page_rel + ',' in line):
            cur['rows'] += 1
            if cur['rows'] == 1:
                out.append(cur)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('pages', nargs='+')
    ap.add_argument('--inet-root', default=os.environ.get('INET_ROOT'))
    ap.add_argument('--since')
    ap.add_argument('--until', default='HEAD')
    ap.add_argument('--max-indirect', type=int, default=40)
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    root = Path(args.inet_root or git(Path(args.pages[0]).resolve(), 'rev-parse', '--show-toplevel').stdout.strip()).resolve()
    page_dirs = [Path(p).resolve() for p in args.pages]
    index = NedIndex().scan([root / 'src', root / 'showcases', root / 'tutorials'] + page_dirs)

    results = []
    for page_dir in page_dirs:
        rst = page_dir / 'doc' / 'index.rst'
        page_rel = rel(root, page_dir)
        res = {'page': page_rel}
        results.append(res)
        if not rst.exists():
            res['error'] = 'no doc/index.rst'
            continue
        since, origin = (args.since, 'command line') if args.since else resolve_since(root, rst)
        if not since:
            page = parse_rst(rst)
            res['error'] = ('page has no "Verified with INET version" line; pass --since' if not page['stamp']
                            else f'no verified-commit comment and no tag v{page["stamp"]}*; pass --since')
            continue
        if git(root, 'rev-parse', '-q', '--verify', since + '^{commit}').returncode:
            res['error'] = f'--since {since} is not a commit'
            continue
        rng = f'{since}..{args.until}'
        res.update({'since': since, 'since_origin': origin, 'until': args.until})

        direct, why = direct_types(index, page_dir, rst)
        indirect = closure(index, direct)
        direct_paths = sorted({rel(root, f) for t in direct for f in index.source_files(t)})
        indirect_dirs = sorted({str(Path(rel(root, index.types[t].file)).parent) for t in indirect})

        res['direct_types'] = {t: why[t] for t in sorted(direct)}
        res['indirect_type_count'] = len(indirect)
        res['page_commits'] = commits(root, rng, [page_rel])
        res['fingerprint_commits'] = fingerprint_commits(root, rng, page_rel)
        res['direct_commits'] = commits(root, rng, direct_paths, with_files=True)
        res['indirect_commits'] = commits(root, rng, indirect_dirs)

    if args.json:
        print(json.dumps(results, indent=1))
        return

    for res in results:
        print(f'# {res["page"]}')
        if 'error' in res:
            print(f'ERROR: {res["error"]}\n')
            continue
        print(f'range: {res["since"]}..{res["until"]}  (since = {res["since_origin"]})')
        print(f'direct types: {len(res["direct_types"])}, transitive types: {res["indirect_type_count"]}')
        n = (len(res['page_commits']), len(res['fingerprint_commits']), len(res['direct_commits']), len(res['indirect_commits']))
        print(f'commits: page {n[0]}, fingerprint rows {n[1]}, direct {n[2]}, indirect {n[3]}\n')
        if not any(n):
            print('NOTHING CHANGED in the dependency set: deterministic checks alone decide this page.\n')
            continue
        for title, key in (('Page directory commits', 'page_commits'), ('Fingerprint-row commits', 'fingerprint_commits')):
            if res[key]:
                print(f'## {title}')
                for c in res[key]:
                    print(f'- {c["sha"]} {c["date"]} {c["subject"]}')
                print()
        if res['direct_commits']:
            print('## Direct commits (files implementing types the page names)')
            for c in res['direct_commits']:
                print(f'- {c["sha"]} {c["date"]} {c["subject"]}')
                for f in c.get('files', []):
                    print(f'    {f}')
            print()
        if res['indirect_commits']:
            shown = res['indirect_commits'][:args.max_indirect]
            print(f'## Indirect commits ({len(res["indirect_commits"])}, showing {len(shown)}; directories of submodule types)')
            for c in shown:
                print(f'- {c["sha"]} {c["date"]} {c["subject"]}')
            print()
        print('## Direct types and why')
        for t, w in res['direct_types'].items():
            print(f'- {t}: {w}')
        print()


if __name__ == '__main__':
    main()
