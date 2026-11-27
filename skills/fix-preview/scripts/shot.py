"""Screenshot a built doc page between two text anchors, with phrases and blocks highlighted.

Usage: shot.py URL PHRASES COLOR OUT.png START_TEXT END_TEXT [BLOCK_CSS_SELECTOR]

PHRASES  "|"-separated; each is marked in the first text node that contains it. A phrase must lie
         inside ONE DOM text node (inline roles like :ned:/:par: split text: mark the pieces).
         Spaces in a phrase match any whitespace. "" marks nothing.
COLOR    highlight colour, e.g. "#fbc4c0" (before) or "#bfe8c8" (after).
START_TEXT / END_TEXT  the crop runs from the first p/h1-h4/li/dt element containing START_TEXT
         to the first such element (at or after the start) containing END_TEXT, 24 px padding.
BLOCK_CSS_SELECTOR  optional; every match is outlined and filled with COLOR
         (e.g. ".admonition.note", 'img[src*="elog2"]'; Sphinx may rename images, match substrings).
Run with ~/.cache/inet-docreview/venv/bin/python (needs websocket-client).
"""
import base64, json, socket, subprocess, sys, tempfile, time, urllib.request, shutil
import websocket

if len(sys.argv) < 7:
    sys.exit(__doc__)
url, phrases, color, out, start_t, end_t = sys.argv[1:7]
block_sel = sys.argv[7] if len(sys.argv) > 7 else ''
W, H = 1440, 1100

JS = r'''(() => {
  const [phrases, color, startT, endT, blockSel] = ARGS;
  const norm = e => e.textContent.replace(/\s+/g, ' ');
  const esc = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const root = document.querySelector('article') || document.body;
  for (const ph of phrases.split('|').filter(x => x)) {
    const re = new RegExp(esc(ph).replace(/ /g, '\\s+'));
    const walk = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    let t, found = false;
    while ((t = walk.nextNode())) {
      const mm = re.exec(t.data);
      if (mm) {
        const r = document.createRange(); r.setStart(t, mm.index); r.setEnd(t, mm.index + mm[0].length);
        const m = document.createElement('mark');
        m.style.cssText = 'background:' + color + ';color:inherit;padding:1px 2px;border-radius:2px';
        r.surroundContents(m); found = true; break;
      }
    }
    if (!found) throw new Error('phrase not found (must lie within one text node): ' + ph);
  }
  if (blockSel) {
    const bs = document.querySelectorAll(blockSel);
    if (!bs.length) throw new Error('block selector matched nothing: ' + blockSel);
    for (const b of bs) { b.style.outline = '4px solid ' + color; b.style.background = color; }
  }
  const els = [...root.querySelectorAll('p,h1,h2,h3,h4,li,dt')];
  const ia = els.findIndex(e => norm(e).includes(startT));
  if (ia < 0) throw new Error('START_TEXT not found: ' + startT);
  const ib = els.findIndex((e, i) => i >= ia && norm(e).includes(endT));
  if (ib < 0) throw new Error('END_TEXT not found after START_TEXT: ' + endT);
  const a = els[ia], b = els[ib];
  const top = a.getBoundingClientRect().top + window.scrollY - 24;
  const bottom = b.getBoundingClientRect().bottom + window.scrollY + 24;
  const body = (a.closest('section') || a.parentElement).getBoundingClientRect();
  return {x: Math.max(0, body.left - 24), y: top, w: body.width + 48, h: bottom - top};
})()'''.replace('ARGS', json.dumps([phrases, color, start_t, end_t, block_sel]))

s = socket.socket(); s.bind(('127.0.0.1', 0)); port = s.getsockname()[1]; s.close()
prof = tempfile.mkdtemp(prefix='fix-preview-chrome-')
chrome = subprocess.Popen(['google-chrome', '--headless=new', f'--remote-debugging-port={port}',
                           f'--user-data-dir={prof}', '--hide-scrollbars', f'--window-size={W},{H}', 'about:blank'],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    tabs = None
    for _ in range(100):
        try:
            tabs = json.load(urllib.request.urlopen(f'http://127.0.0.1:{port}/json'))
            if any(t['type'] == 'page' for t in tabs):
                break
        except Exception:
            pass
        time.sleep(0.2)
    ws = websocket.create_connection([t for t in tabs if t['type'] == 'page'][0]['webSocketDebuggerUrl'], max_size=None)
    n = [0]

    def cdp(m, p=None):
        n[0] += 1
        ws.send(json.dumps({'id': n[0], 'method': m, 'params': p or {}}))
        while True:
            r = json.loads(ws.recv())
            if r.get('id') == n[0]:
                if 'error' in r:
                    raise RuntimeError(r['error'])
                return r.get('result', {})

    def js(e):
        r = cdp('Runtime.evaluate', {'expression': e, 'returnByValue': True, 'awaitPromise': True})
        if r.get('exceptionDetails'):
            d = r['exceptionDetails']
            raise SystemExit('error: ' + (d.get('exception', {}).get('description') or d.get('text', str(d))))
        return r['result'].get('value')

    cdp('Page.enable')
    cdp('Emulation.setDeviceMetricsOverride', {'width': W, 'height': H, 'deviceScaleFactor': 1, 'mobile': False})
    cdp('Page.navigate', {'url': url})
    for _ in range(150):
        if js('document.readyState') == 'complete':
            break
        time.sleep(0.1)
    js('document.fonts.ready.then(() => true)')
    js('Promise.all([...document.images].map(i => i.complete ? 1 : new Promise(r => { i.onload = i.onerror = r; })))')
    rect = js(JS)
    shot = cdp('Page.captureScreenshot', {'format': 'png', 'captureBeyondViewport': True,
               'clip': {'x': rect['x'], 'y': rect['y'], 'width': rect['w'], 'height': rect['h'], 'scale': 1}})
    open(out, 'wb').write(base64.b64decode(shot['data']))
    print(out, {k: round(v) for k, v in rect.items()})
finally:
    chrome.terminate()
    try:
        chrome.wait(5)
    except Exception:
        chrome.kill()
    shutil.rmtree(prof, ignore_errors=True)
