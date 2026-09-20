"""QA ON THE QA (David, Sept 20).

A probe that cannot fail proves nothing. For each note, this breaks the thing the probe
claims to watch — at runtime, in the page — and asserts the probe NOTICES. A probe that
still passes while its subject is sabotaged is a fake probe and is reported as such.

Usage: CHROMIUM_PATH=/opt/pw-browsers/chromium python3 qc_probe_audit.py
"""
import os
import sys

from playwright.sync_api import sync_playwright

import qc_notes_core as C
import qc_notes_subject as S

FILE = 'file://' + os.path.abspath('L5Y-Show-STANDALONE.html')

# note id -> (probe, sabotage JS, what we broke)
MUTATIONS = {
    'D-015': (C.a_no_lowbat,
              "window.SFX_KEEP_=(()=>{const r=SFX_KEEP_; return ()=>Object.assign(r(),{lowbat:1});})()",
              'put the low-battery chime back'),
    'D-018': (C.a_unlock_audible,
              "window.SFX_KEEP_=(()=>{const r=SFX_KEEP_; return ()=>{const o=r(); delete o.unlock; return o;};})()",
              'silenced the unlock'),
    'D-023': (C.a_jump_panel,
              "document.getElementById('btnMenu').onclick=()=>{}",
              'made the Menu button a dead end again'),
    'D-025': (C.a_perf_fill,
              "window.fitPad=()=>{}",
              'stopped the performer name filling the sheet'),
    'D-031': (C.a_foot_solo,
              "window.footSolo=()=>{}",
              'stopped the divider hiding when there is no event'),
    'D-035': (C.a_photo_bed,
              "window.PILE_CFG=()=>({h:40, every:[9000,12000], fall:[20000,26000]})",
              'made the prints huge and rare'),
    'D-037': (C.a_one_receipt,
              "(()=>{const r=Element.prototype.querySelectorAll;"
              "Element.prototype.querySelectorAll=function(s){"
              "  return s==='.rcpt' ? [] : r.call(this,s); };})()",
              'stopped the send handler clearing stale receipts'),
    'D-038': (C.a_laptop_legible,
              "document.getElementById('l5ycss')||(()=>{const s=document.createElement('style');"
              "s.textContent='.mb-screen .fs{font-size:13.5px !important}.menubar{font-size:12px !important}';"
              "document.head.appendChild(s);})()",
              'put the laptop back to hardcoded 13.5px type'),
    'D-041': (C.a_timer_format,
              "window.fmtDur=(s)=>String(Math.floor(s/60)).padStart(2,'0')+':'+String(s%60).padStart(2,'0')",
              'made the call timer pad the minutes again'),
    'D-046': (C.a_call_buttons_match,
              "(()=>{const r=callHTML; window.callHTML=(st)=>r(Object.assign({},st,"
              "{call:Object.assign({},st.call||{},{st:'incoming call'})}));})()",
              'made every call render the Answer/Decline pair'),
    'D-048': (S.a_subject_never_sliced,
              "(()=>{const r=camPush; window.camPush=function(sel,z,d,a,du,f,nf,pf){"
              "return r.call(this,sel,14,d,a,du,true,true,pf); };})()",
              'over-zoomed every camera push so subjects overflow'),
}


def run():
    fake, ok, broken = [], [], []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or None)
        ctx = b.new_context(viewport={'width': 1920, 'height': 1080})
        for nid, (probe, sabotage, what) in MUTATIONS.items():
            pg = ctx.new_page()
            pg.goto(FILE)
            pg.wait_for_timeout(700)
            try:
                pg.evaluate(sabotage)
            except Exception as e:
                broken.append(f'{nid}: the sabotage itself failed — {e}')
                pg.close()
                continue
            try:
                found = list(probe(pg))
            except Exception as e:
                found = [f'probe raised: {e}']        # a crash IS a detection
            pg.close()
            if found:
                ok.append((nid, what, found[0][:88]))
            else:
                fake.append((nid, what))
        b.close()
    for nid, what, first in ok:
        print(f'✓ {nid}  caught it — {what}\n      → {first}')
    for nid, what in fake:
        print(f'✗ {nid}  FAKE PROBE — I {what} and the gate still passed')
    for x in broken:
        print('· ' + x)
    print(f'\n{len(ok)} probes proved they can fail · {len(fake)} fake · {len(broken)} inconclusive')
    return 1 if (fake or broken) else 0


if __name__ == '__main__':
    sys.exit(run())
