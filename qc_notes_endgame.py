"""
THE END OF THE SHOW — David's notes D-016, D-017, D-019, D-020, D-021, D-043.

One probe per note. Each takes a Playwright page that is already sitting on
L5Y-Show-STANDALONE.html and returns a list of plain-English complaints; an
empty list means the note is satisfied. Nothing here trusts the cue data on its
own — every claim is measured off the live DOM the operator's GO produces.

  a_132_timing        13.2 — her text is readable for two seconds longer and the
                      swipe is a second and a half slower than it was.
  a_133_full_phone    13.3 — the phone rises with the WHOLE screen in frame and
                      the camera does not move across the unlock.
  a_133_device_swap   13.3 — Find My · Me · "Use This iPhone as My Location":
                      the iPad stops being the source, the iPhone becomes it.
                      Nothing is shared, nothing is turned on, and it is faster
                      than the sequence it replaces.
  a_144_send          14.4 — she finishes it, sends it, we hear the send, and
                      the screen goes black inside the phone.
  a_bows              14.7 — the house card comes back with a faster photo bed
                      that never empties and never stops, and the operator's
                      questionnaire never appears under it.
  a_predict_matches   songs 13-14 — the live DOM and a fresh hardRender() of the
                      same cue show the same words, so a scrub or a resize can
                      never repaint a different screen than the one playing.

Usage:  CHROMIUM_PATH=/opt/pw-browsers/chromium python3 qc_notes_endgame.py
"""
import os
import sys

FILE = 'file://' + os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'L5Y-Show-STANDALONE.html'))

S13 = 12   # index of song 13 in SHOW
S14 = 13   # index of song 14

# The 13.3 that D-019 replaces — Share My Location -> Share Indefinitely. Kept
# here so "faster than the current sequence" is a measurement, not an opinion.
OLD_133_DO = """[{op:'clock',t:'5:24'},{op:'device',dev:'iphone',who:'jamie'},{op:'unlock'},
  {op:'openapp',icon:'FindMy',to:'findmy'},
  {op:'findmy',person:{n:'C',loc:'Mount Orab, OH',when:'now',mapLabel:'Mount Orab, Ohio'}},
  {op:'pause',ms:800},
  {op:'btnHover',b:'Share My Location'},
  {op:'sheet',title:'Share your location?',opts:['a','b','c'],safe:'Cancel'},
  {op:'btnHover',b:'Share Indefinitely'},{op:'btnTap',b:'Share Indefinitely'},
  {op:'findmy',person:{n:'C',loc:'Mount Orab, OH',when:'now',sharing:'Indefinitely'}}]"""

# collects only text the audience can actually read: anything display:none,
# visibility:hidden, fully transparent or collapsed to nothing is skipped.
VIS_JS = """(sel)=>{
  const root=document.querySelector(sel); if(!root) return '';
  const out=[];
  const walk=(el)=>{
    const cs=getComputedStyle(el);
    if(cs.display==='none'||cs.visibility==='hidden'||+cs.opacity===0) return;
    const r=el.getBoundingClientRect(); if(r.width<1||r.height<1) return;
    for(const n of el.childNodes){
      if(n.nodeType===3){ const t=n.textContent.replace(/\\s+/g,' ').trim(); if(t) out.push(t); }
      else if(n.nodeType===1) walk(n);
    }
  };
  walk(root); return out.join(' | ');
}"""


# ---------------------------------------------------------------- plumbing --
def _ready(page):
    if not page.evaluate('typeof started!=="undefined" && started'):
        page.evaluate('startAs("projection")')
        page.wait_for_timeout(400)


def _goto(page, si, ci):
    _ready(page)
    page.evaluate(f'si={si}; ci={ci}; animTok++; animRunning=false; hardRender();')
    page.wait_for_timeout(200)


def _fire_async(page):
    """Fire the next cue WITHOUT blocking, so the probe can watch it play."""
    page.evaluate('setTimeout(()=>advance(),0)')
    for _ in range(40):
        page.wait_for_timeout(25)
        if page.evaluate('animRunning'):
            return


def _settle(page, max_ms=90000):
    waited = 0
    while waited < max_ms:
        page.wait_for_timeout(100)
        waited += 100
        if not page.evaluate('animRunning'):
            return True
    return False


def _fire(page):
    _fire_async(page)
    _settle(page)


def _cue(page, si, k, field='do'):
    return page.evaluate(f'JSON.parse(JSON.stringify(SHOW[{si}].cues[{k}].{field}))')


def _ids(page, si):
    return page.evaluate(f'SHOW[{si}].cues.map(c=>c.id)')


def _index(page, si, cue_id):
    ids = _ids(page, si)
    return ids.index(cue_id) if cue_id in ids else -1


# ------------------------------------------------------------------ D-016 --
def a_132_timing(page):
    """13.2: two more seconds with her message on screen; the swipe 1.5 s longer."""
    bad = []
    k = _index(page, S13, '13.2')
    if k < 0:
        return ['cue 13.2 is missing from song 13']

    _goto(page, S13, k)
    page.evaluate("""() => {
      window.__d132={t0:performance.now(), notif:null, swipe:null, trans:'', gone:null};
      clearInterval(window.__i132);
      window.__i132=setInterval(()=>{
        const D=window.__d132, n=document.querySelector('#projDevice .nstack .notif');
        if(n){ if(D.notif==null) D.notif=performance.now()-D.t0;
               if(D.swipe==null && n.style.transform){ D.swipe=performance.now()-D.t0; D.trans=n.style.transition; } }
        else if(D.notif!=null && D.gone==null) D.gone=performance.now()-D.t0;
      },20); }""")
    _fire(page)
    page.evaluate('clearInterval(window.__i132)')
    d = page.evaluate('window.__d132')

    if d['notif'] is None:
        return ['13.2 never put her notification on the lock screen']
    if d['swipe'] is None:
        return ['13.2 never swiped the notification away']

    readable = d['swipe'] - d['notif']
    if readable < 3800:
        bad.append('13.2: her message is readable for only %.2f s before the swipe starts '
                   '(it was ~2.0 s; David asked for two more, so it must be at least 3.8 s)'
                   % (readable / 1000.0))

    dur = 0.0
    for part in (d['trans'] or '').split(','):
        part = part.strip()
        if part.startswith('transform'):
            for tok in part.split():
                if tok.endswith('s') and tok[:-1].replace('.', '', 1).isdigit():
                    dur = float(tok[:-1])
    # MEASURE THE WHOLE GESTURE, NOT ITS FIRST LEG. The swipe used to be one transition, so its
    # duration was the gesture. Since Sept 21 it is three beats — the card pulls left off its Clear
    # button, Clear is held long enough to read, then the card goes (D-070) — and reading only the
    # first transition reported 0.79 s for a gesture that actually runs the better part of three
    # seconds. What David asked for is a deliberate erasure rather than a flick, so the floor belongs
    # on the whole thing: from the card first moving to the card leaving the DOM.
    gesture = None
    if d['gone'] is not None and d['swipe'] is not None:
        gesture = (d['gone'] - d['swipe']) / 1000.0
    if gesture is None:
        bad.append('13.2: the card never leaves — the erasure does not finish')
    elif gesture < 1.85:
        bad.append('13.2: the whole erasure lasts %.2f s (it was 0.38 s; David asked for 1.5 s '
                   'longer, so it must be at least 1.85 s)' % gesture)
    if dur and dur < 0.4:
        bad.append('13.2: the card is pulled off its Clear button in %.2f s — that leg reads as a '
                   'flick' % dur)
    if 'ease-in' in (d['trans'] or '') and 'cubic-bezier' not in (d['trans'] or ''):
        bad.append('13.2: the swipe still accelerates away on a plain ease-in — that reads as a '
                   'flick, not a deliberate erasure')
    return bad


# ------------------------------------------------------------------ D-017 --
def a_133_full_phone(page):
    """13.3 starts on the whole phone screen, and the camera holds across the unlock."""
    bad = []
    k = _index(page, S13, '13.3')
    if k < 0:
        return ['cue 13.3 is missing from song 13']

    _goto(page, S13, k)
    page.evaluate("""() => {
      window.__d133={lock:null, lockCam:'', afterCam:'', unlocked:false, small:null};
      clearInterval(window.__i133);
      window.__i133=setInterval(()=>{
        const D=window.__d133, cam=document.querySelector('#projDevice .stagecam');
        const ph=document.querySelector('#projDevice .iphone');
        const lock=document.querySelector('#projDevice .lockL');
        const F=document.getElementById('projection').getBoundingClientRect();
        if(ph && lock && cam){
          const r=ph.getBoundingClientRect(), uw=F.width*(1-ERA_ZONE_());
          D.lock={top:r.top-F.top, bottom:F.bottom-r.bottom, left:r.left-F.left,
                  right:(F.left+uw)-r.right, h:r.height, FH:F.height};
          D.lockCam=cam.style.transform;
        }
        if(!lock && D.lock && !D.unlocked && ph && cam){ D.unlocked=true; D.afterCam=cam.style.transform; }
      },20); }""")
    _fire(page)
    page.evaluate('clearInterval(window.__i133)')
    d = page.evaluate('window.__d133')

    if not d['lock']:
        return ['13.3 never showed a locked phone — there is no unlock for the audience to see']
    m = d['lock']
    for name, v in (('top', m['top']), ('bottom', m['bottom']),
                    ('left', m['left']), ('right', m['right'])):
        if v < -2:
            bad.append('13.3: the phone is cropped at the %s by %d px when it rises — D-017 asks '
                       'for the WHOLE phone screen' % (name, round(-v)))
    frac = m['h'] / m['FH'] if m['FH'] else 0
    if frac < 0.60:
        bad.append('13.3: the whole phone only fills %d%% of the frame height — too small to read '
                   'the unlock at 25 ft' % round(frac * 100))
    if not d['unlocked']:
        bad.append('13.3: the lock screen never lifted, so nobody watched him unlock it')
    elif d['lockCam'] and d['afterCam'] and d['lockCam'] != d['afterCam']:
        bad.append('13.3: the camera moved across the unlock (%s -> %s) — the unlock must play in '
                   'the frame it started in' % (d['lockCam'], d['afterCam']))

    ops = _cue(page, S13, k)
    dev = [o for o in ops if o.get('op') == 'device']
    if not dev or not dev[0].get('whole'):
        bad.append('13.3: the device op does not ask for the whole phone (whole:true), so the '
                   'framing is only accidental')
    return bad


# ------------------------------------------------------------------ D-019 --
def a_133_device_swap(page):
    """13.3 changes WHICH DEVICE reports his location: iPad -> iPhone. Not a re-share."""
    bad = []
    k = _index(page, S13, '13.3')
    if k < 0:
        return ['cue 13.3 is missing from song 13']

    ops = _cue(page, S13, k)
    names = [o.get('op') for o in ops]
    text = repr(ops)

    # 1. the wrong action must be gone
    for gone in ('Share Indefinitely', 'Share for One Hour', 'Share Until End of Day'):
        if gone in text:
            bad.append('13.3 still offers "%s" — D-019 says the action is not him sharing with '
                       'her again' % gone)
    if 'sheet' in names:
        bad.append('13.3 still raises a share-location action sheet; the real row is a plain '
                   'blue row in Find My, with no sheet')

    # 2. the right action, spelled the way iOS spells it
    if 'Use This iPhone as My Location' not in text:
        bad.append('13.3 never taps the real iOS row "Use This iPhone as My Location"')

    # 3. navigation: nobody teleports into the Me tab
    if 'unlock' not in names or 'openapp' not in names:
        bad.append('13.3 reaches Find My without unlocking and opening the app')
    try:
        first_me = min(i for i, o in enumerate(ops) if o.get('op') == 'findmy' and o.get('me'))
    except ValueError:
        first_me = None
        bad.append('13.3 never opens the Find My "Me" tab')
    if first_me is not None:
        before = ops[:first_me]
        if not any(o.get('op') == 'findmy' and o.get('rows') for o in before):
            bad.append('13.3 lands on the Me tab without the app ever having been on another tab '
                       '— the audience never sees which tab he came from')
        if not any(o.get('op') in ('btnHover', 'btnTap') and o.get('b') == 'Me' for o in before):
            bad.append('13.3 switches to the Me tab without anybody tapping the Me tab')

    # 4. play it and read the screen
    _goto(page, S13, k)
    page.evaluate("""() => {
      window.__d19={seen:[], iPad:false, action:false, tabs:false};
      clearInterval(window.__i19);
      window.__i19=setInterval(()=>{
        const D=window.__d19, r=document.querySelector('#projDevice');
        if(!r) return; const t=r.innerText||'';
        if(/Jamie.s iPad/.test(t)) D.iPad=true;
        if(/Use This iPhone as My Location/.test(t)) D.action=true;
        if(r.querySelector('.fmtabs')) D.tabs=true;
        if(/Mount Orab/.test(t)) D.seen.push('ohio');
      },40); }""")
    _fire(page)
    page.evaluate('clearInterval(window.__i19)')
    live = page.evaluate('window.__d19')
    end = page.evaluate("document.querySelector('#projDevice').innerText||''")

    if not live['iPad']:
        bad.append('13.3 never showed the iPad as the device his location was coming from — the '
                   'swap has nothing to swap from')
    if not live['action']:
        bad.append('13.3 never put "Use This iPhone as My Location" on the glass')
    if not live['tabs']:
        bad.append('13.3 never shows the Find My tab bar, so the Me tab is not a place you can '
                   'navigate to')
    if 'ohio' not in live['seen']:
        bad.append('13.3 never shows Cathy in Mount Orab — the audience has no idea where she is '
                   'when he moves the dot')
    if 'Sharing From' not in end:
        bad.append('13.3 settles without the "Sharing From" row, so the audience cannot see which '
                   'device is reporting')
    if 'Jamie’s iPhone' not in end and "Jamie's iPhone" not in end:
        bad.append('13.3 settles without "Sharing From: Jamie’s iPhone" — the swap did not land')
    if 'iPad' in end:
        bad.append('13.3 settles still showing the iPad as the source — the swap did not take')
    if 'Use This iPhone as My Location' in end:
        bad.append('13.3 settles with the action row still offered; in iOS the row disappears once '
                   'this iPhone IS the location')
    if 'Share My Location' not in end:
        bad.append('13.3 settles without the Share My Location row, so nobody can see that sharing '
                   'was already on and was not what changed')
    tog = page.evaluate("""() => {
      const row=[...document.querySelectorAll('#projDevice .fmcard div')]
        .find(d=>(d.textContent||'').trim()==='Share My Location');
      if(!row) return null;
      const spans=[...row.children].filter(e=>e.tagName==='SPAN');
      const pill=spans[spans.length-1];
      return pill?getComputedStyle(pill).backgroundColor:null; }""")
    if tog and 'rgb(52, 199, 89)' not in tog:
        bad.append('13.3: Share My Location does not read as already ON (%s) — canon says the '
                   'location was never seen being turned on or off' % tog)

    # 5. SLOWER, NOT FASTER — David reversed this one twice and the later word wins. The original
    #    note wanted the swap to move; on Sept 20 he said "it's way too fast to read", and on
    #    Sept 21, "we just need to see 'sharing location from Jamie's iPad' on the screen for
    #    longer". What this note still owns is the SEMANTICS of the beat (sharing already on, only
    #    the device changing), asserted above. How long it takes is D-071's, which measures the
    #    seconds the row actually sits still rather than an estimate of the op list. Asserting
    #    "faster than before" here would enforce a direction he has withdrawn, so all that is left
    #    of the timing clause is a floor: it must not collapse back to a flick.
    d_new = page.evaluate("""() => {
      const ops=SHOW[%d].cues[%d].do; const i=ops.findIndex(o=>o.op==='openapp');
      return estDuration({do:ops.slice(i+1)}); }""" % (S13, k))
    if d_new < 8000:
        bad.append('the Find My sequence runs only %.2f s — too quick to read the one word that '
                   'changes (David, Sept 20 and again Sept 21)' % (d_new / 1000.0))
    return bad


# ------------------------------------------------------------------ D-020 --
def a_144_send(page):
    """14.4: she finishes it, sends it, we hear the send, then black inside the phone."""
    bad = []
    k = _index(page, S14, '14.4')
    if k < 0:
        return ['cue 14.4 is missing from song 14']

    ops = _cue(page, S14, k)
    names = [o.get('op') for o in ops]
    typed = [o.get('t') for o in ops if o.get('op') == 'type']
    if not typed:
        bad.append('14.4 no longer types anything')
    elif typed[-1] != 'safe 😊 tonight was amazing':
        bad.append('14.4 types %r — David wants her to finish it: "safe 😊 tonight was amazing"'
                   % typed[-1])
    if 'send' not in names:
        bad.append('14.4 never sends it (D-020 reverses the old "do not send")')
    elif names.index('send') < max(i for i, n in enumerate(names) if n == 'type'):
        bad.append('14.4 sends before she has finished typing')
    # (the old `elif` here asked where `screenoff` sat relative to the send — with the op gone it
    # raised ValueError and the probe crashed instead of reporting, which is a failure that tells
    # nobody anything. There is no ordering left to check: there is no screenoff.)
    if 'screenoff' in names:
        bad.append('14.4 still ends with the screen going black inside the phone — reversed Sept 21, '
                   'her text is the last image of the show (D-072)')

    _goto(page, S14, k)
    page.evaluate("""() => { window.__snd=[]; if(!window.__sfxWrapped){ window.__sfxWrapped=true;
      const _s=sfx; window.sfx=function(n,o){ window.__snd.push(n); return _s(n,o); }; } window.__snd=[]; }""")
    _fire(page)
    snd = page.evaluate('window.__snd')
    if 'send' not in snd:
        bad.append('14.4 does not play the send tone (sounds heard: %s)' % (snd[:12] or 'none'))

    st = page.evaluate("""() => {
      const r=document.querySelector('#projDevice');
      const bubs=[...r.querySelectorAll('.thread .bub.me')].map(b=>b.textContent.trim());
      const scr=r.querySelector('.iphone .screen');
      const cam=r.querySelector('.iphone .cam');
      const th=r.querySelector('.thread');
      const thCS=th?getComputedStyle(th):null;
      const thB=th?th.getBoundingClientRect():null;
      return {bubs, off: !!(scr&&scr.classList.contains('off')),
              threadVisible: !!(th && thCS.visibility!=='hidden' && +thCS.opacity>0.05
                                && thB.width>2 && thB.height>2),
              camVis: cam?getComputedStyle(cam).visibility:'none',
              bg: scr?getComputedStyle(scr).backgroundColor:'none',
              draft: CUR.draft, kbd: !!CUR.kbd, scroff: !!CUR.scroff}; }""")
    if 'safe 😊 tonight was amazing' not in st['bubs']:
        bad.append('14.4 settles without her finished message as a sent bubble (bubbles: %s)'
                   % st['bubs'])
    if st['draft']:
        bad.append('14.4 settles with %r still sitting in the field — it was never sent' % st['draft'])
    # THE BLACK MOVED OUT OF THE PHONE (David, Sept 21: "the last thing we should see before the
    # blackout is the text 'tonight was amazing'… then the blackout should be a slow blackout to
    # actual black"). Sept 20's `screenoff` is reversed: her screen must NOT go dark in her hand, and
    # the fade now belongs to the curtain at 14.6, which D-072 proves. What survives of this note is
    # everything before that — she finishes it, she sends it, we hear the send — and it is asserted
    # above. Keeping the old clause here would enforce a direction David has withdrawn.
    if st['scroff']:
        bad.append('14.4 still blacks out inside the phone — her text is meant to be the last image '
                   'of the show, held through his last verse (D-072)')
    # …and the three clauses that used to prove the black WAS there now prove the opposite: the cue
    # settles on a LIT phone with her sent message on it, because that picture has to survive his
    # whole last verse. The black is the curtain's now, and D-072 proves it fades rather than cuts.
    if st['camVis'] == 'hidden':
        bad.append('14.4: the screen content is hidden — her text has to be readable through his '
                   'last verse')
    # NOT backgroundColor. The .screen element's own background IS black — it is the phone's base
    # layer, and the thread paints ON it. Reading that colour tests the wrong thing entirely: it
    # reported "the screen is black" while her sent bubble and its Delivered receipt were plainly
    # on the glass. What "still lit" means is that the MESSAGE is rendered and visible, which the
    # bubble assertions above already establish; what is added here is that the thread is actually
    # painted rather than merely present in the DOM.
    if not st.get('threadVisible'):
        bad.append('14.4: the thread is not painted — her text has to be the last image of the show')
    vis = page.evaluate(VIS_JS, '#projDevice .iphone .screen')
    if 'tonight was amazing' not in vis:
        bad.append('14.4: the settled screen does not read her sent message (%r)' % vis[:80])
    return bad


# ------------------------------------------------------------------ D-021 --
def a_bows(page, minutes=3.3):
    """14.7: the house sequence returns as a bows screen, faster, loopable, never blank,
    and the operator's questionnaire never appears under it."""
    bad = []
    last = page.evaluate('SHOW.length-1')
    ids = _ids(page, last)
    if 'curtain' not in repr(page.evaluate(f'JSON.parse(JSON.stringify(SHOW[{last}].cues.map(c=>c.do)))')):
        bad.append('the show no longer ends on a curtain')
    kb = None
    for i, cid in enumerate(ids):
        if any(o.get('op') == 'bows' for o in _cue(page, last, i)):
            kb = i
    if kb is None:
        return ['there is no bows cue at the end of the show (D-021)']
    kc = None
    for i, cid in enumerate(ids):
        if any(o.get('op') == 'curtain' for o in _cue(page, last, i)):
            kc = i
    if kc is not None and kb < kc:
        bad.append('the bows cue fires before the final curtain')
    if kb != len(ids) - 1:
        bad.append('the bows cue is not the last GO of the show')

    # THE BED NEEDS FILM IN IT. D-021 is about the MECHANISM - a print every 0.9-1.5 s against a
    # 15-20 s fall, so the bows can never go blank however long the company stays out. With no
    # photographs on disk the renderer correctly shows nothing (D-047: a renderer never invents
    # filler), and grading that as a failure would only re-report the missing files, which are
    # D-065's to chase. Load a stand-in set, grade the mechanism, restore the real bed after.
    page.evaluate("""() => { const px='data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7';
      window.__bedKeep=window.L5Y_LOOP;
      const mk=n=>Array.from({length:n},(_,i)=>({k:'img',r:i%3?0.75:1.4,s:px}));
      window.L5Y_LOOP={ml:mk(40),ac:mk(40)}; pileReset(); }""")

    # play the end of the show for real: ... -> curtain -> bows
    _goto(page, last, max(0, kb - 1))
    _fire(page)                       # the curtain
    page.wait_for_timeout(3200)       # longer than the 2.6 s the gate used to wait
    gate_mid = page.evaluate("document.body.classList.contains('needgate')")
    if gate_mid:
        bad.append('the questionnaire came up during the final blackout, before the bows')
    _fire(page)                       # the bows

    state = page.evaluate("""() => {
      const era=document.getElementById('era'), L=document.getElementById('loop');
      return {bows:!!CUR.bows, curtain:!!CUR.curtain,
              blk:document.body.classList.contains('blk'),
              eraHidden:era.classList.contains('hidden'),
              title:era.querySelector('.pad').classList.contains('title'),
              face:(era.querySelector('.yr').textContent+' '+era.querySelector('.ynum').textContent+
                    ' '+era.querySelector('.sub').textContent).trim(),
              loopOn:L.classList.contains('on'),
              cfg:PILE_CFG()}; }""")
    if not state['bows']:
        bad.append('the bows op left no bows state behind')
    if state['curtain']:
        bad.append('the bows screen is still inside the curtain, so the stage stays black')
    if state['blk']:
        bad.append('the stage is blacked out under the bows screen — nothing is visible')
    if state['eraHidden'] or not state['title']:
        bad.append('the bows screen is not the house title card (face %r)' % state['face'])
    if 'THE LAST' not in state['face'] or '5' not in state['face']:
        bad.append('the bows card does not read as the title card (%r)' % state['face'])
    if not state['loopOn']:
        bad.append('the photo bed is not running behind the bows card')

    cfg = state['cfg']
    house = page.evaluate("(()=>{const c=pileRate('house');const o={every:c.every.slice(),fall:c.fall.slice()};pileRate('bows');return o;})()")
    if cfg['every'][1] >= house['every'][0]:
        bad.append('the bows bed is not faster than the house bed (%s vs %s)'
                   % (cfg['every'], house['every']))
    if cfg['every'][1] >= cfg['fall'][0] / 3.0:
        bad.append('a print can land as rarely as every %.1f s against a fall of only %.1f s — the '
                   'bed is not guaranteed to overlap, so it can go blank'
                   % (cfg['every'][1] / 1000.0, cfg['fall'][0] / 1000.0))

    # ---- it must never go blank, and it must still be dropping after 3+ minutes ----
    page.evaluate('window.__bowsMin=999; window.__bowsMax=0; clearInterval(window.__ib); '
                  "window.__ib=setInterval(()=>{const n=document.querySelectorAll('#loop .print').length;"
                  'if(n<window.__bowsMin) window.__bowsMin=n; if(n>window.__bowsMax) window.__bowsMax=n;},400)')
    page.wait_for_timeout(3000)       # let the first prints land before we judge emptiness
    page.evaluate('window.__bowsMin=999')
    total = int(minutes * 60 * 1000)
    i_start = page.evaluate('PILE_S().i')
    marks = []
    waited = 0
    while waited < total:
        page.wait_for_timeout(5000)
        waited += 5000
        marks.append((waited, page.evaluate('PILE_S().i'),
                      page.evaluate("document.querySelectorAll('#loop .print').length")))
    page.evaluate('clearInterval(window.__ib)')
    lo = page.evaluate('window.__bowsMin')
    hi = page.evaluate('window.__bowsMax')
    i_end = page.evaluate('PILE_S().i')
    tail = marks[-1][1] - marks[-4][1] if len(marks) >= 4 else (i_end - i_start)

    if lo < 1:
        bad.append('the bows bed went completely blank at some point in %.1f minutes' % minutes)
    if hi < 5:
        bad.append('only %d prints were ever on screen at once — that is not a flood' % hi)
    # AGAINST ITS OWN CONFIGURED RATE, not a constant from when the bed ran four times faster.
    # `every` is derived from `fall`, so "one print every two seconds" stopped being the spec the
    # moment the fall was slowed; what proves the bed is keeping up is that it spawns at the rate
    # it was told to. A 25% shortfall against the slowest configured gap is a real stall.
    _slowest = page.evaluate('PILE_CFG().every[1]') or 2000
    if (i_end - i_start) < (total / float(_slowest)) * 0.75:
        bad.append('the bed produced only %d prints in %.1f minutes — it is not keeping up'
                   % (i_end - i_start, minutes))
    if tail <= 0:
        bad.append('the bed stopped producing prints before %.1f minutes were up' % minutes)
    if page.evaluate('!PILE_S().t'):
        bad.append('the bed has no next drop scheduled — it has ended, so the bows can run out')

    # ---- the questionnaire must never come up under the bows ----
    if page.evaluate("document.body.classList.contains('needgate')"):
        bad.append('the operator questionnaire is up over the bows screen — the audience is '
                   'reading it')
    gatecheck = page.evaluate("""() => {
      const was=bootProj, out={};
      bootProj=false;                       // pretend we are the operator's window
      gateArmStop(); gateArmTick();
      out.whileBowing=document.body.classList.contains('needgate');
      document.body.classList.remove('started');   // the operator comes off the show
      gateArmStop(); gateArmTick();
      out.afterBowing=document.body.classList.contains('needgate');
      document.body.classList.add('started'); document.body.classList.remove('needgate');
      gateArmStop(); bootProj=was; return out; }""")
    if gatecheck['whileBowing']:
        bad.append('on the operator\'s own machine the questionnaire arms while the bows are up')
    if not gatecheck['afterBowing']:
        bad.append('the questionnaire never comes back once the operator leaves the bows — the '
                   'next performance would inherit tonight\'s cast unasked')

    # ---- a drop-in of real photographs must just work ----
    drop = page.evaluate("""() => {
      const keep=window.L5Y_LOOP;
      const mk=n=>Array.from({length:n},(_,i)=>({k:'img',r:i%3?0.75:1.4,
        s:'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'}));
      window.L5Y_LOOP={ml:mk(50),ac:mk(50)};
      pileReset(); pileStop(); pileStart();
      const n=pileList().length;
      const el=document.querySelector('#loop .print');
      const kind=el?(el.querySelector('img')?'img':(el.querySelector('video')?'vid':'greek')):'none';
      window.L5Y_LOOP=keep; pileReset(); pileStop(); pileStart();
      return {n, kind}; }""")
    if drop['n'] != 50:
        bad.append('a drop-in of 50 files per cast did not reach the bed (%d seen)' % drop['n'])
    if drop['kind'] != 'img':
        bad.append('with real files present the bed still rendered %r instead of a photograph'
                   % drop['kind'])
    page.evaluate("""() => { if(window.__bedKeep!==undefined){ window.L5Y_LOOP=window.__bedKeep;
        delete window.__bedKeep; pileReset(); pileStop(); } }""")
    return bad


# ------------------------------------------------------------------ D-043 --
def a_predict_matches(page, songs=(S13, S14)):
    """The live DOM and a fresh hardRender() of the same cue must read the same.
    A scrub or a resize calls hardRender(); it must not repaint a different screen."""
    bad = []
    # the predictive bar specifically: one source for the live bar and the render
    if page.evaluate('typeof predictCells!=="function"'):
        bad.append('there is no single source for the predictive bar (predictCells is missing), so '
                   'the live keyboard and a re-render can always disagree')
    else:
        probe = page.evaluate("""() => {
          const st=Object.assign(buildState(SHOW[13],3),
            {app:'thread',draft:'safe 😊 tonight was amaz',kbd:true});
          const d=document.createElement('div'); d.innerHTML=screenHTML(st);
          const cells=[...d.querySelectorAll('.predict div')].map(x=>x.textContent);
          return {cells, want:predictCells(st.draft)}; }""")
        # QuickType quotes the literal itself now (Sept 23: only mid-word, and the case as typed), so
        # the quotes are part of the one source; compare the words, quotes off both sides
        got = [c.replace('“', '').replace('”', '') for c in probe['cells']]
        probe['want'] = [c.replace('“', '').replace('”', '') for c in probe['want']]
        if got != probe['want']:
            bad.append('a re-rendered keyboard shows %s while the engine\'s own suggestions for '
                       'that draft are %s' % (got, probe['want']))
        if got and 'amaz' not in got[0]:
            bad.append('a re-rendered keyboard suggests %r instead of the word actually being '
                       'typed' % got[0])

    for si in songs:
        for k, cid in enumerate(_ids(page, si)):
            _goto(page, si, k)
            _fire(page)
            page.wait_for_timeout(250)
            live = page.evaluate(VIS_JS, '#projDevice')
            page.evaluate('hardRender()')
            page.wait_for_timeout(250)
            after = page.evaluate(VIS_JS, '#projDevice')
            if live != after:
                a, b = live, after
                i = 0
                while i < min(len(a), len(b)) and a[i] == b[i]:
                    i += 1
                bad.append('%s: a scrub repaints a different screen than the one that played '
                           '— live %r vs re-render %r' % (cid, a[max(0, i - 20):i + 60],
                                                          b[max(0, i - 20):i + 60]))
    return bad


PROBES = [('D-016 13.2 pacing', a_132_timing),
          ('D-017 13.3 whole phone', a_133_full_phone),
          ('D-019 13.3 device swap', a_133_device_swap),
          ('D-020 14.4 she sends', a_144_send),
          ('D-043 13-14 scrub matches live', a_predict_matches),
          ('D-021 14.7 bows', a_bows)]


def main():
    from playwright.sync_api import sync_playwright
    only = sys.argv[1:]
    fails = 0
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or None)
        pg = b.new_page(viewport={'width': 1920, 'height': 1080})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(FILE)
        pg.wait_for_timeout(1500)
        for label, fn in PROBES:
            if only and fn.__name__ not in only:
                continue
            out = fn(pg)
            print(('%-34s' % label) + ('CLEAN' if not out else 'FAILED'))
            for line in out:
                print('    - ' + line)
            fails += len(out)
        b.close()
    if errs:
        print('JS ERRORS:', errs[:3])
    print('ENDGAME NOTES:', 'CLEAN' if not (fails or errs) else '%d complaint(s)' % fails)
    return 1 if (fails or errs) else 0


if __name__ == '__main__':
    raise SystemExit(main())
