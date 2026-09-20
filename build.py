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
img={}
for f in sorted(glob.glob('assets/img/*')):
    ext=f.lower().rsplit('.',1)[-1]
    if ext in ('png','jpg','jpeg','webp','svg'):
        mt={'jpg':'jpeg','svg':'svg+xml'}.get(ext,ext)
        img[os.path.basename(f).rsplit('.',1)[0]]='data:image/%s;base64,%s'%(mt,base64.b64encode(open(f,'rb').read()).decode())
# THE PHOTO BED: the preshow/intermission prints. Stills are downscaled hard (they render ~25% of
# stage height, so 720 px tall is already generous) and Live Photos ride along as short muted clips.
loop={'ml':[],'ac':[]}
try:
    from PIL import Image
    _HAVE_PIL=True
except Exception:
    _HAVE_PIL=False
import io
for f in sorted(glob.glob('assets/loop/*')):
    base=os.path.basename(f); stem,ext=os.path.splitext(base); ext=ext.lower().lstrip('.')
    up=stem.upper()
    casts=['ml','ac'] if up.endswith('-SHARED') else (['ml'] if up.endswith('-ML') else (['ac'] if up.endswith('-AC') else []))
    if not casts: continue
    if ext in ('jpg','jpeg','png','webp'):
        if _HAVE_PIL:
            im=Image.open(f).convert('RGB'); w,h=im.size
            if h>720: im=im.resize((max(1,round(w*720/h)),720), Image.LANCZOS)
            buf=io.BytesIO(); im.save(buf,'JPEG',quality=72,optimize=True)
            data='data:image/jpeg;base64,'+base64.b64encode(buf.getvalue()).decode(); w,h=im.size
        else:
            data='data:image/%s;base64,%s'%('jpeg' if ext in ('jpg','jpeg') else ext, base64.b64encode(open(f,'rb').read()).decode()); w,h=(4,3)
        ent={'k':'img','s':data,'r':round(w/h,3)}
    elif ext in ('mp4','m4v','mov','webm'):
        mt={'mov':'quicktime','m4v':'mp4'}.get(ext,ext)
        ent={'k':'vid','s':'data:video/%s;base64,%s'%(mt,base64.b64encode(open(f,'rb').read()).decode()),'r':1.333}
    else:
        continue
    for c in casts: loop[c].append(ent)
loopbytes=sum(len(e['s']) for c in loop for e in loop[c])
assets='<script id="l5yassets">window.L5Y_SFX=%s;window.L5Y_PAPER=%s;window.L5Y_IMG=%s;window.L5Y_LOOP=%s;</script>'%(json.dumps(sfx),json.dumps(paper),json.dumps(img),json.dumps(loop))
out=eng.replace('<script src="cues.js"></script>',assets+'\n<script>\n'+cues+'\n</script>')
out=out.replace('</head>', fontcss+'\n</head>', 1)
open('L5Y-Show-STANDALONE.html','w').write(out)
print('embedded fonts:',len(faces))
print('embedded sounds:',len(sfx),'paper scans:',len(paper),'images:',len(img),'| photo bed: %d ML / %d AC (%.1f MB)'%(len(loop['ml']),len(loop['ac']),loopbytes/1.4e6))
open('docs/index.html','w').write(open('L5Y-Show-STANDALONE.html').read())
print('built: index.html, L5Y-Show-STANDALONE.html, docs/index.html')
