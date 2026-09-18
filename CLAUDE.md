# CLAUDE.md — The Second Screen (The Last Five Years)
**Read this before touching anything. This file is law. The director of this system is David (MD). The stage director is Alonzo.**

## What this is
Two projected phone screens tell the digital life of Jamie and Cathy across the five years of *The Last Five Years* (Redline Performing Arts). The engine is `index.html` + `cues.js`; `L5Y-Show-STANDALONE.html` is the single-file build the team opens. Every cue is operator-fired against the live score. Everything is deterministic (seeded) so every night is identical.

## THE PRIME DIRECTIVE: phones behave like phones
Every screen must survive the question **"is this exactly what a real iPhone/MacBook would show this person at this moment?"** If the answer is no, the cue is wrong — no matter how theatrical it looks. David should never have to explain how a phone works. The burden of realism proof is on the builder, before delivery, not on David in review.

### ALWAYS
- **Navigation is real.** Nobody teleports into an app. Unlock → home → tap icon → app opens, or notification-tap → straight in. Every register change is a visible, motivated gesture by the character.
- **Threads have history.** Any conversation between people who know each other opens mid-history, overflowing above the fold, with mundane texts around the dramatic one. The dramatic message must never be the first message in a thread.
- **Senders are correct.** Attachments come from whoever would really have taken the photo. Cathy shoots Ohio; Cathy sends Ohio.
- **Read/unread is earned.** Unread dots and bold rows exist only where the character genuinely has not seen the thing. Wednesday's email is read by Friday.
- **Claims are backed.** "Notes attached" means an attachment bubble exists. A ticket in her inbox has a real reason to be there (a forward from him). Every artifact has a chain of custody.
- **Buttons match state.** A connected call shows mute/end/speaker, never Answer. Incoming shows Answer. Sheets name the real app.
- **Time moves with motion.** Era changes at song tops roll the lock-screen clock (fast-forward or rewind) — the audience watches time travel, never a hard cut between eras.
- **Deletion looks like deletion.** A deleted draft simply backspaces to nothing. Phones do not announce "DRAFT · DELETED." Meta-information lives in the Cue Bible only.
- **State is truth.** Battery, signal, wallpaper, contact names are state, set by cues, consistent across a song, meaningful across the show (9% at dawn; two LTE bars in Ohio; "Jamie ✨" → "Jamie 💙" → "Jamie").
- Real, current-era app design (2021–2026 iOS), correct chrome, correct status bar, newest-first inboxes and notification stacks, new mail lands on top.

### NEVER
- Never caption what a singer is singing. The screens converse with the score; they do not transcribe it.
- Never use Jason Robert Brown's lyrics or any copyrighted text. All written content (Schmuel prose, posts, emails) is original.
- Never invent fallback/filler content in a renderer. If a cue doesn't supply it, the screen is empty.
- Never show a second device inside one song except by declared `cut:` (duets flip by singer; `validatePOV()` enforces).
- Never mix brands (the dating app is **Tinder** everywhere it is readable). Never show fake states ("Not sharing" rows, impossible buttons).
- Never let months pass "invisibly" inside one continuous scene. Time jumps are song-top events, with the clock roll.

## Storyline canon (do not contradict)
Meet Sept 3 2021 · movers-in Oct 2021 · proposal June 2023 · **wedding May 18 2024** (the only shared date) · Ohio summers 2024 & 2025 · pier birthday July 19 2025 (he leaves; forwarded Amtrak receipt) · Elise/R.H. affair seeded May 2024 → Feb 2025 ("for you I'm always up") → April 2026 · breakup by email "Some practical things," June 2026 (lawyer emailed at 2:50, her at 4:12 — he told the lawyer first) · her final text READ 9:44, never answered · show ends on her, 2021, still typing. Jamie escalates by silence and administration (accounts, movers, lawyers); Cathy escalates by asking. His ghosts are cowardice; hers are courage. He cannot delete anything about her (Cancel, every time) except the two sharing buttons he does press: Stop Sharing and Leave Playlist.

## TWO CASTS, ONE SHOW (David, Sept 14)
Two couples alternate performances: **Maegan & Landon** and **Andrew & Charlie**. There is ONE
build, one cues.js, one URL. The couples differ ONLY in which photo/video files the M/V asset
codes resolve to (`CAST_ASSETS.ml` / `CAST_ASSETS.ac` in the engine). **The operator's first
choice on the start screen is tonight's cast** — remembered per browser, synced to the
projection window, shown in the presenter bar. Every content change automatically serves both
casts because cues reference codes, never files; never fork the show per cast, and every asset
must exist in both sets (a missing entry renders the greeked placeholder).

## The prologue memory ladder is FOUR cards (canon arithmetic)
They meet Sept 3, 2021, so Facebook "On This Day" (June 12) can only reach back to 2022:
**2022** nine months in — the couch (M15) · **2023** the proposal, June 12 (the rowboat day
The Next Ten Minutes returns to) · **2024** married three weeks, 600 miles apart (Ohio is forty
miles east of Cincinnati per the script) · **2025** Ohio round two, day one — the card he is
not in (M2). The pier (M1, July 19, 2025) is Song 3's post only — it can never be a June 12
memory. Never reintroduce a 2021 card.

## Song 7 is special
Song 7 will be **one prerecorded FaceTime** (Jamie half-attending at his desk, writing). Do not build elaborate cueing inside 7; keep the FaceTime frame and the log; the video content is produced separately.

## Direction locked Sept 14, 2026 (team call — David, Alonzo, Peyton)
- **The rig is a 75″ LANDSCAPE TV, audience up to 25 ft.** Readability rules everything —
  and **CLOSE-UP IS THE DEFAULT, not an option**: every register auto-zooms to its reading
  region (`AUTOFRAME` in the engine — thread 2.2×, lock/notifications 1.9× top, posts 1.8×…).
  A cue overrides with `{op:'frame', z, at:'top'|'mid'|'bottom'}` or `{op:'frame', off:true}`.
- **The composed stage (revised Sept 14 evening — nothing ever overlays the phone).**
  Landscape is a three-zone stage: **left rail = identity** (CATHY/JAMIE in their color +
  HER PHONE/HIS LAPTOP), **center = the device**, **right rail = the era only** — month
  and year in gold (the stamp, stacked on its `·` separators; no date, no clock — David).
  On every era change the rail **rolls through the months, forward or backward**, then
  settles on the stamp. The close-up renders in a **wide reading window**: the window
  grows to the scaled content width so text is never chopped mid-line — the crop is
  vertical only, to the reading region. **The phone case is neutral graphite** (a real
  iPhone bezel — identity lives on the rail, not the hardware). **The MacBook takes the
  whole screen** under a top info bar (identity left, era right). Preshow and `dev:'full'`
  drop rails/bar entirely. Portrait/rot support (classic floating overlays) stays in the
  engine but is not the rig.
- **TIME IS ALWAYS VISIBLE (David, Sept 14 night).** Every timeline shift — song tops,
  mid-song flashbacks, AND the returns — plays as a visible roll, forward or backward,
  never a hard cut. **ERA-CENTER**: when the phone rests mid-song (`black` with a stamp in
  state), the stage is not empty black — the gold era takes the center of the screen,
  large, and the rolls play there (the rail's `.rera` is the same element, scaled by
  `body.erastage`). True black only between songs, at preshow, and on manual blackout.
  So a "return" cue is `black` + dated `clock` + `stamp` — the phone goes, time rolls
  home center-stage. **TIME NEVER RESETS (David, Sept 18)**: a song inherits the previous
  song's final era (`freshState` reads `songEndState(idx-1)`), so the outgoing era holds
  center-stage between songs and the next song's first cue rolls FROM it — every song-top
  roll travels the true distance. MONTH + YEAR is on screen at every moment that is not
  an animation; true black exists only at preshow and on the operator's manual blackout. Cathy's Stelmyer call is pinned **MAY 2025** (Friday, May 9 — David;
  her backward line between the pier and the party). **Call timers really tick**: any
  "connected · M:SS" status counts up second by second from the moment it appears
  (`liveTimerHTML`/`.calltimer`), FaceTime duration included. **Song 7 is a full call
  arc**: ringing (FaceTime…) → connected (V2 plays, timer runs) → Call Ended → era holds.
- **No touch dots (cut by David).** The blue finger circles are gone everywhere. Taps read
  the way a real screen recording reads: the beat, the control's own pressed state (icon
  press animation, iOS pressed-gray on rows and buttons via `hover`/`btnHover`), then the
  transition. The `hover`/`tap`/`btnHover`/`btnTap` ops remain as timing + pressed-state beats.
- **Preshow**: the house card (title + the two-handed clock) renders at song 1 · cue 0.
- **Non-diegetic is allowed.** The phone plays even when the actor isn't holding it; in
  those moments the frame may drop away entirely (`dev:'full'` full-bleed stage).
- **Simplicity**: target one or two screen moments per song; black is the default state
  while they sing. Songs 3 is deliberately near-empty (post + likes, then Jamie's call).
- **Song 3 is `who:'both'`** by direction: Jamie's outgoing call appears inside Cathy's song.
- **LINES LAW (supreme)**: trigger lines come ONLY from the licensed script. Every line
  not yet checked against it carries a ⚠CONFIRM flag in the cue data and documents.
  Never write, fix, or fill a script line from memory. `apply_lines.py` +
  `L5Y-Lines-Worksheet.docx` are the reconciliation path.

## Workflow law
1. **Verify before delivering.** Playwright harness must pass: state-integrity (all cues), POV/timeline, legibility QC, `audit_teleports.py` (no register appears without navigation), **`qc_livepath.py` (the operator's GO path: every cue fired via advance(), shell chrome + reading window asserted against settled truth — settled-render sweeps cannot see live-swap bugs)**, zero JS errors — plus a screenshot review of anything visually changed. Never hand David anything unverified.
2. Rebuild = splice `cues.js` into `FALLBACK_SHOW`, emit `L5Y-Show-STANDALONE.html`, `node --check` the script.
3. Regenerate the Cue Bible whenever cue content changes: `extract_book.py` → `build_bible_data.py` → `build_bible_docx.js` (DOCX) + `build_bible_pdf.py` (PDF, headless Chromium). Both render the same `bible.json`, so they cannot drift. The Bible carries: ON SCREEN verbatim, PLAYS mechanics, SOUND, PHONES state, gold dramaturgy notes.
4. Ship: STANDALONE + Bible PDF; push to this repo so the team URL stays current.
5. David's notes are punch lists: fix **every** item, then QA beyond the list in the same spirit. Proactive taste is expected; sloppiness anywhere invalidates polish everywhere.
