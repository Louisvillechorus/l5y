"""PROBES for the notes the main session fixed. Each a_* takes a Playwright page already
at the built STANDALONE (700 ms elapsed) and returns a list of plain-English complaints.
Empty list = the note is satisfied, measured, on the live path."""

FILE_Q = '?view=projection'


# ---------- helpers ----------
def boot(pg, view='projection'):
    pg.evaluate(f'startAs("{view}")')
    pg.wait_for_timeout(300)


def song_ix(pg, n):
    return pg.evaluate(f'SHOW.findIndex(s=>s.n==={n})')


def goto(pg, n, c=0):
    i = song_ix(pg, n)
    pg.evaluate(f'si={i}; ci={c}; animTok++; animRunning=false; hardRender();')
    pg.wait_for_timeout(180)


def fire(pg, budget_ms=30000, settle=True):
    """Fire a cue the way the operator does, and — unless told otherwise — WAIT FOR THE CAMERA.

    animRunning going false only means the cue's own animation finished. The camera's glide is a
    further 1.4 s CSS transition, so a probe that measures a rect the instant the cue ends reads a
    subject that is still travelling and reports a chop that the audience never sees. This cost a
    false regression on D-032; every geometry probe now settles by default.
    """
    pg.evaluate('advance()')
    waited = 0
    while waited < budget_ms:
        pg.wait_for_timeout(150)
        waited += 150
        if not pg.evaluate('animRunning'):
            break
    if settle:
        pg.wait_for_timeout(1800)
        waited += 1800
    return waited


def tap_sfx(pg):
    """record every sound the engine actually plays, with a timestamp"""
    pg.evaluate("""(()=>{ if(window.__sfxlog) return; window.__sfxlog=[];
      const t0=performance.now(); const real=window.sfx;
      window.sfx=function(n,o){ window.__sfxlog.push([n, Math.round(performance.now()-t0)]); return real.apply(this,arguments); }; })()""")


def sfx_log(pg):
    return pg.evaluate('window.__sfxlog||[]')


def cue_ops(pg, n, cid):
    return pg.evaluate(
        f'(SHOW.find(s=>s.n==={n}).cues.find(q=>q.id==="{cid}")||{{}}).do||[]')


# ---------- D-015 · the low-battery chime is cut ----------
def a_no_lowbat(pg):
    bad = []
    if pg.evaluate("'lowbat' in SFX_KEEP_()"):
        bad.append('lowbat is still in SFX_KEEP_')
    if pg.evaluate("Object.keys(SFX_MAP_()).some(k=>k==='lowbat')"):
        bad.append('lowbat is still mapped to a sample')
    if pg.evaluate("document.documentElement.innerHTML.includes('low_power')"):
        bad.append('the low_power sample is still embedded')
    tap_sfx(pg)
    boot(pg)
    # drive every cue that sets a battery level and prove nothing chimes
    pg.evaluate("""(()=>{ for(const s of SHOW) for(const q of s.cues)
        for(const o of (q.do||[])) if(o.op==='batt'){ const st=buildState(s,0); applyOp(st,o); } })()""")
    if any(n == 'lowbat' for n, _ in sfx_log(pg)):
        bad.append('a battery op still played the chime')
    return bad


# ---------- D-018 · the unlock is audible, everywhere ----------
def a_unlock_audible(pg):
    bad = []
    if not pg.evaluate("SFX_KEEP_().unlock"):
        bad.append('unlock is not in SFX_KEEP_ — it would be silenced')
    boot(pg)
    where = pg.evaluate("""(()=>{ const out=[]; SHOW.forEach((s,i)=>s.cues.forEach((q,k)=>{
        if((q.do||[]).some(o=>o.op==='unlock')) out.push([i,k,s.n,q.id]); })); return out; })()""")
    if not where:
        return bad + ['no cue unlocks a phone at all']
    for i, k, n, cid in where[:4]:
        pg.evaluate(f'si={i}; ci={k}; animTok++; animRunning=false; hardRender();')
        pg.wait_for_timeout(150)
        pg.evaluate('window.__sfxlog=null')
        tap_sfx(pg)
        fire(pg)
        if not any(x == 'unlock' for x, _ in sfx_log(pg)):
            bad.append(f'cue {cid} unlocks the phone in silence')
    return bad


# ---------- D-023 · the song + cue selector, and no dead end ----------
def a_jump_panel(pg):
    bad = []
    boot(pg, 'presenter')
    for _ in range(3):
        fire(pg)
    pg.click('#btnMenu')
    pg.wait_for_timeout(250)
    if not pg.is_visible('#jump'):
        return ['the Menu button does not open the selector']
    if pg.evaluate("document.querySelectorAll('#jSongs .jsong').length") < 14:
        bad.append('the running order is incomplete in the selector')
    if not pg.evaluate("document.querySelector('#jCues .jcue.live')"):
        bad.append('the live cue is not marked NOW')
    before = pg.evaluate('[si,ci]')
    pg.keyboard.press('Space')
    pg.wait_for_timeout(250)
    if pg.evaluate('[si,ci]') != before:
        bad.append('SPACE fires a cue behind the open selector')
    pg.keyboard.press('ArrowDown')
    pg.wait_for_timeout(120)
    pg.keyboard.press('Enter')
    pg.wait_for_timeout(400)
    if pg.evaluate('ci') != before[1] + 1:
        bad.append('Enter did not land on the highlighted cue')
    if pg.evaluate("document.body.classList.contains('jumping')"):
        bad.append('the selector stayed open after a jump')
    pg.keyboard.press('Escape')
    pg.wait_for_timeout(200)
    pg.keyboard.press('Escape')
    pg.wait_for_timeout(200)
    if not pg.evaluate('started'):
        bad.append('Esc un-started the show — the dead end is back')
    if pg.is_visible('#menu'):
        bad.append('the old dead-end menu is reachable')
    b4 = pg.evaluate('ci')
    pg.keyboard.press('Space')
    pg.wait_for_timeout(600)
    if pg.evaluate('ci') <= b4:
        bad.append('GO did not resume after closing the selector')
    p2 = pg.context.new_page()
    p2.goto(pg.url.split('?')[0] + FILE_Q)
    p2.wait_for_timeout(600)
    p2.evaluate("document.body.classList.add('jumping')")
    p2.wait_for_timeout(150)
    if p2.is_visible('#jump'):
        bad.append('THE AUDIENCE CAN SEE THE SELECTOR on the projection window')
    p2.close()
    return bad


# ---------- D-024 · the audience never sees the questionnaire ----------
def a_gate_black(pg):
    import io
    bad = []
    if not pg.is_visible('#gate'):
        bad.append('the first window does not ask the questions')
    def luma(shot):
        from PIL import Image
        return max(Image.open(io.BytesIO(shot)).convert('L').resize((60, 34)).getdata())
    # W2: a second window opened exactly the same way must stand down, black, no gate
    w2 = pg.context.new_page()
    w2.goto(pg.url)
    w2.wait_for_timeout(1600)
    if w2.is_visible('#gate'):
        bad.append('THE AUDIENCE SEES THE QUESTIONNAIRE — the second window asked it too')
    pk = luma(w2.screenshot())
    if pk > 26:
        bad.append(f'the second window is not black while the gate is up (peak luma {pk})')
    # the owner answers and starts; the projector must WAKE, not stay black all night
    pg.evaluate("gateSel('cast','ml')")
    pg.wait_for_timeout(150)
    pg.evaluate("gateSel('perf','Gayle King')")
    pg.wait_for_timeout(150)
    pg.evaluate('gateYes(1)')
    pg.wait_for_timeout(150)
    pg.evaluate('gateYes(2)')
    pg.wait_for_timeout(250)
    pg.evaluate("startAs('presenter')")
    pg.wait_for_timeout(1200)
    if w2.evaluate("document.body.classList.contains('gatewait')"):
        bad.append('the projector never woke when the show started')
    if luma(w2.screenshot()) < 30:
        bad.append('the projector stayed black after the show started')
    # W3: a window opened MID-SHOW must join as a projector, never ask
    w3 = pg.context.new_page()
    w3.goto(pg.url)
    w3.wait_for_timeout(1600)
    if w3.is_visible('#gate'):
        bad.append('a window opened MID-SHOW asked the questions')
    # …and the cues still reach the projector
    pg.evaluate('next()')
    pg.wait_for_timeout(6000)
    if pg.evaluate('[si,ci]') != w2.evaluate('[si,ci]'):
        bad.append(f'the windows are out of sync: {pg.evaluate("[si,ci]")} vs {w2.evaluate("[si,ci]")}')
    w3.close()
    w2.close()
    return bad


# ---------- D-025 · the performer name spans the sheet, line by line ----------
def a_perf_fill(pg):
    bad = []
    boot(pg)
    pg.evaluate("""PERF='Gayle King'; (()=>{ const st=buildState(SHOW[0],0); st.perfcard=true; st.housecard=false;
        setStamp(st); })()""")
    pg.wait_for_timeout(400)
    m = pg.evaluate("""(()=>{ const sh=document.querySelector('#era .pad .sheet.top'); if(!sh) return null;
        const cs=getComputedStyle(sh), inner=sh.clientWidth-parseFloat(cs.paddingLeft)-parseFloat(cs.paddingRight);
        // measure the TYPE, not the box: .fl is display:block, so its rect always spans the sheet
        // whatever size the letters are. A Range around the text gives the ink's real width.
        // …and measure it in the SAME SPACE as the box: clientWidth is layout, a Range rect is screen,
        // and the house cards carry a declared scale (--hsc), so the ink is divided back out of it.
        const K=parseFloat(getComputedStyle(sh.closest('.pad')||sh).getPropertyValue('--hsc'))||1;
        const fl=[...sh.querySelectorAll('.fl')].map(e=>{
          const r=document.createRange(); r.selectNodeContents(e);
          return r.getBoundingClientRect().width/K; });
        const grp=sh.querySelector('.grp');
        const vbound = !!(grp && grp.scrollHeight > grp.clientHeight - 2);
        return {inner, fl, vbound}; })()""")
    if not m or not m['fl']:
        return ['the performer card renders no fill-lines']
    if len(m['fl']) < 2:
        bad.append('the name is not set one word per line')
    # THE REAL RULE: fill the width unless HEIGHT binds first. Once the house sheets were widened
    # for D-012, two full-width lines overflow the sheet vertically, so the stack is scaled down to
    # fit — that guard is correct and the names must not be asked to overflow the card. What must
    # always hold is that the lines match each other and use whatever width is available to them.
    floor = 0.93 if not m['vbound'] else 0.84
    for w in m['fl']:
        if w < m['inner'] * floor:
            bad.append(f'a name line is {w:.0f}px in a {m["inner"]:.0f}px sheet — it does not span'
                       + (' (height-bound)' if m['vbound'] else ''))
    if max(m['fl']) - min(m['fl']) > m['inner'] * 0.02:
        bad.append('the name lines are not the same width — the brand sets them to one measure')
    return bad


# ---------- D-030 · the time warp tapers, and runs backwards when time does ----------
def a_warp(pg):
    bad = []
    if not pg.evaluate("!!(window.L5Y_SFX||{})['reverse_timewarp.mp3']"):
        bad.append('the reverse time-warp clip is not embedded')
    if not pg.evaluate("!!(window.L5Y_SFX||{})['timewarp.mp3']"):
        bad.append('the forward time-warp clip is not embedded')
    if not pg.evaluate("typeof warpVerb==='function'"):
        bad.append('there is no reverb on the warp')
    src = pg.evaluate('warpStart.toString()')
    if 'reverse_timewarp' not in src:
        bad.append('warpStart never reaches for the reverse clip')
    if 'tail' not in src:
        bad.append('warpStart has no taper — the end is abrupt')
    if 'dir<0' not in pg.evaluate('eraRoll.toString()'):
        bad.append('a backward roll does not ask for the reverse clip')
    boot(pg)
    # a real backward roll: song 14 rolls JUNE YEAR 5 back to SEPTEMBER YEAR 1
    goto(pg, 14, 0)
    pg.evaluate("window.__warp=[]; (()=>{ const r=window.warpStart; window.warpStart=function(d,b){ window.__warp.push([d,!!b]); return r.apply(this,arguments); }; })()")
    fire(pg)
    w = pg.evaluate('window.__warp||[]')
    if not w:
        bad.append('the finale roll played no time-warp music')
    elif not any(b for _, b in w):
        bad.append('the backward roll played the forward clip')
    elif any(abs(d - 6000) > 1 for d, _ in w):
        bad.append(f'a roll is not 6 s: {w}')
    return bad


# ---------- D-031 · no divider when there is no event ----------
def a_foot_solo(pg):
    bad = []
    boot(pg)
    goto(pg, 13, 1)          # off cue 0, or isPreshow() forces the title face and blanks the foot
    r = pg.evaluate("""(()=>{ const s13=SHOW.find(x=>x.n===13); const st=buildState(s13,1);
        st.black=true; st.dev=null; st.housecard=false; st.perfcard=false; st.inter=false; st.next5=false;
        const read=()=>{ const fr=document.querySelector('#era .pad .sheet.top .frow');
          if(!fr) return null; const p=fr.querySelector('.pipe');
          return {solo:fr.classList.contains('solo'),
                  pipe: p ? getComputedStyle(p).display!=='none' : false,
                  foot:(fr.querySelector('.foot')||{}).textContent||''}; };
        st.foot='the engagement'; setStamp(st); const withE=read();
        st.foot='';               setStamp(st); const without=read();
        return {withE, without}; })()""")
    if not r or not r['withE'] or not r['without']:
        return ['the calendar renders no foot row at all']
    if r['without']['pipe']:
        bad.append('a divider is drawn on a card with no event')
    if not r['without']['solo']:
        bad.append('a card with no event is not marked solo')
    if not r['withE']['pipe']:
        bad.append('the divider vanished on a card that DOES have an event')
    if r['withE']['solo']:
        bad.append('a card with an event is wrongly marked solo')
    # and it must hold on the real cards too, not only in the unit case
    live = pg.evaluate("""(()=>{ const bad=[]; si=1; ci=1; SHOW.forEach((s,i)=>s.cues.forEach((q,k)=>{
        const st=buildState(s,k+1); if(st.dev) return; setStamp(st);
        const fr=document.querySelector('#era .pad .sheet.top .frow'); if(!fr) return;
        const f=(fr.querySelector('.foot')||{}).textContent||''; const p=fr.querySelector('.pipe');
        const shown=p?getComputedStyle(p).display!=='none':false;
        if(!f.trim() && shown) bad.push(q.id); })); return bad; })()""")
    if live:
        bad.append('cards with a divider and no event: ' + ', '.join(live[:6]))
    return bad


# ---------- D-032 · the song 9 notifications are pushed in on ----------
def a_song9_push(pg):
    bad = []
    boot(pg)
    goto(pg, 9, 0)
    fire(pg)
    fire(pg)          # 9.2 — the first notification (fire() settles the camera for us)
    r = pg.evaluate("""(()=>{ const n=document.querySelector('#projDevice .nstack .notif'); if(!n) return null;
        const b=n.getBoundingClientRect(); return {w:b.width,h:b.height,x:b.x,y:b.y,
        fw:innerWidth*(1-ERA_ZONE_()), fh:innerHeight}; })()""")
    if not r:
        return ['no notification on screen at 9.2']
    if r['w'] < r['fw'] * 0.55:
        bad.append(f'the notification is {r["w"]:.0f}px of a {r["fw"]:.0f}px reading window — the camera never came in')
    if r['x'] < -2 or r['x'] + r['w'] > r['fw'] + 2:
        bad.append(f'the notification is chopped horizontally (x {r["x"]:.0f} w {r["w"]:.0f} in {r["fw"]:.0f})')
    if r['y'] < -2 or r['y'] + r['h'] > r['fh'] + 2:
        bad.append(f'the notification is chopped vertically (y {r["y"]:.0f} h {r["h"]:.0f} in {r["fh"]:.0f})')
    return bad


# ---------- D-033 · the mail lands, with its tone, three seconds before his text ----------
def a_10_mail_first(pg):
    boot(pg)
    goto(pg, 10, 0)
    tap_sfx(pg)
    fire(pg, 40000, settle=False)
    log = sfx_log(pg)
    mail = [t for n, t in log if n == 'mail']
    txt = [t for n, t in log if n in ('receive', 'notif')]
    if not mail:
        return ['no mail tone in 10.1 — the Casting Networks email arrives in silence']
    if not txt:
        return ['his text never lands after the mail']
    gap = (min(txt) - min(mail)) / 1000.0
    if gap < 2.4:
        return [f'his text lands {gap:.1f}s after the mail — David asked for three seconds']
    return []


# ---------- D-034 · the flashback holds long enough to read ----------
def a_105_hold(pg):
    bad = []
    ops = cue_ops(pg, 10, '10.5')
    if any(o.get('op') in ('notiftap', 'unlock', 'history') for o in ops):
        bad.append('10.5 still unlocks the phone or opens the thread — David cut that')
    pause = max([o.get('ms', 0) for o in ops if o.get('op') == 'pause'] or [0])
    if pause < 10000:
        bad.append(f'the paragraph holds only {pause} ms — not enough to read')
    boot(pg)
    goto(pg, 10, 4)
    pg.evaluate('advance()')
    pg.wait_for_timeout(12000)
    r = pg.evaluate("""(()=>{ const d=document.querySelector('#projDevice .iphone'); if(!d) return null;
        const lock=!!d.querySelector('.layer.lock, .lockwrap, .nstack');
        const txt=(d.innerText||'').replace(/\\s+/g,' ').trim();
        return {lock, len:txt.length}; })()""")
    if not r or not r['lock']:
        bad.append('twelve seconds in, the lock screen is gone')
    elif r['len'] < 120:
        bad.append(f'only {r["len"]} characters on screen — the paragraph is not there')
    return bad


# ---------- D-035 · the photo bed falls, never piles, never goes blank ----------
def a_photo_bed(pg):
    """With photographs it falls; with none it shows NOTHING (a renderer never invents filler)."""
    bad = []
    cfg = pg.evaluate('PILE_CFG()')
    if cfg['h'] != 25:
        bad.append(f'the prints are {cfg["h"]}% of stage height, not 25%')
    lo, hi = cfg['every']
    if not (2500 <= lo <= 3500 and 4500 <= hi <= 5500):
        bad.append(f'a new print every {lo}-{hi} ms, not every 3-5 s')
    css = pg.evaluate("""(()=>{ for(const s of document.styleSheets){ let r; try{ r=s.cssRules; }catch(e){ continue; }
        for(const x of r) if(x.name==='pfall') return x.cssText; } return ''; })()""")
    if '120vh' not in css:
        bad.append('the prints do not fall all the way off the bottom of the stage')
    boot(pg)
    pg.evaluate("(()=>{ const st=buildState(SHOW[0],0); st.housecard=true; setStamp(st); })()")
    pg.wait_for_timeout(400)
    # 1 · NO PHOTOGRAPHS YET: the stage stays empty. A greeked placeholder drifting over the black
    #     is invented filler and the audience saw one at 8.6.
    if pg.evaluate("(pileList()||[]).length") == 0:
        pg.evaluate('pileStop(); pileReset(); pileDrop();')
        pg.wait_for_timeout(300)
        if pg.evaluate("document.querySelectorAll('#loop .print').length"):
            bad.append('the bed invents a placeholder print when no photographs are loaded')
    # 2 · WITH PHOTOGRAPHS: it falls, it never accumulates, it never runs dry
    pg.evaluate("""(()=>{ const px='data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7';
        window.L5Y_LOOP={ml:[],ac:[]};
        for(let i=0;i<8;i++){ const e={k:'img',s:px,r:1.5}; window.L5Y_LOOP.ml.push(e); window.L5Y_LOOP.ac.push(e); }
        pileStop(); pileReset(); })()""")
    if pg.evaluate("(pileList()||[]).length") != 8:
        return bad + ['could not load test photographs into the bed']
    pg.evaluate("(()=>{ for(let i=0;i<6;i++){ pileDrop(); const S=PILE_S(); if(S.t){clearTimeout(S.t); S.t=null;} } })()")
    pg.wait_for_timeout(300)
    n = pg.evaluate("document.querySelectorAll('#loop .print').length")
    if n != 6:
        bad.append(f'six drops produced {n} prints on screen')
    if not pg.evaluate("[...document.querySelectorAll('#loop .print')].every(e=>/pfall/.test(e.style.animation))"):
        bad.append('a print is on stage without a fall animation — it would just sit there')
    if not pg.evaluate("[...document.querySelectorAll('#loop .print img')].length"):
        bad.append('the prints render no photograph')
    pg.evaluate("document.querySelectorAll('#loop .print').forEach(e=>e.dispatchEvent(new Event('animationend')))")
    pg.wait_for_timeout(150)
    left = pg.evaluate("document.querySelectorAll('#loop .print').length")
    if left:
        bad.append(f'{left} prints accumulated at the bottom instead of leaving')
    pg.evaluate("pileReset(); PILE_S().i=8*7; pileDrop();")
    pg.wait_for_timeout(250)
    if pg.evaluate("document.querySelectorAll('#loop .print').length") < 1:
        bad.append('the bed goes blank after seven passes through the photographs')
    inflight = cfg['fall'][0] / hi
    if inflight < 3:
        bad.append(f'only ~{inflight:.1f} prints in flight — the stage goes empty between them')
    return bad


# ---------- the three still blocked on David ----------
def a_ringback_twice(pg):
    """David's licensed recording, trimmed to one burst, played exactly twice and tight."""
    bad = []
    if not pg.evaluate("!!(window.L5Y_SFX||{})['ringback.mp3']"):
        return ['the licensed ringback is not embedded in the build']
    if not pg.evaluate('!!SFX_KEEP_().ringback'):
        bad.append('ringback is not in SFX_KEEP_ — the sound law would silence it')
    from qc_notes_sound import _audio
    _audio(pg)                                        # SOUND_HOST + a running AudioContext, or this
                                                      # probe grades silence and blames the engine
    pg.evaluate("""(()=>{ window.__rb=[]; const t0=performance.now(); const r=window.sample;
        window.sample=function(n,o){ const out=r.apply(this,arguments);
          if(n==='ringback') window.__rb.push([Math.round(performance.now()-t0), !!out]);
          return out; }; })()""")
    # every cue that dials out must ring twice
    dials = pg.evaluate("""(()=>{ const out=[]; SHOW.forEach((s,i)=>s.cues.forEach((q,k)=>{
        if((q.do||[]).some(o=>o.op==='call' && o.dir==='out')) out.push([i,k,q.id]); })); return out; })()""")
    if not dials:
        return bad + ['nobody dials out anywhere in the show']
    for i, k, cid in dials:
        pg.evaluate(f'si={i}; ci={k}; animTok++; animRunning=false; hardRender();')
        pg.wait_for_timeout(150)
        pg.evaluate('window.__rb=[]; advance()')
        pg.wait_for_timeout(9000)
        rb = pg.evaluate('window.__rb')
        if len(rb) != 2:
            bad.append(f'{cid}: the ringback played {len(rb)} time(s), not two')
            continue
        if not all(x[1] for x in rb):
            bad.append(f'{cid}: the synthesised fallback played, not the licensed recording')
        gap = rb[1][0] - rb[0][0]
        if not (2600 <= gap <= 3300):
            bad.append(f'{cid}: {gap} ms between the rings — not two tight rings')
    dur = pg.evaluate("""(()=>{ const b=SFX_BUF_()['ringback.mp3']; return b?+b.duration.toFixed(2):0; })()""")
    if dur and not (1.9 <= dur <= 2.2):
        bad.append(f'the trimmed ring is {dur}s — it still carries dead air')
    return bad


def a_bell(pg):
    """The agent's text arrives on its own tone, distinct from the bank alert and the mail."""
    bad = []
    boot(pg)
    tones = pg.evaluate("""(()=>{ const pick=o=>o.tone||(o.app==='Mail'?'mail':(o.app==='Chase'?'tink':'notif'));
        const out={}; SHOW.forEach(s=>s.cues.forEach(q=>(q.do||[]).forEach(o=>{
          if(o.op!=='notif') return; out[q.id]=out[q.id]||[]; out[q.id].push([o.app, pick(o), String(o.t||'').slice(0,18)]); })));
        return out; })()""")
    sonny = [(cid, v) for cid, rows in tones.items() for v in rows if 'SONNY' in (v[2] or '').upper()]
    if not sonny:
        return ["the agent's text is not in the show any more"]
    cid, (app, tone, _) = sonny[0]
    mail = {v[1] for rows in tones.values() for v in rows if v[0] == 'Mail'}
    bank = {v[1] for rows in tones.values() for v in rows if v[0] == 'Chase'}
    plain = {v[1] for rows in tones.values() for v in rows
             if v[0] == 'Messages' and 'SONNY' not in (v[2] or '').upper()}
    if tone in mail:
        bad.append(f'{cid}: the agent\'s text uses the same tone as the emails ({tone})')
    if tone in bank:
        bad.append(f'{cid}: the agent\'s text uses the same tone as the bank alert ({tone})')
    if tone in plain:
        bad.append(f'{cid}: the agent\'s text sounds like every other text ({tone})')
    if not pg.evaluate(f"!!SFX_KEEP_()['{tone}']"):
        bad.append(f'{cid}: its tone "{tone}" is not a kept phone sound — it would be silenced')
    return bad


def a_paper(pg):
    if pg.evaluate("(window.L5Y_PAPER||[]).length"):
        return []
    return ['WAITING ON DAVID: only 1 of the 50 licensed scans is retrievable (the rest exceed the '
            'Drive download cap) and they are brown kraft, not the off-white the sheets need']


def a_qr(pg):
    if not pg.evaluate("!!(window.L5Y_IMG||{})['qr-next5']"):
        return ['the money-minute QR is not embedded']
    return ['WAITING ON DAVID: the new code decodes to a Cloudinary .jpg, not a donation page — '
            'confirm the destination before the house scans it']


# ---------- D-067 · a second window must not be a dead end ----------
def a_gate_recoverable(pg):
    """David, Sept 21: he loaded the cue URL and landed on the projection screen with no start
    screen. A window opened while another window of the same origin has the show up deliberately
    becomes that show's projector - that is the design and it must not change. What was wrong is
    that a tab left open from an EARLIER session claimed the same thing for ever, and a window
    swallowed either way had no gate, no explanation and no key that did anything."""
    import os
    bad = []
    URL = 'file://' + os.path.abspath('L5Y-Show-STANDALONE.html')
    Q = """(()=>{const b=document.body, gw=document.getElementById('gatewrap');
      return {gate: gw?getComputedStyle(gw).display:null,
              needgate: b.classList.contains('needgate'),
              gatewait: b.classList.contains('gatewait'),
              started: b.classList.contains('started'),
              view: b.classList.contains('v-projection')?'projection':'presenter'};})()"""

    # 1 · a cold load asks the questions, full-screen
    pg.wait_for_timeout(1200)
    m = pg.evaluate(Q)
    if not m['needgate'] or m['gate'] == 'none':
        bad.append('a cold load does not put the questionnaire up (%r)' % m)

    # 2 · while a show is genuinely LIVE, a second window is still its silent projector
    pg.evaluate("startAs('presenter'); advance();")
    pg.wait_for_timeout(900)
    live = pg.context.new_page()
    try:
        live.goto(URL); live.wait_for_timeout(3200)
        m = live.evaluate(Q)
        if m['view'] != 'projection' or m['needgate']:
            bad.append('a window opened during a live show no longer becomes its projector (%r) — '
                       'the operator would get a questionnaire on the house screen' % m)
        # 3 · …and Shift+G takes the questions back on that window
        live.keyboard.press('Shift+G')
        live.wait_for_timeout(1200)
        m = live.evaluate(Q)
        if not m['needgate'] or m['gate'] == 'none' or m['started']:
            bad.append('Shift+G does not recover a swallowed window (%r) — it is a dead end again'
                       % m)
    finally:
        live.close()

    # 4 · a STALE owner (idle past the threshold) does not swallow a fresh window
    pg.evaluate("LAST_ACT(Date.now() - 3*3600e3)")
    stale = pg.context.new_page()
    try:
        stale.goto(URL); stale.wait_for_timeout(3200)
        m = stale.evaluate(Q)
        if not m['needgate'] or m['gate'] == 'none':
            bad.append('a tab left open from an earlier session still swallows a fresh load (%r) — '
                       'David gets the projection screen instead of the start screen' % m)
    finally:
        stale.close()
    return bad


# ---------- D-037 · one receipt in a thread, ever ----------
def a_one_receipt(pg):
    bad = []
    boot(pg)
    i = song_ix(pg, 1)
    for k in range(pg.evaluate(f'SHOW[{i}].cues.length')):
        pg.evaluate(f'si={i}; ci={k}; animTok++; animRunning=false; hardRender();')
        pg.wait_for_timeout(120)
        cid = pg.evaluate(f'SHOW[{i}].cues[{k}].id')
        fire(pg)
        r = pg.evaluate("""(()=>{ const t=document.querySelector('#projDevice .thread'); if(!t) return null;
            const live=[...t.querySelectorAll('.rcpt')].map(e=>e.textContent.trim());
            const want=(CUR.msgs||[]).filter(m=>m.k==='rcpt').map(m=>m.t);
            return {live, want}; })()""")
        if not r:
            continue
        if len(r['live']) > 1:
            bad.append(f'{cid}: {len(r["live"])} receipts in the thread at once — {r["live"]}')
        if len(r['live']) != len(r['want']):
            bad.append(f'{cid}: the screen shows {r["live"]} but the state holds {r["want"]}')
    return bad


# ---------- D-038 · the laptop is legible from the back row ----------
def a_laptop_legible(pg):
    bad = []
    boot(pg)
    i = song_ix(pg, 7)
    for k in range(pg.evaluate(f'SHOW[{i}].cues.length')):
        pg.evaluate(f'si={i}; ci={k}; animTok++; animRunning=false; hardRender();')
        pg.wait_for_timeout(120)
        cid = pg.evaluate(f'SHOW[{i}].cues[{k}].id')
        fire(pg)
        r = pg.evaluate("""(()=>{ const w=document.querySelector('#projDevice .mb-screen'); if(!w) return null;
            const out=[]; const walk=document.createTreeWalker(w, NodeFilter.SHOW_TEXT);
            let t; while(t=walk.nextNode()){ const s=(t.textContent||'').trim(); if(!s) continue;
              const e=t.parentElement, b=e.getBoundingClientRect(); if(!b.width||!b.height) continue;
              if(e.closest('.greek,.ml')) continue;              // greeked asset labels are placeholders
              out.push([s.slice(0,24), parseFloat(getComputedStyle(e).fontSize)]); }
            const mb=document.querySelector('#projDevice .macbook');
            const era=document.getElementById('era');
            return {out, mbRight: mb?mb.getBoundingClientRect().right:0,
                    eraLeft: era?era.getBoundingClientRect().left:1e9}; })()""")
        if not r:
            continue
        for txt, sz in r['out']:
            if sz < 22:
                bad.append(f'{cid}: "{txt}" is {sz:.0f}px — under the 22px floor for 25 feet')
        if r['mbRight'] > r['eraLeft'] + 1:
            bad.append(f'{cid}: the laptop runs under the calendar strip by {r["mbRight"]-r["eraLeft"]:.0f}px')
    return bad


# ---------- D-041 · a call timer never leading-zeroes the minutes ----------
def a_timer_format(pg):
    bad = []
    boot(pg)
    for i in range(pg.evaluate('SHOW.length')):
        for k in range(pg.evaluate(f'SHOW[{i}].cues.length')):
            if not pg.evaluate(f"(SHOW[{i}].cues[{k}].do||[]).some(o=>/^connected/i.test(o.st||''))"):
                continue
            pg.evaluate(f'si={i}; ci={k}; animTok++; animRunning=false; hardRender();')
            pg.wait_for_timeout(120)
            cid = pg.evaluate(f'SHOW[{i}].cues[{k}].id')
            pg.evaluate('advance()')
            pg.wait_for_timeout(120)      # the FIRST frame is the one that used to read 00:00
            txt = pg.evaluate("""(()=>{ const e=document.querySelector('#projDevice .calltimer');
                return e?e.textContent.trim():''; })()""")
            if txt and txt.startswith('0') and not txt.startswith('0:'):
                bad.append(f'{cid}: the call timer reads "{txt}" — iOS never pads the minutes')
    return bad


# ---------- D-046 · the buttons always match the call's state ----------
def a_call_buttons_match(pg):
    bad = []
    boot(pg)
    seen = {'in': 0, 'live': 0}
    for i in range(pg.evaluate('SHOW.length')):
        for k in range(pg.evaluate(f'SHOW[{i}].cues.length')):
            if not pg.evaluate(f"(SHOW[{i}].cues[{k}].do||[]).some(o=>o.op==='call'||o.op==='callState')"):
                continue
            pg.evaluate(f'si={i}; ci={k}; animTok++; animRunning=false; hardRender();')
            pg.wait_for_timeout(150)
            cid = pg.evaluate(f'SHOW[{i}].cues[{k}].id')
            fire(pg)
            r = pg.evaluate("""(()=>{ const row=document.querySelector('#projDevice .callbtns');
                const st=((CUR.call||{}).st)||''; if(!row) return {st, n:0};
                return {st, n:row.children.length,
                        glyphs:[...row.children].map(e=>(e.textContent||'').trim()).join('')}; })()""")
            st = (r['st'] or '').lower()
            if 'ended' in st or not st:
                continue
            incoming = 'incoming' in st
            if not r['n']:
                bad.append(f'{cid}: a live call ("{r["st"]}") with no buttons at all')
                continue
            answer = '✆' in (r.get('glyphs') or '')
            if incoming and not answer:
                bad.append(f'{cid}: an INCOMING call with no Answer button')
            if not incoming and answer:
                bad.append(f'{cid}: "{r["st"]}" still shows Answer — a phone never does that')
            if not incoming and r['n'] != 3:
                bad.append(f'{cid}: "{r["st"]}" shows {r["n"]} buttons, not mute/end/speaker')
            seen['in' if incoming else 'live'] += 1
    if not seen['in'] or not seen['live']:
        bad.append(f'the probe never saw both states: {seen}')
    return bad
