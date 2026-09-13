"""Apply corrected trigger lines to cues.js — the one-pass fix after the team
checks every cue line against the licensed script.

Input: a JSON file mapping cue id -> the real line, e.g.
    {"1.5": "the actual line from the script", "3.14": "..."}
(only include cues that need correcting; everything else is left alone)

Usage:
    python3 apply_lines.py corrections.json
    python3 build.py          # then rebuild + regenerate documents

Never fills gaps from memory: this tool only writes lines a human sourced
from the script.
"""
import json
import re
import sys

corrections = json.load(open(sys.argv[1]))
src = open('cues.js', encoding='utf8').read()

applied, missing = [], []
for cid, line in corrections.items():
    line = line.strip()
    if not line:
        continue
    # locate this cue's trig:'...' (id appears once; trig follows on the same object)
    pat = re.compile(r"(\{id:'%s',kind:'[a-z]+',trig:')((?:[^'\\]|\\.)*)(')" % re.escape(cid))
    esc = line.replace('\\', '\\\\').replace("'", "\\'")
    new, n = pat.subn(lambda m: m.group(1) + esc + m.group(3), src)
    if n == 1:
        src = new
        applied.append(cid)
    else:
        missing.append(cid)

open('cues.js', 'w', encoding='utf8').write(src)
print('applied: %d cue lines' % len(applied))
if missing:
    print('NOT FOUND (fix by hand): %s' % ', '.join(missing))
print('next: python3 build.py  ·  re-run QA  ·  regenerate the documents')
