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

SLOW = {'a_subject_never_sliced', 'a_bows', 'a_photo_bed', 'a_ringback_twice',
        'a_105_hold', 'a_app_tap_visible', 'a_call_buttons_match', 'a_timer_format'}
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
        b = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or None)
        ctx = b.new_context(viewport={'width': 1920, 'height': 1080})   # probes may open a second window
        for n in reg:
            if fast and n['proof'] in SLOW:
                rows.append((n, 'SKIPPED', []))
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
            # THE CLOSURE LAW: a clean run only counts if the build has changed since the last one,
            # and only a FULL run counts at all — a targeted check cannot close a loop.
            if ok and not partial:
                if n.get('last_build') != bid:
                    n['clean'] = n.get('clean', 0) + 1
                    n['last_build'] = bid
            else:
                n['clean'] = 0
                n.pop('last_build', None)
            if ok and n['status'] == 'fixed' and n.get('clean', 0) >= 2:
                n['status'] = 'closed'
            rows.append((n, 'PASS' if ok else 'FAIL', bad))
            if bad and n['status'] in ('fixed', 'closed'):
                failed.append(n['id'])
        b.close()
    json.dump(doc, open('notes.json', 'w'), indent=1, ensure_ascii=False)
    show_all = '--all' in sys.argv
    for n, verdict, bad in rows:
        mark = {'PASS': '✓', 'FAIL': '✗', 'NO PROBE': '·', 'SKIPPED': '~'}[verdict]
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
    print(f"\n{len(reg)} notes · {len(open_n)} open · {len(closed)} CLOSED · "
          f"{len(pend)} awaiting a second clean build · {len(failed)} regressions")
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
