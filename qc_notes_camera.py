"""CAMERA PROBES — the assertions behind David's framing / navigation / pacing notes.

qc_notes.py loads every a_* in this file and runs it against the built STANDALONE on the
LIVE path (advance(), like the operator). Each probe returns [] or a list of plain-English
complaints. Nothing here is an opinion: every complaint carries the number that failed.

THE GEOMETRY EVERY PROBE IS MEASURED AGAINST
  frame          1920 x 1080
  reading window the frame minus ERA_ZONE_ (the docked calendar strip owns the right 19%)
                 -> 1555 x 1080
  resting scale  camFill() = window width / phone width = 3.39x. At that scale the phone
                 fills the window edge to edge and the audience sees 318 of the phone's 994
                 points of height -- a wide, short slot that holds a little under three
                 notification cards. That is why the lock screen is framed by PANNING and
                 never by zooming out: zooming out is what opened the black bars.
"""
import os
import re

FILE = 'file://' + os.path.abspath('L5Y-Show-STANDALONE.html')

# ---------------------------------------------------------------- driving

BOOT = 'startAs("projection")'


def boot(pg):
    pg.evaluate(BOOT)
    pg.wait_for_timeout(250)


STILL = """(() => {
  const s=document.querySelector('#projection .screen,#projection .fullstage');
  if(!s) return true;
  return [...s.getAnimations(), ...[...s.querySelectorAll('*')].flatMap(e=>e.getAnimations())]
    .every(a=>a.playState!=='running');
})()"""


def still(pg, cap=30):
    """the phone rises on `phoneIn` and cards land on `bannerIn`: a rect read mid-entrance is
       the animation's, not the camera's. Wait for the screen to stop moving before measuring."""
    for _ in range(cap):
        if pg.evaluate(STILL):
            return
        pg.wait_for_timeout(80)


def at(pg, si, ci):
    """park the operator on cue index ci of song si (the state is rebuilt from the cue data)"""
    pg.evaluate(f'si={si}; ci={ci}; animTok++; animRunning=false; hardRender();')
    pg.wait_for_timeout(180)
    still(pg)


def fire(pg, settle=1800):
    """fire the next GO and wait for the cue AND any camera glide it left in flight"""
    pg.evaluate('advance()')          # evaluate awaits the cue's promise
    pg.wait_for_timeout(settle)
    still(pg)


def fire_async(pg):
    """fire the next GO without waiting, so the beat can be sampled while it plays"""
    pg.evaluate('advance(); 0')


def idle(pg, cap=240):
    for _ in range(cap):
        pg.wait_for_timeout(100)
        if not pg.evaluate('animRunning'):
            return True
    return False


def cueids(pg, si):
    return pg.evaluate(f'SHOW[{si}].cues.map(c=>c.id)')


def nsongs(pg):
    return pg.evaluate('SHOW.length')


def find_cue(pg, cid):
    for s in range(nsongs(pg)):
        ids = cueids(pg, s)
        if cid in ids:
            return s, ids.index(cid)
    return None, None


def cues_with(pg, opname):
    """[(si, ci, cueid)] for every cue in the show carrying an op of this name"""
    return pg.evaluate("""(op)=>{const out=[];SHOW.forEach((s,si)=>s.cues.forEach((c,ci)=>{
      if(c.do.some(o=>o.op===op)) out.push([si,ci,c.id]);}));return out;}""", opname)


# ---------------------------------------------------------------- measuring

GEO = """(() => {
  const P=document.getElementById('projection'); const F=P.getBoundingClientRect();
  const cam=P.querySelector('.stagecam');
  const dev=P.querySelector('.iphone,.macbook,.carplay,.fullstage');
  const r=e=>{const b=e.getBoundingClientRect();
    return {l:+b.left.toFixed(1),t:+b.top.toFixed(1),r:+b.right.toFixed(1),b:+b.bottom.toFixed(1),
            w:+b.width.toFixed(1),h:+b.height.toFixed(1)};};
  const q=s=>{const e=P.querySelector(s); return e?r(e):null;};
  const all=s=>[...P.querySelectorAll(s)].map(r);
  let z=null; if(cam){ try{ z=new DOMMatrix(getComputedStyle(cam).transform).a; }catch(e){} }
  return {
    frame:{l:F.left,t:F.top,r:F.right,b:F.bottom,w:F.width,h:F.height},
    uw:F.width*(1-ERA_ZONE_()), ux:F.left,
    z: z===null?null:+z.toFixed(3), dz: cam?cam.dataset.z:null,
    kind: dev?(dev.className.split(' ')[0]):null,
    app: CUR.app, black: !!CUR.black, dev: CUR.dev,
    phone: q('.iphone'), clock: q('.lk-time'), stack: q('.nstack'),
    notifs: all('.nstack .notif'),
    tapped: q('.happ.tapped'), cnm: q('.cnm'), btns: q('.callbtns'),
    them: q('.thread .bub.them'), field: q('.imsg .bar .field'),
    text: (P.querySelector('.screenstack')||{}).innerText||''
  };
})()"""


def geo(pg):
    return pg.evaluate(GEO)


def inside(rect, g, pad=0.0):
    """is this rect wholly inside the reading window?"""
    return (rect['l'] >= g['ux'] - pad and rect['r'] <= g['ux'] + g['uw'] + pad
            and rect['t'] >= g['frame']['t'] - pad and rect['b'] <= g['frame']['b'] + pad)


def partial(rect, g):
    """does this rect straddle a frame edge (partly on stage, partly cut off)?"""
    F = g['frame']
    if rect['b'] <= F['t'] or rect['t'] >= F['b']:
        return False                      # wholly off stage: honest
    return rect['t'] < F['t'] - 0.5 or rect['b'] > F['b'] + 0.5


def fillfrac(g):
    """share of the reading window's width the phone actually covers"""
    if not g['phone']:
        return None
    lo, hi = max(g['phone']['l'], g['ux']), min(g['phone']['r'], g['ux'] + g['uw'])
    return max(0.0, hi - lo) / g['uw']


# ================================================================ D-001

def a_house_to_prologue(pg):
    """1.0b -> 1.1: the title page must fall LOOKING LIKE THE TITLE PAGE.

    The bug: tearTop clones the top sheet and setStamp then strips the pad's face classes,
    so the clone was re-typeset in mid-air (THE LAST 9vh -> 28vh, wrapped to two lines, the
    5 off the bottom of the sheet) for the whole second of the fall.
    """
    bad = []
    boot(pg)
    s, c = find_cue(pg, '1.1')
    if s is None:
        return ['there is no cue 1.1 in the show']
    at(pg, s, c - 2)
    fire(pg, 500)            # 1.0a
    fire(pg, 500)            # 1.0b
    before = pg.evaluate("""(()=>{const sh=document.querySelector('#era .pad .sheet.top');
      const f=s=>{const e=sh.querySelector(s); return e?{fs:+parseFloat(getComputedStyle(e).fontSize).toFixed(1),
        txt:e.textContent.trim(), h:+e.getBoundingClientRect().height.toFixed(1)}:null;};
      return {yr:f('.yr'), ynum:f('.ynum'), sub:f('.sub'), frow:f('.frow')};})()""")
    if not before['yr'] or before['yr']['txt'] != 'THE LAST':
        bad.append(f"the page on the pad before the prologue is not the title page ({before['yr']})")
    fire_async(pg)
    seen = []
    for _ in range(9):
        pg.wait_for_timeout(70)
        seen.append(pg.evaluate("""(()=>{const t=document.querySelector('#era .pad .tear'); if(!t) return null;
          const sb=t.getBoundingClientRect();
          const f=s=>{const e=t.querySelector(s); if(!e) return null; const b=e.getBoundingClientRect();
            return {fs:+parseFloat(getComputedStyle(e).fontSize).toFixed(1), txt:e.textContent.trim(),
                    h:+b.height.toFixed(1), over:+(b.bottom-sb.bottom).toFixed(1), wide:+(b.right-sb.right).toFixed(1)};};
          return {yr:f('.yr'), ynum:f('.ynum'), sub:f('.sub')};})()"""))
    got = [x for x in seen if x]
    if not got:
        return bad + ['no torn page ever appeared: the title card is replaced, not torn off']
    f = got[0]
    for key in ('yr', 'ynum', 'sub'):
        b4, now = before.get(key), f.get(key)
        if not b4 or not now:
            continue
        if abs(b4['fs'] - now['fs']) > 0.6:
            bad.append(f"the falling page re-typesets '{now['txt']}': {b4['fs']}px on the pad, "
                       f"{now['fs']}px in the air ({now['fs']/max(b4['fs'],.1):.2f}x)")
        if abs(b4['h'] - now['h']) > 2.0:
            bad.append(f"the falling '{now['txt']}' reflows: {b4['h']}px tall on the pad, {now['h']}px in the air")
    for key in ('yr', 'ynum', 'sub'):
        now = f.get(key)
        if now and now['over'] > 1.0:
            bad.append(f"the falling page's '{now['txt']}' runs {now['over']}px off the bottom of its own sheet")
    return bad


# ================================================================ D-002

def a_13_to_14(pg):
    """1.3 -> 1.4 must not be a jump cut: same scale, and the thread rolls instead of snapping."""
    bad = []
    boot(pg)
    s, c = find_cue(pg, '1.3')
    if s is None:
        return ['there is no cue 1.3 in the show']
    at(pg, s, c - 1)
    fire(pg, 2500)                      # 1.2 lands us in the thread
    z12 = geo(pg)['z']
    fire(pg, 2500)                      # 1.3 Delivered -> Read
    g13 = geo(pg)
    top0 = pg.evaluate("(()=>{const t=document.querySelector('#projection .thread'); return t?t.scrollTop:null;})()")
    tr13 = pg.evaluate("document.querySelector('#projection .stagecam').style.transform")
    fire_async(pg)                      # 1.4 his typing bubble
    tops = []
    for _ in range(14):
        pg.wait_for_timeout(55)
        tops.append(pg.evaluate("(()=>{const t=document.querySelector('#projection .thread'); return t?t.scrollTop:null;})()"))
    pg.wait_for_timeout(1500)
    g14 = geo(pg)
    for nm, z in (('1.2', z12), ('1.3', g13['z']), ('1.4', g14['z'])):
        if z is None:
            bad.append(f'{nm}: no camera on the thread at all')
    zs = {round(z, 2) for z in (z12, g13['z'], g14['z']) if z is not None}
    if len(zs) > 1:
        bad.append(f'the camera changes scale inside one register across 1.2/1.3/1.4: {sorted(zs)}')
    tr14 = pg.evaluate("document.querySelector('#projection .stagecam').style.transform")
    if tr13 != tr14:
        bad.append(f'the camera moves on 1.4 while a bubble lands in frame ({tr13} -> {tr14})')
    seq = [t for t in tops if t is not None]
    if top0 is not None and seq:
        total = max(seq) - top0
        if total > 6:
            steps = [seq[0] - top0] + [seq[i] - seq[i - 1] for i in range(1, len(seq))]
            big = max(abs(x) for x in steps)
            if big > total * 0.55:
                bad.append(f'the thread SNAPS to its foot on 1.4: {big:.0f}px of a {total:.0f}px '
                           f'move in a single frame (a roll would be under {total*0.55:.0f})')
    return bad


# ================================================================ D-003 / D-006

def _tap_beat(pg, si, ci, cid, icon):
    """fire one openapp cue and watch the icon press: [visible ms, in-frame ms, complaints]"""
    bad = []
    at(pg, si, ci)
    fire_async(pg)
    vis = held = 0
    step = 60
    # 1.2 is a FIFTY-SECOND cue and its icon press lands at 9.7 s. The old 140-step window stopped
    # looking after 8.4 s and reported the press missing on a beat that plays perfectly. The loop
    # still exits the moment the press has been seen and released, so the cost is only paid when
    # something really is wrong.
    for _ in range(1000):
        pg.wait_for_timeout(step)
        m = pg.evaluate("""(()=>{const P=document.getElementById('projection');
          const e=P.querySelector('.happ.tapped'); if(!e) return null; const b=e.getBoundingClientRect();
          const F=P.getBoundingClientRect();
          return {l:b.left,t:b.top,r:b.right,b:b.bottom,ux:F.left,uw:F.width*(1-ERA_ZONE_()),ft:F.top,fb:F.bottom,
                  scale:+parseFloat(getComputedStyle(e.querySelector('.gi')).transform.split(',')[3]||1)};})()""")
        if m:
            vis += step
            if (m['l'] >= m['ux'] - 1 and m['r'] <= m['ux'] + m['uw'] + 1
                    and m['t'] >= m['ft'] - 1 and m['b'] <= m['fb'] + 1):
                held += step
        elif vis:
            break
        if not pg.evaluate('animRunning') and vis:
            break
    if vis == 0:
        bad.append(f'{cid}: the {icon} icon is never shown pressed — the app just opens')
    elif held < 600:
        bad.append(f'{cid}: the pressed {icon} icon is only inside the reading window for {held}ms '
                   f'(visible {vis}ms) — the click happens off camera')
    return vis, held, bad


def a_17_facebook_tap(pg):
    """we must SEE her press Facebook before the Memories open."""
    boot(pg)
    hits = [x for x in cues_with(pg, 'openapp')
            if pg.evaluate(f"SHOW[{x[0]}].cues[{x[1]}].do.filter(o=>o.op==='openapp')[0].icon") == 'Facebook']
    if not hits:
        return ['no cue opens Facebook from the home screen']
    out = []
    for si, ci, cid in hits:
        vis, held, bad = _tap_beat(pg, si, ci, cid, 'Facebook')
        out += bad
    return out


def a_app_tap_visible(pg):
    """EVERY app launch in the show: the icon is pressed, on camera, long enough to read."""
    boot(pg)
    out = []
    for si, ci, cid in cues_with(pg, 'openapp'):
        icon = pg.evaluate(f"SHOW[{si}].cues[{ci}].do.filter(o=>o.op==='openapp')[0].icon")
        vis, held, bad = _tap_beat(pg, si, ci, cid, icon)
        out += bad
    return out


# ================================================================ D-004

def a_17_slower(pg):
    """the memory beat runs 15% slower than it did — in the engine and in the cue."""
    bad = []
    boot(pg)
    k = pg.evaluate("typeof MEM_SLOW_==='function' ? MEM_SLOW_() : null")
    if k is None:
        return ['there is no MEM_SLOW_ factor in the engine']
    if abs(k - 1.15) > 0.001:
        bad.append(f'the memory slow factor is {k}, not 1.15')
    # end to end: the same gesture, timed at 1.00x and at the show's factor
    t = pg.evaluate("""(async()=>{
      const d=document.createElement('div');
      d.style.cssText='position:fixed;left:-9999px;top:0;width:200px;height:200px;overflow:auto';
      d.innerHTML='<div style="height:2000px"></div>'; document.body.appendChild(d);
      const run=async k=>{ d.scrollTop=0; const t0=performance.now();
        await humanScroll(d,900,'qcslow',animTok,{gesture:'drag',slow:k}); return performance.now()-t0; };
      const a=await run(1), b=await run(MEM_SLOW_()); d.remove(); return {a,b};
    })()""")
    ratio = t['b'] / max(t['a'], 1)
    if abs(ratio - 1.15) > 0.06:
        bad.append(f'the memory scroll gesture runs {ratio:.3f}x slower, not 1.15x '
                   f'({t["a"]:.0f}ms -> {t["b"]:.0f}ms)')
    # the cue's own beats moved with it
    s, c = find_cue(pg, '1.6')
    if s is None:
        return bad + ['there is no cue 1.6']
    pauses = pg.evaluate(f"SHOW[{s}].cues[{c}].do.filter(o=>o.op==='pause').map(o=>o.ms)")
    want = [2070, 5750, 5750, 5750, 2070]
    if pauses != want:
        bad.append(f'the memory cue still holds its old beats: {pauses} (15% slower is {want})')
    return bad


# ================================================================ D-005 / D-044

def _stack_complaints(g, cid):
    """the lock-screen framing law, measured. Returns a list of complaints."""
    bad = []
    if not g['notifs']:
        return bad
    F = g['frame']
    if g['clock'] and partial(g['clock'], g):
        bad.append(f"{cid}: the clock is sliced by the frame edge "
                   f"(top {g['clock']['t']:.0f}, bottom {g['clock']['b']:.0f} in a 0..{F['b']:.0f} frame)")
    for i, n in enumerate(g['notifs']):
        if partial(n, g) and n['t'] < F['t'] - 0.5:
            bad.append(f'{cid}: notification {i+1} is sliced by the TOP of the frame (top {n["t"]:.0f})')
    newest = g['notifs'][0]
    if not inside(newest, g, 1.0):
        bad.append(f'{cid}: the NEWEST notification is not whole in the reading window '
                   f'(top {newest["t"]:.0f}, bottom {newest["b"]:.0f}, right {newest["r"]:.0f})')
    if len(g['notifs']) >= 2:
        n = g['notifs'][1]
        fits = (n['b'] - g['notifs'][0]['t']) <= F['h']      # can two cards be on stage together at all?
        if fits and not inside(n, g, 1.0):
            bad.append(f'{cid}: the second notification is not whole in the reading window '
                       f'(top {n["t"]:.0f}, bottom {n["b"]:.0f}) — this is the "Rob\'s card is chopped" picture')
    return bad


def a_22_two_notifs_framed(pg):
    """2.1/2.2: both texts whole and centred in the reading window; the clock is not the subject."""
    bad = []
    boot(pg)
    s, c = find_cue(pg, '2.1')
    if s is None:
        return ['there is no cue 2.1']
    at(pg, s, c)
    fire(pg, 2600)
    g = geo(pg)
    cid = '2.1 (the lock screen 2.2 is called on)'
    bad += _stack_complaints(g, cid)
    ff = fillfrac(g)
    if ff is None:
        return bad + [f'{cid}: no phone on stage']
    if ff < 0.99:
        bad.append(f'{cid}: the phone covers {ff*100:.1f}% of the reading window — '
                   f'{(1-ff)*g["uw"]:.0f}px of black down the sides')
    if g['clock'] and g['clock']['b'] > g['frame']['t'] + 1:
        bad.append(f"{cid}: the clock is still on stage (bottom {g['clock']['b']:.0f}) — "
                   f'David: the clock is not the subject')
    if len(g['notifs']) >= 2:
        pair_t, pair_b = g['notifs'][0]['t'], g['notifs'][1]['b']
        mid = (pair_t + pair_b) / 2
        off = abs(mid - (g['frame']['t'] + g['frame']['h'] / 2))
        if off > 140:
            bad.append(f'the two texts are not centred: their centre is {off:.0f}px off the '
                       f'frame centre (allowed 140)')
        if pair_t < 40:
            bad.append(f'no air above the first text: {pair_t:.0f}px')
    else:
        bad.append(f'{cid}: fewer than two notifications on the lock screen')
    return bad


def a_stack_whole(pg):
    """SHOW-WIDE: nothing on a lock screen is ever sliced by the frame edge.

    The law this asserts, and why it is the strongest one the geometry allows: at the resting
    scale the reading window shows 318 of the phone's 994 points, which holds two notification
    cards and a little more. Songs 4 and 9 end the number with FIVE cards on the lock screen
    (1829px of card at that scale, in a 1080px frame), so "every card whole" is impossible
    without zooming out and opening black bars down both sides. What is asserted instead:
      * the clock is never half in frame  (it is the thing that goes -- David's priority)
      * no card is ever sliced by the TOP edge
      * the newest card is always whole, and when a second one can fit beside it, so is that
    A card below those may run past the bottom edge: that is a real lock screen continuing
    below the fold, and it is the only thing that gives way.
    """
    bad = []
    boot(pg)
    # every cue in the show, settled (hardRender is the resting frame by definition)...
    for si in range(nsongs(pg)):
        ids = cueids(pg, si)
        for ci in range(len(ids)):
            at(pg, si, ci + 1)
            g = geo(pg)
            if g['black'] or not g['notifs']:
                continue
            bad += _stack_complaints(g, ids[ci])
    # ...and every cue that actually delivers a notification, on the live path
    for si, ci, cid in cues_with(pg, 'notif'):
        at(pg, si, ci)
        fire(pg, 2600)
        bad += _stack_complaints(geo(pg), cid + ' (live)')
    return bad


# ================================================================ D-007

def a_23_pingpong(pg):
    """2.2: while the dead drafts are typed the camera goes keyboard -> her message -> keyboard."""
    bad = []
    boot(pg)
    s, c = find_cue(pg, '2.2')
    if s is None:
        return ['there is no cue 2.2']
    looks = pg.evaluate(f"SHOW[{s}].cues[{c}].do.filter(o=>o.op==='type').map(o=>({{t:o.t,look:!!o.look}}))")
    if not looks:
        return ['cue 2.2 types nothing']
    if looks[-1]['look']:
        bad.append('the last thing he types ("home safe?") still glances away — '
                   'the going back and forth must stop when he lands on it')
    if sum(1 for x in looks[:-1] if x['look']) < 3:
        bad.append(f'only {sum(1 for x in looks[:-1] if x["look"])} of the {len(looks)-1} dead drafts '
                   'look back at her message')
    at(pg, s, c)
    fire_async(pg)
    her_whole = field_whole = 0
    tys, mid = [], []
    for _ in range(700):
        pg.wait_for_timeout(100)
        m = pg.evaluate("""(()=>{const P=document.getElementById('projection');const F=P.getBoundingClientRect();
          const ux=F.left, uw=F.width*(1-ERA_ZONE_()); const cam=P.querySelector('.stagecam');
          let ty=null; if(cam){try{ty=new DOMMatrix(getComputedStyle(cam).transform).f;}catch(e){}}
          const w=e=>{if(!e) return false; const b=e.getBoundingClientRect();
            return b.left>=ux-1 && b.right<=ux+uw+1 && b.top>=F.top-1 && b.bottom<=F.bottom+1;};
          const her=P.querySelector('.thread .bub.them');
          const c=her?her.getBoundingClientRect():null;
          return {them:w(her), field:w(P.querySelector('.imsg .bar .field')), ty,
                  herMid:c?Math.abs((c.top+c.bottom)/2-(F.top+F.height/2)):null, run:animRunning};})()""")
        if m['them']:
            her_whole += 100
            if m['herMid'] is not None and m['herMid'] < 220:
                mid.append(m['herMid'])
        if m['field']:
            field_whole += 100
        if m['ty'] is not None:
            tys.append(m['ty'])
        if not m['run']:
            break
    # the camera's own travel: count the reversals of direction, each one a real glide
    legs, d = 0, 0
    for i in range(1, len(tys)):
        step = tys[i] - tys[i - 1]
        if abs(step) < 1.0:
            continue
        s2 = 1 if step > 0 else -1
        if s2 != d:
            legs += 1
            d = s2
    if her_whole < 2000:
        bad.append(f'her message is whole in centre frame for only {her_whole}ms of the drafts — '
                   'David: "it is cut off"')
    if not mid:
        bad.append('her message is never brought to the CENTRE of the frame, only into it')
    if legs < 6:
        bad.append(f'the camera only travels {legs} legs across three dead drafts — it must go back '
                   'and forth, keyboard to message, like his mind (6 = up and down on each draft)')
    if field_whole < 4000:
        bad.append(f'the keyboard/field is only in frame for {field_whole}ms — he has to be seen typing')
    return bad


# ================================================================ D-008

def a_maybe_cathy(pg):
    """an unsaved number reads "Maybe: Cathy" on every surface song 2 shows it on."""
    bad = []
    boot(pg)
    RAW = '555-0148'
    want = {'2.1': 'the lock-screen notification', '2.2': 'the Messages list and the thread header',
            '2.3': 'the call screen'}
    s, _ = find_cue(pg, '2.1')
    if s is None:
        return ['song 2 has no cue 2.1']
    ids = cueids(pg, s)
    for cid, where in want.items():
        if cid not in ids:
            bad.append(f'no cue {cid}')
            continue
        at(pg, s, ids.index(cid) + 1)
        txt = pg.evaluate("(document.querySelector('#projection .screenstack')||{}).innerText||''")
        if RAW in txt:
            bad.append(f'{cid}: {where} still shows the bare number')
        if 'Maybe: Cathy' not in txt:
            bad.append(f'{cid}: {where} does not read "Maybe: Cathy" (screen reads: '
                       f'{re.sub(chr(10), " / ", txt)[:90]})')
    # the thread header and the list row specifically
    at(pg, s, ids.index('2.2') + 1)
    hdr = pg.evaluate("(()=>{const e=document.querySelector('#projection .imsg .hdr .nm'); return e?e.textContent.trim():null;})()")
    if hdr and 'Maybe: Cathy' not in hdr:
        bad.append(f'the thread header reads "{hdr}"')
    # ...and iOS draws the generic person, never a monogram, for a name it only guessed
    mono = pg.evaluate("""(()=>{const e=document.querySelector('#projection .imsg .hdr .av');
      return e?{txt:e.textContent.trim(), svg:!!e.querySelector('svg')}:null;})()""")
    if mono and mono['txt'] and not mono['svg']:
        bad.append(f'the thread avatar shows the monogram "{mono["txt"]}" for a number that is not in Contacts')
    # the whole show: the bare number must not survive anywhere
    for si in range(nsongs(pg)):
        for ci in range(len(cueids(pg, si))):
            at(pg, si, ci + 1)
            t = pg.evaluate("(document.querySelector('#projection .screenstack')||{}).innerText||''")
            if RAW in t:
                bad.append(f'{cueids(pg, si)[ci]}: the bare number is still on screen')
    return bad


# ================================================================ D-009 / D-045

def _call_beat(pg, si, ci, cid):
    """fire a connected-call cue and watch for the wide beat. -> (minz, btns_ms, complaints)"""
    at(pg, si, ci)
    fire_async(pg)
    minz, maxz, btns_ms, both = 9.9, 0.0, 0, 0
    for _ in range(200):
        pg.wait_for_timeout(100)
        m = pg.evaluate("""(()=>{const P=document.getElementById('projection');const F=P.getBoundingClientRect();
          const ux=F.left, uw=F.width*(1-ERA_ZONE_()); const cam=P.querySelector('.stagecam');
          let z=null; if(cam){try{z=new DOMMatrix(getComputedStyle(cam).transform).a;}catch(e){}}
          const w=e=>{if(!e) return false; const b=e.getBoundingClientRect();
            return b.left>=ux-1 && b.right<=ux+uw+1 && b.top>=F.top-1 && b.bottom<=F.bottom+1;};
          return {z, btns:w(P.querySelector('.callbtns')), nm:w(P.querySelector('.cnm')), run:animRunning};})()""")
        if m['z']:
            minz = min(minz, m['z'])
            maxz = max(maxz, m['z'])
        if m['btns']:
            btns_ms += 100
            if m['nm']:
                both += 100
        if not m['run']:
            break
    pg.wait_for_timeout(1800)
    return minz, maxz, btns_ms, both, geo(pg)


def a_24_wide_then_in(pg):
    """2.3: out to the whole call UI first, then in on "Maybe: Cathy"."""
    bad = []
    boot(pg)
    s, c = find_cue(pg, '2.3')
    if s is None:
        return ['there is no cue 2.3']
    minz, maxz, btns_ms, both, g = _call_beat(pg, s, c, '2.3')
    if minz > 1.6:
        bad.append(f'the camera never pulls out: its widest during 2.3 is {minz:.2f}x '
                   f'(the whole call UI needs about 1.09x)')
    if both < 900:
        bad.append(f'the whole call UI (name AND buttons together) is only on stage for {both}ms')
    if maxz - minz < 1.0:
        bad.append(f'no push-in after the wide: the camera only travels {minz:.2f}x -> {maxz:.2f}x')
    if not g['cnm'] or not inside(g['cnm'], g, 2):
        bad.append('2.3 does not settle on the name')
    ff = fillfrac(g)
    if ff is not None and ff < 0.99:
        bad.append(f'2.3 settles {ff*100:.1f}% wide — the push-in must come back to a full window')
    return bad


def a_call_controls(pg):
    """every connected call shows mute / end / speaker on stage (CLAUDE.md: buttons match state)."""
    bad = []
    boot(pg)
    hits = []
    for si, ci, cid in cues_with(pg, 'callState'):
        sts = pg.evaluate(f"SHOW[{si}].cues[{ci}].do.filter(o=>o.op==='callState').map(o=>o.st||'')")
        if any(not re.search('ended', x, re.I) for x in sts):
            hits.append((si, ci, cid))
    if not hits:
        return ['no cue in the show connects a call']
    for si, ci, cid in hits:
        if pg.evaluate(f"(()=>{{const s=buildState(SHOW[{si}],{ci+1}); return s.dev;}})()") != 'iphone':
            continue
        minz, maxz, btns_ms, both, g = _call_beat(pg, si, ci, cid)
        if btns_ms < 1200:
            bad.append(f'{cid}: the call controls are on stage for only {btns_ms}ms — '
                       'a connected call must show mute / end / speaker')
    return bad


# ================================================================ D-039

def a_fills_window(pg):
    """no cue settles with black down the sides of the reading window."""
    bad = []
    boot(pg)
    for si in range(nsongs(pg)):
        ids = cueids(pg, si)
        for ci in range(len(ids)):
            at(pg, si, ci + 1)
            g = geo(pg)
            if g['black'] or g['kind'] != 'iphone':
                continue
            ff = fillfrac(g)
            if ff is None:
                continue
            if ff < 0.99:
                bad.append(f'{ids[ci]}: the phone covers {ff*100:.1f}% of the reading window '
                           f'({(1-ff)*g["uw"]:.0f}px of black), cam {g["z"]}x')
    return bad


# ================================================================ D-040

def a_one_scale_per_register(pg):
    """one register, one resting scale — everywhere it appears in the show."""
    bad = []
    boot(pg)
    seen = {}
    for si in range(nsongs(pg)):
        ids = cueids(pg, si)
        for ci in range(len(ids)):
            at(pg, si, ci + 1)
            g = geo(pg)
            if g['black'] or g['kind'] != 'iphone' or g['z'] is None:
                continue
            seen.setdefault(g['app'], {}).setdefault(round(g['z'], 2), []).append(ids[ci])
    for app, scales in sorted(seen.items()):
        if len(scales) > 1:
            parts = '; '.join(f'{z}x on {v[:4]}' for z, v in sorted(scales.items()))
            bad.append(f'the {app} register renders at {len(scales)} different scales: {parts}')
    allz = sorted({z for s in seen.values() for z in s})
    if len(allz) > 1:
        bad.append(f'the show has {len(allz)} resting scales across its registers: {allz} '
                   '(the body text changes size from song to song)')
    return bad
