#!/usr/bin/env python3
"""Record the commit a page was verified at.

Usage: stamp.py PAGE_DIR... --commit REV [--version TEXT] [--dry-run]

Writes/updates a ".. verified-commit: <full sha>" RST comment right after the
"| Verified with INET version: ..." line block, and with --version also
rewrites the visible version text (e.g. "4.6" or "master"). Only run this
after the user has accepted the verification report for the page.
"""
import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nedindex import STAMP_RE, VERIFIED_COMMIT_RE  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('pages', nargs='+')
    ap.add_argument('--commit', required=True)
    ap.add_argument('--version', help='new text for the visible "Verified with INET version" line')
    ap.add_argument('--inet-root', default=os.environ.get('INET_ROOT'), help='repository the commit lives in (default: INET_ROOT, else the current directory\'s repo)')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    root = Path(args.inet_root) if args.inet_root else Path.cwd()
    sha = subprocess.run(['git', '-C', str(root), 'rev-parse', '--verify', args.commit + '^{commit}'],
                         capture_output=True, text=True)
    if sha.returncode:
        sys.exit(f'not a commit: {args.commit}')
    sha = sha.stdout.strip()

    for p in args.pages:
        rst = Path(p) / 'doc' / 'index.rst'
        if not rst.exists():
            print(f'{p}: no doc/index.rst', file=sys.stderr)
            continue
        lines = rst.read_text().splitlines()
        stamp_idx = next((i for i, l in enumerate(lines) if STAMP_RE.match(l)), None)
        if stamp_idx is None:
            print(f'{rst}: no "Verified with INET version" line, skipped', file=sys.stderr)
            continue
        if args.version:
            lines[stamp_idx] = re.sub(r'``[^`]*``', f'``{args.version}``', lines[stamp_idx], count=1)
        end = stamp_idx
        while end + 1 < len(lines) and lines[end + 1].startswith('|'):
            end += 1
        comment = f'.. verified-commit: {sha}'
        existing = next((i for i, l in enumerate(lines) if VERIFIED_COMMIT_RE.match(l)), None)
        if existing is not None:
            lines[existing] = comment
        else:
            lines[end + 1:end + 1] = ['', comment]
        text = '\n'.join(lines) + '\n'
        if args.dry_run:
            print(f'{rst}: would set {comment}' + (f' and version ``{args.version}``' if args.version else ''))
        else:
            rst.write_text(text)
            print(f'{rst}: {comment}')


if __name__ == '__main__':
    main()
