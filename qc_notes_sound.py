"""PROBES for the sound findings from the 48-agent law audit (D-049 … D-056)."""

from qc_notes_core import boot, fire, song_ix


def _audio(pg):
    pg.evaluate('startAs("projection"); audioInit()')
    pg.wait_for_timeout(400)
    pg.evaluate("sample('notif',{gain:0.0001})")      # force the decoder to run
    pg.wait_for_timeout(900)


# ---------- D-049 · a blackout takes the sound with it ----------
def a_blackout_is_silent(pg):
    bad = []
    _audio(pg)
    pg.evaluate("bedStart('lake.mp3',0.2,0.45); warpStart(6000,false); sfxRing('ring');")
    pg.wait_for_timeout(800)
    before = pg.evaluate("({bed:!!BED, warp:!!WARP, ring:!!RING})")
    if not (before['warp'] and before['ring']):
        bad.append(f'could not get the noisemakers running to test against: {before}')
    pg.evaluate('setBlackout(true)')
    pg.wait_for_timeout(1300)
    after = pg.evaluate("({bed:!!BED, warp:!!WARP, ring:!!RING})")
    for k, v in after.items():
        if v:
            bad.append(f'BLACKOUT left the {k} playing to a black stage')
    pg.evaluate('setBlackout(false)')
    src = pg.evaluate('setBlackout.toString()')
    for fn in ('bedStop', 'warpStop', 'sfxRingStop'):
        if fn not in src:
            bad.append(f'setBlackout never calls {fn}')
    return bad


# ---------- D-050 · every embedded sound decodes ----------
def a_all_sounds_decode(pg):
    bad = []
    _audio(pg)
    pg.evaluate("(()=>{ Object.keys(SFX_MAP_()).forEach(n=>{ try{ sample(n,{gain:0.0001}); }catch(e){} }); })()")
    pg.wait_for_timeout(1500)
    dead = pg.evaluate("""(()=>{ const all=Object.keys(window.L5Y_SFX||{}), ok=Object.keys(SFX_BUF_()||{});
        return all.filter(f=>!ok.includes(f)); })()""")
    if dead:
        bad.append(f'these embedded files never decode: {dead}')
    if pg.evaluate("Object.keys(window.L5Y_SFX||{}).some(f=>/Reflection/i.test(f))"):
        bad.append('an iOS RINGTONE is still shipped in a build whose law says NO RINGTONES')
    return bad


# ---------- D-051 · the hang-up tone fires once ----------
def a_one_hangup(pg):
    bad = []
    _audio(pg)
    pg.evaluate("""(()=>{ window.__e=[]; const r=window.sfx;
      window.sfx=function(n,o){ if(n==='end'&&SFX_KEEP_()[n]) window.__e.push(1); return r.apply(this,arguments); }; })()""")
    for i in range(pg.evaluate('SHOW.length')):
        for k in range(pg.evaluate(f'SHOW[{i}].cues.length')):
            if not pg.evaluate(f"(SHOW[{i}].cues[{k}].do||[]).some(o=>o.op==='call'||o.op==='callState'||o.op==='black'||o.op==='device')"):
                continue
            pg.evaluate(f'si={i}; ci={k}; animTok++; animRunning=false; hardRender();')
            pg.wait_for_timeout(150)
            cid = pg.evaluate(f'SHOW[{i}].cues[{k}].id')
            pg.evaluate('window.__e=[]')
            fire(pg, settle=False)
            pg.wait_for_timeout(500)
            n = len(pg.evaluate('window.__e'))
            if n > 1:
                bad.append(f'{cid}: the hang-up tone fired {n} times')
    return bad


# ---------- D-055 · the ringback stops the instant the call is answered ----------
def a_ring_stops_on_answer(pg):
    bad = []
    if 'RING.src=src' not in pg.evaluate('sfxRing.toString()'):
        bad.append('sfxRing discards the ringback source, so stopping it cannot cut the ring already sounding')
    _audio(pg)
    pg.evaluate("sfxRing('ringback')")
    pg.wait_for_timeout(500)
    if not pg.evaluate('!!(RING && RING.src)'):
        bad.append('the ringback is playing with no handle on its source')
    pg.evaluate('sfxRingStop()')
    pg.wait_for_timeout(200)
    if pg.evaluate('!!RING'):
        bad.append('sfxRingStop did not clear the ring')
    return bad


# ---------- D-052 / D-053 · the warp tapers, and the whole clip is heard ----------
def a_warp_tapers(pg):
    bad = []
    _audio(pg)
    pg.evaluate('warpStop(0); warpStart(6000,false)')
    read = []
    last = 0
    for ms in (3000, 4200, 5000, 5600):
        pg.wait_for_timeout(ms - last)
        last = ms
        read.append((ms, pg.evaluate("WARP? +WARP.g.gain.value : 0")))
    pg.evaluate('warpStop(0)')
    g = dict(read)
    if g[3000] < 0.6:
        bad.append(f'the warp is already fading at 3 s ({g[3000]:.2f}) — it should still be up')
    # a real taper falls gradually; a collapse is already near zero a second in
    if g[4200] < 0.45:
        bad.append(f'the taper collapses: {g[4200]:.2f} at 4.2 s, only 0.6 s into the fall')
    if not (0.15 <= g[5000] <= 0.55):
        bad.append(f'the middle of the taper reads {g[5000]:.2f} — not an even recession')
    if g[5600] > 0.12:
        bad.append(f'the warp is still at {g[5600]:.2f} with 0.4 s to go — it will end abruptly')
    src = pg.evaluate('warpStart.toString()')
    if 'setValueCurveAtTime' not in src:
        bad.append('the taper is still a bare exponential ramp, which perceptually collapses')
    if 'warpVerb' not in src:
        bad.append('there is no reverb on the warp')
    return bad


def a_warp_fits_roll(pg):
    bad = []
    _audio(pg)
    d = pg.evaluate("""(()=>{ const b=SFX_BUF_(); return {fwd:(b['timewarp.mp3']||{}).duration,
        rev:(b['reverse_timewarp.mp3']||{}).duration}; })()""")
    if not d['fwd'] or not d['rev']:
        return ['the warp clips are not decoded']
    if 'b.duration - d' not in pg.evaluate('warpStart.toString()'):
        bad.append('a clip longer than the roll is still played from its top, so its ending is cut off')
    for k, v in d.items():
        if v < 5.8:
            bad.append(f'the {k} clip is only {v:.2f}s — a 6 s roll would end in silence')
    return bad


# ---------- D-054 · every backspace ticks ----------
def a_every_backspace(pg):
    bad = []
    src = pg.evaluate("""(()=>{ const f=playCue.toString(); const i=f.indexOf("o.op==='wipe'");
        return i<0?'':f.slice(i,i+900); })()""")
    if 'i%4===0' in src:
        bad.append('the wipe still sounds only one backspace in four')
    _audio(pg)
    pg.evaluate("""(()=>{ window.__d=0; const r=window.sfx;
      window.sfx=function(n,o){ if(n==='del') window.__d++; return r.apply(this,arguments); }; })()""")
    i = song_ix(pg, 2)
    pg.evaluate(f'si={i}; ci=1; animTok++; animRunning=false; hardRender();')
    pg.wait_for_timeout(200)
    fire(pg, 120000, settle=False)
    ticks = pg.evaluate('window.__d')
    if ticks < 60:
        bad.append(f'only {ticks} backspace ticks across the three drafts')
    return bad


# ---------- D-056 · the bank alert sounds like the text message it is ----------
def a_bell_audible(pg):
    bad = []
    boot(pg)
    if pg.evaluate("playCue.toString().includes(\"'Chase'?'tink'\")"):
        bad.append("the bank alert still uses the 22 ms tick instead of the text tone")
    tones = pg.evaluate("""(()=>{ const pick=o=>o.tone||(o.app==='Mail'?'mail':'notif'); const out=[];
        SHOW.forEach(s=>s.cues.forEach(q=>(q.do||[]).forEach(o=>{ if(o.op==='notif' && o.app==='Chase')
          out.push([q.id, pick(o)]); }))); return out; })()""")
    for cid, tone in tones:
        if tone == 'tink':
            bad.append(f'{cid}: the bank alert is still a 22 ms tick')
        if not pg.evaluate(f"!!SFX_KEEP_()['{tone}']"):
            bad.append(f'{cid}: its tone "{tone}" is not a kept phone sound')
    return bad
