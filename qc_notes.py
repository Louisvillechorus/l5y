"""DAVID'S NOTES GATE — trackable, traceable, provable, repeatable.

Every note in notes.json names a proof. A proof lives in one of the qc_notes_*.py
probe files as a function of the same name taking (pg) and returning [] or a list
of complaints. This runs every probe once, against the built STANDALONE, on the
LIVE path (advance(), like the operator), and prints a line per note.

A note whose status is 'fixed' but whose proof is missing or failing FAILS the gate.
Usage: CHROMIUM_PATH=/opt/pw-browsers/chromium python3 qc_notes.py [--all] [--only D-001,D-005] [--fast]
  --only   run just these notes (seconds, not the full sweep) — use while fixing one thing
  --fast   skip the probes that take minutes (the show-wide sweeps); NEVER the shipping run
  --all    also print blocked/confirm rows that are behaving as expected

The closure law needs a FULL clean run on a new build, so --only and --fast do not advance
the clean counter. Only the whole gate can close a loop.
"""

# SHOW-WIDE SWEEPS — the probes that walk all 69 cues. Each is worth minutes on the shipping run
# and is skipped by --fast so the operator's loop in tech stays under a minute. Measured, not guessed:
# a_maybe_cathy 84s · a_13_to_14 48s · a_subject_never_sliced ~20min · a_bows 3.3min.
SLOW = {'a_subject_never_sliced', 'a_bows', 'a_photo_bed', 'a_ringback_twice',
        'a_105_hold', 'a_app_tap_visible', 'a_call_buttons_match', 'a_timer_format',
        'a_maybe_cathy', 'a_13_to_14', 'a_fills_window', 'a_one_scale_per_register',
        'a_stack_whole', 'a_23_pingpong', 'a_call_controls', 'a_laptop_legible',
        'a_one_receipt', 'a_no_lowbat', 'a_unlock_audible', 'a_era_never_overlays',
        'a_no_stray_pages', 'a_predict_matches', 'a_map_moves', 'a_dash_legible'}
import glob, hashlib, importlib.util, json, os, sys, time

from playwright.sync_api import sync_playwright

FILE = 'file://' + os.path.abspath('L5Y-Show-STANDALONE.html')


def probes():
    """every a_* function found in the qc_notes_*.py probe files, by name"""
    out = {}
    for path in sorted(glob.glob('qc_notes_*.py')):
        spec = importlib.util.spec_from_file_location(path[:-3], path)
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
        except Exception as e:                       # a broken probe is a failing probe, never a silent skip
            out['!' + path] = e
            continue
        for name in dir(mod):
            if name.startswith('a_'):
                out[name] = getattr(mod, name)
    return out


def build_id():
    return hashlib.md5(open('L5Y-Show-STANDALONE.html', 'rb').read()).hexdigest()[:12]


def run():
    doc = json.load(open('notes.json'))
    reg = doc['notes']
    bid = build_id()
    only = set()
    for a in sys.argv:
        if a.startswith('--only'):
            only = {x.strip().upper() for x in a.split('=', 1)[-1].replace('--only', '').split(',') if x.strip()}
    if '--only' in sys.argv:
        i = sys.argv.index('--only')
        if i + 1 < len(sys.argv):
            only = {x.strip().upper() for x in sys.argv[i + 1].split(',') if x.strip()}
    fast = '--fast' in sys.argv
    partial = bool(only) or fast
    if only:
        reg = [n for n in reg if n['id'].upper() in only]
        if not reg:
            print('no notes matched --only'); return 1
    pr = probes()
    broken = {k: v for k, v in pr.items() if k.startswith('!')}
    rows, failed = [], []
    with sync_playwright() as p:
        # THE AUDIO PROBES MUST BE ABLE TO HEAR. Without this flag Chromium keeps the AudioContext
        # suspended until a user gesture, so every sound probe grades a graph that was never allowed
        # to run and reports the fix missing. It cost four false regressions in one gate run.
        b = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or None,
                              args=['--autoplay-policy=no-user-gesture-required'])
        ctx = b.new_context(viewport={'width': 1920, 'height': 1080})   # probes may open a second window
        for n in reg:
            if fast and n['proof'] in SLOW:
                rows.append((n, 'SKIPPED', []))
                print(f"  ~ {n['id']} skipped (slow)", flush=True)
                continue
            fn = pr.get(n['proof'])
            if not callable(fn):
                rows.append((n, 'NO PROBE', ['no probe named ' + n['proof']]))
                if n['status'] == 'fixed':
                    failed.append(n['id'])
                continue
            pg = ctx.new_page()
            errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.goto(FILE)
            pg.wait_for_timeout(700)
            t0 = time.time()
            try:
                bad = list(fn(pg)) + [f'JS ERROR: {e}' for e in errs[:2]]
            except Exception as e:
                bad = [f'probe crashed: {e}']
            n['secs'] = round(time.time() - t0, 1)   # so a slow probe can be found and moved to SLOW
            pg.close()
            ok = not bad
            # WAITING ON A PERSON IS NOT A BROKEN SHOW. Two notes can only be finished by David —
            # the licensed paper scans, and the worksheet pass over the quoted lines — and their
            # probes say so in words. Printed as failures they sat in the same column as real
            # breakage, and a gate that is permanently red is a gate people stop reading. They get
            # their own verdict and their own line in the summary; they still cannot be forgotten,
            # because they are still listed every single run.
            waiting = bool(bad) and all(str(x).startswith('WAITING ON') for x in bad)
            # THE CLOSURE LAW: a clean run only counts if the build has changed since the last one,
            # and only a FULL run counts at all — a targeted check cannot close a loop.
            if ok:
                # A PARTIAL RUN NEVER ADVANCES A LOOP — and must never UNDO one either. This used to
                # fall through to the reset on a passing --only run, knocking notes that were one
                # clean build from closure back to zero for having been spot-checked.
                if not partial and n.get('last_build') != bid:
                    n['clean'] = n.get('clean', 0) + 1
                    n['last_build'] = bid
            else:
                n['clean'] = 0
                n.pop('last_build', None)
            if ok and n['status'] == 'fixed' and n.get('clean', 0) >= 2:
                n['status'] = 'closed'
            rows.append((n, 'PASS' if ok else ('WAITING' if waiting else 'FAIL'), bad))
            print(f"  {'✓' if ok else ('⏸' if waiting else '✗')} {n['id']} {n.get('secs', 0):>5.1f}s {n['status']:<8}"
                  f"{'' if ok else '  ' + bad[0][:90]}", flush=True)
            if bad and not waiting and n['status'] in ('fixed', 'closed'):
                failed.append(n['id'])
        b.close()
    # MERGE, NEVER CLOBBER. This used to write back the whole document it read at start, so any note
    # added to notes.json while a 40-minute run was in flight was silently erased on completion —
    # it cost the entire law audit once. Re-read the file now and touch ONLY the fields this run
    # actually decided, for the notes it actually ran.
    try:
        live = json.load(open('notes.json'))
    except Exception:
        live = doc
    ran = {n['id']: n for n, _, _ in rows}
    for n in live['notes']:
        r = ran.get(n['id'])
        if not r:
            continue
        for k in ('status', 'clean', 'last_build', 'secs'):
            if k in r:
                n[k] = r[k]
            elif k in n and k in ('last_build',):
                n.pop(k, None)
    json.dump(live, open('notes.json', 'w'), indent=1, ensure_ascii=False)
    show_all = '--all' in sys.argv
    for n, verdict, bad in rows:
        mark = {'PASS': '✓', 'FAIL': '✗', 'WAITING': '⏸', 'NO PROBE': '·', 'SKIPPED': '~'}[verdict]
        if not show_all and n['status'] in ('blocked', 'confirm') and verdict != 'FAIL':
            continue
        seal = {0: '', 1: ' [1 of 2 clean]'}.get(n.get('clean', 0), ' [CLOSED]')
        secs = f" {n['secs']:>5.1f}s" if n.get('secs') else '       '
        print(f"{mark} {n['id']}{secs}  {n['status']:<8} {verdict:<9} {n['note'][:56]}{seal}")
        for x in bad[:3]:
            print(f"      → {x}")
    if broken:
        print('BROKEN PROBE FILES:', {k: str(v)[:90] for k, v in broken.items()})
    open_n = [n['id'] for n, v, _ in rows if n['status'] == 'open']
    closed = [n['id'] for n, v, _ in rows if n['status'] == 'closed']
    pend = [n['id'] for n, v, _ in rows if n['status'] == 'fixed' and n.get('clean', 0) == 1]
    waiting_n = [n['id'] for n, v, _ in rows if v == 'WAITING']
    print(f"\n{len(reg)} notes · {len(open_n)} open · {len(closed)} CLOSED · "
          f"{len(pend)} awaiting a second clean build · {len(waiting_n)} waiting on David · "
          f"{len(failed)} regressions")
    if waiting_n:
        print('WAITING ON DAVID (not a code fault):', ', '.join(waiting_n))
    if pend:
        print('one more clean build closes:', ', '.join(pend))
    slowest = sorted((n.get('secs', 0), n['id'], n['proof']) for n, _, _ in rows)[-5:]
    print('slowest probes:', ', '.join(f'{i} {p} {t:.0f}s' for t, i, p in reversed(slowest) if t))
    if failed:
        print('REGRESSIONS (marked fixed, proof failing):', ', '.join(failed))
    if partial:
        print('PARTIAL RUN — this cannot close a loop; the closure law needs the full gate.')
    return 1 if (failed or broken) else 0


if __name__ == '__main__':
    sys.exit(run())
