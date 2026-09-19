"""Rebuild pipeline: splice cues.js into index.html and emit the standalone.
Usage: python3 build.py   (then run QA: python3 qc_legibility.py, audit_teleports.py)"""
import re
eng=open('index.html').read(); cues=open('cues.js').read()
m=re.search(r'window\.L5Y_SHOW\s*=\s*(\[[\s\S]*\]);\s*$', cues.strip())
start=eng.index('const FALLBACK_SHOW = '); end=eng.index('let SHOW = (typeof window')
eng = eng[:start] + 'const FALLBACK_SHOW = ' + m.group(1) + ';\n' + eng[end:]
open('index.html','w').write(eng)
import glob,base64,json,os
sfx={}
for f in sorted(glob.glob('assets/sfx/*')):
    if f.lower().endswith(('.caf','.m4r','.m4a','.mp3','.wav','.aif','.aiff')):
        sfx[os.path.basename(f)]=base64.b64encode(open(f,'rb').read()).decode()
paper=[]
for f in sorted(glob.glob('assets/paper/*')):
    ext=f.lower().rsplit('.',1)[-1]
    if ext in ('jpg','jpeg','png','webp'):
        paper.append('data:image/%s;base64,%s'%('jpeg' if ext in ('jpg','jpeg') else ext, base64.b64encode(open(f,'rb').read()).decode()))
assets='<script id="l5yassets">window.L5Y_SFX=%s;window.L5Y_PAPER=%s;</script>'%(json.dumps(sfx),json.dumps(paper))
open('L5Y-Show-STANDALONE.html','w').write(eng.replace('<script src="cues.js"></script>',assets+'\n<script>\n'+cues+'\n</script>'))
print('embedded sounds:',len(sfx),'paper scans:',len(paper))
open('docs/index.html','w').write(open('L5Y-Show-STANDALONE.html').read())
print('built: index.html, L5Y-Show-STANDALONE.html, docs/index.html')
