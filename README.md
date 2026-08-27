# The Second Screen — *The Last Five Years* (Redline Performing Arts)
Projection cue system: two phones tell the digital life of Jamie & Cathy, 2021–2026.

**▶ Run the show:** open `L5Y-Show-STANDALONE.html` (double-click; no server needed) — or visit the GitHub Pages URL once enabled.
Presenter on the laptop, ⧉ opens the synced projection window. Space = GO · ← back (crosses songs) · [ ] song · B blackout · F fullscreen.

- `L5Y-Cue-Bible.pdf` — every cue: trigger, verbatim screen content, mechanics, sound, dramaturgy.
- `index.html` + `cues.js` — engine + show data (the standalone is these two fused).
- `CLAUDE.md` — the realism law & canon. Read before proposing changes.
- `build_bible_*`, `qc_legibility.py` — regeneration & QA tooling.
- `docs/index.html` — copy of the standalone for GitHub Pages.
- `ASSETS.md` — every photo/video (M/V code) the team must shoot, with the cues that use it.

**Two-window sync note:** the ⧉ projection window syncs via BroadcastChannel. From a plain double-clicked file some browsers isolate the two windows — if sync fails, use the GitHub Pages URL (or any localhost server); it always works there.

## Development
Edit `cues.js` (show data) or `index.html` (engine), then: `python3 build.py` → run QA (`python3 qc_legibility.py`, `python3 audit_teleports.py` against a fresh book.json) → regenerate the Bible (`python3 build_bible_data.py && node build_bible_docx.js`; needs `npm i` once for the docx package, and `pip install playwright` for QA). `CLAUDE.md` defines the realism law all changes must satisfy.

**Team URL (once Pages is on):** Settings → Pages → Deploy from branch → `main` / `docs`. The show then lives at `https://<user>.github.io/<repo>/` permanently.
