#!/usr/bin/env python3
"""Deterministic checks for INET showcase/tutorial pages.

Usage: check_page.py PAGE_DIR... [--inet-root R] [--since REV] [--run] [--literals] [--json]

PAGE_DIR is the directory that holds the simulation (ini/ned) and a doc/index.rst.
Checks: stamp + verified-commit comment, :ned:/:par:/:cpp:/:download: targets,
figure/image/video files, literalinclude anchors and slices (and their drift
since REV), ini parameter and typename names, optional 0-second run of every
non-abstract config. Exit code 1 when any ERROR was found.
"""
import argparse
import difflib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nedindex import NedIndex, parse_rst, parse_ini, slice_lines  # noqa: E402

CAMEL_RE = re.compile(r'^[a-z][a-z0-9]*[A-Z]\w*$')


def git(root, *args, check=False):
    r = subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True, errors='replace')
    if check and r.returncode:
        raise RuntimeError(r.stderr.strip())
    return r


class Report:
    def __init__(self, page):
        self.page = page
        self.items = []

    def add(self, level, category, where, msg, extra=None):
        self.items.append({'level': level, 'category': category, 'where': where, 'msg': msg, 'extra': extra})

    def count(self, level):
        return sum(1 for i in self.items if i['level'] == level)


def in_src(root, ident):
    """True when IDENT occurs as a whole word anywhere under src/ (C++, NED, MSG, comments)."""
    return git(root, 'grep', '-qlw', '-e', ident, '--', 'src/').returncode == 0


def unknown_name(rep, root, where, category, label, name, what):
    """Report a name that no NED file declares: WARN if src/ still mentions it, ERROR if nowhere."""
    if in_src(root, name):
        rep.add('WARN', category, where, f'{label}: "{name}" is not a NED {what}, but the word occurs in src/ (a key, field, figure attribute or result-filter parameter?)')
    else:
        rep.add('ERROR', category, where, f'{label}: "{name}" is not a NED {what} and does not occur anywhere in src/ (renamed or removed?)')


def rel(root, p):
    try:
        return str(Path(p).resolve().relative_to(Path(root).resolve()))
    except ValueError:
        return str(p)


def check_rst(rep, root, page_dir, rst_path, index, since, want_literals, stamp=True):
    page = parse_rst(rst_path)
    docdir = rst_path.parent
    loc = lambda n: f'{rel(root, rst_path)}:{n}'

    if not stamp:
        pass  # a tutorial step or other non-index file: the stamp lives in index.rst
    elif page['stamp'] is None:
        rep.add('ERROR', 'stamp', rel(root, rst_path), 'no "Verified with INET version" line')
    else:
        rep.add('INFO', 'stamp', loc(page['stamp_line']), f'verified with INET version {page["stamp"]}')
    if not stamp:
        pass
    elif page['verified_commit']:
        r = git(root, 'rev-parse', '--verify', '-q', page['verified_commit'] + '^{commit}')
        if r.returncode:
            rep.add('ERROR', 'stamp', loc(page['verified_commit_line']),
                    f'verified-commit {page["verified_commit"]} is not a commit in this repository')
        else:
            rep.add('INFO', 'stamp', loc(page['verified_commit_line']), f'verified-commit {r.stdout.strip()[:12]}')
    else:
        rep.add('WARN', 'stamp', rel(root, rst_path), 'no ".. verified-commit: <sha>" comment; diff-driven review has no base')

    for n, line in enumerate(rst_path.read_text(errors='replace').splitlines(), 1):
        if 'Source files location' in line:
            m = re.search(r'tree/[^/]+/([^>\s]+)', line)
            actual = rel(root, page_dir)
            if not m:
                rep.add('WARN', 'source-link', loc(n), 'Source files location line has no github tree URL')
            elif m.group(1).rstrip('/') != actual:
                rep.add('ERROR', 'source-link', loc(n), f'Source files location URL points at {m.group(1)}, the page lives in {actual}')
            break

    for r_ in page['roles']:
        role, target, n = r_['role'], r_['target'], r_['line']
        if role == 'ned':
            name = target.split('.')[-1]
            if not index.has_type(name):
                hint = ' (it is a parameter name: use :par:)' if index.has_param(name) else ''
                rep.add('ERROR', 'ned-ref', loc(n), f':ned:`{target}` is not a NED type in src/, showcases/ or tutorials/{hint}')
        elif role == 'par':
            if not re.fullmatch(r'[\w.\[\]*?$]+', target):
                rep.add('WARN', 'par-ref', loc(n), f':par:`{target}` holds an expression, not a parameter name')
                continue
            name = target.split('.')[-1]
            if any(ch in name for ch in '*?[') or not name:
                continue
            if not index.has_param(name):
                unknown_name(rep, root, loc(n), 'par-ref', f':par:`{target}`', name, 'parameter')
        elif role == 'cpp':
            ident = re.split(r'::|\(', target)[0].strip()
            if ident and re.fullmatch(r'\w+', ident):
                r = git(root, 'grep', '-lw', '-e', ident, '--', 'src/')
                if r.returncode:
                    rep.add('ERROR', 'cpp-ref', loc(n), f':cpp:`{target}` does not occur as a word in src/')
        elif role == 'download':
            p = (docdir / target).resolve()
            if not p.exists():
                rep.add('ERROR', 'download', loc(n), f':download: target missing: {target}')

    for d in page['directives']:
        kind, arg, opts, n = d['kind'], d['arg'], d['options'], d['line']
        if kind in ('figure', 'image', 'video', 'include'):
            if not arg:
                continue
            p = (docdir / arg).resolve()
            if not p.exists():
                note = ' (doc/media is a symlink into the separate media tree)' if (docdir / 'media').is_symlink() else ''
                rep.add('ERROR', kind, loc(n), f'{kind} file missing: {arg}{note}')
            elif kind == 'video' and p.stat().st_size == 0:
                rep.add('ERROR', kind, loc(n), f'video file is empty: {arg}')
        elif kind == 'literalinclude':
            p = (docdir / arg).resolve()
            if not p.exists():
                rep.add('ERROR', 'literalinclude', loc(n), f'included file missing: {arg}')
                continue
            src_lines = p.read_text(errors='replace').splitlines()
            lines, err = slice_lines(src_lines, opts)
            if err:
                rep.add('ERROR', 'literalinclude', loc(n), f'{arg}: {err}')
                continue
            if not lines or not any(l.strip() for l in lines):
                rep.add('ERROR', 'literalinclude', loc(n), f'{arg}: selected slice is empty')
                continue
            if since:
                relp = rel(root, p)
                r = git(root, 'show', f'{since}:{relp}')
                if r.returncode:
                    rep.add('INFO', 'literalinclude', loc(n), f'{arg}: file did not exist at {since}')
                    continue
                old, err = slice_lines(r.stdout.splitlines(), opts)
                if err:
                    rep.add('WARN', 'literalinclude', loc(n), f'{arg}: at {since} the anchors did not resolve ({err}); snippet is new or moved')
                elif old != lines:
                    diff = '\n'.join(difflib.unified_diff(old, lines, f'{relp}@{since}', f'{relp}@now', lineterm='', n=1))
                    rep.add('WARN', 'literalinclude', loc(n), f'{arg}: included snippet changed since {since}', extra=diff)

    if want_literals:
        for l in page['literals']:
            t = l['text']
            if CAMEL_RE.match(t) and not index.has_param(t) and not index.has_type(t):
                rep.add('INFO', 'literal', loc(l['line']), f'``{t}`` looks like a parameter name but no NED file declares it')


def tracked_ini_files(root, page_dir):
    """The page's ini files as git knows them; untracked backups and .omnetpp/ state files are not part of the page."""
    r = git(root, 'ls-files', '--', str(page_dir))
    if r.returncode == 0 and r.stdout.strip():
        return sorted(root / f for f in r.stdout.split('\n') if f.endswith('.ini'))
    return sorted(p for p in page_dir.rglob('*.ini') if not any(part.startswith('.') or part == 'results' for part in p.parts))


ENV_ERRORS = ('Operation not permitted', 'Failed to unshare', 'Cannot open network namespace', 'Cannot create TAP',
              'command execution failed', 'Unable to access jarfile', 'Permission denied')


def check_ini(rep, root, page_dir, index):
    seen_entries = []
    configs = []
    for ini in tracked_ini_files(root, page_dir):
        entries, cfgs = parse_ini(ini)
        for c in cfgs:
            c['file'] = str(ini)
        configs.extend(cfgs)
        for e in entries:
            where = f'{rel(root, ini)}:{e["line"]}'
            if e['kind'] == 'include':
                if not (ini.parent / e['value']).exists():
                    rep.add('ERROR', 'ini-include', where, f'included ini file missing: {e["value"]}')
            elif e['kind'] == 'typename':
                v = e['value'].strip().strip('"')
                if not v or '$' in v or v.startswith('ned.'):
                    continue
                name = v.split('.')[-1]
                if not index.has_type(name):
                    rep.add('ERROR', 'ini-typename', where, f'{e["key"]} = "{v}": not a NED type')
            elif e['kind'] == 'param':
                if not index.has_param(e['last']):
                    unknown_name(rep, root, where, 'ini-param', e['key'], e['last'], 'parameter')
        seen_entries.extend(entries)
    return configs


def run_configs(rep, root, page_dir, configs, timeout, omnetpp_root):
    by_file = {}
    for c in configs:
        by_file.setdefault(c['file'], []).append(c)
    for ini, cfgs in by_file.items():
        names = [c['name'] for c in cfgs if not c['abstract'] and c['name'] != 'General']
        if not names and any(c['name'] == 'General' for c in cfgs) and len(cfgs) == 1:
            names = ['General']
        for name in names:
            with tempfile.TemporaryDirectory() as tmp:
                cmd = (f'. {omnetpp_root}/setenv >/dev/null 2>&1; . {root}/setenv >/dev/null 2>&1; '
                       f'cd {Path(ini).parent} && inet -u Cmdenv -c {name} -r 0 --sim-time-limit=0s '
                       f'--cmdenv-express-mode=true --cmdenv-status-frequency=1000s --record-eventlog=false '
                       f'--result-dir={tmp} -f {Path(ini).name}')
                try:
                    r = subprocess.run(['bash', '-c', cmd], capture_output=True, text=True, timeout=timeout)
                    out = (r.stdout + r.stderr).strip().splitlines()
                    tail = '\n'.join(out[-8:])
                    if r.returncode and any(e in tail for e in ENV_ERRORS):
                        rep.add('WARN', 'run-env', f'{rel(root, ini)} [Config {name}]', 'needs privileges, real interfaces or an external tool; cannot be checked here', extra=tail.splitlines()[-1])
                    elif r.returncode:
                        rep.add('ERROR', 'run', f'{rel(root, ini)} [Config {name}]', f'exit code {r.returncode}', extra=tail)
                    else:
                        rep.add('INFO', 'run', f'{rel(root, ini)} [Config {name}]', 'network set up OK')
                except subprocess.TimeoutExpired:
                    rep.add('WARN', 'run', f'{rel(root, ini)} [Config {name}]', f'no result within {timeout}s (setup too slow for this check)')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('pages', nargs='+', help='page directories (the dir holding doc/index.rst)')
    ap.add_argument('--inet-root', default=os.environ.get('INET_ROOT'))
    ap.add_argument('--omnetpp-root', default=os.environ.get('OMNETPP_ROOT') or os.environ.get('__omnetpp_root_dir'))
    ap.add_argument('--since', help='git rev to diff literalinclude snippets against (default: the page\'s verified-commit)')
    ap.add_argument('--run', action='store_true', help='set up every non-abstract config with sim-time-limit=0s')
    ap.add_argument('--timeout', type=int, default=300)
    ap.add_argument('--literals', action='store_true', help='also flag ``camelCase`` literals that are not parameters')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--quiet', action='store_true', help='hide INFO lines')
    args = ap.parse_args()

    root = Path(args.inet_root or git(Path(args.pages[0]).resolve(), 'rev-parse', '--show-toplevel').stdout.strip()).resolve()
    if args.run and not args.omnetpp_root:
        sys.exit('--run needs --omnetpp-root or OMNETPP_ROOT (or run after ". setenv")')

    page_dirs = [Path(p).resolve() for p in args.pages]
    index = NedIndex().scan([root / 'src', root / 'showcases', root / 'tutorials'] + page_dirs)

    reports = []
    for page_dir in page_dirs:
        rep = Report(rel(root, page_dir))
        rst = page_dir / 'doc' / 'index.rst'
        if not rst.exists():
            rep.add('ERROR', 'page', rel(root, page_dir), 'no doc/index.rst')
            reports.append(rep)
            continue
        since = args.since or parse_rst(rst)['verified_commit']
        check_rst(rep, root, page_dir, rst, index, since, args.literals)
        for other in sorted(p for p in (page_dir / 'doc').glob('*.rst') if p.name != 'index.rst'):
            check_rst(rep, root, page_dir, other, index, since, args.literals, stamp=False)
        configs = check_ini(rep, root, page_dir, index)
        if args.run:
            run_configs(rep, root, page_dir, configs, args.timeout, args.omnetpp_root)
        reports.append(rep)

    if args.json:
        print(json.dumps([{'page': r.page, 'items': r.items} for r in reports], indent=1))
    else:
        for r in reports:
            print(f'== {r.page}: {r.count("ERROR")} error(s), {r.count("WARN")} warning(s)')
            for it in r.items:
                if args.quiet and it['level'] == 'INFO':
                    continue
                print(f'  {it["level"]:5} {it["category"]:15} {it["where"]}: {it["msg"]}')
                if it['extra']:
                    for l in it['extra'].splitlines():
                        print(f'        | {l}')
    sys.exit(1 if any(r.count('ERROR') for r in reports) else 0)


if __name__ == '__main__':
    main()
