"""DAVID'S NOTES GATE — trackable, traceable, provable, repeatable.

Every note in notes.json names a proof. A proof lives in one of the qc_notes_*.py
probe files as a function of the same name taking (pg) and returning [] or a list
of complaints. This runs every probe once, against the built STANDALONE, on the
LIVE path (advance(), like the operator), and prints a line per note.

A note whose status is 'fixed' but whose proof is missing or failing FAILS the gate.
Usage: CHROMIUM_PATH=/opt/pw-browsers/chromium python3 qc_notes.py [--all]
"""
import glob, importlib.util, json, os, sys

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


def run():
    reg = json.load(open('notes.json'))['notes']
    pr = probes()
    broken = {k: v for k, v in pr.items() if k.startswith('!')}
    rows, failed = [], []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or None)
        for n in reg:
            fn = pr.get(n['proof'])
            if not callable(fn):
                rows.append((n, 'NO PROBE', ['no probe named ' + n['proof']]))
                if n['status'] == 'fixed':
                    failed.append(n['id'])
                continue
            pg = b.new_page(viewport={'width': 1920, 'height': 1080})
            errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.goto(FILE)
            pg.wait_for_timeout(700)
            try:
                bad = list(fn(pg)) + [f'JS ERROR: {e}' for e in errs[:2]]
            except Exception as e:
                bad = [f'probe crashed: {e}']
            pg.close()
            rows.append((n, 'PASS' if not bad else 'FAIL', bad))
            if bad and n['status'] == 'fixed':
                failed.append(n['id'])
        b.close()
    show_all = '--all' in sys.argv
    for n, verdict, bad in rows:
        mark = {'PASS': '✓', 'FAIL': '✗', 'NO PROBE': '·'}[verdict]
        if not show_all and n['status'] in ('blocked', 'confirm') and verdict != 'FAIL':
            continue
        print(f"{mark} {n['id']}  {n['status']:<8} {verdict:<9} {n['note'][:72]}")
        for x in bad[:3]:
            print(f"      → {x}")
    if broken:
        print('BROKEN PROBE FILES:', {k: str(v)[:90] for k, v in broken.items()})
    open_n = [n['id'] for n, v, _ in rows if n['status'] == 'open']
    print(f"\n{len(reg)} notes · {len(open_n)} open · {len(failed)} regressions")
    if failed:
        print('REGRESSIONS (marked fixed, proof failing):', ', '.join(failed))
    return 1 if (failed or broken) else 0


if __name__ == '__main__':
    sys.exit(run())
