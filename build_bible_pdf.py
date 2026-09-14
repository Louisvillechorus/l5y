"""Render bible.json to L5Y-Cue-Bible.pdf via headless Chromium.
Run after build_bible_data.py. (The DOCX renderer is build_bible_docx.js;
both read the same bible.json, so the two documents cannot drift apart.)
Usage: python3 build_bible_pdf.py
"""
import html
import json
import os

from playwright.sync_api import sync_playwright

B = json.load(open('bible.json'))
e = html.escape

CSS = """
@page{size:letter;margin:20mm 17mm 18mm}
body{font-family:Georgia,serif;font-size:10.5pt;color:#1a1d26;margin:0}
.mono{font-family:'Courier New',monospace}
.title{ text-align:center;margin-top:2.2em}
.title .kicker{font-family:'Courier New',monospace;font-weight:700;color:#c2447a;font-size:10pt;letter-spacing:.12em}
.title h1{font-size:34pt;margin:.2em 0 .1em;font-weight:700}
.title .build{font-family:'Courier New',monospace;color:#6b7280;font-size:8.5pt}
.title .sub{color:#6b7280;font-style:italic;font-size:9.5pt;margin-top:.6em}
.rule{background:#f2ede2;padding:.7em .9em;margin:1.6em 0 .6em}
.howto{color:#6b7280;font-style:italic;font-size:9pt;margin-bottom:2em}
.song{page-break-before:always}
.song h2{font-size:19pt;margin:.2em 0 .2em}
.song h2 .meta{font-family:'Courier New',monospace;font-size:9pt;color:#c2447a;font-weight:700;margin-left:.8em}
.intro{background:#eef0f4;padding:.6em .8em;margin-bottom:1.1em;font-size:9.5pt}
.cue{border-top:1px solid #d8d2c2;padding-top:.55em;margin-top:1em;page-break-inside:avoid}
.cue .id{font-family:'Courier New',monospace;font-weight:700;font-size:11pt}
.cue .where{font-family:'Courier New',monospace;font-size:8.5pt;color:#2a5db0;margin-left:.6em}
.cue .trig{font-style:italic;margin-left:.6em}
.what{color:#3a3f4d;margin:.25em 0 .35em;font-size:9.8pt}
.lbl{font-family:'Courier New',monospace;font-size:8pt;font-weight:700;color:#6b7280;letter-spacing:.08em;margin-top:.45em}
.on{font-family:'Courier New',monospace;font-size:9pt;margin-left:1.4em;line-height:1.45}
.on b{font-weight:700}
.plays{margin-left:1.4em;color:#3a3f4d;font-size:9.5pt;line-height:1.4}
.sound{margin-left:1.4em;color:#6a5a20;font-size:9.5pt}
.phones{font-family:'Courier New',monospace;font-size:8.5pt;color:#6b7280;margin-top:.4em}
.gold{background:#faf3dc;color:#8a6d10;padding:.35em .6em;margin-top:.45em;font-size:9.5pt;font-style:italic}
.gold b{font-family:'Courier New',monospace;font-style:normal;font-size:8.5pt}
"""

out = ['<!doctype html><meta charset="utf-8"><style>%s</style>' % CSS]
total = sum(s['fires'] for s in B['songs'])
out.append(f"""<div class="title">
 <div class="kicker">THE LAST FIVE YEARS · THE SECOND SCREEN</div>
 <h1>The Cue Bible</h1>
 <div class="build">{e(B['build'])}</div>
 <div class="sub">{total} cues · {len(B['songs'])} songs · generated from the live show build,
 so this document cannot drift from what the phones actually do</div></div>
<div class="rule"><b>THE STANDING RULE: the phone behaves exactly like a real phone.</b>
 Tapping a notification IS the unlock — the app opens directly, no home screen. Inboxes and
 message lists load whole the instant the app opens, and a full life continues past the bottom
 edge of the glass. Only what would genuinely arrive right now — a text, a notification, new
 mail — appears live, and new mail lands at the top. Anything that violates this is a bug,
 even if it would make a nice theatrical beat.</div>
<div class="howto">How to read each entry: the header gives the cue ID, which screen, whose
 phone, the app, and the musical anchor. ON SCREEN is the complete content, verbatim and
 untruncated. PLAYS covers mechanics the engine performs on its own — navigation, self-timed
 animation, synthesized sound. PHONES gives the state after the cue when it changed. Gold
 notes carry dramaturgy, holds, and open director choices.</div>""")

for s in B['songs']:
    sings = 'BOTH SING' if s['who'] == 'both' else ('CATHY SINGS' if s['who'] == 'cathy' else 'JAMIE SINGS')
    out.append(f'<div class="song"><h2>{s["n"]} · {e(s["t"])}'
               f'<span class="meta">{sings} · {s["fires"]} FIRES</span></h2>')
    if s.get('intro'):
        out.append(f'<div class="intro">{e(s["intro"])}</div>')
    prev_app = prev_stamp = None
    for c in s['cues']:
        where = f'{c["screen"]} · {c["who"]}' + ('' if c['black'] else ' · ' + e(c['app']))
        out.append(f'<div class="cue"><span class="id">{c["id"]}</span>'
                   f'<span class="where">{where}</span>'
                   f'<span class="trig">— {e(c["trig"])}</span>')
        if c['what']:
            out.append(f'<div class="what">{e(c["what"])}</div>')
        if c['content']:
            out.append('<div class="lbl">ON SCREEN</div>')
            for pre, txt in c['content']:
                out.append(f'<div class="on"><b>{e(pre)}</b>{e(txt)}</div>')
        if c['plays']:
            out.append('<div class="lbl">PLAYS</div>')
            for p in c['plays']:
                out.append(f'<div class="plays">{e(p)}</div>')
        if c.get('sound'):
            out.append('<div class="lbl">SOUND</div>')
            for p in c['sound']:
                out.append(f'<div class="sound">{e(p)}</div>')
        if not c['black'] and (c['app'] != prev_app or c['stamp'] != prev_stamp):
            ph = f'{c["screen"]} = {e(c["app"])}'
            if c['stamp']: ph += f' · stamp “{e(c["stamp"])}”'
            if c['clock']: ph += f' · clock {e(c["clock"])}'
            out.append(f'<div class="phones">PHONES&nbsp;&nbsp;{ph}</div>')
        prev_app, prev_stamp = c['app'], c['stamp']
        if c.get('hold'):
            out.append(f'<div class="gold"><b>HOLD ·</b> {e(c["hold"])}</div>')
        if c.get('cut'):
            out.append(f'<div class="gold"><b>CUTAWAY ·</b> {e(c["cut"])}</div>')
        out.append('</div>')
    out.append('</div>')

open('_bible_print.html', 'w').write('\n'.join(out))
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or None)
    pg = b.new_page()
    pg.goto('file://' + os.path.abspath('_bible_print.html'))
    pg.wait_for_timeout(300)
    pg.pdf(path='L5Y-Cue-Bible.pdf', format='Letter', print_background=True,
           display_header_footer=True,
           header_template='<div style="font-family:monospace;font-size:6.5pt;color:#6b7280;width:100%;text-align:right;padding-right:14mm">L5Y · THE SECOND SCREEN — CUE BIBLE</div>',
           footer_template='<div style="font-family:monospace;font-size:6.5pt;color:#6b7280;width:100%;text-align:center"><span class="pageNumber"></span></div>',
           margin={'top': '16mm', 'bottom': '14mm', 'left': '0', 'right': '0'})
    b.close()
os.remove('_bible_print.html')
print('L5Y-Cue-Bible.pdf written')
