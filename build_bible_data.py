# Turn book.json (extracted from the live build) into structured Cue Bible entries.
import json, html

data=json.load(open('book.json'))
DEV={'iphone':'iPhone','ipad':'iPad','macbook':'MacBook'}
APPNAME={'lock':'Lock screen','home':'Home screen','msglist':'Messages','thread':'Messages',
 'mail':'Mail','mailread':'Mail — reading','memories':'Facebook Memories','fbpost':'Facebook',
 'cards':'System card','photos':'Photos','call':'Phone','facetime':'FaceTime','ember':'Ember',
 'pages':'Pages','search':'Search','focus':'Focus','standby':'Standby','off':'Screen off'}

SOUND_MAP=[('unlock','unlock swish'),('send','send whoosh'),('notif','notification tri-tone (soft)'),
 ('notiftap','tap thock'),('facetime','FaceTime trill, then connect pop'),('call','outgoing ring'),
 ('type','keyboard clicks (follow the projection rhythm)'),('wipe','rapid delete clicks'),
 ('vm','voicemail playback: her recorded VO, 0:47'),('match','match chime (Ember)'),('black','room tone out')]
def sound_for(ops):
    names=[o.get('op') for o in ops]
    out=[]; 
    for op,lbl in SOUND_MAP:
        if op in names and lbl not in out: out.append(lbl)
    return out

def onscreen(o):
    """The verbatim content a cue puts on the glass."""
    op=o['op']
    if op=='stamp': return [('STAMP → ', f"“{o['t']}”")]
    if op=='clock': return [('LOCK CLOCK — ', f"{o['t']}" + (f" · {o['d']}" if o.get('d') else ''))]
    if op=='notif':
        t=o.get('title'); head=o['app']+(f' · {t}' if t and t!=o['app'] else '')
        return [(f"NOTIFICATION — {head} ({o.get('w','now')}): ", f"“{o['t']}”")]
    if op=='mem':
        L=[('MEMORY CARD — ', f"{o['yr']} — {o['who']} · {o['when']}"),
           ('  post: ', f"“{o['txt']}”")]
        if o.get('media'): L.append(('  media: ', o['media']))
        L.append(('  reactions: ', f"👍 {o.get('likes',0)}"))
        return L
    if op=='msgrows':
        L=[('MESSAGES LIST — loads whole, already full: ','')]
        for r in o['rows']:
            L.append(('   · ', f"{r['n']}{' ●' if r.get('un') else ''} — “{r['p']}” ({r['w']})"))
        return L
    if op=='inbox':
        L=[(f"{o.get('title','INBOX').upper()} — loads whole, the instant the app opens: ",'')]
        for r in o['rows']:
            L.append(('   · ', f"{'⚑ ' if r.get('flag') else ''}{r['f']}{' ●' if r.get('unread') else ''} — {r['s']}"
                             + (f" — {r['p']}" if r.get('p') else '') + f" ({r.get('w','')})"))
        return L
    if op=='mail':
        return [('NEW MAIL — arrives live at the TOP of the inbox: ',
                 f"{o['f']}{' ●' if o.get('unread') else ''} — {o['s']} — {o.get('p','')} ({o.get('w','now')})")]
    if op=='mailopen':
        L=[('THE EMAIL, OPENED — ', f"{o['f']} → {o.get('to','')} · “{o['s']}” · {o.get('w','')}")]
        for pgh in o.get('body',[]): L.append(('   ', pgh))
        return L
    if op=='history':
        L=[('THREAD HISTORY — loads whole with the thread: ','')]
        for it in o['items']:
            k=it['k']
            if k=='stamp': L.append(('   — ', it['t'].replace('|',' · ')))
            elif k in ('me','them'):
                side='SENT (blue)' if k=='me' else 'RECEIVED (gray)'
                if it.get('link'): L.append((f'   {side} — LINK CARD: ', f"{it['link']['t']} · {it['link'].get('d','')} · image: {it['link'].get('m','')}"))
                elif it.get('media'): L.append((f"   {side} — {'VIDEO '+it['video'] if it.get('video') else 'PHOTO'} BUBBLE: ", it['media']))
                else: L.append((f'   {side}: ', f"“{it['t']}”"))
            elif k=='rcpt': L.append(('   status: ', it['t']))
        return L
    if op=='stampline': return [('thread caption: ', o['t'].replace('|',' · '))]
    if op=='type': return [('TYPES LIVE (keyboard up, keys flashing, self-timed): ', f"“{o['t']}”")]
    if op=='send': return [('SEND — ', 'the draft springs up into the thread as a blue bubble')]
    if op=='wipe': return [('BACKSPACES the draft to nothing (fast rattle)', '')] + ([('  caption: ',o['t'])] if o.get('t') else [])
    if op=='rcpt': return [('delivery status: ', o['t'])]
    if op=='rcptswap': return [('STATUS FLIPS → ', o['t'])]
    if op=='typing': return [('typing indicator rises (three dots)','')]
    if op=='untyping': return [('typing indicator disappears','')]
    if op=='them':
        if o.get('link'): return [('RECEIVED — LINK PREVIEW CARD: ', f"{o['link']['t']} · {o['link'].get('d','')}"),
                                  ('  card image: ', o['link'].get('m',''))]
        if o.get('media'): return [(('RECEIVED — VIDEO BUBBLE ('+o['video']+'): ') if o.get('video') else 'RECEIVED — PHOTO BUBBLE: ', o['media'])]
        return [('RECEIVED BUBBLE (gray): ', f"“{o['t']}”")]
    if op=='post':
        L=[(f"SOCIAL POST — {o.get('who','')} ({o.get('w','now')}): ", f"“{o.get('txt','')}”")]
        if o.get('media'): L.append(('  media: ', o['media']))
        if 'likes' in o: L.append(('  reactions: ', f"👍 {o['likes']}"))
        return L
    if op=='like': return [('LIKE COUNTER SPINS → ', str(o.get('to','')))]
    if op=='comment': return [('COMMENT APPEARS — ', f"{o['n']}: “{o['t']}”")]
    if op=='row':
        return [('row: ', (f"[{o['tag']}] " if o.get('tag') else '') + o['t'] + (f" — {o['s']}" if o.get('s') else ''))]
    if op=='docline': return [('a greeked line types itself — ', 'key clicks, text illegible by design')]
    if op=='deck':
        return [('CARD STACK: ','')]+[('   · ',f"{c['n']}, {c['a']} — {c['d']}") for c in o['cards']]
    if op=='swipe': return [('SWIPE RIGHT — ', 'LIKE stamp, the card flies off')]
    if op=='search': return [('SEARCH BAR — types live: ', f"“{o['t']}”")]
    if op=='searchClear': return [('search BACKSPACED clear','')]
    if op=='call': return [('CALL SCREEN — ', f"{o['n']} · {o['st']}" + (' · incoming' if o.get('dir')=='in' else ' · outgoing'))]
    if op=='callState': return [('call state → ', o.get('t') or o.get('st',''))]
    if op=='facetime':
        L=[('FACETIME — ', f"{o.get('n','')} · {o.get('st','')}")]
        if o.get('main'): L.append(('  main feed: ', o['main']))
        if o.get('pip'): L.append(('  PiP self-view: ', o['pip']))
        return L
    if op=='ftState': return [('FaceTime state → ', o.get('t') or o.get('st',''))]
    if op=='ftMain': return [('main feed swaps → ', o.get('l',''))]
    if op=='wall': return [('WALLPAPER — ', o['t'])]
    if op=='sheet':
        return [('ACTION SHEET slides up over the app — ', f"“{o.get('title','')}”"),
                ('  buttons: ', f"[{o.get('danger','')}] (red) · [{o.get('safe','Cancel')}]")]
    if op=='sheetDismiss': return [('sheet slides away — ', 'nothing chosen')]
    if op=='btnHover': return [('TOUCH-DOT lands on ', f"[{o['b']}] — hovering, pulsing, not pressing")]
    if op=='btnTap': return [('PRESSES ', f"[{o['b']}]")]
    if op=='contactcard':
        out=[('CONTACT CARD — ', o.get('n','') + (f" · {o['sub']}" if o.get('sub') else ''))]
        if o.get('rename'): out.append(('  name mid-edit: ', f"“{o['rename']['from']}” struck through → “{o['rename']['to']}” typed in"))
        if o.get('toggle'): out.append(('  toggle: ', f"{o['toggle']['l']} — {'ON' if o['toggle'].get('on') else 'OFF'}"))
        return out
    if op=='findmy':
        return [('FIND MY — People: ', ' · '.join(f"{r['n']}: {r['s']}" for r in o.get('rows',[])))]
    if op=='calevent':
        out=[('CALENDAR EVENT — ', f"“{o.get('title','')}” · {o.get('when','')}" + (f" · {o['where']}" if o.get('where') else ''))]
        if o.get('invitees'): out.append(('  invitees: ', ' · '.join(f"{v['n']} {'✓' if v['st']=='accepted' else '✗' if v['st']=='declined' else v['st']}" for v in o['invitees'])))
        if o.get('resp'): out.append(('  response bar: ', f"✓ {o['resp']}ed (green)"))
        return out
    if op=='settings2':
        out=[('SETTINGS — ', f"{o.get('back','Settings')} › {o.get('title','')}")]
        if o.get('gauge') is not None: out.append(('  gauge: ', f"{o['gauge']}% · {o.get('gaugeSub','')}"))
        for g in o.get('groups',[]):
            for r in g.get('rows',[]):
                v = ('ON' if r.get('on') else 'OFF') if 'on' in r else r.get('v','')
                out.append(('  · ', f"{r['l']}" + (f" — {v}" if v else '') + (f" ({r['sub']})" if r.get('sub') else '')))
        if o.get('foot'): out.append(('  footer: ', o['foot']))
        return out
    if op=='reminders':
        return [('REMINDERS — list ', f"“{o.get('list','')}”")] +                [('  ○ ', r['t'] + (f" — {r['sub']}" if r.get('sub') else '')) for r in o.get('rows',[])]
    if op=='ftrecents':
        return [('FACETIME RECENTS: ', '')] +                [('  · ', f"{r['n']} — {r['sub']} · {r.get('w','')}" + (' (red)' if r.get('missed') else '')) for r in o.get('rows',[])]
    if op=='maps':
        return [('MAPS NAVIGATION — ', f"{o.get('instr','')} · {o.get('via','')}"),
                ('  ETA card: ', f"{o.get('eta','')} → {o.get('dest','')}" + (' · ARRIVING (green)' if o.get('arriving') else ''))]
    if op=='music':
        return [('MUSIC — playlist ', f"“{o.get('title','')}” · {o.get('sub','')}")]+                [('  ♪ ', f"(greeked track) — {r.get('by','')}") for r in o.get('rows',[])]
    if op=='musicBanner': return [('banner over the playlist: ', f"“{o['t']}”")]
    if op=='shot':
        return [('PHOTOS — a saved screenshot, opened: ', f"{o.get('album','')} · {o.get('date','')}"),
                ('  inside the screenshot (gray bubble): ', f"“{o.get('t','')}”")] +                ([('  caption: ', o['note'])] if o.get('note') else [])
    if op=='note':
        return [('NOTES — ', f"“{o.get('title','')}” · {o.get('edited','')}")] +                [('  ', l) for l in o.get('lines',[]) if l]
    if op=='vm':
        return [('VOICEMAIL — ', f"{o.get('n','')} · {o.get('date','')} · 0:{o.get('dur',0):02d}" + (' · SAVED' if o.get('saved') else '')),
                ('  scrubber: ', f"{'playing' if o.get('playing') else 'stopped'} at 0:{o.get('pos',0):02d}")] +                ([('  transcription: ', f"“{o['transcript']}”")] if o.get('transcript') else [])
    if op=='vmState': return [('voicemail scrubber → ', f"0:{o.get('pos',0):02d}" + (' · playing' if o.get('playing') else ' · stopped'))]
    if op=='igreq':
        return [('INSTAGRAM — message request from ', f"{o.get('user','')} ({o.get('followers','')})"),
                ('  request bubble: ', f"“{o.get('msg','')}”"),
                ('  buttons: ', '[Delete] · [Accept] — side by side')]
    if op=='match':
        return [('IT’S A MATCH — full-screen overlay: ', f"You and {o.get('n','')} have liked each other"),
                ('  buttons: ', '[Send a Message] · [Keep Swiping]')]
    if op=='black': return [('HOUSE BLACK — ', 'the phone vanishes into it')]
    if op=='notifDismiss': return [('notification SWIPED AWAY — ', 'slides off and is gone')]
    return []

def plays(o, cue, songwho):
    """Mechanics: what the engine performs on its own — navigation, sound, timing."""
    op=o['op']
    if op=='device': return f"the {DEV.get(o['dev'],o['dev'])} shell appears — {o['who'].upper()}’s screen"
    if op=='notiftap': return ("TAP THE NOTIFICATION — the touch-dot lands on the banner, presses, Face ID passes, "
                               f"and the app opens DIRECTLY onto {APPNAME.get(o['to'],o['to'])}. One motion. No home screen.")
    if op=='unlock': return 'UNLOCK — the lock slides up and away → home screen · sound: unlock swish'
    if op=='openapp': return (f"OPENS {o['icon']} — closes the current app if one is open, a beat on the home screen, "
                              'the thumb travels to the icon, presses, the app opens · sound: tap')
    if op=='setapp': return f"cut to {APPNAME.get(o['to'],o['to'])} (instant)"
    if op=='hover': return f"HESITATION — the pulsing touch-dot hovers over “{o['row']}” … and does not commit. Holds until the next cue."
    if op=='tap': return 'TAP COMMITS — the dot presses through and vanishes · sound: tap'
    if op=='push': return f"thread pushes in from the list — {o.get('contact','')}"
    if op=='mailopen': return 'the dot presses through — the email pushes in over the inbox'
    if op=='mail': return 'sound: receive ding — the new row fades in above everything already there'
    if op=='inbox': return 'no animation — a real inbox does not populate; it is simply THERE, continuing past the bottom edge'
    if op=='msgrows': return 'no animation — the list is already full; the last rows cut off at the bottom of the glass'
    if op=='type': return 'sound: key clicks'
    if op=='send': return 'sound: send swoosh'
    if op=='wipe': return 'sound: backspace rattle'
    if op=='notif': return 'sound: receive ding'
    if op=='mem': return 'the feed advances one full-screen card · sound: soft pop'
    if op=='post': return 'sound: soft pop'
    if op=='row' or op=='cards': return 'sound: soft pop'
    if op=='swipe': return 'sound: whoosh'
    if op=='docline': return 'sound: key-click burst (self-timed)'
    if op=='black': return 'hard black'
    return None

OPS_SILENT={'device','clock'}  # covered inline

book={'build':data['build'],'songs':[]}
for s in data['songs']:
    entries=[]
    for c in s['cues']:
        content=[]; mech=[]
        for o in c['do']:
            content += onscreen(o)
            pl=plays(o,c,s['who'])
            if pl and pl not in mech: mech.append(pl)
        entries.append({
            'id':c['id'],'kind':c['kind'],'trig':c['trig'],'what':c['what'],
            'hold':c['hold'],'cut':c['cut'],
            'screen':'BOTH' if s['who']=='both' else ('SR' if c['who']=='cathy' else 'SL'),
            'who':c['who'].upper(),'app':APPNAME.get(c['app'],c['app']),
            'clock':c['clock'],'stamp':c['stamp'],'black':c['black'],
            'content':content,'plays':mech,'sound':sound_for(c['do'])})
    book['songs'].append({'n':s['n'],'t':s['t'],'who':s['who'],'fires':len(entries),'cues':entries})

json.dump(book, open('bible.json','w'), ensure_ascii=False)
print('bible.json:', sum(s['fires'] for s in book['songs']), 'entries across', len(book['songs']), 'songs')
