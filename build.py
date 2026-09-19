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
# THE TYPE IS THE SHOW (David, Sept 19 night): the fonts are embedded, so the projection machine
# never waits on — or goes without — theatre Wi-Fi. Re-run fetch_fonts.py only when a face changes.
faces=[]
for f in sorted(glob.glob('assets/fonts/*.woff2')):
    fam,wt,sty=os.path.basename(f)[:-6].split('-')
    fam={'CourierPrime':'Courier Prime'}.get(fam,fam)
    faces.append("@font-face{font-family:'%s';font-style:%s;font-weight:%s;font-display:block;src:url(data:font/woff2;base64,%s) format('woff2')}"
                 %(fam,sty,wt.replace('_',' '),base64.b64encode(open(f,'rb').read()).decode()))
fontcss='<style id="l5yfonts">'+''.join(faces)+'</style>'
assets='<script id="l5yassets">window.L5Y_SFX=%s;window.L5Y_PAPER=%s;</script>'%(json.dumps(sfx),json.dumps(paper))
out=eng.replace('<script src="cues.js"></script>',assets+'\n<script>\n'+cues+'\n</script>')
out=out.replace('</head>', fontcss+'\n</head>', 1)
open('L5Y-Show-STANDALONE.html','w').write(out)
print('embedded fonts:',len(faces))
print('embedded sounds:',len(sfx),'paper scans:',len(paper))
open('docs/index.html','w').write(open('L5Y-Show-STANDALONE.html').read())
print('built: index.html, L5Y-Show-STANDALONE.html, docs/index.html')
