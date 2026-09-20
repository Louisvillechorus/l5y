"""ERA / HOUSE-CARD QC — the probes that prove David's notes D-010 … D-014 and D-036.

The other gates read the settled DOM. These watch the artifact WHILE it moves: every probe
fires cues exactly as the operator does (advance()), records the calendar's type and paper on
every animation frame from inside the page, and then argues about the numbers.

  a_era_morph            D-010  the type TRAVELS between the card and the strip — one continuous
                                motion per piece, never a cross-dissolve, in both directions.
  a_cards_fall           D-011  every house page falls in from above the frame and the outgoing
                                page falls clear off the bottom. Nothing appears out of thin air.
  a_title_fills          D-012  the house pages use the black either side; the date cards stay square.
  a_typed_foot           D-013  the scene name types itself, with keyboard clicks, and fumbles a
                                letter on a seeded one cue in five — identically every night.
  a_92_no_inter_flash    D-014  "Intermission" is never on stage in a square frame.
  a_no_stray_pages       D-047  nothing is left behind on the stage by any transition.
  a_era_never_overlays   D-036  the calendar and the phone never share a pixel, at any instant,
                                in any cue of the show.

Each probe takes a Playwright page that is already at L5Y-Show-STANDALONE.html with the show
loaded, and returns a list of plain-English complaints (empty = the note is satisfied).

Usage: CHROMIUM_PATH=/opt/pw-browsers/chromium python3 qc_notes_era.py
"""
import os
import sys

from playwright.sync_api import sync_playwright

FILE = 'file://' + os.path.abspath('L5Y-Show-STANDALONE.html')
W, H = 1920, 1080
# setEraHome()'s two durations: the dock has to be over before the phone paints, the trip
# home has the stage to itself.
ERA_DUR = {'docked': 420, 'center': 780}

# --------------------------------------------------------------------------- in-page recorder
RECORDER = r"""
window.__ERA = {on:false, rows:[], t0:0, every:0, last:-1e9};
window.__eraRect = function(el){
  const b = el.getBoundingClientRect();
  return [+b.left.toFixed(1), +b.top.toFixed(1), +b.width.toFixed(1), +b.height.toFixed(1)];
};
window.__eraPainted = function(){
  /* every box of the artifact that actually puts ink or paper on the stage, including a page in
     flight and a falling house card. Anything at opacity 0 paints nothing and does not count. */
  const era = document.getElementById('era');
  const out = [];
  if(!era) return out;
  const cs = getComputedStyle(era);
  if(cs.opacity === '0' || cs.visibility === 'hidden' || cs.display === 'none') return out;
  era.querySelectorAll('.pf,.yr,.ynum,.mo,.ttl,.sub,.rule,.frow,.qr').forEach(el => {
    const c = getComputedStyle(el);
    if(c.display === 'none' || c.visibility === 'hidden' || parseFloat(c.opacity) < 0.02) return;
    let p = el.parentElement, dead = false;
    while(p && p !== era){ const pc = getComputedStyle(p);
      if(pc.display === 'none' || pc.visibility === 'hidden' || parseFloat(pc.opacity) < 0.02){ dead = true; break; }
      p = p.parentElement; }
    if(dead) return;
    const b = el.getBoundingClientRect();
    if(b.width < 1 || b.height < 1) return;
    if(!(el.textContent || '').trim() && !el.classList.contains('pf')
       && !el.classList.contains('rule') && !el.classList.contains('qr')) return;
    out.push({k: el.className.split(' ')[0], r: [b.left, b.top, b.right, b.bottom]});
  });
  return out;
};
window.__eraDevice = function(){
  const d = document.querySelector('#projDevice .iphone,#projDevice .macbook,#projDevice .carplay,#projDevice .fullstage');
  if(!d) return null;
  const b = d.getBoundingClientRect();
  return [b.left, b.top, b.right, b.bottom];
};
window.__eraSample = function(){
  const era = document.getElementById('era');
  if(!era) return null;
  const pad = era.querySelector('.pad:not(.ghost)');
  const ghost = era.querySelector('.pad.ghost');
  const pick = (root, sel) => {
    if(!root) return null;
    const el = root.querySelector(sel); if(!el) return null;
    const c = getComputedStyle(el);
    if(c.display === 'none' || c.visibility === 'hidden') return null;
    const b = el.getBoundingClientRect();
    if(b.width < 1 && b.height < 1) return null;
    let an = [];
    try { an = el.getAnimations().map(a => (a.transitionProperty || a.animationName || '?') +
             ':' + Math.round((a.effect && a.effect.getTiming().duration) || 0)); } catch(e){}
    return {r: [+b.left.toFixed(1), +b.top.toFixed(1), +b.width.toFixed(1), +b.height.toFixed(1)],
            o: +(+c.opacity).toFixed(3), t: (el.textContent || '').trim().slice(0, 18), an: an,
            from: el.dataset.flipFrom || ''};
  };
  const dev = window.__eraDevice();
  const painted = window.__eraPainted();
  let worst = 0;
  if(dev){
    const F = document.getElementById('projection').getBoundingClientRect();
    const clip = r => [Math.max(r[0], F.left), Math.max(r[1], F.top), Math.min(r[2], F.right), Math.min(r[3], F.bottom)];
    const d = clip(dev);
    const da = Math.max(0, d[2] - d[0]) * Math.max(0, d[3] - d[1]);
    if(da > 1) painted.forEach(p => {
      const q = clip(p.r);
      const ix = Math.max(0, Math.min(q[2], d[2]) - Math.max(q[0], d[0])) *
                 Math.max(0, Math.min(q[3], d[3]) - Math.max(q[1], d[1]));
      if(ix / da > worst) worst = ix / da;
    });
  }
  return {
    t: +(performance.now() - window.__ERA.t0).toFixed(0),
    home: era.dataset.home, face: era.dataset.face || '',
    hidden: era.classList.contains('hidden'),
    yr: pick(pad, '.sheet.top .yr'), num: pick(pad, '.sheet.top .ynum'),
    mo: pick(pad, '.sheet.top .mo'), foot: pick(pad, '.sheet.top .foot'),
    pf: pick(pad, '.sheet.top .pf'),
    pad: pad ? window.__eraRect(pad) : null,
    padAn: pad ? (()=>{ try { return pad.getAnimations().map(a=>a.animationName||a.transitionProperty||'?'); } catch(e){ return []; } })() : [],
    ghost: ghost ? window.__eraRect(ghost) : null,
    ghostAn: ghost ? (()=>{ try { return ghost.getAnimations().map(a=>a.animationName||a.transitionProperty||'?'); } catch(e){ return []; } })() : [],
    ghostFace: ghost ? ghost.className : '',
    nInk: painted.length,
    inter: painted.filter(p => /INTERMISSION/i.test((era.querySelector('.pad .ttl') || {}).textContent || '')).length > 0,
    interTxt: [...document.querySelectorAll('#era .ttl')].filter(e => {
        const c = getComputedStyle(e);
        return /INTERMISSION/i.test(e.textContent || '') && c.display !== 'none' && parseFloat(c.opacity) > .02;
      }).map(e => { const b = e.getBoundingClientRect(); const host = e.closest('.pad');
        return {r: [+b.left.toFixed(0), +b.top.toFixed(0), +b.width.toFixed(0), +b.height.toFixed(0)],
                band: !!(host && host.classList.contains('inter'))}; }),
    dev: dev ? dev.map(v => +v.toFixed(1)) : null,
    ov: +worst.toFixed(4)
  };
};
window.__eraStart = function(every){
  window.__ERA = {on:true, rows:[], t0: performance.now(), every: every || 0, last: -1e9};
  const loop = () => {
    if(!window.__ERA.on) return;
    const now = performance.now();
    if(now - window.__ERA.last >= window.__ERA.every){
      window.__ERA.last = now;
      const s = window.__eraSample();
      if(s) window.__ERA.rows.push(s);
    }
    requestAnimationFrame(loop);
  };
  requestAnimationFrame(loop);
};
window.__eraStop = function(){ window.__ERA.on = false; return window.__ERA.rows; };
"""


# --------------------------------------------------------------------------- helpers
def _boot(page):
    """Put the show on the stage, then install the recorder.

    THE GATE OWNS THE STAGE. qc_notes.py hands every probe a page that is still sitting at the
    operator's gate: `body.needgate` is set and `#projection` is `display:none`. Every
    getBoundingClientRect() inside #era then reads [0,0,0,0], and CSS animations do not run in a
    display:none subtree — so this file's measurements silently became measurements of NOTHING and
    reported four false failures (a 0 px title sheet, "fills only -0%", the type "not on the
    calendar during the move", a foot line that "appears whole"). The show itself was perfect:
    fired properly, 1.0a's incoming page travels top=-1522→+32 under cardIn and the ghost
    32→1557 under cardOut.

    This file's own main() called startAs() and the gate runner does not, which is why the probes
    passed on their own branch and failed in the gate. Every other qc_notes_*.py boots the show;
    so does this one now. The assert afterwards makes the same mistake impossible to make
    quietly ever again: a stage that is not laid out is a loud error, never a silent zero."""
    if not page.evaluate('typeof started !== "undefined" && started'):
        page.evaluate("startAs('projection')")
        page.wait_for_timeout(400)
    box = page.evaluate("""(()=>{const p=document.getElementById('projection');
        if(!p) return null; const b=p.getBoundingClientRect();
        return [+b.width.toFixed(1), +b.height.toFixed(1),
                getComputedStyle(p).display,
                document.body.classList.contains('needgate')];})()""")
    if not box or box[0] < 2 or box[1] < 2:
        raise RuntimeError(
            'the stage is not laid out (#projection is %r) — every rect in #era would measure '
            'zero and every probe in this file would report a false failure. Boot the show '
            'before measuring it.' % (box,))
    page.evaluate(RECORDER)


def _goto_cue(page, si, ci):
    """Park the engine immediately before cue index ci of song si, with nothing animating."""
    page.evaluate(f'si={si}; ci={ci}; animTok++; animRunning=false; hardRender();')
    page.wait_for_timeout(260)


def _play(page, every=0, cap_s=95, tail=1900, watch_ms=None):
    """Fire the next cue the way the operator does and record every frame of it — and keep
    recording `tail` ms after the cue settles, because a fall and a morph outlive the GO.

    watch_ms caps the watch. Every move the calendar ever makes happens in the first seconds of
    a cue (the morph is 0.42-0.78 s, a card falls in 0.84 s, a roll is exactly 6 s), while the
    longest cues in the show run for fifty seconds of phone business the artifact sits out. Where
    a probe only cares about the artifact it caps the watch, cuts the cue off the way a second GO
    would, and lets the stage settle — which also proves the cleanup survives an interruption."""
    page.evaluate(f'window.__eraStart({every})')
    page.evaluate('setTimeout(()=>advance(),0)')
    waited = 0
    while waited < cap_s * 1000:
        page.wait_for_timeout(100)
        waited += 100
        if not page.evaluate('animRunning'):
            break
        if watch_ms and waited >= watch_ms:
            page.evaluate('animTok++; animRunning=false')      # the operator's next GO would do this
            break
    page.wait_for_timeout(tail)
    return page.evaluate('window.__eraStop()')


def _cue_index(page, cid):
    return page.evaluate("""(cid)=>{ for(let s=0;s<SHOW.length;s++){
        const k=SHOW[s].cues.findIndex(c=>c.id===cid); if(k>=0) return [s,k]; } return null; }""", cid)


def _all_cues(page):
    return page.evaluate("""(()=>{const o=[];for(let s=0;s<SHOW.length;s++)
        for(let k=0;k<SHOW[s].cues.length;k++) o.push([s,k,SHOW[s].cues[k].id]); return o;})()""")


def _centre(box):
    return (box['r'][0] + box['r'][2] / 2, box['r'][1] + box['r'][3] / 2)


def _travel(rows, key, max_dt=10000):
    """Largest jump of one piece of type between two consecutive SAMPLES, as a share of frame
    width, normalised to one 60 Hz frame. Samples further than max_dt apart are skipped: that is
    the harness dropping frames, not the engine cutting."""
    worst, worst_at = 0.0, None
    prev = None
    for s in rows:
        b = s.get(key)
        if b is None:
            prev = None
            continue
        if prev is not None:
            dt = max(1, s['t'] - prev[0])
            if dt <= max_dt:
                dx = abs(_centre(b)[0] - prev[1][0])
                dy = abs(_centre(b)[1] - prev[1][1])
                d = (dx * dx + dy * dy) ** .5
                per_frame = d / max(1.0, dt / 16.7)
                if per_frame > worst:
                    worst, worst_at = per_frame, dt
        prev = (s['t'], _centre(b))
    return worst / W, worst_at


def _present_run(rows, key):
    """(first index present, last index present, count of gaps in the middle)"""
    idx = [i for i, s in enumerate(rows) if s.get(key) is not None]
    if not idx:
        return None
    gaps = sum(1 for a, b in zip(idx, idx[1:]) if b - a > 1)
    return idx[0], idx[-1], gaps


# --------------------------------------------------------------------------- D-010
def a_era_morph(page):
    """The type travels between the two homes: one real transform transition per piece of type,
    starting where the piece was and ending where it belongs, in both directions, repeatedly.

    Frame-to-frame continuity is also measured, but only across samples the harness actually
    delivered close together — a software rasteriser drops frames that a projector will not."""
    bad = []
    _boot(page)
    trips = ['1.2', '1.4', '2.1', '2.4', '3.2', '3.4', '9.1', '13.3']
    seen = {'docked': 0, 'center': 0}
    for cid in trips:
        loc = _cue_index(page, cid)
        if not loc:
            continue
        si, ci = loc
        _goto_cue(page, si, ci)
        before = page.evaluate("document.getElementById('era').dataset.home")
        page.evaluate("document.querySelectorAll('#era [data-flip-from]')"
                      ".forEach(e=>delete e.dataset.flipFrom)")
        rows = _play(page, tail=2400)
        after = page.evaluate("document.getElementById('era').dataset.home")
        if before == after:
            continue
        seen[after] = seen.get(after, 0) + 1
        what = f'{cid} ({"card → strip" if after == "docked" else "strip → card"})'
        moved = [i for i, r in enumerate(rows) if r['home'] == after]
        if not moved:
            bad.append(f'{what}: the artifact never reached its new home')
            continue
        m0 = moved[0]
        live = rows[m0:]
        for key, sel, name in (('yr', '.yr', 'the word YEAR'),
                               ('num', '.ynum', 'the year numeral'),
                               ('mo', '.mo', 'the month')):
            run = _present_run(live, key)
            if run is None:
                bad.append(f'{what}: {name} is not on the calendar during the move')
                continue
            first, last, gaps = run
            if first != 0 or last != len(live) - 1 or gaps:
                bad.append(f'{what}: {name} blinks out during the move (frames {first}..{last} '
                           f'of {len(live)-1}, {gaps} gaps) — a piece of the artifact must never '
                           f'disappear and reappear')
            # it is CARRIED: a real transform transition is running on this very element
            if not any('transform' in a for r in live[:6] if r.get(key) for a in r[key]['an']):
                bad.append(f'{what}: no transform transition is running on {name} when the home '
                           f'changes — it is being swapped, not carried')
            # …starting exactly where it was on screen (the engine records the position it was
            # asked to start from; the first frame of the new layout must be sitting on it)
            src = next((r[key]['from'] for r in live[:4] if r.get(key) and r[key]['from']), '')
            if not src:
                bad.append(f'{what}: {name} was never held back onto its old position — the two '
                           f'layouts are being swapped, not carried')
            elif live[0].get(key) and live[-1].get(key):
                fx, fy = [float(v) for v in src.split(',')]
                c0, cz = _centre(live[0][key]), _centre(live[-1][key])
                off = ((c0[0] - fx) ** 2 + (c0[1] - fy) ** 2) ** .5
                journey = ((cz[0] - fx) ** 2 + (cz[1] - fy) ** 2) ** .5
                # the first frame we caught must still be at the start of the journey; on a
                # software rasteriser the first sample can already be a frame or two late.
                if off > max(W * 0.02, journey * 0.16):
                    bad.append(f'{what}: {name} starts {off:.0f} px from where it was (a '
                               f'{journey:.0f} px journey) — the new layout is not held back onto '
                               f'the old one, so the swap shows')
            # …and ending where the new layout puts it
            endc = _centre(live[-1][key]) if live[-1].get(key) else None
            startc = _centre(live[0][key]) if live[0].get(key) else None
            journey = 1.0
            if endc and startc:
                journey = ((endc[0] - startc[0]) ** 2 + (endc[1] - startc[1]) ** 2) ** .5
                if journey < W * 0.05:
                    bad.append(f'{what}: {name} only travels {journey:.0f} px while the artifact '
                               f'changes home — it is not making the journey')
            # CONTINUITY, measured against the journey and the clock rather than against 60 Hz:
            # no two consecutive samples may be further apart than the declared animation could
            # carry the piece in the time between them (3.2x the average rate bounds any sane
            # ease; a cut covers the whole journey at once).
            dur = ERA_DUR[after]
            worst = None                       # (excess over what the move allows, frac, dt)
            prev = None
            for r in live:
                if not r.get(key):
                    prev = None
                    continue
                c = _centre(r[key])
                if prev is not None:
                    dt = r['t'] - prev[0]
                    # 5 ms apart is the same painted frame sampled twice; 150 ms apart is the
                    # harness having stalled, and says nothing about the engine.
                    if 5 <= dt <= 150:
                        step = ((c[0] - prev[1][0]) ** 2 + (c[1] - prev[1][1]) ** 2) ** .5
                        frac = step / max(journey, 1.0)
                        allow = min(1.0, (dt / dur) * 3.2 + 0.06)
                        if worst is None or frac - allow > worst[0]:
                            worst = (frac - allow, frac, dt)
                prev = (r['t'], c)
            if worst and worst[0] > 0:
                bad.append(f'{what}: {name} covers {worst[1]*100:.0f}% of its journey in one '
                           f'{worst[2]} ms step — more than a {dur} ms move could carry it; '
                           f'that is a cut, not a travel')
        dbl = page.evaluate("""(()=>[...document.querySelectorAll('#era .yr')]
            .filter(e=>getComputedStyle(e).display!=='none'&&parseFloat(getComputedStyle(e).opacity)>.02).length)()""")
        if dbl > 1:
            bad.append(f'{what}: {dbl} copies of YEAR on stage at rest — the two faces have not '
                       f'been merged into one')
    if not seen.get('docked'):
        bad.append('no card → strip trip was exercised; the morph is unproven in that direction')
    if not seen.get('center'):
        bad.append('no strip → card trip was exercised; the morph is unproven in that direction')
    return bad


# --------------------------------------------------------------------------- D-011
def a_cards_fall(page):
    """Every house page arrives from above the frame and leaves through the bottom of it —
    one heavy sheet with gravity, never a swap in place."""
    bad = []
    _boot(page)
    page.evaluate("PERF='Gayle King'")
    for cid in ('1.0a', '1.0b', '8.4', '8.5', '8.6'):
        loc = _cue_index(page, cid)
        if not loc:
            bad.append(f'{cid}: cue not found')
            continue
        si, ci = loc
        _goto_cue(page, si, ci)
        rows = _play(page, tail=3000)
        g0 = next((i for i, r in enumerate(rows) if r['ghost']), None)
        if g0 is None:
            bad.append(f'{cid}: the outgoing page never exists — the old card vanishes instead of '
                       f'falling off the bottom')
            continue
        live = rows[g0:]
        tops = [r['pad'][1] for r in live if r['pad']]
        if not tops:
            bad.append(f'{cid}: the incoming page is not on stage')
            continue
        if not any('cardIn' in a for r in live[:8] for a in r['padAn']):
            bad.append(f'{cid}: the incoming page has no fall animation running — it is swapped in')
        if not any('cardOut' in a for r in live[:8] for a in r['ghostAn']):
            bad.append(f'{cid}: the outgoing page has no fall animation running — it is swapped out')
        if min(tops) > -H * 0.5:
            bad.append(f'{cid}: the incoming page never rises above the frame (highest y={min(tops):.0f}) '
                       f'— it appears out of thin air instead of falling in from above')
        if abs(tops[-1]) > 120:
            bad.append(f'{cid}: the incoming page settles at y={tops[-1]:.0f} instead of landing on stage')
        gy = [r['ghost'][1] for r in live if r['ghost']]
        if max(gy) < H * 0.85 or (max(gy) - min(gy)) < H * 0.8:
            bad.append(f'{cid}: the outgoing page only reaches y={max(gy):.0f} after travelling '
                       f'{max(gy)-min(gy):.0f} px — it must drop fully clear of the bottom')
        jump, dt = _travel([{'t': r['t'], 'p': {'r': [0, r['pad'][1], 1, 1]}} for r in live if r['pad']],
                           'p', max_dt=90)
        if jump > 0.2:
            bad.append(f'{cid}: the incoming page jumps {jump*W:.0f} px between two frames {dt} ms '
                       f'apart — that is a cut, not a fall')
    return bad


# --------------------------------------------------------------------------- D-012
def a_title_fills(page):
    """The house pages use the black left and right; the date cards stay square."""
    bad = []
    _boot(page)
    page.evaluate("PERF='Gayle King'")
    M = """(()=>{const e=document.getElementById('era');
      const sh=e.querySelector('.pad .sheet.top'); if(!sh) return null;
      const b=sh.getBoundingClientRect(), cs=getComputedStyle(sh);
      const inner=sh.clientWidth-parseFloat(cs.paddingLeft)-parseFloat(cs.paddingRight);
      const line=s=>{const el=sh.querySelector(s); if(!el||!el.textContent.trim()) return null;
        const r=document.createRange(); r.selectNodeContents(el); const rb=r.getBoundingClientRect();
        return {w:+rb.width.toFixed(1), t:el.textContent.trim()};};
      return {face:e.dataset.face, w:+b.width.toFixed(1), h:+b.height.toFixed(1), inner:+inner.toFixed(1),
              yr:line('.yr'), sub:line('.sub'), num:line('.ynum'), ttl:line('.ttl')};})()"""
    # the title page
    _goto_cue(page, 0, 0)
    t = page.evaluate(M)
    if not t or t['face'] != 'title':
        bad.append('the title page is not on stage at song 1 cue 0')
    else:
        if t['w'] <= H * 0.99:
            bad.append(f'the title sheet is {t["w"]:.0f} px wide — no wider than the square date card, '
                       f'so the black left and right is still wasted')
        for k, nm in (('yr', 'THE LAST'), ('sub', 'YEARS')):
            ln = t[k]
            if not ln:
                bad.append(f'the title page has no {nm} line')
                continue
            fill = ln['w'] / t['inner']
            if fill < 0.9:
                bad.append(f'“{ln["t"]}” fills only {fill*100:.0f}% of the title sheet — it is not a '
                           f'full-width line')
        if t['num'] and t['yr'] and t['num']['w'] < 1:
            bad.append('the 5 is missing from the title page')
    # the numeral must still be the hero
    hero = page.evaluate("""(()=>{const sh=document.querySelector('#era .pad .sheet.top');
        const f=s=>parseFloat(getComputedStyle(sh.querySelector(s)).fontSize)||0;
        return {num:f('.ynum'), yr:f('.yr'), sub:f('.sub')};})()""")
    if hero['num'] <= max(hero['yr'], hero['sub']):
        bad.append(f'the 5 ({hero["num"]:.0f} px) is no bigger than THE LAST/YEARS '
                   f'({max(hero["yr"], hero["sub"]):.0f} px) — the hierarchy of the mockup is lost')
    # the performer page
    loc = _cue_index(page, '1.0a')
    if loc:
        _goto_cue(page, loc[0], loc[1])
        page.evaluate('advance()')
        page.wait_for_timeout(1400)
        p = page.evaluate("""(()=>{const sh=document.querySelector('#era .pad .sheet.top');
            const cs=getComputedStyle(sh); const inner=sh.clientWidth-parseFloat(cs.paddingLeft)-parseFloat(cs.paddingRight);
            return [...sh.querySelectorAll('.fl')].map(e=>{const r=document.createRange();
              r.selectNodeContents(e); return {t:e.textContent, f:+(r.getBoundingClientRect().width/inner).toFixed(3)};});})()""")
        for ln in p:
            if ln['f'] < 0.84:
                bad.append(f'the performer line “{ln["t"]}” fills only {ln["f"]*100:.0f}% of the sheet')
        if p and max(l['f'] for l in p) - min(l['f'] for l in p) > 0.02:
            bad.append('the performer lines are not set to the same width — they must span the '
                       'sheet line by line')
    # the INTERMISSION band must use the stage too (D-012, widened)
    loc = _cue_index(page, '8.4')
    if loc:
        _goto_cue(page, loc[0], loc[1])
        page.evaluate('advance()')
        page.wait_for_timeout(1700)
        bnd = page.evaluate(M)
        if not bnd or bnd['face'] != 'inter':
            bad.append('the INTERMISSION band is not on stage at 8.4')
        else:
            if bnd['w'] < W * 0.72:
                bad.append(f'the INTERMISSION band is {bnd["w"]:.0f} px — {bnd["w"]/W*100:.0f}% of the '
                           f'stage. It is meant to be a wide torn band across the middle')
            if bnd['ttl']:
                fill = bnd['ttl']['w'] / bnd['inner']
                if fill < 0.9:
                    bad.append(f'the word on the band fills only {fill*100:.0f}% of it — a small word '
                               f'floating in a strip, not a full-width line')
            else:
                bad.append('the INTERMISSION band has no word on it')
    # the date cards stay square
    loc = _cue_index(page, '8.3')
    if loc:
        _goto_cue(page, loc[0], loc[1] + 1)
        d = page.evaluate(M)
        if d and abs(d['w'] - H * 0.96) > 24:
            bad.append(f'the date card is {d["w"]:.0f} px wide, not the square {H*0.96:.0f} px — '
                       f'David’s own mockup says the date cards stay square')
    return bad


# --------------------------------------------------------------------------- D-013
def a_typed_foot(page):
    """The scene name types itself, with key clicks, and fumbles on a seeded one cue in five."""
    bad = []
    _boot(page)
    page.evaluate("""window.__snd=[]; if(!window.__sfxWrapped){ window.__sfxWrapped=1;
      const _s=window.sfx; window.sfx=function(n,o){ window.__snd.push(n); return _s(n,o); }; }""")
    stamps = page.evaluate("""(()=>{const o=[];for(let s=0;s<SHOW.length;s++)
        for(let k=0;k<SHOW[s].cues.length;k++){ const c=SHOW[s].cues[k];
          if(c.do.some(d=>d.op==='stamp'&&d.t&&String(d.t).trim())) o.push([s,k,c.id]); } return o;})()""")
    if not stamps:
        return ['no cue in the show carries a scene name']
    runs = []
    for si, ci, cid in stamps:
        _goto_cue(page, si, ci)
        page.evaluate('window.__snd=[]')
        rows = _play(page, every=24, tail=900, watch_ms=13000)
        snd = page.evaluate('window.__snd')
        seq, prev = [], None
        for s in rows:
            f = s.get('foot')
            n = len(f['t']) if f else 0
            if n != prev:
                seq.append(n)
                prev = n
        final = page.evaluate("""(()=>{const f=document.querySelector('#era .pad .sheet.top .foot');
            return f?f.textContent.trim():'';})()""")
        want = page.evaluate("""([s,k])=>{const d=SHOW[s].cues[k].do.slice().reverse().find(x=>x.op==='stamp');
            return d?String(d.t||''):'';}""", [si, ci])
        grew = [n for n in seq if n > 0]
        typed = len(set(grew)) >= max(4, min(8, len(want) // 2))
        backs = sum(1 for a, b in zip(seq, seq[1:]) if 0 < b < a)
        runs.append((cid, typed, backs, final, want, snd.count('click'), snd.count('del')))
    for cid, typed, backs, final, want, clicks, dels in runs:
        if final != want.strip():
            bad.append(f'{cid}: the foot line settles on “{final}”, not “{want}”')
        if not typed:
            bad.append(f'{cid}: “{want}” appears whole instead of being typed letter by letter')
        if clicks < 3:
            bad.append(f'{cid}: only {clicks} key clicks behind the typing — the haptics are missing')
    fumbled = [r[0] for r in runs if r[2] > 0]
    share = len(fumbled) / len(runs)
    if not fumbled:
        bad.append('no scene name ever fumbles a letter — the one-in-five typo is missing')
    elif not (0.06 <= share <= 0.42):
        bad.append(f'{len(fumbled)} of {len(runs)} scene names fumble ({share*100:.0f}%) — David '
                   f'asked for about one in five')
    for cid, typed, backs, final, want, clicks, dels in runs:
        if backs and dels < backs:
            bad.append(f'{cid}: the backspace makes no delete sound')
    # deterministic: the same cues must fumble on a second pass
    again = []
    for si, ci, cid in stamps:
        _goto_cue(page, si, ci)
        rows = _play(page, every=24, tail=900, watch_ms=13000)
        seq, prev = [], None
        for s in rows:
            f = s.get('foot')
            n = len(f['t']) if f else 0
            if n != prev:
                seq.append(n)
                prev = n
        if any(0 < b < a for a, b in zip(seq, seq[1:])):
            again.append(cid)
    if sorted(again) != sorted(fumbled):
        bad.append(f'the typo is not deterministic: pass 1 fumbled {sorted(fumbled)}, '
                   f'pass 2 fumbled {sorted(again)} — every night must be identical')
    return bad


# --------------------------------------------------------------------------- D-014
def a_92_no_inter_flash(page):
    """Intermission never shows up in a square frame — not at the tear, not at the top of 9.2."""
    bad = []
    _boot(page)
    for cid in ('9.1', '9.2'):
        loc = _cue_index(page, cid)
        if not loc:
            bad.append(f'{cid}: cue not found')
            continue
        si, ci = loc
        if cid == '9.1':
            _goto_cue(page, si, ci)
        rows = _play(page)
        for s in rows:
            for it in s['interTxt']:
                if cid == '9.2':
                    bad.append(f'9.2: “Intermission” is on stage at {s["t"]} ms '
                               f'({it["r"][2]:.0f}×{it["r"][3]:.0f} at x={it["r"][0]:.0f}) — '
                               f'the act has started; the word must be gone')
                    break
                if not it['band']:
                    bad.append(f'9.1: “Intermission” is showing at {s["t"]} ms on a page that is no '
                               f'longer the torn band — it snaps into the square frame '
                               f'({it["r"][2]:.0f}×{it["r"][3]:.0f}) and is cut off')
                    break
            else:
                continue
            break
    return bad


# --------------------------------------------------------------------------- D-047
def a_no_stray_pages(page):
    """Nothing is left on the stage but the calendar and the photo bed — no orphaned page from a
    cancelled, overlapping or completed transition, anywhere in the show."""
    bad = []
    _boot(page)
    page.evaluate("PERF='Gayle King'")
    CLEAN = """(()=>{const era=document.getElementById('era'); if(!era) return null;
      const on=el=>{const c=getComputedStyle(el);
        return c.display!=='none'&&c.visibility!=='hidden'&&parseFloat(c.opacity)>0.02;};
      const strays=[];
      era.querySelectorAll('.pad.ghost').forEach(g=>{ if(on(g)){const b=g.getBoundingClientRect();
        strays.push({w:'ghost pad',x:+b.x.toFixed(0),y:+b.y.toFixed(0),ww:+b.width.toFixed(0),hh:+b.height.toFixed(0)});}});
      era.querySelectorAll('.sheet.tear,.sheet.settle').forEach(g=>{ if(on(g)){const b=g.getBoundingClientRect();
        strays.push({w:'page in flight',x:+b.x.toFixed(0),y:+b.y.toFixed(0),ww:+b.width.toFixed(0),hh:+b.height.toFixed(0)});}});
      return {strays, pads:era.querySelectorAll('.pad').length,
              sheets:era.querySelectorAll('.pad:not(.ghost) .sheet').length};})()"""
    for si, ci, cid in _all_cues(page):
        _goto_cue(page, si, ci)
        _play(page, every=120, tail=3000, watch_ms=9000)
        r = page.evaluate(CLEAN)
        if not r:
            bad.append(f'{cid}: the era artifact is gone from the stage')
            continue
        for st in r['strays']:
            bad.append(f'{cid}: a {st["w"]} ({st["ww"]}x{st["hh"]}) is still on stage at '
                       f'({st["x"]},{st["y"]}) after the cue has settled')
        if r['pads'] != 1:
            bad.append(f'{cid}: {r["pads"]} calendar pads on stage, expected 1')
        if r['sheets'] != 3:
            bad.append(f'{cid}: the calendar has {r["sheets"]} sheets, expected 3')
    # …and an INTERRUPTED cue must clean up too: fire a house swap and cut it off with the next GO
    loc = _cue_index(page, '8.4')
    if loc:
        _goto_cue(page, loc[0], loc[1])
        page.evaluate('setTimeout(()=>advance(),0)')
        page.wait_for_timeout(220)
        page.evaluate('setTimeout(()=>advance(),0)')
        page.wait_for_timeout(2800)
        r = page.evaluate(CLEAN)
        for st in r['strays']:
            bad.append(f'8.4 cut off by the next GO: a {st["w"]} ({st["ww"]}x{st["hh"]}) is stranded '
                       f'at ({st["x"]},{st["y"]})')
    return bad


# --------------------------------------------------------------------------- D-036
def a_era_never_overlays(page):
    """Nothing ever overlays the phone: the calendar and the device never share a pixel, in any
    cue, at any instant of any animation."""
    bad = []
    _boot(page)
    worst = {}
    for si, ci, cid in _all_cues(page):
        _goto_cue(page, si, ci)
        rows = _play(page, every=24, tail=2200, watch_ms=14000)
        hot = [s for s in rows if s['ov'] > 0.001]
        if hot:
            top = max(hot, key=lambda s: s['ov'])
            worst[cid] = (top['ov'], top['t'], len(hot))
    for cid, (ov, t, n) in sorted(worst.items(), key=lambda kv: -kv[1][0]):
        bad.append(f'{cid}: the calendar covers {ov*100:.1f}% of the phone at {t} ms '
                   f'({n} frames) — nothing ever overlays the phone')
    return bad


# --------------------------------------------------------------------------- runner
PROBES = [a_era_morph, a_cards_fall, a_title_fills, a_typed_foot,
          a_92_no_inter_flash, a_no_stray_pages, a_era_never_overlays]

NOTE = {'a_era_morph': 'D-010', 'a_cards_fall': 'D-011', 'a_title_fills': 'D-012',
        'a_typed_foot': 'D-013', 'a_92_no_inter_flash': 'D-014',
        'a_no_stray_pages': 'D-047', 'a_era_never_overlays': 'D-036'}


def main():
    only = [a for a in sys.argv[1:] if not a.startswith('-')]
    fails = 0
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or None)
        pg = b.new_page(viewport={'width': W, 'height': H})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(FILE)
        pg.wait_for_timeout(1600)
        pg.evaluate("startAs('projection')")
        pg.wait_for_timeout(400)
        for fn in PROBES:
            if only and fn.__name__ not in only:
                continue
            try:
                out = fn(pg)
            except Exception as exc:                        # a probe must never hide a failure
                out = [f'probe crashed: {exc!r}']
            tag = f'{NOTE[fn.__name__]} {fn.__name__}'
            if out:
                fails += 1
                print(f'\n{tag}: {len(out)} PROBLEM(S)')
                for line in out[:14]:
                    print('   · ' + line)
                if len(out) > 14:
                    print(f'   · … and {len(out)-14} more')
            else:
                print(f'{tag}: CLEAN')
        b.close()
    if errs:
        fails += 1
        print('\nJS ERRORS:', errs[:4])
    print('\nERA NOTES:', 'CLEAN' if not fails else f'{fails} note(s) still open')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
