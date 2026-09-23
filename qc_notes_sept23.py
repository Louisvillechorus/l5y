"""The Sept 23 notes: the four simple changes and the Find My map, each proved on the live GO path.

9.1 became two cues (the card, then the phone); 10.4 lands already on the call with the timer
running from 0:10; the interstate shields on the dash carry their numerals inside the crest; and
the Find My beat got a real map — HOME pinned where the iPad reports from, gone once the iPhone
takes over — framed so the camera never moves while the word changes.
"""
import os
import re

W, H = 1920, 1080
URL = 'file://' + os.path.abspath('L5Y-Show-STANDALONE.html')


def _boot(pg, w=W, h=H):
    pg.set_viewport_size({'width': w, 'height': h})
    pg.evaluate("setCast('ml'); startAs('projection');")
    pg.wait_for_timeout(300)


def _at(pg, cid):
    return pg.evaluate("""(cid)=>{ for(let s=0;s<SHOW.length;s++){
        const k=SHOW[s].cues.findIndex(c=>c.id===cid); if(k>=0) return [s,k]; } return null; }""", cid)


def _park(pg, cid):
    loc = _at(pg, cid)
    if not loc:
        return None
    pg.evaluate(f"si={loc[0]}; ci={loc[1]}; animTok++; animRunning=false; hardRender();")
    pg.wait_for_timeout(400)
    return loc


def _fire(pg, cap=400):
    pg.evaluate("setTimeout(()=>advance(),0)")
    for _ in range(cap):
        pg.wait_for_timeout(100)
        if not pg.evaluate('animRunning'):
            pg.wait_for_timeout(300)
            return True
    return False


# ---------- D-076 · 9.1 is the card, 9.1a is the phone ----------
def a_91_card_then_phone(pg):
    """The Intermission page tears and the calendar rolls to OCTOBER · YEAR 4 on its own GO, with no
    phone; the next GO (9.1a) raises his locked phone with the wedding portrait behind the clock."""
    bad = []
    _boot(pg)
    if not _park(pg, '9.1'):
        return ['there is no 9.1']
    if not _fire(pg, 250):
        return ['9.1 never settles']
    st = pg.evaluate("""(()=>{const e=document.querySelector('#era'); const t=e?e.innerText.replace(/\\s+/g,' '):'';
        return {txt:t, phone:!!document.querySelector('#projDevice .iphone'), inter:/intermission/i.test(t)};})()""")
    if st['inter']:
        bad.append('9.1 settles with the Intermission band still on stage')
    if 'October' not in st['txt'] or not re.search(r'\b4\b', st['txt']):
        bad.append('9.1 does not settle on OCTOBER · YEAR 4 — the card reads %r' % st['txt'][:60])
    if st['phone']:
        bad.append('9.1 raises a phone; it is the card alone')
    if not _fire(pg, 250):
        return bad + ['the cue after 9.1 never settles']
    st2 = pg.evaluate("""(()=>{const ph=document.querySelector('#projDevice .iphone'); const lk=document.querySelector('#projDevice .lockL');
        const bg=lk?getComputedStyle(lk).backgroundImage:''; return {id:SHOW[si].cues[ci-1].id, phone:!!ph, lock:!!lk, wall:/url\\(/.test(bg)};})()""")
    if st2['id'] != '9.1a':
        bad.append('the cue after 9.1 is %s, not 9.1a' % st2['id'])
    if not st2['phone'] or not st2['lock']:
        bad.append('9.1a does not raise his locked phone')
    elif not st2['wall']:
        bad.append('9.1a’s lock screen carries no wallpaper photograph')
    return bad


# ---------- D-077 · 10.4 lands on the call ----------
def a_104_lands_connected(pg):
    """After the warp to JANUARY · YEAR 5 his phone rises already connected to her: no buzz, never an
    Answer button, the timer already at 0:10 and counting."""
    bad = []
    _boot(pg)
    if not _park(pg, '10.4'):
        return ['there is no 10.4']
    pg.evaluate("""(()=>{window.__rings=[]; const _r=sfxRing;
        window.sfxRing=function(k){ window.__rings.push(k); return _r.apply(this,arguments); };})()""")
    pg.evaluate("setTimeout(()=>advance(),0)")
    seen, first = set(), None
    for _ in range(300):
        pg.wait_for_timeout(100)
        c = pg.evaluate("""(()=>{const e=document.querySelector('#projDevice .cst'); if(!e) return null;
            const acts=[...document.querySelectorAll('#projDevice .callbtns [data-act]')].map(x=>x.dataset.act);
            return [e.dataset.st||'', e.textContent.trim(), acts];})()""")
        if c:
            seen.add(c[0].split('·')[0].strip().lower())
            if first is None:
                first = c
        if not pg.evaluate('animRunning'):
            break
    rings = pg.evaluate('window.__rings')
    if rings:
        bad.append('10.4 rang (%s) — the call must land already connected' % ', '.join(rings))
    if 'incoming call' in seen:
        bad.append('10.4 showed “incoming call”; he walks in already talking')
    if not first:
        bad.append('no call screen appeared')
    else:
        if not re.match(r'connected', first[0], re.I):
            bad.append('the call screen opened in state %r, not connected' % first[0])
        m = re.match(r'0:(\d\d)$', first[1])
        if not m:
            bad.append('the status line reads %r, not the duration alone' % first[1])
        elif not 10 <= int(m.group(1)) <= 13:
            bad.append('the timer started at 0:%s, not 0:10' % m.group(1))
        if 'accept' in first[2] or 'end' not in first[2]:
            bad.append('the connected screen offers %s — it must show the in-call controls and End' % first[2])
    return bad


# ---------- D-078 · the Find My map ----------
def a_findmy_home(pg):
    """Before the swap his dot sits at HOME with the Home pin beside it, inside the reading window
    together with the Sharing From row; after it the map has jumped, the pin is gone, and the
    camera has not moved a pixel between the two states."""
    bad = []
    _boot(pg)
    if not _park(pg, '13.3'):
        return ['there is no 13.3']
    uw = pg.evaluate('Math.round(innerWidth*(1-ERA_ZONE_()))')
    pg.evaluate("setTimeout(()=>advance(),0)")
    home_seen = away_seen = None
    for _ in range(450):
        pg.wait_for_timeout(100)
        r = pg.evaluate("""(()=>{const L=document.querySelector('#projDevice .layer.fs'); if(!L) return null;
            const c=document.querySelector('#projDevice [data-z]'); const tf=c?c.style.transform:'';
            const q=s=>{const e=L.querySelector(s); if(!e) return null; const b=e.getBoundingClientRect();
                        return [Math.round(b.left),Math.round(b.top),Math.round(b.right),Math.round(b.bottom)];};
            const share=L.querySelector('.fmshare');
            return {from:share?share.textContent:'', home:q('.fmhome:not(.gone)'), away:!!L.querySelector('.fmmap.away'),
                    dot:q('.fmdot'), share:q('.fmshare'), tf};})()""")
        if r and r['from']:
            if 'iPad' in r['from']:
                home_seen = r
            if 'iPhone' in r['from']:
                away_seen = r
        if not pg.evaluate('animRunning'):
            break

    def inside(b):
        return bool(b) and b[0] >= -2 and b[1] >= -2 and b[2] <= uw + 2 and b[3] <= H + 2

    if not home_seen:
        bad.append('the “Sharing From: iPad” state never showed')
    else:
        if not home_seen['home']:
            bad.append('no Home pin on the map while the iPad is reporting')
        elif not inside(home_seen['home']):
            bad.append('the Home pin sits outside the reading window: %s' % home_seen['home'])
        if not inside(home_seen['dot']):
            bad.append('his dot sits outside the reading window: %s' % home_seen['dot'])
        if not inside(home_seen['share']):
            bad.append('the Sharing From row is outside the reading window: %s' % home_seen['share'])
        if home_seen['away']:
            bad.append('the away map is already showing while the iPad is reporting')
    if not away_seen:
        bad.append('the “Sharing From: iPhone” state never showed')
    else:
        if not away_seen['away']:
            bad.append('after the swap the map did not jump — no away map')
        if away_seen['home']:
            bad.append('the Home pin is still on the map after the swap')
        if not inside(away_seen['dot']):
            bad.append('his dot left the reading window after the swap: %s' % away_seen['dot'])
        if home_seen and home_seen['tf'] != away_seen['tf']:
            bad.append('the camera moved between the two states: %s → %s' % (home_seen['tf'], away_seen['tf']))
    return bad


# ---------- D-079 · the interstate shields ----------
def a_shield_fits(pg):
    """The numeral on every route shield sits in the crest — clear of the red band above and of the
    point below — and the shields are drawn at a size that reads from the house."""
    bad = []
    _boot(pg, 1280, 720)
    drive = pg.evaluate("""(()=>{ for(let s=0;s<SHOW.length;s++){
        const k=SHOW[s].cues.findIndex(c=>(c.do||[]).some(o=>o.op==='device'&&o.dev==='carplay'));
        if(k>=0) return SHOW[s].cues[k].id; } return null; })()""")
    if not drive or not _park(pg, drive):
        return ['no cue in the show raises the CarPlay dash']
    pg.evaluate("setTimeout(()=>advance(),0)")
    for _ in range(60):
        pg.wait_for_timeout(100)
        if pg.evaluate("!!document.querySelector('#projDevice #i95')"):
            break
    r = pg.evaluate("""(()=>{
        // elements inside <defs> are never laid out, so each shield is copied into a live SVG to be measured
        const out={}; const S=document.createElementNS('http://www.w3.org/2000/svg','svg');
        S.setAttribute('width','200'); S.setAttribute('height','200'); S.setAttribute('viewBox','-60 -60 120 120');
        S.style.cssText='position:fixed;left:0;top:0;opacity:0;pointer-events:none'; document.body.appendChild(S);
        ['i95','i295'].forEach(id=>{ const src=document.querySelector('#projDevice #'+id); if(!src){ out[id]=null; return; }
          const g=src.cloneNode(true); g.removeAttribute('id'); S.appendChild(g);
          const t=g.querySelector('text'), paths=[...g.querySelectorAll('path')];
          const pb=paths[0].getBBox(); const band=paths[1]?paths[1].getBBox():null; const tb=t.getBBox();
          const fs=parseFloat(t.getAttribute('font-size')), base=parseFloat(t.getAttribute('y')||'0');
          out[id]={crest:[pb.y, pb.y+pb.height, pb.width], band:band?band.y+band.height:pb.y, inkTop:base-0.73*fs, inkBot:base, inkW:tb.width};
          const u=document.querySelector('#projDevice use[href="#'+id+'"]'); out[id].scale=u?(u.getAttribute('transform')||''):'(no use)'; });
        S.remove(); return out; })()""")
    for sid, m in r.items():
        if not m:
            bad.append('the dash has no %s shield' % sid)
            continue
        top, bot, w = m['crest']
        h = bot - top
        if m['inkTop'] < m['band'] + 0.5:
            bad.append('%s: the numeral runs into the band above it' % sid)
        if m['inkBot'] > bot - 0.28 * h:
            bad.append('%s: the numeral sits in the crest’s point (baseline %.0f, point begins at %.0f)' % (sid, m['inkBot'], bot - 0.28 * h))
        if m['inkW'] > 0.66 * w:
            bad.append('%s: the numeral is wider than the crest can hold (%.0f of %.0f)' % (sid, m['inkW'], w))
        if 'scale' not in m['scale']:
            bad.append('%s is drawn at map scale; it needs the 1.3× that reads from 25 ft' % sid)
    return bad


# ---------- D-080 · the wallpapers ("the screensavers on phones") ----------
def a_wallpapers(pg):
    """A photo wallpaper is cropped by its owner (the wedding portrait carries a per-cast crop, never
    centre/cover) and a colour wallpaper is lit, never a flat slab: the lock and home layers carry
    a radial light on top of the gradient."""
    bad = []
    _boot(pg)
    for cast in ('ml', 'ac'):
        pg.evaluate("setCast('%s')" % cast)
        if not _park(pg, '9.1a'):
            return ['there is no 9.1a']
        _fire(pg, 120)
        bg = pg.evaluate("(()=>{const l=document.querySelector('#projDevice .lockL'); return l?l.style.background||getComputedStyle(l).background:'';})()")
        if 'url(' not in bg:
            bad.append('%s: 9.1a’s lock screen carries no photograph' % cast)
        elif 'center/cover' in bg.replace(' ', '') or '/ cover' in bg:
            bad.append('%s: the wedding portrait is dropped centre/cover — nobody cropped it' % cast)
    pg.evaluate("setCast('ml')")
    if not _park(pg, '2.1'):
        return bad + ['there is no 2.1']
    _fire(pg, 120)
    bg = pg.evaluate("(()=>{const l=document.querySelector('#projDevice .lockL'); return l?l.style.background:'';})()")
    if 'radial-gradient' not in bg or bg.count('gradient') < 2:
        bad.append('2.1: the colour wallpaper is a flat slab — no light on it')
    return bad


# ---------- D-081 · the paper ("more gritty") ----------
def a_paper_grit(pg):
    """The sheet reads as paper from the house: the rendered card's luminance varies visibly across
    the sheet (formation and tooth), and the top sheet casts a shadow that survives the torn clip."""
    try:
        from PIL import Image
        import io
    except Exception as e:
        return ['cannot measure the paper: %s' % e]
    bad = []
    _boot(pg)
    if not _park(pg, '1.1'):
        return ['there is no 1.1']
    _fire(pg, 150)
    pg.wait_for_timeout(600)
    box = pg.evaluate("""(()=>{const e=document.querySelector('#era .sheet.top .pf'); if(!e) return null; const r=e.getBoundingClientRect();
        return {x:Math.round(r.x+r.width*0.04), y:Math.round(r.y+r.height*0.40), w:Math.round(r.width*0.18), h:Math.round(r.height*0.26)};})()""")   # the margin left of the numeral: paper only
    if not box:
        return ['no top sheet on stage after 1.1']
    im = Image.open(io.BytesIO(pg.screenshot(clip={'x': box['x'], 'y': box['y'], 'width': box['w'], 'height': box['h']}))).convert('L')
    px = list(im.getdata())
    # the band under the numeral: paper only (the foot rule sits lower). Ink would spike the spread, so clamp it away.
    paper = [v for v in px if v > 150]
    if len(paper) < len(px) * 0.9:
        return ['the sampled band is not clean paper (%d%% light pixels)' % (100 * len(paper) // len(px))]
    mean = sum(paper) / len(paper)
    sd = (sum((v - mean) ** 2 for v in paper) / len(paper)) ** 0.5
    if sd < 5.0:
        bad.append('the paper is flat: luminance spread %.1f (a sheet the house can read as paper needs ≥ 5)' % sd)
    filt = pg.evaluate("(()=>{const e=document.querySelector('#era .sheet.top'); return e?getComputedStyle(e).filter:'';})()")
    if 'drop-shadow' not in filt:
        bad.append('the top sheet casts no shadow (filter is %r)' % filt)
    return bad


# ---------- D-082 · the notification card is the iOS 15+ card ----------
def a_notif_card(pg):
    """A card carries its icon at the left spanning the text, the bold title with the time beside
    it, the body beneath — and never prints the app's name in a header. A text from a contact
    with a photo carries that photo with a Messages badge."""
    bad = []
    _boot(pg)
    if not _park(pg, '13.2'):
        return ['there is no 13.2']
    pg.evaluate("setTimeout(()=>advance(),0)")
    card = None
    for _ in range(80):
        pg.wait_for_timeout(100)
        card = pg.evaluate("""(()=>{const c=document.querySelector('#projDevice .nstack .notif'); if(!c) return null;
            const ni=c.querySelector('.ni'), nt=c.querySelector('.nt'), nw=c.querySelector('.nw'), nb=c.querySelector('.nb');
            const r=e=>e?e.getBoundingClientRect():null; const R=r(c), I=r(ni), T=r(nt), B=r(nb);
            return {txt:c.innerText, hasIcon:!!ni, iconH:I?I.height:0, cardH:R?R.height:0, person:!!(ni&&ni.classList.contains('person')),
                    photo:!!(ni&&/url\\(/.test(ni.style.background||'')), badge:!!(ni&&ni.querySelector('.badge')),
                    titleLeftOfIcon:!!(T&&I&&T.left<I.right), title:nt?nt.textContent:'', time:nw?nw.textContent:'',
                    upper:/\\b(MESSAGES|MAIL|INSTAGRAM|CHASE|CALENDAR)\\b/.test(c.innerText)};})()""")
        if card:
            break
    if not card:
        return ['no notification card landed on 13.2']
    if card['upper']:
        bad.append('the card prints the app’s name in uppercase — that is the iOS 12 header')
    if not card['hasIcon'] or card['iconH'] < card['cardH'] * 0.42:
        bad.append('the icon is not the large left-hand icon (%.0f of a %.0f px card)' % (card['iconH'], card['cardH']))
    if card['titleLeftOfIcon']:
        bad.append('the title sits left of the icon')
    if not card['person'] or not card['photo'] or not card['badge']:
        bad.append('a text from Cathy does not carry her photo with the Messages badge')
    if card['time'].strip().lower() != 'now':
        bad.append('the time reads %r, not “now”' % card['time'])
    return bad


# ---------- D-083 · the call screen is iOS 17 ----------
def a_call_screen(pg):
    """Under the name a phone prints the duration alone (never the word connected), the label
    while it rings (never “incoming call”), and Call Ended keeps the layout; the connected
    controls are the captioned six plus the red handset."""
    bad = []
    _boot(pg)
    if not _park(pg, '3.8a'):
        return ['there is no 3.8a']
    pg.evaluate("setTimeout(()=>advance(),0)")
    words = set()
    for _ in range(140):
        pg.wait_for_timeout(100)
        r = pg.evaluate("""(()=>{const e=document.querySelector('#projDevice .cst'); if(!e) return null;
            const acts=[...document.querySelectorAll('#projDevice .callbtns [data-act]')].map(x=>x.dataset.act);
            const caps=[...document.querySelectorAll('#projDevice .callbtns .cap')].map(x=>x.textContent.trim());
            const ff=getComputedStyle(e).fontFamily; return {t:e.textContent.trim(), st:e.dataset.st||'', acts, caps, ff};})()""")
        if r:
            words.add(r['t'].lower())
            if 'courier' in (r['ff'] or '').lower():
                bad.append('the status line is set in Courier — a phone uses the system face')
                break
            if 'connected' in r['st'].lower():
                if not re.match(r'^\d+:\d\d$', r['t']):
                    bad.append('connected, the status line reads %r, not the duration alone' % r['t'])
                if not {'mute', 'keypad', 'speaker', 'add', 'facetime', 'contacts', 'end'} <= set(r['acts']):
                    bad.append('the connected controls are %s, not the six plus End' % r['acts'])
                if 'FaceTime' not in r['caps'] or 'mute' not in r['caps']:
                    bad.append('the controls carry no captions')
                break
        if not pg.evaluate('animRunning'):
            break
    if any('connected' in w or 'incoming call' in w for w in words):
        bad.append('the words on the glass were %s — a phone never prints those' % sorted(words))
    return bad


# ---------- D-084 · nothing peeks under the compose bar ----------
def a_keyboard_down(pg):
    """With the keyboard down the compose bar sits flush at the foot of the screen: the keyboard
    element is zero-height, and no keycap is visible on the show's final held image (14.4)."""
    bad = []
    _boot(pg)
    if not _park(pg, '14.4'):
        return ['there is no 14.4']
    _fire(pg, 450)
    pg.wait_for_timeout(500)
    r = pg.evaluate("""(()=>{const k=document.querySelector('#projDevice .kbd'); if(!k) return null;
        const keys=[...k.querySelectorAll('.key')].filter(e=>{const b=e.getBoundingClientRect(); return b.height>0 && b.top<innerHeight && b.bottom>0;});
        const kb=k.getBoundingClientRect(); return {up:k.classList.contains('up'), h:kb.height, visibleKeys:keys.length,
          padding:getComputedStyle(k).paddingTop+' '+getComputedStyle(k).paddingBottom};})()""")
    if not r:
        return ['no thread on stage at the end of 14.4']
    if r['up']:
        bad.append('the keyboard is still up on the final image')
    if r['h'] > 1:
        bad.append('the keyboard element is %.0f px tall while down (padding %s) — a strip of keycaps peeks under the bar' % (r['h'], r['padding']))
    return bad
