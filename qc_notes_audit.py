"""PROBES for the tail of the 48-agent law audit (D-057 … D-065).

Several of these check the DOCUMENTS and the TOOLS rather than the stage: a Bible that
prints an unverified line as verified, or a gate whose test cannot fail, misleads the team
just as surely as a wrong pixel does.
"""
import json
import os
import re

from qc_notes_core import boot, fire, song_ix


def _cues_src():
    return open('cues.js', encoding='utf-8').read()


# ---------- D-057 · every quoted script line is either verified or flagged ----------
def a_lines_flagged(pg):
    """Reports the state of the LINES LAW. Only David can clear a line; this keeps the count honest."""
    s = _cues_src()
    quoted, flagged = [], []
    for blk in re.split(r"(?=\{id:')", s):
        m = re.match(r"\{id:'([^']+)'", blk)
        if not m:
            continue
        t = re.search(r"trig:'((?:[^'\\]|\\.)*)'", blk)
        if not t:
            continue
        head = blk.split('do:')[0]
        if '“' in t.group(1) or '”' in t.group(1):
            quoted.append(m.group(1))
            if 'confirm:true' in head:
                flagged.append(m.group(1))
    reg = json.load(open('notes.json'))
    cleared = next((n.get('lines_cleared') for n in reg['notes'] if n['id'] == 'D-057'), None)
    if cleared is None:
        return [f'WAITING ON DAVID: {len(quoted)} cues quote a script line and {len(flagged)} carry '
                f'⚠CONFIRM ({", ".join(flagged)}). The other {len(quoted)-len(flagged)} are unflagged, '
                'which under the law means the worksheet pass cleared them — only David can confirm '
                'that. Set "lines_cleared" on D-057 in notes.json once he has.']
    missing = [c for c in quoted if c not in flagged and c not in cleared]
    return [f'these quoted lines are neither flagged nor cleared: {", ".join(missing[:12])}'] if missing else []


# ---------- D-058 · the CONFIRM flag survives into the printed Bible ----------

def _bible_describes_build():
    """Does the Bible describe the show that is built? Compare CONTENT, not timestamps.

    mtime was the old test and it is a bad one: a git checkout rewrites the working tree and bumps
    every mtime without changing a byte, so the Bible could be reported stale purely because a
    branch was switched. What actually matters is whether the two agree about the show."""
    out = []
    try:
        cues = open('cues.js', encoding='utf-8').read()
        want = set(re.findall(r"\{id:'([^']+)'", cues))
    except Exception as e:
        return ['cannot read cues.js: %s' % e]
    for f, label in (('book.json', 'the state record'), ('bible.json', 'the Bible')):
        if not os.path.exists(f):
            out.append('%s has not been built' % f); continue
        try:
            d = json.load(open(f, encoding='utf-8'))
        except Exception as e:
            out.append('%s will not parse: %s' % (f, e)); continue
        got = set()
        for s_ in (d.get('songs') or []):
            for c in (s_.get('cues') or []):
                if c.get('id'):
                    got.add(c['id'])
        if not got:
            out.append('%s lists no cues at all' % f); continue
        missing, extra = want - got, got - want
        if missing:
            out.append('%s is stale — it is missing %s' % (label, ', '.join(sorted(missing)[:6])))
        if extra:
            out.append('%s is stale — it still carries %s' % (label, ', '.join(sorted(extra)[:6])))
    return out

def a_confirm_survives_bible(pg):
    bad = []
    src = _cues_src()
    flagged = set(re.findall(r"\{id:'([^']+)'[^}]*?confirm:true", src, re.S))
    if not flagged:
        # NOTHING IS UNVERIFIED ANY MORE — which is the goal, not a failure. The mechanism still has
        # to be proved, so prove it without a real unverified line: check that the extractor reads
        # the flag at all and that the renderers can print the marker. Otherwise the day the last
        # CONFIRM is cleared is the day this protection silently stops being tested.
        eb = open('extract_book.py', encoding='utf-8').read()
        if 'confirm' not in eb:
            bad.append('extract_book.py drops the confirm flag before the Bible ever sees it')
        # The marker is prepended where the Bible's data is assembled, not in the two renderers —
        # they print whatever bible.json carries, so checking THEM for the word proves nothing.
        bd = open('build_bible_data.py', encoding='utf-8').read()
        if "c.get('confirm')" not in bd or 'CONFIRM' not in bd:
            bad.append('build_bible_data.py no longer marks an unverified line, so one would print '
                       'as verified the moment it appears')
        bad += _bible_describes_build()
        return bad
    if 'confirm' not in open('extract_book.py', encoding='utf-8').read():
        bad.append('extract_book.py drops the confirm flag before the Bible ever sees it')
    bad += _bible_describes_build()
    try:
        book = json.load(open('book.json'))
        got = {c['id'] for s in book['songs'] for c in s['cues'] if c.get('confirm')}
        miss = flagged - got
        if miss:
            bad.append(f'the confirm flag never reaches book.json for {sorted(miss)}')
        bib = json.dumps(json.load(open('bible.json')), ensure_ascii=False)
        n = bib.count('⚠CONFIRM')
        if n < len(flagged):
            bad.append(f'the Bible prints {n} CONFIRM markers for {len(flagged)} unverified lines — '
                       'the documents show unverified lines as verified')
    except Exception as e:
        bad.append(f'could not read the documents: {e}')
    return bad


# ---------- D-059 · the law, the Bible and the build agree about song 6 ----------
def a_song6_agrees(pg):
    bad = []
    boot(pg)
    i = song_ix(pg, 6)
    phone = pg.evaluate(f"""(()=>{{ const s=SHOW[{i}];
        return s.cues.some(q=>(q.do||[]).some(o=>o.op==='device')); }})()""")
    law = open('CLAUDE.md', encoding='utf-8').read()
    claims_lock = bool(re.search(r'\*\*6\*\*[^.]{0,80}lock screen', law))
    if claims_lock and not phone:
        bad.append('CLAUDE.md says song 6 is his lock screen with the Christmas wallpaper, '
                   'but no cue in song 6 raises a device — the build is calendar-only')
    if phone and not claims_lock:
        bad.append('song 6 raises a device but the law describes it as calendar-only')
    return bad


# ---------- D-060 · his name in her phone matches the era ----------
def a_contact_name_era(pg):
    """CLAUDE.md: "Jamie ✨" → "Jamie 💙" → "Jamie". The first night cannot use the 2026 name."""
    bad = []
    s = _cues_src()
    # Song 14's her-side cues are the FIRST NIGHT (Sept 3 2021), whatever date op the cue carries —
    # the date is set by its neighbours. Any bare "Jamie" there is the 2026 name in 2021.
    early = []
    for blk in re.split(r"(?=\{id:')", s):
        m = re.match(r"\{id:'(14\.[1-9])'", blk)
        if not m:
            continue
        if re.search(r"(contact|title|n):'Jamie'(?!\s*\u2728|\s*\U0001F499)", blk):
            early.append(m.group(1))
    if early:
        bad.append('on the first night her contact for him reads the 2026 name "Jamie" at '
                   + ', '.join(sorted(set(early))) + ' — the law says ✨ then 💙 then bare')
    # …and the 2026 songs must NOT still be on the early name
    for song, want in (("1.", 'bare'),):
        for blk in re.split(r"(?=\{id:')", s):
            mm = re.match(r"\{id:'(1\.[0-9])'", blk)
            if mm and ('Jamie \u2728' in blk or 'Jamie \U0001F499' in blk):
                bad.append(f'{mm.group(1)}: June 2026 still uses an early contact name for him')
    return bad


# ---------- D-061 · one Linda Whitfield ----------
def a_one_whitfield(pg):
    """Two names for her is CORRECT and is the chain of custody, not a break in it: he saves a
    stranger's office number from Dr. Adler's tip as "Ms. Whitfield (office)" in 2021, and by the
    time she is his agent of three years she is "Linda Whitfield" — the same progression the law
    sets for "Jamie ✨ → Jamie 💙 → Jamie". What must never happen is the order reversing."""
    bad = []
    s = _cues_src()
    office, full = [], []
    for blk in re.split(r"(?=\{id:')", s):
        m = re.match(r"\{id:'(\d+)\.", blk)
        if not m:
            continue
        song = int(m.group(1))
        if 'Ms. Whitfield (office)' in blk:
            office.append(song)
        if re.search(r"Linda Whitfield", blk):
            full.append(song)
    if not office or not full:
        return []          # only one form in the show: nothing to order
    if max(office) > min(full):
        bad.append(f'the office number reappears (song {max(office)}) after she is already saved '
                   f'as Linda Whitfield (song {min(full)}) — the contact went backwards')
    return bad


# ---------- D-062 · the census's camera test can actually fail ----------
def a_census_can_fail(pg):
    """The census flags a camera move that is too fast. Prove the test DISCRIMINATES by feeding it
    the engine's own transition strings — real slow glides must pass, real fast ones must be
    caught. A source grep proves nothing; this runs the predicate."""
    bad = []
    src = open('qc_census.py', encoding='utf-8').read()
    # RUN THE CENSUS'S OWN FUNCTION, don't pattern-match its source. The test used to be an inline
    # expression and is now a parsed duration against a floor; a grep for the old shape reported
    # "it may have been renamed" while the test was present and working. Lift the real helper and
    # the real floor out of the file and exercise them.
    fn = re.search(r"(def _transform_secs\(.*?)(?=\n(?:def |[A-Za-z_]+\s*=|#\s*-{3,}))", src, re.S)
    floor = re.search(r"elif dur < ([\d.]+):", src)
    if not fn or not floor:
        return ['could not find the FAST CAMERA test in qc_census.py — it may have been renamed']
    ns = {'re': re}
    exec(fn.group(1), ns)
    _ts, LIM = ns['_transform_secs'], float(floor.group(1))

    def flags(tr):
        d = _ts(tr)
        return d is not None and d < LIM               # the census's own rule, verbatim

    # the real strings this engine emits, collected from the page
    real = pg.evaluate("""(()=>{ const out=[]; const t=camTempo();
        [1.4, 0.8, 1.0, 0.5, 2.2].forEach(d=>out.push(
          `transform ${(d*t).toFixed(2)}s cubic-bezier(.33,.02,.16,1)`));
        out.push('transform .8s cubic-bezier(.4,0,.2,1)');
        out.push('transform 1s cubic-bezier(.65,0,.25,1), opacity .8s ease');
        return out; })()""")
    slow = [t for t in real if float(re.search(r'([\d.]+)s', t).group(1)) >= 1.4]
    fast = [t for t in real if float(re.search(r'([\d.]+)s', t).group(1)) < 1.4]
    for t in slow:
        if flags(t):
            bad.append(f'the census calls a legitimate slow glide fast: "{t}"')
    caught = [t for t in fast if flags(t)]
    if fast and not caught:
        bad.append('the FAST CAMERA test caught none of '
                   + '; '.join(f'"{t}"' for t in fast) + ' — it cannot fail')
    return bad


# ---------- D-063 · no black gutter beside the phone ----------
def a_no_gutter(pg):
    bad = []
    boot(pg)
    i = song_ix(pg, 9)
    pg.evaluate(f'si={i}; ci=0; animTok++; animRunning=false; hardRender();')
    pg.wait_for_timeout(200)
    # 9.1 is the card alone and 9.1a raises his phone: fire until the phone is actually up
    for _ in range(3):
        fire(pg)
        if pg.evaluate("!!document.querySelector('#projDevice .iphone')"):
            break
    r = pg.evaluate("""(()=>{ const pj=document.getElementById('projection').getBoundingClientRect();
        const era=document.getElementById('era'); const dev=document.querySelector('#projDevice .iphone');
        if(!era||!dev) return null;
        const e=era.getBoundingClientRect(), d=dev.getBoundingClientRect();
        return {zone:+(ERA_ZONE_()*100).toFixed(1), stripLeft:Math.round(e.left-pj.left),
                stripW:Math.round(e.width), phoneRight:Math.round(d.right-pj.left),
                frameW:Math.round(pj.width)}; })()""")
    if not r:
        return ['no phone and strip on stage to measure']
    gutter = r['stripLeft'] - r['phoneRight']
    if gutter > 40:
        bad.append(f'{gutter}px of black between the phone and the strip — ERA_ZONE_ reserves '
                   f'{r["zone"]}% of the frame for a strip {round(r["stripW"]/r["frameW"]*100,1)}% wide')
    return bad


# ---------- D-064 · no dead duplicate renderer ----------
def a_no_dead_renderer(pg):
    """Two renderers share these names; the later declaration wins. Removing ~1200 lines of dead
    code two days before a run is the wrong risk, so the rule is: every shadowed copy carries a
    loud DO-NOT-EDIT marker, and the LIVE copy is the one the page actually resolves. Both are
    asserted here, and the page is asked which copy it is running rather than being trusted."""
    bad = []
    src = open('index.html', encoding='utf-8').read()
    for fn in ('deviceHTML', 'screenHTML', 'callHTML', 'paintAll'):
        hits = [i for i in range(len(src)) if src.startswith('function ' + fn + '(', i)]
        if len(hits) <= 1:
            continue
        for i in hits[:-1]:                      # every copy but the last is shadowed
            if 'DEAD CODE' not in src[max(0, i - 700):i]:
                bad.append(f'{fn} is defined {len(hits)} times and a shadowed copy carries no '
                           f'DO-NOT-EDIT marker — an edit can land there and do nothing')
    live = pg.evaluate("""(()=>({dev: deviceHTML.toString().includes('non-diegetic'),
                                 pa: paintAll.toString().includes('const preshow')}))()""")
    if live['dev'] or live['pa']:
        bad.append('the page is running a copy marked dead — the marker is on the wrong one')
    return bad


# ---------- D-065 · the photo bed, once photographs land ----------
def a_bed_quality(pg):
    bad = []
    boot(pg)
    pg.evaluate("""(()=>{ const px='data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7';
        window.L5Y_LOOP={ml:[],ac:[]};
        for(let i=0;i<24;i++){ const e={k:'img',s:px,r:1.5}; window.L5Y_LOOP.ml.push(e); window.L5Y_LOOP.ac.push(e); }
        pileStop(); pileReset(); const st=buildState(SHOW[0],0); st.housecard=true; setStamp(st); })()""")
    pg.wait_for_timeout(300)
    pg.evaluate("(()=>{ for(let i=0;i<10;i++){ pileDrop(); const S=PILE_S(); if(S.t){clearTimeout(S.t); S.t=null;} } })()")
    pg.wait_for_timeout(400)
    # THE BED FADES IN OVER 1.2 s. Read it settled, or the probe grades the fade instead of the bed
    # (it read 0.43, 0.08 — whatever the ramp had reached when the timer fired).
    last = -1
    for _ in range(30):
        op = pg.evaluate("+getComputedStyle(document.getElementById('loop')).opacity")
        if abs(op - last) < 0.005 and op > 0:
            break
        last = op
        pg.wait_for_timeout(100)
    r = pg.evaluate("""(()=>{ const L=document.getElementById('loop');
        const w=innerWidth; const out=[...L.querySelectorAll('.print')].map(e=>{
          const b=e.getBoundingClientRect(); return {l:Math.round(b.left), r:Math.round(b.right)}; });
        const tilts=new Set([...L.querySelectorAll('.pw')].map(e=>(e.style.transform||'').match(/rotate\\(([^)]+)\\)/)?.[1]));
        return {out, w, op:+getComputedStyle(L).opacity, tilts:[...tilts].length}; })()""")
    # A PRINT HANGING OFF THE EDGE IS NOW THE DIRECTION, NOT THE DEFECT (David, Sept 22: the bed
    # "can completely envelope the screen"). The field is meant to continue past the frame. What
    # would still be wrong is a print dealt so far out that it is more off the stage than on it —
    # that is a wasted photograph, not an enveloping one.
    lost = [p for p in r['out'] if min(p['r'], r['w']) - max(p['l'], 0) < (p['r'] - p['l']) * 0.42]
    if lost:
        bad.append(f'{len(lost)} of {len(r["out"])} prints are dealt more off the stage than on it')
    if r['op'] < 0.6:
        bad.append(f'the bed runs at {r["op"]:.2f} opacity — a photograph over near-black will be muddy at 25 ft')
    if r['tilts'] <= 1:
        bad.append('every print carries the identical tilt — the per-print variation never renders')
    return bad
