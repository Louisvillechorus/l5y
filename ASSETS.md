# ASSETS.md — media the team must produce
**The source of truth is the shot list:** `L5Y-Shot-List.pdf` (stage manager's copy), `SHOTLIST.md`, `L5Y-Shot-List.docx` — all generated from `shotlist.json` (`python3 build_shotlist.py && node build_shotlist_docx.js && python3 build_shotlist_pdf.py`).

## Two casts
Maegan & Landon (ML) and Andrew & Charlie (AC) alternate. The show is one build; the operator picks the couple on the start screen and every asset code resolves to that couple's file. Each per-cast asset is shot twice, same composition; SHARED assets (no people) are shot once.

## Filename convention
`S<song>-<code>-<what>-<CAST>.<ext>` — e.g. `S03-M1-pier-golden-hour-ML.jpg`, `S05-M12-dedication-for-cathy-SHARED.jpg`, `S07-V2-facetime-jamie-desk-AC.mp4`. The code is what the engine reads (`CAST_ASSETS.ml` / `.ac`); the rest is for humans. Upload flat into one Drive folder, **L5Y ASSETS**. A missing file keeps its greeked placeholder — the show never breaks.

## Also to produce
Cathy's recorded 0:47 voicemail VO (A1, original words, not lyrics) — only if the voicemail beat survives the Song 14 decisions.
