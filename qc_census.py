"""LIVE CENSUS QC: play every cue exactly like the operator (advance) and log every sound that plays and every camera move — name, zoom, anchor, duration. Flags non-phone sounds, fast moves, and busy cues. Usage: CHROMIUM_PATH=... python3 qc_census.py"""
import os,json,time
from playwright.sync_api import sync_playwright
KEEP={'send','receive','notif','mail','mailsent','lock','ftring','ring','end','connect','click','del','keymod'}
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=os.environ['CHROMIUM_PATH']); pg=b.new_page(viewport={'width':1920,'height':1080}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+os.path.abspath('L5Y-Show-STANDALONE.html')); pg.wait_for_timeout(2500)
    pg.evaluate("""setCast('ml'); startAs('projection'); window.__log=[]; window.__t0=performance.now();
      SOUND_HOST=true; audioInit();
      const _sample=sample; window.sample=function(n,o){ const r=_sample(n,o); window.__log.push({k:'snd',n,ok:!!r,t:performance.now()-window.__t0}); return r; };
      const _sfx=sfx; window.sfx=function(n,o){ window.__log.push({k:'sfxcall',n,t:performance.now()-window.__t0}); return _sfx(n,o); };
      const _apply=camApply; window.camApply=function(c,g,z,qx,qy,anchor,instant,dur){ if(!c||!c.style) return _apply(c,g,z,qx,qy,anchor,instant,dur); const before=c.style.transform; const r=_apply(c,g,z,qx,qy,anchor,instant,dur);
        if(c.closest('#projection')) window.__log.push({k:'cam',z:+z.toFixed(2),anchor:anchor||'',instant:!!instant,tr:c.style.transition,moved:before!==c.style.transform,t:performance.now()-window.__t0}); return r; }; 0""")
    pg.wait_for_timeout(1500)
    out=[]
    nsongs=pg.evaluate('SHOW.length')
    for si in range(nsongs):
        pg.evaluate(f'si={si}; ci=0; animTok++; animRunning=false; hardRender();'); pg.wait_for_timeout(150)
        n=pg.evaluate(f'SHOW[{si}].cues.length')
        for k in range(n):
            pg.evaluate("window.__log=[]; window.__t0=performance.now(); setTimeout(()=>advance(),0)")
            t0=time.time()
            for _ in range(700):
                pg.wait_for_timeout(100)
                if not pg.evaluate('animRunning'): break
            dur=time.time()-t0
            cid=pg.evaluate(f'SHOW[{si}].cues[{k}].id'); log=pg.evaluate('window.__log')
            out.append({'cue':cid,'dur':round(dur,1),'log':log})
    b.close()
json.dump(out,open('census.json','w'),indent=0)
bad=[]
for c in out:
    snd=[l for l in c['log'] if l['k']=='snd' and l['ok']]; calls=[l for l in c['log'] if l['k']=='sfxcall']; cam=[l for l in c['log'] if l['k']=='cam' and l['moved']]
    names=[l['n'] for l in snd]
    for l in snd:
        if l['n'] not in KEEP: bad.append(f"{c['cue']}: NON-PHONE SOUND {l['n']}")
    for l in cam:
        if not l['instant'] and ('1.4' not in l['tr'] and '2.' not in l['tr'] and '3.' not in l['tr'] and '4.' not in l['tr'] and '5.' not in l['tr'] and '6.' not in l['tr']): bad.append(f"{c['cue']}: FAST CAMERA {l['tr']}")
    if len(cam)>3: bad.append(f"{c['cue']}: {len(cam)} camera moves")
    print(f"{c['cue']:>5} {c['dur']:5.1f}s  sounds={names}  camMoves={len(cam)}  " + ' '.join(f"[z{l['z']} {l['anchor'] or 'c'} {'inst' if l['instant'] else l['tr'].split(' ')[1]}]" for l in cam))
print('ERRS', errs if errs else 'none'); print('VIOLATIONS', bad if bad else 'none')
