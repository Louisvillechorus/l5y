"""FRAME QC — the camera, the type size, and what is actually inside the crop.

The other gates look at the settled DOM. This one watches the STAGE while the
cue plays: it fires every cue with advance() exactly as the operator does and
samples the frame several times mid-animation, measuring what the audience
actually sees on the 75" rig.

Per sample it records:
  * the camera scale (the .stagecam matrix) and the reading window
    (the frame minus ERA_ZONE_, which the docked calendar strip owns)
  * every visible text node inside the reading window, in PROJECTED screen
    pixels (computed font-size x the accumulated transform scale) — anything
    under MIN_PX cannot be read from the house
  * anything in the window that does not belong to the current register:
    a second .layer in the stack, a layer animating out, the calendar
    artifact lying over the phone, and (at settle) any text in the
    screenstack that screenHTML(CUR) does not produce
  * whether the phone actually fills the window (a centred push leaves black
    bars where the audience expects screen)
  * the inline font-size fitPad() has written onto the calendar card, against
    that element's stylesheet value — the shrink bug

Violations: TINY, STALE, GHOST, OVERLAY, ZOOMJUMP, GAP, PADSHRINK, JSERROR.
Usage: CHROMIUM_PATH=/opt/pw-browsers/chromium python3 qc_frames.py [--json out.json]
"""
import json
import os
import sys
import time

from playwright.sync_api import sync_playwright

FILE = 'file://' + os.path.abspath('L5Y-Show-STANDALONE.html')

MIN_PX = 22.0          # readable floor from the house, in projected 1080p pixels
ZOOM_JUMP = 0.25       # settled-to-settled scale change inside one register
PAD_SHRINK = 0.60      # fitPad may not take a calendar word below 60% of its sheet size
GAP_TOL = 0.02         # share of the reading window allowed to show no device
SETTLE_MS = 1500       # the camera glide is 1.4 s — let it land before the settled read
SAMPLE_MS = 300        # mid-animation cadence
CUE_CAP_S = 95         # 2.2 is the longest cue in the show (~53 s)

# chrome the audience never reads (keys, predictive bar, notch furniture) plus
# the greeked asset labels that a real photo file replaces. Still measured and
# reported, never a violation — same exclusions the legibility gate uses.
CHROME_RE = (r"(^|\s)(key|kbd|predict|sb-r|nw|pt|mcount|yr|hlbl|searchpill|"
             r"ni|ibh|tl|sep|dock|cp-sig|homebar|ml|mi|vlen)(\s|$)")

VIS_AREA = 0.35        # a text box clipped below this share of itself is not on screen
VIS_MIN_H = 5.0        # …nor is a sliver thinner than this

PROBE = r"""
window.__CHROME_RE = new RegExp(__CHROME_SRC__);
window.__MINPX = __MINPX__;

window.__norm = function(s){
  return String(s||'').replace(/\s+/g,' ').replace(/[0-9]/g,'#').trim().toLowerCase();
};
window.__tok = function(s){
  const t = window.__norm(s);
  return (t.length >= 4) ? t : '';
};
window.__scaleOf = function(el){
  let s = 1, n = el;
  while(n && n.nodeType === 1 && n !== document.documentElement){
    const cs = getComputedStyle(n);
    if(cs.transform && cs.transform !== 'none'){
      try{
        const m = new DOMMatrix(cs.transform);
        const k = Math.sqrt(Math.abs(m.a*m.d - m.b*m.c));
        if(k > 0) s *= k;
      }catch(e){}
    }
    n = n.parentElement;
  }
  return s;
};
window.__vis = function(el){
  if(el.checkVisibility) {
    try{ return el.checkVisibility({checkOpacity:true, checkVisibilityCSS:true}); }catch(e){}
  }
  const cs = getComputedStyle(el);
  return !(cs.display==='none' || cs.visibility==='hidden' || +cs.opacity === 0);
};
window.__ix = function(a, b){   // intersection area of two rects
  const w = Math.min(a.r,b.r) - Math.max(a.l,b.l);
  const h = Math.min(a.b,b.b) - Math.max(a.t,b.t);
  return (w > 0 && h > 0) ? w*h : 0;
};
/* WHAT IS ACTUALLY ON SCREEN: a range rect ignores every overflow:hidden box
   above it (the collapsed predictive bar, a scrolled thread, the phone's own
   screen). Clip the rect through the ancestor chain before believing it. */
window.__clip = function(el, r){
  let box = {l:r.left, t:r.top, r:r.right, b:r.bottom};
  let n = el;
  while(n && n.nodeType === 1 && n !== document.documentElement){
    const cs = getComputedStyle(n);
    if(cs.overflow !== 'visible' || cs.overflowX !== 'visible' || cs.overflowY !== 'visible'){
      const a = n.getBoundingClientRect();
      box = {l:Math.max(box.l,a.left), t:Math.max(box.t,a.top),
             r:Math.min(box.r,a.right), b:Math.min(box.b,a.bottom)};
      if(box.r <= box.l || box.b <= box.t) return null;
    }
    n = n.parentElement;
  }
  const full = Math.max(1, r.width*r.height);
  const got = (box.r-box.l)*(box.b-box.t);
  if(got/full < __VIS_AREA__) return null;
  if((box.b-box.t) < __VIS_MIN_H__) return null;
  return box;
};
window.__opacityOf = function(el){
  let o = 1, n = el;
  while(n && n.nodeType === 1 && n !== document.documentElement){
    o *= parseFloat(getComputedStyle(n).opacity);
    n = n.parentElement;
  }
  return o;
};

/* the text the CURRENT state would paint into the screenstack — the truth the
   settled frame is measured against (digits normalised away: live clocks and
   call timers tick past the state's own value) */
window.__expected = function(st){
  const out = new Set();
  try{
    const d = document.createElement('div');
    d.innerHTML = screenHTML(st);
    const w = document.createTreeWalker(d, NodeFilter.SHOW_TEXT);
    let n;
    while((n = w.nextNode())){ const t = window.__tok(n.nodeValue); if(t) out.add(t); }
  }catch(e){}
  return out;
};

window.__probe = function(settled){
  const P = document.getElementById('projection');
  if(!P) return null;
  const F = P.getBoundingClientRect();
  const zone = (typeof ERA_ZONE_ === 'function') ? ERA_ZONE_() : 0.19;
  const st = (typeof CUR === 'object' && CUR) ? CUR : {};
  const cam = document.querySelector('#projDevice .stagecam');
  const eraEl = document.getElementById('era');

  let z = null;
  if(cam){
    try{
      const m = new DOMMatrix(getComputedStyle(cam).transform);
      z = Math.sqrt(Math.abs(m.a*m.d - m.b*m.c)) || 1;
    }catch(e){ z = 1; }
  }

  const dev = cam && cam.querySelector('.iphone,.macbook,.carplay,.fullstage,.ipad');
  let devkind = null, devR = null;
  if(dev){
    devkind = (dev.className.match(/iphone|macbook|carplay|fullstage|ipad/) || [null])[0];
    const r = dev.getBoundingClientRect();
    devR = {l:r.left, t:r.top, r:r.right, b:r.bottom};
  }

  /* THE READING WINDOW: the frame minus the strip's zone when a device is up.
     With the phone away the whole frame belongs to the calendar. */
  const win = dev ? {l:F.left, t:F.top, r:F.left + F.width*(1-zone), b:F.bottom}
                  : {l:F.left, t:F.top, r:F.right, b:F.bottom};
  const winArea = Math.max(1, (win.r-win.l)*(win.b-win.t));

  /* does the phone actually fill the window? (a centred push leaves bars) */
  let gap = 0, restZ = null;
  if(devR && devkind === 'iphone'){
    gap = 1 - window.__ix(win, devR)/winArea;
    const fill = (typeof CAM_FILL_ === 'function') ? CAM_FILL_() : 3.6;
    const dw = (devR.r - devR.l) / (z || 1);                 // the phone's layout width
    if(dw > 1) restZ = +Math.min(fill, (win.r - win.l)/dw).toFixed(3);   // what camRest() would set
  }

  /* ---- text in the window, in projected pixels ---- */
  const tiny = [], chrome = [];
  let minpx = null, minwhat = null;
  const stack = document.querySelector('#projDevice .screenstack');
  const seen = new Set();
  const inWin = [];
  if(cam){
    const w = document.createTreeWalker(cam, NodeFilter.SHOW_TEXT);
    let n;
    while((n = w.nextNode())){
      const raw = (n.nodeValue||'').trim();
      if(raw.length < 1) continue;
      const el = n.parentElement;
      if(!el || !window.__vis(el)) continue;
      const rg = document.createRange(); rg.selectNodeContents(n);
      const r = rg.getBoundingClientRect();
      if(!(r.width > 0.5 && r.height > 0.5)) continue;
      const box = window.__clip(el, r);       // clipped by every overflow box above it
      if(!box) continue;
      if(window.__ix(win, box) <= 0) continue;
      const cls = String(el.className || el.tagName || '');
      const px = parseFloat(getComputedStyle(el).fontSize) * window.__scaleOf(el);
      const rec = {c: cls.slice(0,34), px: +px.toFixed(1), s: raw.slice(0,44)};
      const isChrome = window.__CHROME_RE.test(cls);
      if(minpx === null || px < minpx){
        if(!isChrome){ minpx = px; minwhat = rec; }
      }
      const key = (isChrome?'c:':'t:') + rec.c + '|' + rec.px + '|' + rec.s;
      if(!seen.has(key)){
        seen.add(key);
        if(px < window.__MINPX) (isChrome ? chrome : tiny).push(rec);
      }
      if(settled && stack && stack.contains(el)) inWin.push(raw);
    }
  }

  /* ---- what does not belong here ----
     swapLayer() replaces the whole stack, so a second .layer or a text-bearing
     sibling of the live layer is content the register left behind. Deliberate
     exit animations (.lockUp, .appClose) ride on the LIVE layer and are not
     counted — they are the transition, not a ghost. */
  const ghosts = [], overlay = [];
  let layers = 0;
  if(stack){
    const kids = [...stack.children];
    layers = kids.filter(c => c.classList.contains('layer')).length;
    kids.filter(c => !c.classList.contains('layer')).forEach(e => {
      if(!window.__vis(e)) return;
      const r = e.getBoundingClientRect();
      if(window.__ix(win, {l:r.left,t:r.top,r:r.right,b:r.bottom}) <= 0) return;
      const txt = (e.textContent||'').replace(/\s+/g,' ').trim();
      if(txt) ghosts.push({k:String(e.className).slice(0,24)||e.tagName, s:txt.slice(0,44)});
    });
  }
  /* the calendar artifact must never lie across the phone's window */
  if(dev && eraEl && window.__vis(eraEl)){
    eraEl.querySelectorAll('.sheet, .stop, .tear, .settle').forEach(sh => {
      if(!window.__vis(sh)) return;
      const op = window.__opacityOf(sh);
      if(op < 0.15) return;                       // a face already crossfaded away
      if(!(sh.textContent||'').trim()) return;
      const r = sh.getBoundingClientRect();
      const a = window.__ix(win, {l:r.left,t:r.top,r:r.right,b:r.bottom});
      if(a/winArea > 0.01){
        overlay.push({c:String(sh.className).slice(0,26),
                      pct:+(100*a/winArea).toFixed(1), op:+op.toFixed(2),
                      s:(sh.textContent||'').replace(/\s+/g,' ').trim().slice(0,40)});
      }
    });
  }

  /* ---- fitPad's inline shrink against the sheet's own stylesheet size ---- */
  const pad = [];
  const top = eraEl && eraEl.querySelector('.pad .sheet.top');
  if(top){
    ['.yr','.ynum','.sub','.ttl','.frow'].forEach(sel => {
      const e = top.querySelector(sel);
      if(!e || !(e.textContent||'').trim()) return;
      const inline = e.style.fontSize;
      if(!inline) return;
      const got = parseFloat(inline);
      e.style.fontSize = '';                                  // read the sheet's own size…
      const base = parseFloat(getComputedStyle(e).fontSize);
      e.style.fontSize = inline;                              // …and put it straight back
      if(!(base > 0)) return;
      pad.push({sel: sel, px: +got.toFixed(1), base: +base.toFixed(1),
                r: +(got/base).toFixed(3), s:(e.textContent||'').trim().slice(0,30)});
    });
  }

  /* THE BODY-TEXT YARDSTICK: .fs is iOS Larger Text (2.4% of --ph) and is the
     same layout size in every register, so its PROJECTED size is purely the
     camera's doing — one number per cue that says how big the show reads. */
  let fsPx = null;
  const fsEl = cam && cam.querySelector('.fs');
  if(fsEl) fsPx = +(parseFloat(getComputedStyle(fsEl).fontSize) * window.__scaleOf(fsEl)).toFixed(1);

  return {
    app: st.app || null, black: !!st.black, dev: devkind,
    z: z === null ? null : +z.toFixed(3), restZ: restZ, fsPx: fsPx,
    win: [Math.round(win.l), Math.round(win.t), Math.round(win.r), Math.round(win.b)],
    devR: devR ? [Math.round(devR.l), Math.round(devR.t), Math.round(devR.r), Math.round(devR.b)] : null,
    gap: +gap.toFixed(3),
    home: eraEl ? (eraEl.dataset.home||'') : '',
    erahid: eraEl ? eraEl.classList.contains('hidden') : true,
    tiny: tiny.slice(0,14), chrome: chrome.slice(0,8),
    minpx: minpx === null ? null : +minpx.toFixed(1), minwhat: minwhat,
    layers: layers, ghosts: ghosts.slice(0,6), overlay: overlay.slice(0,4),
    pad: pad,
    inwin: settled ? inWin.slice(0,400) : null
  };
};

window.__expectedNow = function(){
  const st = (typeof CUR === 'object' && CUR) ? CUR : {};
  return [...window.__expected(st)];
};
0
"""
PROBE = (PROBE.replace('__CHROME_SRC__', json.dumps(CHROME_RE))
              .replace('__MINPX__', repr(MIN_PX))
              .replace('__VIS_AREA__', repr(VIS_AREA))
              .replace('__VIS_MIN_H__', repr(VIS_MIN_H)))


def rects_overlap_note(s):
    return f"win {s['win']} dev {s['devR']}"


def wanted_songs(n):
    """--songs 0,1,8  walks only those songs (0-based) — for tuning the gate."""
    if '--songs' in sys.argv:
        return [int(x) for x in sys.argv[sys.argv.index('--songs') + 1].split(',')
                if 0 <= int(x) < n]
    return list(range(n))


def run():
    viol = []           # (cue, kind, detail)
    info = []
    errs = []
    rows = []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or None)
        pg = b.new_page(viewport={'width': 1920, 'height': 1080})
        pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)))
        # a blocked font/asset fetch is the theatre Wi-Fi case the build already
        # covers (the type is embedded) — it is not a JS error
        pg.on('console', lambda m: errs.append('console.error: ' + m.text)
              if (m.type == 'error' and 'Failed to load resource' not in m.text) else None)
        pg.goto(FILE)
        pg.wait_for_timeout(2500)
        pg.evaluate("setCast('ml'); startAs('projection'); 0")
        pg.wait_for_timeout(1200)
        pg.evaluate(PROBE)

        nsongs = pg.evaluate('SHOW.length')
        prev_settled = None      # (cue, app, z)
        for si in wanted_songs(nsongs):
            pg.evaluate(f'si={si}; ci=0; animTok++; animRunning=false; hardRender();')
            pg.wait_for_timeout(250)
            ncues = pg.evaluate(f'SHOW[{si}].cues.length')
            for k in range(ncues):
                cid = pg.evaluate(f'SHOW[{si}].cues[{k}].id')
                pg.evaluate('setTimeout(()=>advance(),0)')
                pg.wait_for_timeout(70)
                mids = []
                t0 = time.time()
                while time.time() - t0 < CUE_CAP_S:
                    s = pg.evaluate('__probe(false)')
                    if s:
                        mids.append(s)
                    if not pg.evaluate('animRunning'):
                        break
                    pg.wait_for_timeout(SAMPLE_MS)
                pg.wait_for_timeout(SETTLE_MS)
                st = pg.evaluate('__probe(true)')
                exp = set(pg.evaluate('__expectedNow()'))

                rows.append({'cue': cid, 'mids': len(mids), 'settled': st})
                if not st:
                    continue

                # ---------- the settled frame ----------
                app = st['app'] or ('black' if st['black'] else '—')
                seen_tiny = set()
                for t in sorted(st['tiny'], key=lambda t: t['px'])[:4]:
                    seen_tiny.add((t['c'], t['s']))
                    viol.append((cid, 'TINY',
                                 f"{t['px']}px projected  <{t['c']}>  “{t['s']}”  (floor {MIN_PX:.0f}px)"))
                if len(st['tiny']) > 4:
                    viol.append((cid, 'TINY',
                                 f"…and {len(st['tiny'])-4} more text runs under {MIN_PX:.0f}px "
                                 f"in the same frame"))
                for t in st['chrome']:
                    info.append((cid, 'tiny-chrome', f"{t['px']}px <{t['c']}> “{t['s']}”"))

                # THE CAMERA WAS RESET: a repaint built a fresh .stagecam and
                # nothing re-aimed it, so the phone sits at native size
                camreset = (st['dev'] == 'iphone' and st['z'] is not None
                            and abs(st['z'] - 1.0) < 0.005 and st['restZ']
                            and st['restZ'] > 1.2)
                if camreset:
                    viol.append((cid, 'CAMRESET',
                                 f"camera at 1.00x — the phone is at native size; camRest() would "
                                 f"hold it at {st['restZ']:.2f}x. Body text projects "
                                 f"{st['fsPx']:.0f}px instead of ~{st['fsPx']*st['restZ']:.0f}px"))

                if st['layers'] > 1:
                    viol.append((cid, 'STALE',
                                 f"{st['layers']} .layer elements stacked in the screenstack at rest"))
                for g in st['ghosts']:
                    viol.append((cid, 'GHOST',
                                 f"<{g['k']}> is a sibling of the live .layer, still in the "
                                 f"window at rest — “{g['s']}”"))
                for o in st['overlay']:
                    viol.append((cid, 'OVERLAY',
                                 f"calendar <{o['c']}> covers {o['pct']}% of the reading window "
                                 f"at opacity {o['op']} — “{o['s']}”"))
                for q in st['pad']:
                    if q['r'] < PAD_SHRINK:
                        viol.append((cid, 'PADSHRINK',
                                     f"calendar {q['sel']} forced to {q['px']}px of {q['base']}px "
                                     f"({q['r']*100:.0f}% of the sheet size) — “{q['s']}”"))
                if st['dev'] == 'iphone' and st['gap'] > GAP_TOL and not camreset:
                    viol.append((cid, 'GAP',
                                 f"{st['gap']*100:.0f}% of the reading window shows no phone at rest "
                                 f"(camera {st['z']:.2f}x, the resting fit is {st['restZ']:.2f}x) — "
                                 + rects_overlap_note(st)))

                # stale text at rest: in the stack but not in screenHTML(CUR)
                if st['inwin']:
                    norm = pg.evaluate('(a)=>a.map(s=>window.__tok(s)).filter(Boolean)', st['inwin'])
                    foreign = sorted({t for t in norm if t not in exp})
                    for f in foreign[:6]:
                        viol.append((cid, 'STALE',
                                     f"text in the window that screenHTML(CUR) does not paint — “{f[:48]}”"))

                # ---------- mid-animation ----------
                mid_bad = {}
                for s in mids:
                    for g in s['ghosts']:
                        mid_bad.setdefault(('GHOST', g['k'], g['s']), 0)
                        mid_bad[('GHOST', g['k'], g['s'])] += 1
                    for o in s['overlay']:
                        key = ('OVERLAY', o['c'], o['s'])
                        prevpct = mid_bad.get(key, 0)
                        mid_bad[key] = max(prevpct, o['pct'])
                    if s['layers'] > 1:
                        mid_bad[('STALE', 'layers', str(s['layers']))] = \
                            mid_bad.get(('STALE', 'layers', str(s['layers'])), 0) + 1
                    for q in s['pad']:
                        if q['r'] < PAD_SHRINK:
                            key = ('PADSHRINK', q['sel'], q['s'])
                            mid_bad[key] = min(mid_bad.get(key, 9), q['r'])
                    for t in s['tiny']:
                        if (t['c'], t['s']) in seen_tiny:
                            continue        # already reported from the settled frame
                        key = ('TINY', t['c'], t['s'])
                        mid_bad[key] = min(mid_bad.get(key, 1e9), t['px'])
                midtiny = 0
                for (kind, a, bdetail), v in sorted(mid_bad.items()):
                    if kind == 'TINY':
                        midtiny += 1
                        if midtiny > 3:
                            continue
                    if kind == 'OVERLAY':
                        viol.append((cid, 'OVERLAY',
                                     f"MID-CUE: calendar <{a}> crosses {v}% of the reading window — “{bdetail}”"))
                    elif kind == 'GHOST':
                        viol.append((cid, 'GHOST',
                                     f"MID-CUE: exiting .{a} visible in the window ({v} samples) — “{bdetail}”"))
                    elif kind == 'STALE':
                        viol.append((cid, 'STALE',
                                     f"MID-CUE: {bdetail} .layer elements stacked ({v} samples)"))
                    elif kind == 'PADSHRINK':
                        viol.append((cid, 'PADSHRINK',
                                     f"MID-CUE: calendar {a} at {v*100:.0f}% of its sheet size — “{bdetail}”"))
                    elif kind == 'TINY':
                        viol.append((cid, 'TINY',
                                     f"MID-CUE: {v}px projected <{a}> — “{bdetail}”"))

                # ---------- the zoom, settled to settled ----------
                z = st['z']
                if z and prev_settled and prev_settled[1] == app and prev_settled[2]:
                    d = abs(z - prev_settled[2]) / prev_settled[2]
                    if d > ZOOM_JUMP:
                        viol.append((cid, 'ZOOMJUMP',
                                     f"camera {prev_settled[2]:.2f}x → {z:.2f}x ({d*100:.0f}%) with the "
                                     f"register unchanged ({app}) since {prev_settled[0]}"))
                if z:
                    prev_settled = (cid, app, z)
                elif st['dev'] is None:
                    prev_settled = None

                zs = f"{z:.2f}x" if z else "  —  "
                mn = f"{st['minpx']:.0f}px" if st['minpx'] else "  —  "
                fs = f"{st['fsPx']:.0f}px" if st.get('fsPx') else "  —  "
                flags = []
                if st['tiny']:
                    flags.append(f"TINY×{len(st['tiny'])}")
                if st['overlay'] or any(s['overlay'] for s in mids):
                    flags.append('OVERLAY')
                if st['ghosts'] or any(s['ghosts'] for s in mids):
                    flags.append('GHOST')
                if any(q['r'] < PAD_SHRINK for q in st['pad']):
                    flags.append('PADSHRINK')
                if camreset:
                    flags.append('CAMRESET')
                if st['dev'] == 'iphone' and st['gap'] > GAP_TOL:
                    flags.append(f"GAP {st['gap']*100:.0f}%")
                print(f"{cid:>5}  {str(st['dev'] or '—'):<8} {app:<10} cam {zs}  "
                      f"body {fs}  min {mn}  win {st['win'][0]}–{st['win'][2]}  "
                      f"samples {len(mids):>3}  {' '.join(flags)}")
                sys.stdout.flush()
        b.close()
    return viol, info, rows, errs


if __name__ == '__main__':
    viol, info, rows, errs = run()
    out = None
    if '--json' in sys.argv:
        out = sys.argv[sys.argv.index('--json') + 1]
        json.dump({'violations': viol, 'info': info, 'rows': rows, 'errs': errs},
                  open(out, 'w'), indent=0)

    print()
    # ---- how big does the show actually read? one line per register ----
    byreg = {}
    for r in rows:
        s = r['settled']
        if not s or not s.get('fsPx') or s['dev'] != 'iphone':
            continue
        byreg.setdefault(s['app'] or '—', []).append((r['cue'], s['fsPx'], s['z']))
    if byreg:
        print('BODY TEXT (.fs, iOS Larger Text) AS PROJECTED, BY REGISTER')
        print(f"  {'register':<12} {'min':>7} {'max':>7} {'spread':>7}   smallest at")
        for reg, v in sorted(byreg.items(), key=lambda kv: min(x[1] for x in kv[1])):
            lo = min(v, key=lambda x: x[1])
            hi = max(v, key=lambda x: x[1])
            spread = (hi[1] - lo[1]) / lo[1] * 100 if lo[1] else 0
            print(f"  {reg:<12} {lo[1]:>6.0f}p {hi[1]:>6.0f}p {spread:>6.0f}%   "
                  f"{lo[0]} (cam {lo[2]:.2f}x)  widest {hi[0]} (cam {hi[2]:.2f}x)")
        print()
    smallest = None
    for r in rows:
        s = r['settled']
        if s and s['minpx'] and (smallest is None or s['minpx'] < smallest[1]):
            smallest = (r['cue'], s['minpx'], s['minwhat'])
    if smallest:
        w = smallest[2] or {}
        print(f"SMALLEST CONTENT TEXT: {smallest[1]}px projected at cue {smallest[0]} "
              f"<{w.get('c','?')}> “{w.get('s','')}”")
    if info:
        print(f"(chrome text under {MIN_PX:.0f}px, not counted: {len(info)} instances)")
    if errs:
        for e in errs[:5]:
            viol.append(('—', 'JSERROR', e[:160]))

    if not viol:
        print('FRAME QC: CLEAN')
        sys.exit(0)

    order = {'CAMRESET': 0, 'STALE': 1, 'OVERLAY': 2, 'GHOST': 3, 'PADSHRINK': 4,
             'ZOOMJUMP': 5, 'GAP': 6, 'TINY': 7, 'JSERROR': 8}
    viol.sort(key=lambda v: (order.get(v[1], 9), v[0]))
    print(f'FRAME QC: {len(viol)} violation(s)\n')
    for i, (cue, kind, det) in enumerate(viol, 1):
        print(f'{i:>3}. [{kind}] {cue}  {det}')
    sys.exit(1)
