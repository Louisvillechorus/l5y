"""
LEGIBILITY QC
Walks every cue of every song in the projection view and reports:
  CLIP     – an element whose content is cut off (scrollHeight/Width > client)
  TINY     – text below the readable floor for a 10-foot projection
  EMPTY    – a screen that rendered nothing
It renders at the real projection aspect so the numbers mean something.
"""
from playwright.sync_api import sync_playwright
import os
import sys

FILE = 'file://' + os.path.abspath('L5Y-Show-STANDALONE.html')
# a phone on a 10ft-tall projection: text under ~1.1% of screen height is unreadable at 50ft
MIN_PX_AT_880 = 9.0

CHECK_JS = r"""() => {
  const root = document.querySelector('#projDevice');
  if(!root) return {empty:true, clips:[], tiny:[]};
  const screen = root.querySelector('.screen, .mb-screen');
  if(!screen) return {empty:true, clips:[], tiny:[]};
  const clips=[], tiny=[]; const MINPX=%f;
  const H = screen.getBoundingClientRect().height;
  root.querySelectorAll('*').forEach(el=>{
    const cs=getComputedStyle(el);
    if(cs.display==='none'||cs.visibility==='hidden'||+cs.opacity===0) return;
    // deliberately collapsed (keyboard / predictive bar tucked away) is not a clip
    if(el.clientHeight<4) return;
    const r=el.getBoundingClientRect();
    if(r.height<1||r.width<1) return;
    // content clipped by its own box
    const oy=cs.overflowY, ox=cs.overflowX;
    if((oy==='hidden'||ox==='hidden')){
      const vy = el.scrollHeight - el.clientHeight;
      const vx = el.scrollWidth  - el.clientWidth;
      if(vy>6 && el.className && !/memfeed|thread|grid|nstack|mailrows|screenstack|hgrid|kbd|predict|fbfeed|screenstack|deck|layer|mailwrap|mailbody|msglist2/.test(el.className))
        clips.push({cls:String(el.className).slice(0,40), by:Math.round(vy), axis:'y',
                    txt:(el.textContent||'').trim().slice(0,42)});
      if(vx>4 && el.className && !/memfeed|thread|grid|screenstack|deck|layer|fbfeed|mailwrap|mailbody|msglist2/.test(el.className))
        clips.push({cls:String(el.className).slice(0,40), by:Math.round(vx), axis:'x',
                    txt:(el.textContent||'').trim().slice(0,42)});
    }
    // readable text floor — ignore chrome the audience never actually reads
    var cn = String(el.className||'');
    var isChrome = /(^|\s)(ml|wallnote|key|mcount|yr|nw|pt|rcpt|tstamp|sb-r)(\s|$)/.test(cn)
                   || /media|kbd|predict|statusbar|dock|happ|mailwrap|mailbody|msglist2|hlbl|searchpill/.test(cn);
    var kids=[].slice.call(el.childNodes).some(function(n){
      return n.nodeType===3 && n.textContent.trim().length>1; });
    if(kids && !isChrome){
      var fs=parseFloat(cs.fontSize);
      if(fs>0 && fs < MINPX) tiny.push({cls:cn.slice(0,30), px:+fs.toFixed(1),
                                        txt:(el.textContent||'').trim().slice(0,42)});
    }
  });
  // THE CHECK THAT MATTERS: in any scrolling feed, the newest item must be visible.
  const offscreen=[];
  [['.fbfeed','.post'],['.memfeed','.memscreen'],['.thread','.bub'],['.grid','.thumb']].forEach(function(pair){
    const feed=root.querySelector(pair[0]); if(!feed) return;
    const items=feed.querySelectorAll(pair[1]); if(!items.length) return;
    const last=items[items.length-1];
    const fb=feed.getBoundingClientRect(), lb=last.getBoundingClientRect();
    const visible = lb.top < fb.bottom-4 && lb.bottom > fb.top+4;
    if(!visible) offscreen.push({feed:pair[0], n:items.length,
                                 txt:(last.textContent||'').trim().slice(0,44)});
  });
  [['.mailwrap','.mrow2'],['.msglist2','.mrow2']].forEach(function(pair){
    const feed=root.querySelector(pair[0]); if(!feed) return;
    const items=feed.querySelectorAll(pair[1]); if(!items.length) return;
    const first=items[0];
    const fb=feed.getBoundingClientRect(), ib=first.getBoundingClientRect();
    const visible = ib.top >= fb.top-2 && ib.bottom <= fb.bottom+2;
    if(!visible) offscreen.push({feed:pair[0]+' (newest-first)', n:items.length,
                                 txt:(first.textContent||'').trim().slice(0,44)});
  });
  const painted = (root.textContent||'').trim().length>0;
  return {empty:!painted, clips, tiny, offscreen};
}""" % MIN_PX_AT_880


def run():
    # optional WxH arg runs the walk at another projection aspect, e.g. the
    # vertical TV: python3 qc_legibility.py 1080x1920 (device layout renders at
    # the same reference scale under the portrait transform, so MIN_PX holds)
    vp = (1500, 880)
    if len(sys.argv) > 1 and 'x' in sys.argv[1]:
        vp = tuple(int(v) for v in sys.argv[1].split('x'))
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or None)
        pg = b.new_page(viewport={'width': vp[0], 'height': vp[1]})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(FILE); pg.wait_for_timeout(800)
        pg.click('text=Start — Projection only'); pg.wait_for_timeout(300)

        nsongs = pg.evaluate('SHOW.length')
        problems = []
        for si in range(nsongs):
            n = pg.evaluate(f'SHOW[{si}].cues.length')
            for ci in range(n):
                cue = pg.evaluate(f'SHOW[{si}].cues[{ci}].id')
                # land on the settled state of this cue (no animation)
                pg.evaluate(f'si={si}; ci={ci+1}; animTok++; animRunning=false; hardRender();')
                pg.wait_for_timeout(70)
                r = pg.evaluate(CHECK_JS)
                black = pg.evaluate('CUR.black')
                if black:
                    continue
                if r['empty']:
                    problems.append((si+1, cue, 'EMPTY', 'nothing rendered'))
                for o in r.get('offscreen', []):
                    problems.append((si+1, cue, 'HIDDEN',
                                     f"newest item in {o['feed']} is off screen ({o['n']} items) — “{o['txt']}”"))
                for c in r['clips']:
                    problems.append((si+1, cue, 'CLIP',
                                     f"{c['cls']} cut {c['by']}px [{c['axis']}] — “{c['txt']}”"))
                seen = set()
                for t in r['tiny']:
                    k = (t['cls'], t['px'])
                    if k in seen: continue
                    seen.add(k)
                    problems.append((si+1, cue, 'TINY',
                                     f"{t['px']}px  {t['cls']} — “{t['txt']}”"))
        b.close()
        return problems, errs


if __name__ == '__main__':
    probs, errs = run()
    if errs:
        print('JS ERRORS:', errs[:3])
    if not probs:
        print('LEGIBILITY QC: CLEAN — no clipped, empty, or unreadable content in any cue.')
        sys.exit(0)
    print(f'LEGIBILITY QC: {len(probs)} issue(s)\n')
    print(f"{'SONG':>4} {'CUE':<7} {'KIND':<6} DETAIL")
    for s, c, k, d in probs[:80]:
        print(f'{s:>4} {c:<7} {k:<6} {d}')
    if len(probs) > 80:
        print(f'… and {len(probs)-80} more')
