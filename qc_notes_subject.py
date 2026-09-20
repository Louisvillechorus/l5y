"""THE SUBJECT LAW — the thing a cue points the camera at is never cut by the frame.

CLAUDE.md allows content to leave the frame with feathers: a long thread is meant to run
off the top. What is NOT allowed is the SUBJECT of the beat being sliced — Rob's text cut in
half at 2.2, the second notification cut at 9.3, the bubble cut at 14.4. This gate defines
"subject" mechanically as the last element camPush aimed at in a cue, and asserts that when
the glide settles, that element sits whole inside the reading window.

It is the family-level version of D-005/D-039/D-044: one rule, swept across the whole show,
so the same defect cannot come back in a song nobody happened to look at.
"""

WRAP = """(()=>{ if(window.__subjWrapped) return; window.__subjWrapped=true;
  window.__subj=[];
  const real=window.camPush;
  window.camPush=function(sel,z,delay,anchor,dur,force,nofit){
    window.__subj.push({sel, z, anchor:anchor||'center', force:!!force, at:(CUR&&CUR.__cid)||''});
    return real.apply(this,arguments); }; })()"""

MEASURE = """(()=>{
  const list=window.__subj||[]; if(!list.length) return {none:true};
  const s=list[list.length-1];                       // the last aim of this cue = its subject
  const c=document.querySelector('#projDevice .stagecam'); if(!c) return {none:true, sel:s.sel};
  const el=c.querySelector(s.sel); if(!el) return {missing:true, sel:s.sel};
  const r=el.getBoundingClientRect();
  if(!r.width || !r.height) return {none:true, sel:s.sel};
  const pj=document.getElementById('projection').getBoundingClientRect();
  const uw=pj.width*(1-ERA_ZONE_());                 // the reading window: the strip owns the right
  return {sel:s.sel, anchor:s.anchor,
          L:Math.round(r.left-pj.left), R:Math.round(r.right-pj.left),
          T:Math.round(r.top-pj.top),  B:Math.round(r.bottom-pj.top),
          uw:Math.round(uw), uh:Math.round(pj.height)};
})()"""


def a_subject_never_sliced(pg):
    bad = []
    pg.evaluate('startAs("projection")')
    pg.wait_for_timeout(300)
    for i in range(pg.evaluate('SHOW.length')):
        for k in range(pg.evaluate(f'SHOW[{i}].cues.length')):
            pg.evaluate(f'si={i}; ci={k}; animTok++; animRunning=false; hardRender();')
            pg.wait_for_timeout(120)
            cid = pg.evaluate(f'SHOW[{i}].cues[{k}].id')
            pg.evaluate(WRAP)
            pg.evaluate('window.__subj=[]')
            pg.evaluate('advance()')
            w = 0
            while w < 45000 and pg.evaluate('animRunning'):
                pg.wait_for_timeout(200)
                w += 200
            pg.wait_for_timeout(1500)          # let the 1.4 s glide land
            m = pg.evaluate(MEASURE)
            if not m or m.get('none'):
                continue
            if m.get('missing'):
                bad.append(f'{cid}: the camera aimed at "{m["sel"]}" and nothing matched it')
                continue
            cut = []
            if m['T'] < -1:
                cut.append(f'top by {-m["T"]}px')
            if m['B'] > m['uh'] + 1:
                cut.append(f'bottom by {m["B"] - m["uh"]}px')
            if m['L'] < -1:
                cut.append(f'left by {-m["L"]}px')
            if m['R'] > m['uw'] + 1:
                cut.append(f'right by {m["R"] - m["uw"]}px')
            if cut:
                bad.append(f'{cid}: the subject "{m["sel"]}" is cut {" and ".join(cut)}')
    return bad
