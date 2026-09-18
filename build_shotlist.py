"""Render shotlist.json → SHOTLIST.md (the team's shot list + Drive naming rules).
Usage: python3 build_shotlist.py   (then node build_shotlist_docx.js for the DOCX)
"""
import json

S = json.load(open('shotlist.json'))
N = S['naming']
out = []
out.append('# L5Y — SHOT LIST & ASSET NAMING\n')
out.append('*Every photo/video/audio the show needs, what to shoot, and the exact filename to upload.*\n')
out.append('## How to name and upload\n')
out.append(f"- **Naming rule:** {N['rule']}")
out.append(f"- **Examples:** `{'`, `'.join(N['examples'])}`")
out.append(f"- **Photos:** {N['photos']}")
out.append(f"- **Video:** {N['video']}")
out.append(f"- **Audio:** {N['audio']}")
out.append(f"- **Where:** {N['folder']}\n")

def files_for(a):
    ext = {'photo': 'jpg', 'video': 'mp4', 'audio': 'm4a'}[a['kind']]
    if a['status'] == 'derived':
        return '— (I make this from M7)'
    if a['shared']:
        return f"`{a['code']}.{ext}`  (one file, both casts)"
    return f"`{a['code']}-ml.{ext}`  ·  `{a['code']}-ac.{ext}`"

for status, heading in [('confirmed', 'SHOOT NOW — confirmed for the locked build'),
                        ('derived', 'DERIVED — nothing to shoot'),
                        ('pending', 'HOLD — depends on the Song 10–14 answers')]:
    rows = [a for a in S['assets'] if a['status'] == status]
    if not rows:
        continue
    out.append(f'## {heading}\n')
    out.append('| Code | Upload as | What it is | Shoot this | Who | Era | Format | Appears in |')
    out.append('|---|---|---|---|---|---|---|---|')
    for a in rows:
        out.append(f"| **{a['code']}** | {files_for(a)} | {a['title']} | {a['shoot']} | {a['who']} | {a['era']} | {a['format']} | {a['appears']} |")
    out.append('')

open('SHOTLIST.md', 'w').write('\n'.join(out))
print('SHOTLIST.md written:', len(S['assets']), 'assets')
