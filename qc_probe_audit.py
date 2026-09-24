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
import qc_notes_era as E
import qc_notes_subject as S

FILE = 'file://' + os.path.abspath('L5Y-Show-STANDALONE.html')

# The two era probes that sweep all 68 cues are minutes each. The audit only has to prove the
# probe NOTICES a broken stage, and one broken cue proves that as well as sixty-nine do, so it
# runs them over song 1 alone — which docks the phone (1.2) and swaps a house page (1.0a), the
# two things they watch. `SHOW` is a top-level `let`, so it is assigned, never set on window.
SONG1 = "SHOW = SHOW.slice(0,1); "

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
              # stubbing window.fitPad does NOT work — setStamp calls it by its lexical name, so the
              # stub is never reached. An !important rule beats the inline size fitPad writes.
              "(()=>{const s=document.createElement('style');"
              "s.textContent='#era .pad.house.perf .fl{font-size:9vh !important}';"
              "document.head.appendChild(s);})()",
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

    # ---- the calendar (qc_notes_era). Every one of these breaks the artifact itself, at
    # runtime, and the probe has to say so. An !important rule beats the inline styles
    # fitPad/setEraHome write; the function overrides work because index.html is a classic
    # script, so its top-level `function` declarations ARE properties of window.
    'D-010': (E.a_era_morph,
              "window.ERA_PARTS_=()=>[]",
              'stopped every piece of type being carried between the two homes'),
    'D-011': (E.a_cards_fall,
              "(()=>{const s=document.createElement('style');"
              "s.textContent='#era .pad.cardin{animation:none !important}"
              "#era .pad.ghost.cardout{animation:none !important}';"
              "document.head.appendChild(s);})()",
              'took gravity off the house cards so they swap in place'),
    'D-012': (E.a_title_fills,
              "(()=>{const s=document.createElement('style');"
              "s.textContent='#era .pad.house .sheet{left:0 !important;right:0 !important}';"
              "document.head.appendChild(s);})()",
              'squeezed the house pages back into the square date card'),
    'D-013': (E.a_typed_foot,
              "window.typeFoot=async function(){}",
              'made the scene name appear whole instead of typing itself'),
    'D-014': (E.a_92_no_inter_flash,
              "(()=>{const r=padGhost; window.padGhost=function(era){const g=r(era);"
              "if(g) g.classList.remove('inter','house','title','perf','next5'); return g;};})()",
              'let the tearing page drop its face, so INTERMISSION snaps into the square frame'),
    'D-036': (E.a_era_never_overlays,
              SONG1 + "(()=>{const s=document.createElement('style');"
              "s.textContent='#era.docked{margin-right:40vw !important}';"
              "document.head.appendChild(s);})()",
              'slid the docked calendar strip across the phone'),
    # …in an IIFE, so the statement's value is undefined. page.evaluate() CALLS a string whose
    # value is a function, and `window.x = function(a,b,c){…}` evaluates to that function — it
    # would be invoked here with no arguments and throw before the probe ever ran.
    'D-047': (E.a_no_stray_pages,
              SONG1 + "(()=>{window.padFall=function(era,pad,ghost){"
              "ghost.classList.add('cardout'); pad.classList.add('cardin');};})()",
              'stopped the outgoing house page ever being removed from the stage'),
}


def run():
    # --only D-010,D-011 audits one family in minutes instead of the whole hour. Like the gate's
    # own --only it is a working tool, not a shipping run: only the full audit clears the file.
    only = set()
    if '--only' in sys.argv:
        i = sys.argv.index('--only')
        if i + 1 < len(sys.argv):
            only = {x.strip().upper() for x in sys.argv[i + 1].split(',') if x.strip()}
    fake, ok, broken = [], [], []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or None)
        ctx = b.new_context(viewport={'width': 1920, 'height': 1080})
        for nid, (probe, sabotage, what) in MUTATIONS.items():
            if only and nid.upper() not in only:
                continue
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
    print(f'\n{len(ok)} probes proved they can fail · {len(fake)} fake · {len(broken)} inconclusive'
          + ('   [PARTIAL — only ' + ','.join(sorted(only)) + ']' if only else ''))
    return 1 if (fake or broken) else 0


if __name__ == '__main__':
    sys.exit(run())
