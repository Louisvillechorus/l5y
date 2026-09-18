"""shotlist.json → L5Y-Shot-List.pdf (landscape, for the stage manager) via headless Chromium.
Usage: CHROMIUM_PATH=... python3 build_shotlist_pdf.py
"""
import html
import json
import os

from playwright.sync_api import sync_playwright

S = json.load(open('shotlist.json'))
e = html.escape
EXT = {'photo': 'jpg', 'video': 'mp4', 'audio': 'm4a'}


def fname(a, cast):
    return f"S{a['song']:02d}-{a['code']}-{a['slug']}-{cast}.{EXT[a['kind']]}"


def files(a):
    if a['status'] == 'derived':
        return '<span class="dim">— made from M7, nothing to upload</span>'
    if a['shared']:
        return f'<code>{e(fname(a, "SHARED"))}</code>'
    return f'<code>{e(fname(a, "ML"))}</code><br><code>{e(fname(a, "AC"))}</code>'


CSS = """
@page{size:letter landscape;margin:14mm 12mm}
body{font-family:Georgia,serif;font-size:9.5pt;color:#1a1d26;margin:0}
h1{font-size:24pt;margin:.1em 0 .1em}
.kick{font-family:'Courier New',monospace;font-weight:700;color:#c2447a;font-size:9pt;letter-spacing:.12em}
.sub{color:#6b7280;font-style:italic;margin-bottom:1em}
.rules{background:#f2ede2;padding:.6em .9em;margin-bottom:1.2em;font-size:9pt;line-height:1.45}
.rules b{font-family:'Courier New',monospace;color:#8a6d10}
code{font-family:'Courier New',monospace;font-size:8.6pt;color:#8a6d10;font-weight:700;white-space:nowrap}
h2{font-size:13pt;margin:1.1em 0 .4em;page-break-after:avoid}
table{border-collapse:collapse;width:100%;page-break-inside:auto}
tr{page-break-inside:avoid}
th{font-family:'Courier New',monospace;font-size:7.5pt;color:#6b7280;text-align:left;padding:5px 6px;border-bottom:1px solid #d8d2c2;letter-spacing:.06em}
td{padding:6px 6px;border-bottom:1px solid #eee;vertical-align:top;font-size:8.8pt;line-height:1.35}
td.code{font-family:'Courier New',monospace;font-weight:700;font-size:10pt}
td.what b{display:block;margin-bottom:2px}
.dim{color:#6b7280}
"""

out = [f'<!doctype html><meta charset="utf-8"><style>{CSS}</style>']
out.append('<div class="kick">THE LAST FIVE YEARS · THE SECOND SCREEN</div><h1>Shot List &amp; Asset Naming</h1>')
out.append('<div class="sub">Every photo, video and audio file the show needs — what to shoot, who is in it, and the exact filename to upload. Two casts: shoot each per-cast item twice, same composition.</div>')
N = S['naming']
out.append('<div class="rules">')
out.append(f'<b>NAMING RULE</b> — {e(N["rule"])}<br>')
out.append('<b>EXAMPLES</b> — ' + ' &nbsp;·&nbsp; '.join(f'<code>{e(x)}</code>' for x in N['examples']) + '<br>')
out.append(f'<b>PHOTOS</b> — {e(N["photos"])}<br><b>VIDEO</b> — {e(N["video"])}<br><b>WHERE</b> — {e(N["folder"])}')
out.append('</div>')

groups = [('confirmed', 'SHOOT NOW — confirmed for the locked build'),
          ('derived', 'DERIVED — nothing to shoot'),
          ('confirm', 'CONFIRM — waits on one Song 5 answer (party album)')]
for status, heading in groups:
    rows = [a for a in S['assets'] if a['status'] == status]
    if not rows:
        continue
    out.append(f'<h2>{e(heading)}</h2><table><tr><th>Code</th><th>Upload as (exact filename)</th><th>What it is / shoot this</th><th>Who</th><th>Era</th><th>Format</th><th>Appears in</th></tr>')
    for a in rows:
        out.append(f'<tr><td class="code">{e(a["code"])}</td><td>{files(a)}</td>'
                   f'<td class="what"><b>{e(a["title"])}</b>{e(a["shoot"])}</td>'
                   f'<td>{e(a["who"])}</td><td>{e(a["era"])}</td><td>{e(a["format"])}</td><td>{e(a["appears"])}</td></tr>')
    out.append('</table>')

open('_shotlist_print.html', 'w').write('\n'.join(out))
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or None)
    pg = b.new_page()
    pg.goto('file://' + os.path.abspath('_shotlist_print.html'))
    pg.wait_for_timeout(300)
    pg.pdf(path='L5Y-Shot-List.pdf', format='Letter', landscape=True, print_background=True,
           margin={'top': '12mm', 'bottom': '12mm', 'left': '10mm', 'right': '10mm'})
    b.close()
os.remove('_shotlist_print.html')
print('L5Y-Shot-List.pdf written')
