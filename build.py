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
try:
    from PIL import Image
    _HAVE_PIL=True
except Exception:
    _HAVE_PIL=False
import io
# THE CAST PHOTOS (M/V codes). One build serves both couples: a cue references M2, never a file,
# and CAST_ASSETS resolves it per cast at runtime. Files are named <CODE>-ML / -AC / -SHARED.
cast={'ml':{},'ac':{}}
vids=[]
_VDIR='assets/cast/'   # where a sidecar video is referenced FROM (see the copy step at the foot)
for f in sorted(glob.glob('assets/cast/*')):
    base=os.path.basename(f); stem,ext=os.path.splitext(base); ext=ext.lower().lstrip('.')
    m=re.match(r'^([MV]\d+[a-z]?)-(ML|AC|SHARED)$', stem, re.I)
    if not m: continue
    code, who = m.group(1).upper().replace('A','a') if False else m.group(1), m.group(2).upper()
    if ext in ('jpg','jpeg','png','webp'):
        mt={'jpg':'jpeg'}.get(ext,ext)
        if _HAVE_PIL:
            im=Image.open(f).convert('RGB'); w,h=im.size
            if max(w,h)>1600:
                k=1600/max(w,h); im=im.resize((round(w*k),round(h*k)), Image.LANCZOS)
            buf=io.BytesIO(); im.save(buf,'JPEG',quality=82,optimize=True)
            data='data:image/jpeg;base64,'+base64.b64encode(buf.getvalue()).decode()
        else:
            data='data:image/%s;base64,%s'%(mt, base64.b64encode(open(f,'rb').read()).decode())
    elif ext in ('mp4','m4v','mov','webm'):
        # VIDEO IS A SIDECAR, NEVER EMBEDDED. Base64 inflates by a third, and GitHub hard-rejects any
        # file over 100 MB: one 720p FaceTime for each cast would take docs/index.html from 18 MB to
        # well past that, so the team URL would simply stop existing. A sidecar also STREAMS - it
        # starts and seeks instead of being parsed as a hundred-megabyte string and held in memory.
        # The engine already plays a URL: swapMedia makes a <video> for any assetFor value ending
        # .mp4/.webm/.mov. The file is copied next to each build so a relative path resolves for the
        # hosted page and for the STANDALONE opened out of the repo; if it is missing, assetFor finds
        # nothing and the cue falls back to the greeked placeholder rather than breaking.
        # STORED TWICE, NOT THREE TIMES. The path has to resolve from the repo root (the STANDALONE)
        # and from docs/ (Pages serves that folder AS the root), and docs/index.html is a byte copy of
        # the STANDALONE, so both read the same string. Pointing it at assets/cast -- where the file
        # ALREADY lives, in git, as the source of truth -- means the root build needs no copy at all
        # and only docs takes one. At ~16 MB an encode, two casts and two encodes each, the copy this
        # removes was 60-odd MB of duplicated binary in a repo whose .git is already 682 MB.
        data=_VDIR+base
        vids.append(f)
        # more than one encode of the same code? list them all, webm first (see swapMedia)
        # ONE PREFIX, ONE PLACE. This test used to carry its own copy of the directory literal, so
        # moving the video out of assets/video silently stopped the merge from matching: the two
        # encodes no longer joined, the later filename just overwrote the earlier, and the build
        # printed both files as sidecars while shipping only one source. A path spelled twice is a
        # path that will disagree with itself.
        prev=cast.get(who.lower(),{}).get(code) if who!='SHARED' else cast['ml'].get(code)
        if prev and prev.startswith(_VDIR):
            parts=[x for x in prev.split(',') if x]
            parts.append(data)
            parts.sort(key=lambda u: 0 if u.endswith('.webm') else 1)
            data=','.join(dict.fromkeys(parts))
    else:
        continue
    for c in (['ml','ac'] if who=='SHARED' else [who.lower()]): cast[c][code]=data

img={}
for f in sorted(glob.glob('assets/img/*')):
    ext=f.lower().rsplit('.',1)[-1]
    if ext in ('png','jpg','jpeg','webp','svg'):
        mt={'jpg':'jpeg','svg':'svg+xml'}.get(ext,ext)
        img[os.path.basename(f).rsplit('.',1)[0]]='data:image/%s;base64,%s'%(mt,base64.b64encode(open(f,'rb').read()).decode())
# THE PHOTO BED: the preshow/intermission prints. Stills are downscaled hard (they render ~25% of
# stage height, so 720 px tall is already generous) and Live Photos ride along as short muted clips.
loop={'ml':[],'ac':[]}
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
# WHICH BUILD AM I LOOKING AT? A cached page and a live one are indistinguishable on a projector,
# and GitHub Pages serves docs/index.html with a ten-minute cache — so the operator (and the
# director) can be looking at yesterday's show while being told it is today's. The build stamps
# itself with the commit it was made from, and the presenter prints it behind an info button.
def _build_stamp():
    import subprocess as _sp
    def _git(*a):
        try: return _sp.run(['git',*a],capture_output=True,text=True,timeout=10).stdout.strip()
        except Exception: return ''
    sha = _git('rev-parse','--short','HEAD')
    iso = _git('log','-1','--format=%cI')
    sub = _git('log','-1','--format=%s')
    # the build's OWN output is always modified at this moment — that is not a dirty source tree.
    GEN = ('L5Y-Show-STANDALONE.html','docs/index.html','L5Y-Cue-Bible.docx','L5Y-Cue-Bible.pdf',
           'bible.json','book.json')
    dirty = any(l[3:].strip() not in GEN and not l[3:].strip().startswith('docs/assets/')
                for l in _git('status','--porcelain').splitlines() if l.strip())
    return {'sha':sha or 'unknown','iso':iso or '','subject':sub or '','dirty':dirty,
            'built':__import__('datetime').datetime.now(__import__('datetime').timezone.utc)
                      .isoformat(timespec='seconds')}
BUILD = _build_stamp()
print('build stamp:', BUILD['sha'], BUILD['iso'], '(dirty)' if BUILD['dirty'] else '')

assets='<script id="l5yassets">window.L5Y_SFX=%s;window.L5Y_PAPER=%s;window.L5Y_IMG=%s;window.L5Y_LOOP=%s;window.L5Y_CAST=%s;window.L5Y_BUILDINFO=%s;</script>'%(json.dumps(sfx),json.dumps(paper),json.dumps(img),json.dumps(loop),json.dumps(cast),json.dumps(BUILD))
out=eng.replace('<script src="cues.js"></script>',assets+'\n<script>\n'+cues+'\n</script>')
out=out.replace('</head>', fontcss+'\n</head>', 1)
open('L5Y-Show-STANDALONE.html','w').write(out)
print('cast assets:', {k:sorted(v) for k,v in cast.items()})
print('embedded fonts:',len(faces))
print('embedded sounds:',len(sfx),'paper scans:',len(paper),'images:',len(img),'| photo bed: %d ML / %d AC (%.1f MB)'%(len(loop['ml']),len(loop['ac']),loopbytes/1.4e6))
# A BUILD THAT EMITS A DEAD SHOW MUST NOT EXIT 0. `node --check cues.js` only ever covered the cues;
# a duplicate `const` inside the ENGINE is an early error that kills the whole script, so SHOW is never
# defined and every screen is blank — and the build still said "built" and went green. (Sept 21: one
# slipped through exactly this way and only the register caught it, a gate run later.) Parse every
# inline script the same way the browser will, and fail loudly.
import subprocess, tempfile
_scripts = re.findall(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', out, re.S)
for _i, _js in enumerate(_scripts):
    if not _js.strip():
        continue
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as _f:
        _f.write(_js); _tmp=_f.name
    _r = subprocess.run(['node','--check',_tmp], capture_output=True, text=True)
    os.unlink(_tmp)
    if _r.returncode:
        first = (_r.stderr.strip().splitlines() or ['?'])
        raise SystemExit('BUILD REFUSED — inline script #%d does not parse, the show would be blank:\n  %s'
                         % (_i, '\n  '.join(first[:6])))
print('engine parses: %d inline scripts' % len([x for x in _scripts if x.strip()]))

# the sidecar videos travel with each build
import shutil
_VDST='docs/'+_VDIR.rstrip('/')
os.makedirs(_VDST, exist_ok=True)
for _v in vids:
    _t=os.path.join(_VDST, os.path.basename(_v))
    if os.path.abspath(_t)!=os.path.abspath(_v) and (not os.path.exists(_t) or os.path.getmtime(_v)>os.path.getmtime(_t)):
        shutil.copy2(_v,_t)
print('sidecar video:', [os.path.basename(v) for v in vids] or 'none')

open('docs/index.html','w').write(open('L5Y-Show-STANDALONE.html').read())
print('built: index.html, L5Y-Show-STANDALONE.html, docs/index.html')
