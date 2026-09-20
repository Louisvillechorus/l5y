"""Teleport auditor — no register may appear without navigation.
Run against book.json (produced by the Playwright extraction).
Exemptions (real phone behavior, not violations):
  - incoming calls take over any screen
  - FaceTime/calls launched from a Messages thread
  - Instagram request -> its own in-app thread
  - macOS app switching (dock / cmd-tab idiom)
  - device flips land in-app (the other person was already there)
"""
import json
import os
import sys


def _fresh_or_die():
    """A gate that grades a stale artifact is worse than no gate: it reports CLEAN on a show that
    no longer exists. book.json must be newer than the build it claims to describe."""
    try:
        b, k = os.path.getmtime('book.json'), os.path.getmtime('L5Y-Show-STANDALONE.html')
    except OSError as e:
        sys.exit('TELEPORT AUDIT: cannot run — %s' % e)
    if b < k:
        sys.exit('TELEPORT AUDIT: STALE — book.json predates the build. '
                 'Run: CHROMIUM_PATH=... python3 extract_book.py')


_fresh_or_die()
FAM={'thread':'msg','msglist':'msg','contact':'msg','mail':'mail','mailread':'mail',
 'fbpost':'fb','memories':'fb','photos':'ph','shot':'ph','call':'phone','vm':'phone',
 'facetime':'ft','ftrecents':'ft','settings2':'set','music':'mus','maps':'map','note':'nt',
 'findmy':'fm','calevent':'cal','reminders':'rem','search':'saf','backstage':'saf',
 'ember':'tin','igreq':'ig','pages':'pg','home':'home','lock':'lock','x':'x'}
book=json.load(open('book.json'))
viol=[]
for s in book['songs']:
    for c in s['cues']:
        ops=[o['op'] for o in c['do']]
        a,b=FAM.get(c['preApp'],c['preApp']),FAM.get(c['app'],c['app'])
        if a==b or b in ('lock','home') or 'black' in ops: continue
        if any(x in ops for x in ('openapp','notiftap','device','unlock')): continue
        if b=='phone' and any(o.get('op')=='call' and 'incoming' in (o.get('st') or '') for o in c['do']): continue
        if a=='msg' and b in ('phone','ft'): continue          # FaceTime/call from a thread
        if a=='phone' and b=='ft': continue                     # failed call connects as FaceTime
        if a=='ig' and b=='msg': continue                       # IG request -> IG thread
        if c['dev']=='macbook': continue                        # dock / cmd-tab idiom
        viol.append(f"{c['id']}: {c['preApp']} -> {c['app']} un-navigated")
print('TELEPORT AUDIT:', viol if viol else 'CLEAN')
raise SystemExit(1 if viol else 0)
