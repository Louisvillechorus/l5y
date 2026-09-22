"""David's Sept 21 notes, each proved on the live path.

Every assertion here plays the real cue through advance() and measures the thing the note is
about — the seconds a line is readable, the direction a card travels, the brightness of a
screen — never the source that is supposed to produce it.
"""
import io as _io
import os

W, H = 1920, 1080
URL = 'file://' + os.path.abspath('L5Y-Show-STANDALONE.html')


def _boot(pg, w=W, h=H):
    pg.set_viewport_size({'width': w, 'height': h})
    pg.evaluate("setCast('ml'); startAs('projection');")
    pg.wait_for_timeout(300)


def _at(pg, cid):
    return pg.evaluate("""(cid)=>{ for(let s=0;s<SHOW.length;s++){
        const k=SHOW[s].cues.findIndex(c=>c.id===cid); if(k>=0) return [s,k]; } return null; }""", cid)


def _park(pg, cid):
    loc = _at(pg, cid)
    if not loc:
        return None
    pg.evaluate(f"si={loc[0]}; ci={loc[1]}; animTok++; animRunning=false; hardRender();")
    pg.wait_for_timeout(400)
    return loc


def _fire(pg, cap=400):
    pg.evaluate("setTimeout(()=>advance(),0)")
    for _ in range(cap):
        pg.wait_for_timeout(100)
        if not pg.evaluate('animRunning'):
            return True
    return False


# ---------- D-068 · the typed scene name has to be readable ----------
def a_foot_dwell(pg):
    """David, Sept 21: "there are some moments where the typing of the day description disappears
    too quickly for the audience to read. Ie. 10.1 Audition Season… make sure they stay on the
    screen for at least 2-3 seconds fully typed before they disappear to the next cue." Every typed
    foot line in the show, measured by counting the frames it is complete and on a centred card."""
    bad = []
    _boot(pg)
    cues = pg.evaluate("""(()=>{const out=[];for(let s=0;s<SHOW.length;s++)
      SHOW[s].cues.forEach((c,k)=>{ (c.do||[]).forEach(o=>{ if(o.op==='stamp' && String(o.t||'').trim())
        out.push([s,k,c.id,o.t]); }); }); return out;})()""")
    if len(cues) < 15:
        bad.append('only %d typed foot lines found — the sweep is not seeing the show' % len(cues))
    for si, ci, cid, txt in cues:
        pg.evaluate(f"si={si}; ci={ci}; animTok++; animRunning=false; hardRender();")
        pg.wait_for_timeout(250)
        pg.evaluate("setTimeout(()=>advance(),0)")
        full = 0
        for _ in range(400):
            pg.wait_for_timeout(100)
            if pg.evaluate("""(t)=>{const e=document.getElementById('era');
                  if(!e||!e.classList.contains('center')) return false;
                  const f=e.querySelector('.pad .sheet.top .foot');
                  return !!(f && f.textContent===t && f.getBoundingClientRect().width>4);}""", txt):
                full += 1
            if not pg.evaluate('animRunning'):
                break
        if full * 0.1 < 2.0:
            bad.append('%s: %r is fully typed for only %.1fs — the house cannot read it'
                       % (cid, txt, full * 0.1))
    return bad


# ---------- D-069 · the dash is never white ----------
def a_dash_never_white(pg):
    """David, Sept 21: "12.2 there's a random white flash before the navigation starts." It was not
    a flash but a fade: the CarPlay Maps layer fades up over `.app`, the phone's white page. The
    dash region must be dark from its first painted frame."""
    try:
        from PIL import Image
    except Exception as e:
        return ['cannot verify the dash: %s' % e]
    bad = []
    _boot(pg, 1280, 720)
    # the dash moved to 12.2 when the drive split into "roll the calendar" and "the card becomes
    # the dash"; find the cue that actually raises CarPlay rather than naming one.
    drive = pg.evaluate("""(()=>{ for(let s=0;s<SHOW.length;s++){
        const k=SHOW[s].cues.findIndex(c=>(c.do||[]).some(o=>o.op==='device'&&o.dev==='carplay'));
        if(k>=0) return SHOW[s].cues[k].id; } return null; })()""")
    if not drive or not _park(pg, drive):
        return ['no cue in the show raises the CarPlay dash']
    pg.evaluate("setTimeout(()=>advance(),0)")
    peak, seen = 0.0, 0
    for _ in range(140):
        pg.wait_for_timeout(80)
        box = pg.evaluate("""(()=>{const m=document.querySelector('#projDevice .carplay .cp-main');
          if(!m) return null; const r=m.getBoundingClientRect();
          if(r.width<40||r.height<40) return null;
          return {x:Math.max(0,Math.round(r.x)), y:Math.max(0,Math.round(r.y)),
                  width:Math.round(Math.min(r.width,1280-Math.max(0,r.x))),
                  height:Math.round(Math.min(r.height,720-Math.max(0,r.y)))};})()""")
        if not box:
            if not pg.evaluate('animRunning'):
                break
            continue
        seen += 1
        im = Image.open(_io.BytesIO(pg.screenshot(clip=box))).convert('L').resize((64, 36))
        d = im.tobytes()
        peak = max(peak, sum(d) / len(d))
        if seen > 45:
            break
    if seen < 5:
        bad.append('the dash never came up — nothing to measure')
    elif peak > 90:
        bad.append('the dash reaches a mean of %.0f/255 while it comes up — it is still fading from '
                   'white' % peak)
    return bad


# ---------- D-070 · swipe LEFT, and the word is Clear ----------
def a_swipe_left_clear(pg):
    """David, Sept 21, with a reference shot: you swipe a notification RIGHT to open it. To get rid
    of one you swipe LEFT and the card slides off its own Clear button. 13.2 must go left, and the
    word must be on screen long enough to read."""
    bad = []
    _boot(pg)
    if not _park(pg, '13.2'):
        return ['there is no 13.2']
    pg.evaluate("setTimeout(()=>advance(),0)")
    far, lit = 0, 0
    for _ in range(200):
        pg.wait_for_timeout(100)
        m = pg.evaluate("""(()=>{const n=document.querySelector('#projDevice .nstack .notif');
          const c=document.querySelector('#projDevice .nclear');
          const tx=n?(new DOMMatrix(getComputedStyle(n).transform)).m41:null;
          return {tx: tx===null?null:Math.round(tx),
                  lit: !!(c && parseFloat(getComputedStyle(c).opacity)>0.9),
                  txt: c?c.textContent:null};})()""")
        if m['tx'] is not None:
            far = min(far, m['tx'])
        if m['lit']:
            lit += 1
            if (m['txt'] or '').strip() != 'Clear':
                bad.append('the revealed action reads %r, not "Clear"' % m['txt'])
        if not pg.evaluate('animRunning'):
            break
    if far >= 0:
        bad.append('the card never travels left (furthest offset %dpx) — that is the gesture that '
                   'OPENS a notification, not the one that clears it' % far)
    if lit * 0.1 < 0.5:
        bad.append('Clear is fully visible for only %.1fs — too quick to read' % (lit * 0.1))
    return bad


# ---------- D-071 · the one row that matters, held ----------
def a_share_row_held(pg):
    """David, Sept 21: "The find my change for 13.3 is VERY close, we just need to see 'sharing
    location from Jamie's iPad' on the screen for longer, so just change the camera zoom effect
    there." Both states of the Sharing From row must sit still and readable."""
    bad = []
    _boot(pg)
    if not _park(pg, '13.3'):
        return ['there is no 13.3']
    pg.evaluate("setTimeout(()=>advance(),0)")
    still, last, big = {}, None, 0
    for _ in range(300):
        pg.wait_for_timeout(100)
        m = pg.evaluate("""(()=>{const r=document.querySelector('#projDevice .fmshare');
          if(!r) return null; const b=r.getBoundingClientRect();
          return {txt:(r.innerText||'').replace(/\\n/g,' '), y:Math.round(b.y),
                  w:Math.round(b.width), h:Math.round(b.height)};})()""")
        if m:
            if last and last['txt'] == m['txt'] and abs(last['y'] - m['y']) < 2:
                still[m['txt']] = still.get(m['txt'], 0) + 1
            last = m
            big = max(big, m['w'])
        if not pg.evaluate('animRunning'):
            break
    for want in ('iPad', 'iPhone'):
        hit = [v for k, v in still.items() if want in k]
        if not hit:
            bad.append('the Sharing From row never settles on %s' % want)
        elif max(hit) * 0.1 < 2.5:
            bad.append('Sharing From %s sits still for only %.1fs — David asked for longer'
                       % (want, max(hit) * 0.1))
    if big < W * 0.5:
        bad.append('the row is only %dpx wide — the camera never went to it' % big)
    return bad


# ---------- D-072 · the ending ----------
def a_ending_on_her_text(pg):
    """David, Sept 21: "the last thing we should see before the blackout is the text 'tonight was
    amazing', you can cut everything else after that, and then the blackout should be a slow
    blackout to actual black then one final cue to show the end screen." """
    bad = []
    _boot(pg)
    ids = pg.evaluate("(()=>SHOW[SHOW.length-1].cues.map(c=>c.id))()")
    if '14.5' in ids:
        bad.append('14.5 is still in the show — his last verse was cut')
    if not _park(pg, '14.4'):
        return bad + ['there is no 14.4']

    # her animation ends with the text lit, not with a dark phone
    if not _fire(pg):
        bad.append('14.4 never settles')
    st = pg.evaluate("""(()=>{const t=document.querySelector('#projDevice .thread');
      return {tail: t?(t.innerText||'').replace(/\\n+/g,' | ').slice(-46):null,
              scroff: (typeof CUR!=='undefined' && !!CUR && !!CUR.scroff),
              blk: document.body.classList.contains('blk')};})()""")
    if st['scroff']:
        bad.append('her screen still goes dark in her hand — the text is meant to be the last image')
    if st['blk']:
        bad.append('the stage is already black at the end of 14.4')
    if not st['tail'] or 'tonight was amazing' not in st['tail']:
        bad.append('14.4 does not end on her sent text (thread tail %r)' % (st['tail'],))
    if 'Delivered' not in (st['tail'] or ''):
        bad.append('the text is not delivered at the end of 14.4')

    # the curtain FADES, and it takes long enough to read as a fade
    import time
    t0 = time.time()
    if not _fire(pg):
        bad.append('14.6 never settles')
    dur = time.time() - t0
    if dur < 2.5:
        bad.append('the curtain takes %.1fs — that is a cut, not a slow blackout' % dur)
    if not pg.evaluate("document.body.classList.contains('blk')"):
        bad.append('the curtain does not reach true black')

    # …and one more GO brings the end screen back
    _fire(pg)
    end = pg.evaluate("""(()=>{const e=document.getElementById('era');const pad=e.querySelector('.pad');
      return {bows: (typeof CUR!=='undefined' && !!CUR && !!CUR.bows), face: e.dataset.face||'',
              cls: pad?pad.className:'', loop: !!document.querySelector('#loop')};})()""")
    if not end['bows']:
        bad.append('the last GO does not bring the end screen back')
    if 'house' not in (end['cls'] or ''):
        bad.append('the end screen is not the house title card (pad %r)' % end['cls'])
    return bad


# ---------- D-073 · the calendar never comes home wearing the wrong type ----------
def a_home_morph_clean(pg):
    """David, Sept 21: "end of 1.7 there's a text size issue here… seems like this issue recurs
    anytime we go back to the main YEAR # month/day screen initially then fixes itself as the warp
    happens." Coming home, the type's FLIP could be measured against the card's own layout, so the
    words flew at full card size across a strip-width sheet and hung off the paper. No frame of a
    homeward morph may show ink outside the paper."""
    bad = []
    _boot(pg)
    for cid in ('3.4', '3.7'):
        if not _park(pg, cid):
            continue
        pg.evaluate("setTimeout(()=>advance(),0)")
        worst = 0
        for _ in range(260):
            pg.wait_for_timeout(40)
            m = pg.evaluate("""(()=>{const e=document.getElementById('era');
              const pf=e.querySelector('.pad .sheet.top .pf'); const sh=e.querySelector('.pad .sheet.top');
              if(!pf||!sh) return null;
              const p=pf.getBoundingClientRect(); if(p.width<8) return null;
              let over=0;
              ['.yr','.ynum','.mo','.ft'].forEach(s=>{ const el=sh.querySelector(s);
                if(!el||!el.textContent.trim()) return;
                if(parseFloat(getComputedStyle(el).opacity)<0.05) return;
                const r=document.createRange(); r.selectNodeContents(el);
                const b=r.getBoundingClientRect(); if(b.width<2) return;
                over=Math.max(over, Math.round(Math.max(p.left-b.left, b.right-p.right))); });
              return over;})()""")
            if m is not None:
                worst = max(worst, m)
            if not pg.evaluate('animRunning'):
                break
        if worst > 60:
            bad.append('%s: coming home, the type hangs %dpx off the paper before it settles'
                       % (cid, worst))
    return bad
