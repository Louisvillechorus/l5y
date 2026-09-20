"""MAPS / CARPLAY QC — the drive on the dash, song 12.

D-022, David watching it: "the maps isn't moving for me at all at a all at all.
I see the text changing but the actual map is not moving at all."  The cue was
arithmetically perfect and visually dead, which is the hardest kind of wrong to
catch: every text assertion in the harness passed while the road sat still.  So
this probe works in pixels.  It photographs the MAP REGION ONLY — the cards are
masked out, because a falling mile count would otherwise score as motion — at
three moments of the song, and measures two different things:

  * what FRACTION of the map repainted.  This catches a dead canvas (0.000) and
    nothing finer: a nav map is mostly empty dark ground, so the fraction barely
    moved across the fix (18% at 7 px/s, 19% at 40 px/s).  A floor, not the test.
  * how far the world SLID down the frame, per second of the page's own clock.
    This is the test, and it is the number in David's note: 7.2 px/s before the
    fix — two minutes to cross the dash — against 39 px/s after.

D-042, from the frame sweep: "SPEED LIMIT" projected at 18.2 px against a 22 px
floor.  a_dash_legible holds every text node on the head unit to that floor,
settled and mid-drive, so the next thing to slip under it is caught here.

  a_map_moves(page)     – D-022.  Takes a Playwright page already at the file and
                          loaded; returns plain-English complaints, empty when
                          satisfied.
  a_dash_legible(page)  – D-042, same contract.
  exit_timing(page)     – where the Delaware Memorial Bridge maneuver lands in
                          the song for a range of `startAt` values, so that
                          directorial call can be made on numbers.

Usage: CHROMIUM_PATH=/opt/pw-browsers/chromium python3 qc_notes_maps.py
"""
import io
import os
import sys

import numpy as np
from PIL import Image

FILE = 'file://' + os.path.abspath('L5Y-Show-STANDALONE.html')

# The song runs about 4 min 20 s.  We watch the map early (just after GO) and
# late (well past the Delaware Memorial Bridge beat) — a loop that dies after
# the first maneuver would pass a single-sample test.
SEEK_POINTS = [('just after GO', 0), ('2 min into the song', 120), ('4 min into the song', 240)]
GAPS = [2, 5, 15]                 # seconds between the reference frame and each comparison
DIFF_LEVEL = 10                   # per-channel 0-255 delta that counts as a changed pixel
# Changed pixels catch a DEAD map — a canvas nobody is repainting scores 0.000 —
# but they cannot tell a crawl from a drive, because a nav map is mostly empty dark
# ground and shifting it only disturbs the fifth of the frame that carries road.
# Measured either side of the D-022 fix the fraction barely moved (18% at 7 px/s,
# 19% at 40 px/s), so these are a floor, not the test.
MIN_FRAC = {2: 0.025, 5: 0.040, 15: 0.060}
# THE TEST is how fast the world slides DOWN the frame. 7 px/s — two minutes to cross
# the dash — is what David watched and called not moving at all. A real Apple Maps nav
# view crosses its frame in well under half a minute.
MIN_PX_PER_S = 26.0

# Everything that is NOT the map, drawn on top of it on the dash.  Masked out so
# the trip card's ticking numbers can never be mistaken for the road moving.
CARDS = ['.dv-banner', '.dv-sheet', '.dv-speed', '.dv-comp',
         '.cp-side', '.cp-time', '.cp-apps', '.cp-home']


def _goto_drive(page):
    """Boot the projection view and fire the drive cue the way the operator does."""
    page.evaluate('setCast("ml"); startAs("projection")')
    page.wait_for_timeout(400)
    idx = page.evaluate('SHOW.findIndex(s=>s.n===12)')
    if idx < 0:
        return None
    page.evaluate('si=%d; ci=0; animTok++; animRunning=false; hardRender();' % idx)
    page.wait_for_timeout(200)
    page.evaluate('advance()')
    for _ in range(200):
        page.wait_for_timeout(100)
        if not page.evaluate('animRunning'):
            break
    page.wait_for_timeout(400)
    return idx


def _seek(page, seconds):
    """Put the drive exactly `seconds` into the song.

    The drive is driven from DRIVE_T0 (the moment the screen appeared), so
    moving that origin is exactly equivalent to having watched that long —
    deterministic, and it lets the probe inspect the whole song in seconds.
    """
    page.evaluate('(s)=>{ const n=performance.now();'
                  ' for(const k in DRIVE_T0) DRIVE_T0[k]=n-s*1000; }', seconds)
    page.wait_for_timeout(250)


def _map_geometry(page):
    """The map rect, the card rects to mask, and a card-free window of open road.

    Two rects because they answer two different questions. `map` + `masks` answers
    "how much of the map repainted", which is what the note is about. `open` — the
    band of map to the right of the guidance and trip cards, below the compass and
    above the speed limit sign — is where the displacement is measured: a masked
    block is a constant, and a constant correlates perfectly with itself at zero
    offset, so masking would pin the answer at "nothing moved" no matter what.
    """
    return page.evaluate(
        """(cards)=>{
          const el=document.querySelector('#projection .mapsdrive'); if(!el) return null;
          const map=el.querySelector('.dv-map'); if(!map) return null;
          const R=(n)=>{const r=n.getBoundingClientRect();
            return {x:r.left,y:r.top,w:r.width,h:r.height};};
          const m=R(map); if(m.w<50||m.h<50) return null;
          const root=el.closest('.carplay')||el;
          const masks=[], by={};
          cards.forEach(sel=>root.querySelectorAll(sel).forEach(n=>{
            const cs=getComputedStyle(n);
            if(cs.display==='none'||cs.visibility==='hidden') return;
            const r=R(n); if(r.w>0&&r.h>0){ masks.push(r); (by[sel]=by[sel]||[]).push(r); }
          }));
          const right=(sel)=>(by[sel]||[]).reduce((a,r)=>Math.max(a,r.x+r.w),m.x);
          const L=Math.max(right('.dv-banner'), right('.dv-sheet'), right('.cp-side'))+14;
          const T=Math.max(m.y+8, ((by['.dv-comp']||[])[0]||{y:m.y,h:0}).y
                                  +((by['.dv-comp']||[])[0]||{h:-8}).h+14);
          const B=Math.min(m.y+m.h-8, ((by['.dv-speed']||[])[0]||{y:m.y+m.h+8}).y-14);
          const open={x:L, y:T, w:(m.x+m.w-8)-L, h:B-T};
          if(open.w<120||open.h<160) return {map:m, masks:masks, open:null};
          return {map:m, masks:masks, open:open};
        }""", CARDS)


def _shot(page, rect):
    """One frame of the map, with the page's own clock either side of the capture.

    The elapsed time between two frames is NOT the time this script slept: a
    screenshot of the dash costs real page time, and dividing a displacement by
    the nominal gap would report a drive several times faster than it is.  The
    page is asked what time it is on both sides of the shutter and the midpoint
    is used, so px/s means px/s.
    """
    clip = {'x': round(rect['x']), 'y': round(rect['y']),
            'width': round(rect['w']), 'height': round(rect['h'])}
    t0 = page.evaluate('performance.now()')
    png = page.screenshot(clip=clip, animations='allow')
    t1 = page.evaluate('performance.now()')
    arr = np.asarray(Image.open(io.BytesIO(png)).convert('RGB'), dtype=np.int16)
    return arr, (t0 + t1) / 2000.0, (t1 - t0) / 1000.0


def _mask(geo):
    """True where a pixel belongs to the map and not to a card laid over it."""
    m = geo['map']
    h, w = round(m['h']), round(m['w'])
    keep = np.ones((h, w), dtype=bool)
    for r in geo['masks']:
        x0 = max(0, int(r['x'] - m['x']) - 3)
        y0 = max(0, int(r['y'] - m['y']) - 3)
        x1 = min(w, int(r['x'] - m['x'] + r['w']) + 4)
        y1 = min(h, int(r['y'] - m['y'] + r['h']) + 4)
        if x1 > x0 and y1 > y0:
            keep[y0:y1, x0:x1] = False
    return keep


def _changed_fraction(a, b, keep):
    n = min(a.shape[0], b.shape[0], keep.shape[0])
    m = min(a.shape[1], b.shape[1], keep.shape[1])
    d = np.abs(a[:n, :m] - b[:n, :m]).max(axis=2) > DIFF_LEVEL
    k = keep[:n, :m]
    tot = int(k.sum())
    return (float((d & k).sum()) / tot) if tot else 0.0


DS = 2           # the search runs at half resolution; ±2 px is plenty for a rate
MAX_SHIFT = 420  # px of travel the search can still resolve in one gap


def _edges(img):
    """The map's horizontal edges: what a vertical displacement actually moves.

    A nav map is mostly empty dark ground and one long road running up the frame,
    and both of those look identical after a vertical shift — match raw pixels and
    "nothing moved" scores beautifully at every offset.  The rows where brightness
    changes are the crossings, the roofs, the labels and the shields, and those are
    the things whose travel the audience reads as driving.
    """
    g = img[:, :, :3].mean(axis=2).astype(np.float32)
    dy = np.abs(g[1:, :-1] - g[:-1, :-1])       # horizontal edges: what a pan moves
    dx = np.abs(g[1:, 1:] - g[1:, :-1])         # a little vertical edge, for the turns
    return dy + 0.5 * dx


def _scroll_px(a, b, limit=MAX_SHIFT):
    """How far the world slid DOWN the screen between two frames, in pixels.

    A bounded, normalised vertical search over the edge picture — not phase
    correlation.  Heading-up navigation means the view travels almost purely
    along the screen's vertical axis, and the map's street grids are strongly
    periodic, which hands an FFT phase peak several plausible answers and no way
    to choose between them.  Sliding one frame over the other keeps the answer
    tied to the whole picture, so the periodic parts cannot outvote it.
    Returns (shift, correlation); shift > 0 = the world came down the frame,
    which is what driving forward looks like.  A frozen map matches best at 0.
    """
    ea, eb = _edges(a), _edges(b)
    n = min(ea.shape[0], eb.shape[0])
    m = min(ea.shape[1], eb.shape[1])
    ga = ea[:n:DS, :m:DS]
    gb = eb[:n:DS, :m:DS]
    rows = ga.shape[0]
    lim = min(limit // DS, rows - 24)
    best, bestd = -2.0, 0
    for d in range(-lim, lim + 1):
        x = (ga[:rows - d] if d >= 0 else ga[-d:]).ravel()
        y = (gb[d:] if d >= 0 else gb[:rows + d]).ravel()
        xs, ys = x.std(), y.std()
        if xs < 1e-6 or ys < 1e-6:
            continue
        r = float(np.dot(x - x.mean(), y - y.mean()) / (len(x) * xs * ys))
        if r > best:
            best, bestd = r, d
    return bestd * DS, best


def _crop(arr, geo):
    """The card-free window, cut out of the one frame already taken of the map."""
    m, o = geo['map'], geo['open']
    y0 = max(0, int(round(o['y'] - m['y'])))
    x0 = max(0, int(round(o['x'] - m['x'])))
    return arr[y0:y0 + int(round(o['h'])), x0:x0 + int(round(o['w']))]


def measure(page, label):
    """One motion measurement: reference frame, then a frame after each gap."""
    geo = _map_geometry(page)
    if geo is None:
        return None, ['%s: the CarPlay map region is not on screen at all' % label]
    if geo['open'] is None:
        return None, ['%s: the cards cover the whole dash — no open map left to watch' % label]
    keep = _mask(geo)
    base, t0, _ = _shot(page, geo['map'])
    baseo = _crop(base, geo)
    out, waited = {}, 0
    for g in GAPS:
        if g > waited:
            page.wait_for_timeout((g - waited) * 1000)
        waited = g
        now, t1, spread = _shot(page, geo['map'])
        dy, corr = _scroll_px(baseo, _crop(now, geo))
        out[g] = {'frac': _changed_fraction(base, now, keep),
                  'px': abs(dy), 'dy': dy, 'corr': corr, 'dt': max(0.05, t1 - t0),
                  'blur': spread, 'h': keep.shape[0]}
    return out, []


def _rate(fr):
    """px/s, read off the short gap the search locked on to best.

    Best-correlated, not fastest: a weak lock on a periodic street grid can land
    on the wrong peak and report several times the truth, and taking the maximum
    would let that stand — and would let a frozen map pass on one bad lock. The
    long gap is never used; past the search limit the answer wraps and understates.
    """
    good = [(fr[g]['corr'], fr[g]['px'] / fr[g]['dt']) for g in (2, 5)
            if fr[g]['corr'] > 0.35 and fr[g]['px'] < MAX_SHIFT - 20]
    return max(good)[1] if good else 0.0


def a_map_moves(page):
    """D-022: the CarPlay map must be visibly, continuously in motion."""
    bad = []
    a_map_moves.readings = []
    if _goto_drive(page) is None:
        return ['song 12 is missing from the show, so the drive cannot be checked']

    seen = 0
    for label, offset in SEEK_POINTS:
        if offset:
            _seek(page, offset)
        fr, errs = measure(page, label)
        bad += errs
        if fr is None:
            continue
        seen += 1
        a_map_moves.readings.append((label, fr))
        for g in GAPS:
            if fr[g]['frac'] < MIN_FRAC[g]:
                bad.append(
                    '%s: the map is dead — only %.1f%% of the map pixels changed in %.1f s; '
                    'nothing is repainting the road at all'
                    % (label, fr[g]['frac'] * 100, fr[g]['dt']))
        # The decisive number: how fast the world actually slides down the screen,
        # per second of the page's own clock. Read off the short gaps — the search
        # can only resolve so far, so a long gap on a properly fast map understates it.
        rate = _rate(fr)
        if rate < MIN_PX_PER_S:
            bad.append(
                '%s: the road crawls — the world slides only %.1f px/s down a %d px map '
                '(%.0f s to cross the frame). At 25 ft that reads as a still picture; '
                'a nav map at highway speed needs at least %d px/s'
                % (label, rate, fr[15]['h'], fr[15]['h'] / max(rate, .01), MIN_PX_PER_S))
        elif fr[5]['px'] <= fr[2]['px']:
            bad.append('%s: the map twitches but does not travel — it has slid no further '
                       'in 5 s than in 2 s' % label)

    if seen < 2:
        bad.append('the map could only be sampled at %d point in the song; '
                   'motion must be proven more than once' % seen)

    # the geometry really has to be re-projected, not just repainted
    moved = page.evaluate(
        """()=>{ const el=document.querySelector('#projection .mapsdrive');
          if(!el) return null; const s=el.querySelector('.dv-svg');
          const a=s.getAttribute('viewBox'); const p=el.querySelector('.dv-puck').getAttribute('transform');
          return new Promise(r=>setTimeout(()=>r({vb:a!==s.getAttribute('viewBox'),
            puck:p!==el.querySelector('.dv-puck').getAttribute('transform')}),1500)); }""")
    if moved and not moved['vb']:
        bad.append('the map viewBox never changes: the camera is not following the car')
    if moved and not moved['puck']:
        bad.append('the puck never moves along the route')
    return bad


# ---------------------------------------------------------------- D-042
# The readable floor from the house, in projected 1080p pixels — the same
# number qc_frames.py holds the phone to. The dash does not get a lower bar
# than the phone just because it is a dash.
MIN_DASH_PX = 22.0

DASH_TEXT = r"""(floor)=>{
  const root=document.querySelector('#projection .carplay');
  if(!root) return {none:true};
  /* projected size = the CSS font-size times every transform stacked above it,
     INCLUDING the SVG viewport scale, which is not a CSS transform and so is
     invisible to a naive walk — the map's own labels live under one. */
  const scaleOf=(el)=>{
    let s=1, n=el;
    while(n && n.nodeType===1 && n!==document.documentElement){
      const cs=getComputedStyle(n);
      if(cs.transform && cs.transform!=='none'){
        try{ const mx=new DOMMatrix(cs.transform);
          const k=Math.sqrt(Math.abs(mx.a*mx.d-mx.b*mx.c)); if(k>0) s*=k; }catch(e){}
      }
      if(n.tagName==='svg' && n.viewBox && n.viewBox.baseVal && n.viewBox.baseVal.width>0){
        const r=n.getBoundingClientRect();
        if(r.width>0) s*=r.width/n.viewBox.baseVal.width;
      }
      n=n.parentElement;
    }
    return s;
  };
  const vis=(el)=>{
    if(el.checkVisibility){ try{ return el.checkVisibility({checkOpacity:true,checkVisibilityCSS:true}); }catch(e){} }
    const cs=getComputedStyle(el);
    return !(cs.display==='none'||cs.visibility==='hidden'||+cs.opacity===0);
  };
  const out=[], seen=new Set();
  const w=document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  let n;
  while((n=w.nextNode())){
    const raw=(n.nodeValue||'').trim(); if(!raw) continue;
    const el=n.parentElement; if(!el||!vis(el)) continue;
    if(el.closest('defs')) continue;                       // template artwork, never drawn here
    const rg=document.createRange(); rg.selectNodeContents(n);
    const r=rg.getBoundingClientRect();
    if(!(r.width>0.5 && r.height>0.5)) continue;           // laid out but not painted
    const px=parseFloat(getComputedStyle(el).fontSize)*scaleOf(el);
    const what=String(el.getAttribute&&el.getAttribute('class')||el.className||el.tagName||'');
    const cls=(typeof what==='string'?what:(what.baseVal||'')).slice(0,30);
    const key=cls+'|'+Math.round(px)+'|'+raw.slice(0,24);
    if(seen.has(key)) continue; seen.add(key);
    if(px<floor) out.push({px:+px.toFixed(1), cls:cls, s:raw.slice(0,30)});
    else out.push(null);
  }
  const tiny=out.filter(Boolean);
  return {tiny:tiny, seen:out.length,
          smallest:tiny.length?Math.min.apply(null,tiny.map(t=>t.px)):null};
}"""


def a_dash_legible(page):
    """D-042: nothing on the CarPlay dash may read below the 22 px house floor.

    The note arrived about the SPEED LIMIT sign, which projected at 18.2 px on a
    dash that otherwise reads 32.5 px.  This checks every text node on the head
    unit, settled and mid-drive, so the next thing to slip through is caught
    before David has to see it.
    """
    bad = []
    a_dash_legible.readings = []
    if _goto_drive(page) is None:
        return ['song 12 is missing from the show, so the dash cannot be checked']
    for label, at in [('settled at the top of 12', None), ('90 s into the drive', 90),
                      ('4 min into the drive', 240)]:
        if at is not None:
            _seek(page, at)
        page.wait_for_timeout(250)
        res = page.evaluate(DASH_TEXT, MIN_DASH_PX)
        if not res or res.get('none'):
            bad.append('%s: the CarPlay dash is not on screen' % label)
            continue
        a_dash_legible.readings.append((label, res))
        # a probe that measured nothing is not a pass
        if res['seen'] < 8:
            bad.append('%s: only %d text nodes were found on the dash — the legibility '
                       'check is not looking at the head unit' % (label, res['seen']))
        for t in res['tiny']:
            bad.append('%s: "%s" (%s) projects at %.1f px, under the %.0f px floor — '
                       'unreadable on a 75-inch TV at 25 ft'
                       % (label, t['s'], t['cls'] or 'text', t['px'], MIN_DASH_PX))
    return bad


CANDIDATES = [0.49, 0.5000, 0.5002, 0.502, 0.5035, 0.505]


def exit_timing(page, candidates=None):
    """Where the Delaware Memorial Bridge beat lands, for a set of `startAt` values.

    The bridge beat is DRIVE_STEPS[0] — "Keep right to stay on I-95 S", with the
    bridge signed off to the left.  At rate:1 the arithmetic is fixed: the car
    covers miles/mins miles per minute, so the beat lands (step.at - startAt) *
    miles / speed minutes after GO, and the banner opens reading
    (step.at - startAt) * miles.
    """
    return page.evaluate(
        """(vals)=>{
          const cue=SHOW.find(s=>s.n===12).cues[0].do.find(o=>o.op==='mapsdrive');
          const mph=(cue.miles/cue.mins)*60, step=DRIVE_STEPS[0];
          return {cue:{mins:cue.mins, miles:cue.miles, rate:cue.rate,
                       startAt:cue.startAt, mph:+mph.toFixed(1)},
                  step:step.instr, via:step.via,
                  rows:vals.map(at0=>{
                    const ahead=(step.at-at0)*cue.miles;
                    return {at0:at0, ahead:+ahead.toFixed(2),
                            secs:+((ahead/mph)*3600/(cue.rate||1)).toFixed(1)};
                  })};
        }""", candidates or CANDIDATES)


def _run():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or None)
        pg = b.new_page(viewport={'width': 1920, 'height': 1080})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(FILE)
        pg.wait_for_timeout(1500)
        bad = a_map_moves(pg)
        dash = a_dash_legible(pg)

        print('--- measured map motion (map region only, cards masked out) ---')
        for label, fr in getattr(a_map_moves, 'readings', []):
            print('  %-20s ' % label + '  '.join(
                '%4.1fs: %5.1f%% changed, slid %4d px (r=%.2f)'
                % (fr[g]['dt'], fr[g]['frac'] * 100, fr[g]['dy'], fr[g]['corr'])
                for g in GAPS) + '   => %.1f px/s (map %d px tall, crosses in %.0f s)'
                % (_rate(fr), fr[15]['h'], fr[15]['h'] / max(_rate(fr), .01)))

        print('--- dash type, projected (floor %.0f px) ---' % MIN_DASH_PX)
        for label, res in getattr(a_dash_legible, 'readings', []):
            print('  %-26s %d text nodes checked, smallest %s'
                  % (label, res['seen'],
                     ('%.1f px' % min(t['px'] for t in res['tiny'])) if res['tiny'] else 'all at/above floor'))

        t = exit_timing(pg)
        c = t['cue']
        print('--- exit timing: "%s" (%s) ---' % (t['step'], t['via']))
        print('cue: rate=%s mins=%s miles=%s startAt=%s  (%s mph)'
              % (c['rate'], c['mins'], c['miles'], c['startAt'], c['mph']))
        for r in t['rows']:
            m, s = divmod(r['secs'], 60)
            print('  startAt=%-7s opens at %5.2f mi ahead  ->  beat lands %5.1f s in (%d:%04.1f)'
                  % (r['at0'], r['ahead'], r['secs'], m, s))
        b.close()
    if errs:
        print('JS ERRORS:', errs[:3])
    print('MAP MOTION (D-022):', 'CLEAN' if not bad else '\n  ' + '\n  '.join(bad))
    print('DASH LEGIBILITY (D-042):', 'CLEAN' if not dash else '\n  ' + '\n  '.join(dash))
    return 1 if (bad or dash or errs) else 0


if __name__ == '__main__':
    sys.exit(_run())
