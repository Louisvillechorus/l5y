"""Extract book.json from the live build — the state record the audits run on.
For every cue: the register before it (preApp), after it (app), the device,
and the raw ops. audit_teleports.py consumes this; build_bible_data.py uses a
richer superset captured the same way.
Usage: python3 extract_book.py   (writes book.json next to the standalone)
"""
import json
import os

from playwright.sync_api import sync_playwright

FILE = 'file://' + os.path.abspath('L5Y-Show-STANDALONE.html')

EXTRACT_JS = """() => {
  const songs = [];
  for (let si = 0; si < SHOW.length; si++) {
    const s = SHOW[si];
    const cues = [];
    for (let k = 0; k < s.cues.length; k++) {
      const pre = buildState(s, k), post = buildState(s, k + 1);
      cues.push({id: s.cues[k].id, dev: post.dev, preApp: pre.app,
                 app: post.app, do: s.cues[k].do});
    }
    songs.push({n: s.n, t: s.t, cues});
  }
  return {songs};
}"""


def run():
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or None)
        pg = b.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(FILE)
        pg.wait_for_timeout(600)
        book = pg.evaluate(EXTRACT_JS)
        b.close()
    if errs:
        raise SystemExit('JS ERRORS during extraction: %s' % errs[:3])
    json.dump(book, open('book.json', 'w'), indent=1)
    n = sum(len(s['cues']) for s in book['songs'])
    print('book.json: %d songs, %d cues' % (len(book['songs']), n))


if __name__ == '__main__':
    run()
