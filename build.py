"""Rebuild pipeline: splice cues.js into index.html and emit the standalone.
Usage: python3 build.py   (then run QA: python3 qc_legibility.py, audit_teleports.py)"""
import re
eng=open('index.html').read(); cues=open('cues.js').read()
m=re.search(r'window\.L5Y_SHOW\s*=\s*(\[[\s\S]*\]);\s*$', cues.strip())
start=eng.index('const FALLBACK_SHOW = '); end=eng.index('let SHOW = (typeof window')
eng = eng[:start] + 'const FALLBACK_SHOW = ' + m.group(1) + ';\n' + eng[end:]
open('index.html','w').write(eng)
open('L5Y-Show-STANDALONE.html','w').write(eng.replace('<script src="cues.js"></script>','<script>\n'+cues+'\n</script>'))
open('docs/index.html','w').write(open('L5Y-Show-STANDALONE.html').read())
print('built: index.html, L5Y-Show-STANDALONE.html, docs/index.html')
