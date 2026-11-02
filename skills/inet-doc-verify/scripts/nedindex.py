"""Shared helpers: NED type/parameter index, RST page parsing, ini parsing.

Regex based on purpose: fast, dependency-free, and good enough for an
existence check. It over-approximates (a name declared anywhere counts),
so a reported unknown name is a real defect, while a known name is not a
proof that the page uses it on the right module.
"""
import os
import re
from pathlib import Path

NED_TYPE_RE = re.compile(r'^\s*(simple|module|network|channel|moduleinterface|channelinterface)\s+(\w+)')
NED_SECTION_RE = re.compile(r'^\s*(parameters|gates|submodules|connections|types)\s*(allowunconnected)?\s*:')
NED_PARAM_RE = re.compile(r'^\s*(?:volatile\s+)?(?:(?:int|double|string|bool|object|xml)\s+)?([A-Za-z_]\w*)\s*(?:@[^=;]*)?(=|;)')
NED_CLASS_RE = re.compile(r'@class\(\s*"?([\w:]+)"?\s*\)')
NED_EXTENDS_RE = re.compile(r'\bextends\s+(\w+)')
NED_SUBMODULE_RE = re.compile(r'^\s*\w+(?:\[[^\]]*\])?\s*:\s*(?:<[^>]*>\s*like\s+)?(\w+)')
NED_DEFAULT_LIKE_RE = re.compile(r'<\s*default\(\s*"([\w.]+)"\s*\)\s*>\s*like\s+(\w+)')
NED_CHANNEL_RE = re.compile(r'(?:<-->|-->|<--)\s*(\w+)\s*(?:\{|<-->|-->|<--)')
NED_LIKE_RE = re.compile(r'\blike\s+(\w+)')

# OMNeT++ built-in types that live outside INET's src tree
BUILTIN_TYPES = {'IdealChannel', 'DelayChannel', 'DatarateChannel'}
# parameters of the OMNeT++ built-in channel types
BUILTIN_PARAMS = {'delay', 'datarate', 'ber', 'per', 'disabled'}


class NedType:
    __slots__ = ('name', 'kind', 'file', 'params', 'cppclass', 'uses')

    def __init__(self, name, kind, file):
        self.name = name
        self.kind = kind
        self.file = file
        self.params = set()
        self.cppclass = None
        self.uses = set()   # type names referenced by extends / submodules / like / channels


class NedIndex:
    def __init__(self):
        self.types = {}       # name -> NedType (first definition wins; duplicates recorded)
        self.duplicates = {}
        self.all_params = set()

    def scan(self, roots):
        for root in roots:
            root = Path(root)
            if root.is_file() and root.suffix == '.ned':
                self._scan_file(root)
                continue
            for dirpath, dirnames, filenames in os.walk(root):
                dirnames[:] = [d for d in dirnames if d not in ('out', '.git', 'results')]
                for fn in filenames:
                    if fn.endswith('.ned'):
                        self._scan_file(Path(dirpath) / fn)
        return self

    def _scan_file(self, path):
        try:
            text = path.read_text(errors='replace')
        except OSError:
            return
        cur = None
        section = None
        for raw in text.splitlines():
            line = raw.split('//', 1)[0]
            if not line.strip():
                continue
            m = NED_TYPE_RE.match(line)
            if m and not line.lstrip().startswith('@'):
                kind, name = m.group(1), m.group(2)
                cur = NedType(name, kind, str(path))
                if name in self.types:
                    self.duplicates.setdefault(name, []).append(str(path))
                else:
                    self.types[name] = cur
                section = 'parameters'
                e = NED_EXTENDS_RE.search(line)
                if e:
                    cur.uses.add(e.group(1))
                for l in NED_LIKE_RE.findall(line):
                    cur.uses.add(l)
                continue
            if cur is None:
                continue
            s = NED_SECTION_RE.match(line)
            if s:
                section = s.group(1)
                continue
            c = NED_CLASS_RE.search(line)
            if c:
                cur.cppclass = c.group(1).split('::')[-1]
            if section == 'parameters':
                p = NED_PARAM_RE.match(line)
                if p and not line.lstrip().startswith('@'):
                    cur.params.add(p.group(1))
                    self.all_params.add(p.group(1))
            elif section == 'submodules':
                sm = NED_SUBMODULE_RE.match(line)
                if sm:
                    cur.uses.add(sm.group(1))
                d = NED_DEFAULT_LIKE_RE.search(line)
                if d:
                    cur.uses.add(d.group(1).split('.')[-1])
            elif section == 'connections':
                for ch in NED_CHANNEL_RE.findall(line):
                    cur.uses.add(ch)
                d = NED_DEFAULT_LIKE_RE.search(line)
                if d:
                    cur.uses.add(d.group(1).split('.')[-1])
            elif section == 'types':
                pass

    def has_type(self, name):
        return name in self.types or name in BUILTIN_TYPES

    def has_param(self, name):
        return name in self.all_params or name in BUILTIN_PARAMS

    def types_declaring(self, param):
        return [t for t in self.types.values() if param in t.params]

    def source_files(self, name):
        """Files that implement a NED type: the .ned, plus the C++ class files if any."""
        t = self.types.get(name)
        if not t:
            return []
        files = [t.file]
        nedpath = Path(t.file)
        base = t.cppclass or (name if t.kind in ('simple', 'channel') else None)
        if base:
            for ext in ('.cc', '.h', '.msg'):
                cand = nedpath.with_name(base + ext)
                if cand.exists():
                    files.append(str(cand))
        return files


# ---------------------------------------------------------------- RST --------

ROLE_RE = re.compile(r':(ned|par|cpp|download|doc|ref|ini|gate|var|fun|msg)+:`([^`]+)`')
DIRECTIVE_RE = re.compile(r'^(\s*)\.\. (figure|image|video|literalinclude|include|code-block)::\s*(.*?)\s*$')
OPTION_RE = re.compile(r'^\s+:([\w-]+):\s*(.*?)\s*$')
STAMP_RE = re.compile(r'^\|\s*Verified with INET version:\s*``([^`]*)``')
VERIFIED_COMMIT_RE = re.compile(r'^\.\. verified-commit:\s*([0-9a-fA-F]{7,40})\s*$')
LITERAL_RE = re.compile(r'(?<!`)``([^`\n]+)``(?!`)')


def role_target(text):
    """':ned:`Foo <Bar>`' -> 'Bar'; ':ned:`Foo`' -> 'Foo'."""
    m = re.match(r'.*<([^<>]+)>\s*$', text)
    return m.group(1).strip() if m else text.strip()


def parse_rst(path):
    """Return dict with stamp, verified_commit, roles, directives, literals."""
    lines = Path(path).read_text(errors='replace').splitlines()
    out = {'stamp': None, 'stamp_line': None, 'verified_commit': None, 'verified_commit_line': None,
           'roles': [], 'directives': [], 'literals': []}
    i = 0
    in_code = False
    code_indent = 0
    while i < len(lines):
        line = lines[i]
        m = STAMP_RE.match(line)
        if m:
            out['stamp'] = m.group(1)
            out['stamp_line'] = i + 1
        m = VERIFIED_COMMIT_RE.match(line)
        if m:
            out['verified_commit'] = m.group(1)
            out['verified_commit_line'] = i + 1
        d = DIRECTIVE_RE.match(line)
        if d:
            indent, kind, arg = d.groups()
            opts = {}
            j = i + 1
            while j < len(lines):
                o = OPTION_RE.match(lines[j])
                if o and len(lines[j]) - len(lines[j].lstrip()) > len(indent):
                    opts[o.group(1)] = o.group(2)
                    j += 1
                else:
                    break
            out['directives'].append({'kind': kind, 'arg': arg, 'options': opts, 'line': i + 1})
            if kind == 'code-block':
                in_code, code_indent = True, len(indent)
            i = j
            continue
        if in_code:
            if line.strip() and len(line) - len(line.lstrip()) <= code_indent:
                in_code = False
            else:
                i += 1
                continue
        for r in ROLE_RE.finditer(line):
            out['roles'].append({'role': r.group(1), 'text': r.group(2), 'target': role_target(r.group(2)), 'line': i + 1})
        for l in LITERAL_RE.finditer(line):
            out['literals'].append({'text': l.group(1), 'line': i + 1})
        i += 1
    return out


def slice_lines(src_lines, opts):
    """Apply Sphinx literalinclude filters in Sphinx's order (start, end, lines).

    Mirrors sphinx/directives/code.py: start-at keeps the matching line,
    start-after drops it; end-at keeps it, end-before drops it but ignores a
    match on the very first line; a missing anchor is an error in Sphinx too.
    Returns (lines, error).
    """
    lines = src_lines
    if 'start-at' in opts or 'start-after' in opts:
        key = 'start-at' if 'start-at' in opts else 'start-after'
        idx = next((k for k, l in enumerate(lines) if opts[key] in l), None)
        if idx is None:
            return None, f':{key}: pattern not found: {opts[key]!r}'
        lines = lines[idx:] if key == 'start-at' else lines[idx + 1:]
    if 'end-at' in opts or 'end-before' in opts:
        key = 'end-at' if 'end-at' in opts else 'end-before'
        idx = None
        for k, l in enumerate(lines):
            if opts[key] in l:
                if key == 'end-before' and k == 0:
                    continue
                idx = k
                break
        if idx is None:
            return None, f':{key}: pattern not found after the start anchor: {opts[key]!r}'
        lines = lines[:idx + 1] if key == 'end-at' else lines[:idx]
    if 'lines' in opts:
        sel = []
        for part in opts['lines'].split(','):
            part = part.strip()
            if '-' in part:
                a, b = part.split('-', 1)
                a = int(a) if a else 1
                b = int(b) if b else len(lines)
            else:
                a = b = int(part)
            if a < 1 or b > len(lines) or a > b:
                return None, f':lines: {part} out of range (slice has {len(lines)} lines)'
            sel.extend(lines[a - 1:b])
        lines = sel
    return lines, None


# ---------------------------------------------------------------- INI --------

INI_SECTION_RE = re.compile(r'^\s*\[\s*(?:Config\s+)?([\w-]+)\s*\]')
INI_KEY_RE = re.compile(r'^\s*([^=#\s][^=]*?)\s*=\s*(.*?)\s*$')


def strip_ini_comment(line):
    out, quote = [], None
    for ch in line:
        if quote:
            out.append(ch)
            if ch == quote:
                quote = None
        elif ch in '"\'':
            quote = ch
            out.append(ch)
        elif ch == '#':
            break
        else:
            out.append(ch)
    return ''.join(out)


def parse_ini(path):
    """Yield dicts: file, line, section, key, value, kind in {'option','param','typename','pattern'}."""
    entries, configs = [], []
    section = 'General'
    for n, raw in enumerate(Path(path).read_text(errors='replace').splitlines(), 1):
        line = strip_ini_comment(raw)
        if not line.strip():
            continue
        m = INI_SECTION_RE.match(line)
        if m:
            section = m.group(1)
            configs.append({'name': section, 'line': n, 'abstract': False, 'file': str(path)})
            continue
        if line.strip().startswith('include'):
            entries.append({'file': str(path), 'line': n, 'section': section, 'key': 'include',
                            'value': line.strip()[len('include'):].strip(), 'kind': 'include'})
            continue
        m = INI_KEY_RE.match(line)
        if not m:
            continue
        key, value = m.group(1), m.group(2)
        if key == 'abstract' and value.strip().lower() == 'true' and configs and configs[-1]['name'] == section:
            configs[-1]['abstract'] = True
        last = key.rsplit('.', 1)[-1]
        if '.' not in key:
            kind = 'option'
        elif '-' in last or not re.fullmatch(r'\w+', last):
            kind = 'option' if '-' in last else 'pattern'
        elif last == 'typename':
            kind = 'typename'
        else:
            kind = 'param'
        entries.append({'file': str(path), 'line': n, 'section': section, 'key': key, 'value': value,
                        'last': last, 'kind': kind})
    return entries, configs
