"""David's Sept 22 notes on the house photo bed, proved by watching it fall.

The bed is the one thing on stage that is never fired by a cue, so a settled-DOM sweep can say
nothing useful about it. These probes start the real preshow bed and record every print's
rectangle and rotation on every animation frame, then argue with the numbers.
"""
import os

W, H = 1920, 1080
URL = 'file://' + os.path.abspath('L5Y-Show-STANDALONE.html')

# Long enough that prints born after the recorder starts also die inside it: a ~10 s fall plus a
# ~1.5 s spawn gap means the last judgeable print is born at WATCH-11.5 s, so a 26 s watch yields
# a dozen-plus complete lifecycles without making the gate wait a minute.
WATCH_MS = 26000

REC = r"""
window.__BED={rows:new Map(), on:false, t0:0, seq:0, conc:[]};
window.__bedStart=function(){
  const B=window.__BED; B.rows=new Map(); B.seq=0; B.conc=[]; B.on=true; B.t0=performance.now();
  // a print already falling when the recorder wakes has no first appearance to judge
  document.querySelectorAll('#loop .print').forEach(el=>{ el.__bid=-1; });
  const tick=()=>{
    if(!B.on) return;
    const t=performance.now()-B.t0, all=document.querySelectorAll('#loop .print');
    B.conc.push([t, all.length]);
    all.forEach(el=>{
      if(el.__bid===-1) return;
      if(!el.__bid) el.__bid = ++B.seq;
      const b=el.getBoundingClientRect(), pw=el.querySelector('.pw');
      let ang=0;
      if(pw){ const m=new DOMMatrixReadOnly(getComputedStyle(pw).transform); ang=Math.atan2(m.b,m.a)*180/Math.PI; }
      let r=B.rows.get(el.__bid);
      if(!r){ r={id:el.__bid,t0:t,bot0:b.bottom,h:b.height,cx0:b.left+b.width/2,amin:ang,amax:ang}; B.rows.set(el.__bid,r); }
      r.t1=t; r.top1=b.top;
      if(ang<r.amin) r.amin=ang;
      if(ang>r.amax) r.amax=ang;
    });
    requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
};
window.__bedStop=function(){ const B=window.__BED; B.on=false; return {rows:[...B.rows.values()], conc:B.conc}; };
0
"""


def _watch_bed(pg):
    """Park on the preshow title page, where the bed runs, and record it falling."""
    pg.set_viewport_size({'width': W, 'height': H})
    if not pg.evaluate('typeof started !== "undefined" && started'):
        pg.evaluate("setCast('ml'); startAs('projection');")
        pg.wait_for_timeout(400)
    pg.evaluate("si=0; ci=0; animTok++; animRunning=false; hardRender(); 0")
    pg.wait_for_timeout(700)
    on = pg.evaluate("(()=>{const L=document.getElementById('loop');"
                     "return [!!(L&&L.classList.contains('on')), (window.L5Y_LOOP&&window.L5Y_LOOP[CAST]||[]).length];})()")
    if not on[0] or not on[1]:
        return None, f'the bed is not running at the preshow (on={on[0]}, photographs={on[1]})'
    pg.evaluate(REC)
    pg.evaluate("window.__bedStart()")
    pg.wait_for_timeout(WATCH_MS)
    return pg.evaluate("window.__bedStop()"), None


# ---------- D-074 · the bed falls from the sky and off the page ----------
def a_bed_falls(pg):
    """David, Sept 22: "the photos are like appearing randomly, not falling from the sky, randomly
    changing to another photo... I want it to be SLOWER, and everything falls from the sky and falls
    off the page, each photo should take like 10 seconds to fall from the top to bottom from first
    appearance to last appearance... the variability of angle (to a 15 degree left and right maximum)
    and the placement needs some improvement."

    Four measurements, each against a number he gave:

    FROM THE SKY. pfall used to start every print at a fixed -42vh whatever its size, so once the
    prints doubled, anything taller than 42vh was already a third of the way onto the stage on its
    first painted frame. It appeared. The start is the print's OWN height now (--y0).

    OFF THE PAGE. Its last painted frame has its top edge below the foot of the stage.

    TEN SECONDS. First appearance to last appearance, the whole journey — not a window onto a
    longer one.

    FIFTEEN DEGREES, SWAY INCLUDED. A keyframe's transform REPLACES the element's, so the per-print
    rotate() written inline was discarded the moment psway began: every print in the show swayed
    through the identical ±3.5° and the tilt never rendered once. Measured off the real composited
    matrix, so the only way to pass is for the angle to actually be on the glass.

    THE PLACEMENT IS DEALT. Seven lanes, shuffled, one print each — a bare random() clumps."""
    bad = []
    out, err = _watch_bed(pg)
    if err:
        return [err]
    rows, conc = out['rows'], out['conc']
    done = [r for r in rows if r['t1'] < WATCH_MS - 900 and r['t0'] > 120]
    if len(done) < 8:
        return [f'only {len(done)} complete falls in {WATCH_MS/1000:.0f}s — too few to judge the bed']

    for r in done:
        if r['bot0'] > 4:
            bad.append(f"print #{r['id']} is already {r['bot0']:.0f}px onto the stage at its first "
                       f"appearance — it appears, it does not fall in")
        if r['top1'] < H - 4:
            bad.append(f"print #{r['id']} is still {H-r['top1']:.0f}px on stage at its last "
                       f"appearance — it vanishes, it does not fall off")
        d = (r['t1'] - r['t0']) / 1000
        if not (8.4 <= d <= 12.4):
            bad.append(f"print #{r['id']} crosses in {d:.1f}s — David asked for about ten")

    for r in rows:
        peak = max(abs(r['amin']), abs(r['amax']))
        if peak > 15.05:
            bad.append(f"print #{r['id']} reaches {peak:.1f}° — the arc is ±15° left and right, no more")
    tilts = {round((r['amin'] + r['amax']) / 2, 1) for r in rows}
    if len(tilts) < max(4, len(rows) // 3):
        bad.append(f'only {len(tilts)} distinct tilts across {len(rows)} prints — the angle is not varying')

    N = 7
    cols = [0] * N
    for r in rows:
        cols[min(max(int(min(max(r['cx0'], 0), W - 1) / (W / N)), 0), N - 1)] += 1
    if 0 in cols:
        bad.append(f'column {cols.index(0)+1} of {N} never receives a print (columns {cols}) — the bed clumps')
    elif max(cols) > 2.6 * min(cols):
        bad.append(f'the columns run {min(cols)}…{max(cols)} ({cols}) — the placement is still lumpy')

    # the house opens on an empty stage and fills; judge the bed once it is actually running
    steady = [n for (t, n) in conc if t > 12500]
    if steady and min(steady) < 4:
        bad.append(f'the bed thins to {min(steady)} prints on stage — it should stay full')
    return bad


PROBES = [a_bed_falls]
