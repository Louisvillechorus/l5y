"""CONTACT SHEET — every cue of the show, settled AND mid-flight, tiled so a human can see
the whole night at once. This is how framing bugs get caught before David catches them.
Usage: CHROMIUM_PATH=... python3 qc_contact.py [song ...]
"""
import io, os, sys
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

FILE = 'file://' + os.path.abspath('L5Y-Show-STANDALONE.html')
OUT = 'qa/contact'
COLS, TW = 4, 480


def sheet(shots, path, title):
    if not shots:
        return
    th = TW * 9 // 16
    rows = (len(shots) + COLS - 1) // COLS
    im = Image.new('RGB', (COLS * TW, rows * (th + 22) + 26), (14, 16, 22))
    d = ImageDraw.Draw(im)
    d.text((8, 7), title, fill=(233, 199, 102))
    for i, (label, png) in enumerate(shots):
        t = Image.open(io.BytesIO(png)).convert('RGB').resize((TW, th), Image.LANCZOS)
        x, y = (i % COLS) * TW, 26 + (i // COLS) * (th + 22)
        im.paste(t, (x, y))
        d.text((x + 5, y + th + 4), label, fill=(190, 198, 214))
        d.rectangle([x, y, x + TW - 1, y + th - 1], outline=(40, 46, 60))
    im.save(path)
    print('wrote', path, f'({len(shots)} frames)')


def run(want):
    os.makedirs(OUT, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or None)
        pg = b.new_page(viewport={'width': 1920, 'height': 1080})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(FILE)
        pg.wait_for_timeout(800)
        pg.evaluate('startAs("projection")')
        for i in range(pg.evaluate('SHOW.length')):
            n = pg.evaluate(f'SHOW[{i}].n')
            if want and n not in want:
                continue
            shots = []
            pg.evaluate(f'si={i}; ci=0; animTok++; animRunning=false; hardRender();')
            pg.wait_for_timeout(250)
            for k in range(pg.evaluate(f'SHOW[{i}].cues.length')):
                cid = pg.evaluate(f'SHOW[{i}].cues[{k}].id')
                pg.evaluate('advance()')
                pg.wait_for_timeout(450)
                shots.append((f'{cid} +0.45s', pg.screenshot()))      # mid-flight: where the jarring lives
                waited = 450
                while waited < 40000 and pg.evaluate('animRunning'):
                    pg.wait_for_timeout(200)
                    waited += 200
                shots.append((f'{cid} settled', pg.screenshot()))
            sheet(shots, f'{OUT}/song{n:02d}.png', f'SONG {n} · {pg.evaluate(f"SHOW[{i}].t")}')
        b.close()
    if errs:
        print('JS ERRORS:', errs[:4])


if __name__ == '__main__':
    run({int(a) for a in sys.argv[1:] if a.isdigit()})
