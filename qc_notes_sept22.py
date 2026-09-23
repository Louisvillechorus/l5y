"""David's Sept 22 notes on the house photo bed, proved by watching it fall.

The bed is the one thing on stage that is never fired by a cue, so a settled-DOM sweep can say
nothing useful about it. These probes start the real preshow bed and record every print's
rectangle and rotation on every animation frame, then argue with the numbers.
"""
import os

W, H = 1920, 1080
URL = 'file://' + os.path.abspath('L5Y-Show-STANDALONE.html')

# Long enough that prints born after the recorder starts also die inside it: a ~60 s fall and a
# ~20 s spawn gap mean prints born in the first minute finish inside the watch, two or three of them.
WATCH_MS = 125000

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
      const pw=el.querySelector('.pw');
      // the PAINTED box: .pw carries the rotation and overflows its parent
      const b=(pw||el).getBoundingClientRect();
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

    THE WHOLE JOURNEY. First appearance to last appearance, 50-70 s (the fall was slowed to ~60 s
    after the Sept 22 note) — not a window onto a longer one.

    FIFTEEN DEGREES, SWAY INCLUDED. A keyframe's transform REPLACES the element's, so the per-print
    rotate() written inline was discarded the moment psway began: every print in the show swayed
    through the identical ±3.5° and the tilt never rendered once. Measured off the real composited
    matrix, so the only way to pass is for the angle to actually be on the glass.

    CLEAR OF THE CARD, SIDES ALTERNATING (David, Sept 23, which replaced the seven dealt lanes):
    prints were landing on each other's faces and falling behind the title where nothing sees them.
    So no print is centred in the middle third, and two consecutive prints never share a side.

    THE BED IS SLOW NOW. One print every ~20 s, each falling ~60 s, so a 125 s watch holds two or
    three complete journeys and two or three prints on stage at once. The counts are judged
    against that, not against the Sept 22 flood."""
    bad = []
    out, err = _watch_bed(pg)
    if err:
        return [err]
    rows, conc = out['rows'], out['conc']
    done = [r for r in rows if r['t1'] < WATCH_MS - 900 and r['t0'] > 120]
    if len(done) < 2:
        return [f'only {len(done)} complete falls in {WATCH_MS/1000:.0f}s — too few to judge the bed']

    for r in done:
        if r['bot0'] > 4:
            bad.append(f"print #{r['id']} is already {r['bot0']:.0f}px onto the stage at its first "
                       f"appearance — it appears, it does not fall in")
        if r['top1'] < H - 4:
            bad.append(f"print #{r['id']} is still {H-r['top1']:.0f}px on stage at its last "
                       f"appearance — it vanishes, it does not fall off")
        d = (r['t1'] - r['t0']) / 1000
        if not (50.0 <= d <= 70.0):
            bad.append(f"print #{r['id']} crosses in {d:.1f}s — the fall is ~60 s, top to bottom")

    for r in rows:
        peak = max(abs(r['amin']), abs(r['amax']))
        if peak > 15.05:
            bad.append(f"print #{r['id']} reaches {peak:.1f}° — the arc is ±15° left and right, no more")
    tilts = {round((r['amin'] + r['amax']) / 2, 1) for r in rows}
    if len(rows) >= 3 and len(tilts) < min(len(rows), max(3, len(rows) // 3)):
        bad.append(f'only {len(tilts)} distinct tilts across {len(rows)} prints — the angle is not varying')

    rows_by_birth = sorted(rows, key=lambda r: r['id'])
    for r in rows_by_birth:
        if W / 3 < r['cx0'] < 2 * W / 3:
            bad.append(f"print #{r['id']} enters centred at {r['cx0']/W*100:.0f}% of the width — "
                       f"the middle third belongs to the card")
    sides = [0 if r['cx0'] < W / 2 else 1 for r in rows_by_birth]
    for k in range(1, len(sides)):
        if sides[k] == sides[k - 1]:
            bad.append(f"prints #{rows_by_birth[k-1]['id']} and #{rows_by_birth[k]['id']} fall on the "
                       f"same side back to back — the sides alternate")

    # the house opens with one print and fills; judge the bed once it is actually running
    steady = [n for (t, n) in conc if t > 68000]
    if steady and min(steady) < 2:
        bad.append(f'the bed thins to {min(steady)} print on stage — it should never go bare')
    return bad


# ---------- D-075 · the FaceTime video actually plays, on both casts ----------
def a_ft_video_plays(pg):
    """David, Sept 22, sending both casts' FaceTime recordings: song 7 IS the video. If it does not
    decode there is no song 7 — the number plays against a black rectangle and nobody finds out
    until the room is full.

    So this does not ask whether the <video> element exists, or whether the file is on disk, or
    whether the src looks right. Those all pass on a machine that cannot decode the file. It asks
    the only question that matters: is the picture MOVING? readyState past HAVE_CURRENT_DATA, a
    non-zero videoWidth, no MediaError, and currentTime further along after a wait than before it.

    Chromium ships without H.264, so an mp4-only show plays a black rectangle on a machine that
    looks identical to the one it was tested on. Both encodes are listed as <source> children,
    WebM first, and this proves the element picked one it can actually decode — whichever it is.

    Run for BOTH casts, because the two files are different files and only one of them is the one
    playing tonight."""
    bad = []
    pg.set_viewport_size({'width': W, 'height': H})
    if not pg.evaluate('typeof started !== "undefined" && started'):
        pg.evaluate("startAs('projection')")
        pg.wait_for_timeout(400)

    loc = pg.evaluate("""(()=>{ for(let s=0;s<SHOW.length;s++){
        const k=SHOW[s].cues.findIndex(c=>c.id==='7.2'); if(k>=0) return [s,k]; } return null; })()""")
    if not loc:
        return ['cue 7.2 is missing — song 7 has no connected FaceTime']

    for cast in ('ml', 'ac'):
        pg.evaluate(f"setCast('{cast}')")
        pg.wait_for_timeout(200)
        src = pg.evaluate("assetFor('V2')")
        if not src:
            bad.append(f'{cast.upper()}: V2 resolves to nothing — song 7 would play the greeked placeholder')
            continue
        parts = [x.strip() for x in str(src).split(',') if x.strip()]
        if not any(x.lower().endswith('.webm') for x in parts):
            bad.append(f'{cast.upper()}: V2 carries no WebM encode ({parts}) — a Chromium without '
                       f'H.264 plays a black rectangle')
        if parts and not parts[0].lower().endswith('.webm'):
            bad.append(f'{cast.upper()}: the first source is {parts[0]} — WebM must be listed first')

        pg.evaluate(f'si={loc[0]}; ci={loc[1]}; animTok++; animRunning=false; hardRender();')
        pg.wait_for_timeout(300)
        pg.evaluate('setTimeout(()=>advance(),0)')
        w = 0
        while w < 20000 and pg.evaluate('animRunning'):
            pg.wait_for_timeout(200); w += 200
        pg.wait_for_timeout(1200)

        v0 = pg.evaluate("""(()=>{ const v=document.querySelector('.media video'); if(!v) return null;
            return {ready:v.readyState, vw:v.videoWidth, vh:v.videoHeight,
                    err:v.error?v.error.code:0, t:v.currentTime, paused:v.paused,
                    cur:(v.currentSrc||'').split('/').pop(),
                    srcs:[...v.querySelectorAll('source')].map(s=>s.src.split('/').pop())}; })()""")
        if not v0:
            bad.append(f'{cast.upper()}: 7.2 renders no <video> at all — the FaceTime frame is empty')
            continue
        if v0['err']:
            bad.append(f"{cast.upper()}: the video reports MediaError {v0['err']} "
                       f"({'SRC_NOT_SUPPORTED — nothing in the source list decodes here' if v0['err'] == 4 else 'decode failed'})")
        if v0['vw'] < 1 or v0['ready'] < 2:
            bad.append(f"{cast.upper()}: no picture — videoWidth {v0['vw']}, readyState {v0['ready']} "
                       f"(needs 2+); sources offered {v0['srcs']}")
            continue
        pg.wait_for_timeout(1500)
        t1 = pg.evaluate("(()=>{ const v=document.querySelector('.media video'); return v?v.currentTime:-1; })()")
        if t1 <= v0['t'] + 0.25:
            bad.append(f"{cast.upper()}: the picture is frozen — currentTime {v0['t']:.2f}s then "
                       f"{t1:.2f}s after 1.5 s of wall clock (paused={v0['paused']})")

        # the composition: only Jamie, filling the frame, and the call duration ticking
        fr = pg.evaluate("""(()=>{ const v=document.querySelector('.media video'); if(!v) return null;
            const b=v.getBoundingClientRect(), m=v.parentElement.getBoundingClientRect();
            const tm=document.querySelector('.calltimer');
            return {vr:v.videoWidth/Math.max(1,v.videoHeight), fr:m.width/Math.max(1,m.height),
                    fill:(b.width*b.height)/Math.max(1,m.width*m.height),
                    timer: tm?tm.textContent.trim():null,
                    pip: !!document.querySelector('.ftpip')}; })()""")
        if fr:
            if fr['fill'] < 0.98:
                bad.append(f"{cast.upper()}: the video covers {fr['fill']*100:.0f}% of the FaceTime "
                           f"frame — black down the sides of a call")
            if fr['timer'] is None:
                bad.append(f'{cast.upper()}: the connected call shows no duration — the timer must tick')
    return bad


PROBES = [a_bed_falls, a_ft_video_plays]
