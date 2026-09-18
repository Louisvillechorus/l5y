"""LIVE-PATH INTEGRITY QC
The operator's GO fires advance() — the animated path — not hardRender().
Live register swaps mutate the persistent shell in place, so this walks the
ENTIRE show exactly like the operator (advance, wait for the animation to
finish) and asserts after every cue that the shell chrome (status-bar
background, edge mode) and the close-up reading window match the settled
truth for CUR. Catches everything the settled-render sweeps cannot see.
Usage: CHROMIUM_PATH=... python3 qc_livepath.py
"""
import os
import sys

from playwright.sync_api import sync_playwright

FILE = 'file://' + os.path.abspath('L5Y-Show-STANDALONE.html')

CHECK = """(() => {
  const st=CUR; const out=[];
  const pj=document.getElementById('projDevice');
  if(st.black || (si===0&&ci===0)) return out;
  const dev=pj && pj.querySelector('.iphone,.ipad');
  if(dev){
    const want=shellChrome(st);
    const chrome=dev.style.getPropertyValue('--chrome').trim();
    if(chrome!==want.bg) out.push(`chrome ${chrome} != ${want.bg}`);
    const scr=dev.querySelector('.screen');
    if(scr && scr.classList.contains('edge')!==want.dark) out.push('edge mismatch');
  }
  const mac=pj && pj.querySelector('.macbook');
  if(mac){
    const mb=mac.querySelector('.menubar b');
    if(mb && mb.textContent!==mbMenuFor(st)) out.push(`mac menu ${mb.textContent} != ${mbMenuFor(st)}`);
  }
  if(st.dev==='iphone'){
    const fr = autoFrame(st);   // the engine's own framing truth (whole phone unless a cue asks for a close-up)
    const hasMask=pj.classList.contains('mask');
    if(!!fr!==hasMask) out.push(`mask ${hasMask} but frame ${!!fr} for app ${st.app}`);
  }
  return out;
})()"""


def run():
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or None)
        pg = b.new_page(viewport={'width': 1920, 'height': 1080})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(FILE)
        pg.wait_for_timeout(800)
        pg.evaluate('startAs("projection")')
        bad = []
        for si in range(pg.evaluate('SHOW.length')):
            pg.evaluate(f'si={si}; ci=0; animTok++; animRunning=false; hardRender();')
            pg.wait_for_timeout(100)
            for k in range(pg.evaluate(f'SHOW[{si}].cues.length')):
                pg.evaluate('advance()')
                for _ in range(80):
                    pg.wait_for_timeout(120)
                    if not pg.evaluate('animRunning'):
                        break
                cid = pg.evaluate(f'SHOW[{si}].cues[{k}].id')
                for pr in pg.evaluate(CHECK):
                    bad.append(f'{cid}: {pr}')
        b.close()
    return bad, errs


if __name__ == '__main__':
    bad, errs = run()
    if errs:
        print('JS ERRORS:', errs[:3])
    print('LIVE-PATH INTEGRITY:', 'CLEAN' if not bad else '\n'.join(bad[:20]))
    sys.exit(1 if (bad or errs) else 0)
