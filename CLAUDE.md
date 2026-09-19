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
Meet Sept 3 2021 · movers-in Oct 2021 (Sat Oct 16) · proposal June 12 2023 (the rowboat) · **wedding May 18 2024** (the only shared date) · Ohio summers 2024, 2025 & 2026 (she is in Ohio when he leaves — "what time does your flight land") · pier birthday July 19 2025 (he visits and leaves early) · Cathy's Stelmyer call May 9 2025 · Elise/R.H. affair seeded May 2024 → Feb 2025 ("for you I'm always up") → April 2026 · **his last day is Thursday June 11 2026**: before dawn with Elise (song 13), the afternoon he packs, writes the pad and leaves the ring on the table (song 14), breakup email "Some practical things" (lawyer at 2:50, her at 4:12 — he told the lawyer first) · **she reads the pad Friday June 12 2026, 9:41 AM** (song 1); her final text READ 9:44, never answered; the ring only reaches her with the note, so nothing before Thursday can mention it · show ends on her, 2021, still typing. Whitfield is his literary AGENT (Linda; agency never named — he saved her office number as "Ms. Whitfield (office)"); The Atlantic Monthly prints his chapter; Random House is Elise's house; Stelmyer's agency is never named. Jamie escalates by silence and administration (accounts, movers, lawyers); Cathy escalates by asking. His ghosts are cowardice; hers are courage. He cannot delete anything about her (Cancel, every time) except the two sharing buttons he does press: Stop Sharing and Leave Playlist.

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
miles east of Cincinnati per the script) · **2025** Ohio round two, day one — the bear (M2 — Jamie IS in the frame: he is giving her the bear, David Sept 19). The pier (M1, July 19, 2025) is Song 3's post only — it can never be a June 12
memory. Never reintroduce a 2021 card.

## Song 7 is special
Song 7 will be **one prerecorded FaceTime** (Jamie half-attending at his desk, writing). Do not build elaborate cueing inside 7; keep the FaceTime frame and the log; the video content is produced separately.

## Direction locked Sept 14, 2026 (team call — David, Alonzo, Peyton)
- **The rig is a 75″ LANDSCAPE TV, audience up to 25 ft.** Readability rules everything.
  **FRAMING (David, Sept 18 — supersedes the close-up default): THE WHOLE PHONE IS ALWAYS
  ON STAGE.** Nothing is cropped, nothing re-aims mid-cue, and the presenter preview is
  exactly the projection. Legibility comes from the phone running iOS Larger Text (`.fs` = 2.4% of the
  phone height via `--ph`, so the preview and the projection lay out identically), not from a zoomed window. `CLOSEUP_DEFAULT=false` in the engine; a cue may
  still ask for a close-up explicitly with `{op:'frame', z, at}` — none do in the show.
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
- **Simplicity**: target one or two screen moments per song; black (era-center) is the
  default state while they sing.
- **Song 3 is `who:'both'`** by direction: Jamie's calls appear inside Cathy's song; she has
  no phone in it (her pier post was cut Sept 18).

## TORN SCORE (David, Sept 19 — the facelift; supersedes anything above it contradicts)
- **Stage**: dark ground; the phone bezel-less and squared; NO rails; **NO character names anywhere on
  stage** (David, Sept 19 — it is obvious whose phone it is). **THE ERA IS ONE CONTINUOUS ARTIFACT**
  (`#era`): a torn calendar pad center-stage when the phone is away (a small YEAR label, the
  NUMERAL as the hero, the month beneath, a foot line), a torn paper strip docked at the right when a device is up — **the month small and
  horizontal at the top, YEAR huge running down the strip, the number at the foot** (the year outranks
  the month). It transforms between homes (`setEraHome`), it never disappears.
- **PAPER** is generated in the engine (`paperTex`): a lit heightfield — flat facets, sharp fold
  creases (two warped Voronoi seam layers, only some seams creased), three long folds, ridged
  micro-wrinkles, fibre grain — in four tones (white, cream, grey, off-white), seeded. David's
  references: photos of real crumpled sheets. Real scans can replace it: drop files in
  `assets/paper/` and build.py embeds them as `window.L5Y_PAPER`.
- **TIME ONLY EVER CHANGES ON THE CALENDAR** (`eraRoll`): forward = pages tear off and fall;
  backward = pages rise and settle. Long journeys skip months (≤16 pages, ~3 s at a song top,
  ~2 s mid-song). The phone never rolls; a dated `clock` op rolls the era, then `device` docks it
  and the phone rises already at the new time. `stamp` is now the calendar's FOOT line.
- **YEAR 1…5**, never real years on stage: Year N = years since the night they met (Sept 3);
  the real dates stay in cues.js (`yearN()` derives the label). The wedding is May · Year 3.
- **The phone only comes up when it is used.** Calendar-only songs: 5, 8 (three moves), 11.
- **Preshow / intermission**: the falling torn pages loop (photos, text, score) with a title page.
  **Prologue** = one GO: the title lifts, the pages thin out and the last blows away (~52 s),
  then the calendar lands. **Curtain** (`curtain` op) = true black.
- **THE CAMERA (David, Sept 19 — supersedes "the whole phone is always on stage")**: the frame is
  ALWAYS a window into the phone; the phone is never shown phone-sized. The docked strip owns the
  right 15% of the frame (`ERA_ZONE`); the phone fills the rest (`camRest`, up to `CAM_FILL`=3.5×),
  anchored to the top of the register (bottom for a thread or Find My's card), and on a beat the
  camera pans and tightens on what matters (`camPush(sel,z)`: the notification, the field, the
  last bubble, the receipt, the card, the button, the inbox row, the mail body). z is the ask; the
  fit clamps it so a target is never cropped; the phone never shows black above or below once it
  is taller than the frame. Moves land slowly (ease-out ~0.95 s), rests glide (~0.85 s), a breath
  of drift keeps the shot alive. Product-demo grammar: establish → push → hold → release; every
  register change pulls to rest first. The MacBook (song 7) and the dash (song 12) fill the frame
  natively. The presenter preview is a 16:9 frame running the same camera (with its own strip).
- **CARPLAY (song 12)**: the drive plays on the dash — `dev:'carplay'`, a landscape head unit
  (sidebar: clock, signal, recent apps, home; Maps with the maneuver card and the trip card over the
  map, the same live route model as the phone). The dash clock rides with the trip.
- **SOUND (David, Sept 19 — the licensed iOS set)**: the real system sounds live in `assets/sfx/`
  (SentMessage, ReceivedMessage, sms-received1 = the lock-screen text tone, new-mail, mail-sent,
  key_press_*, Tock, lock, Swish, vc~ringing = the FaceTime ring, vc~ended, vc~invitation-accepted,
  Reflection.m4r = the ringtone, ct-* call tones). build.py embeds them into the STANDALONE and
  docs (never into index.html); the engine decodes Core Audio Format itself (`cafDecode`: lpcm
  and ima4) and plays the mapped sample (`SFX_MAP_`, `sample`); the synthesized sounds in `sfx()`
  remain the fallback, so a missing file never silences a beat. Paper (tear, settle, flutter,
  rustle) stays synthesized. Ringback (outgoing phone) is synthesized — it is a network tone.
  Sound plays only from the window the operator clicked Start in; a window we opened ourselves
  (`?view=projection`) is silent unless its checkbox says otherwise; speaker button → volume popover.
- **OPERATOR SAFETY (Sept 19 review)**: one `setBlackout()` for key, button and the other window;
  a RELOADED presenter resumes at the saved cue (`l5y_pos`, reload only, 3 h); resize never cancels
  a running cue; `hardRender` stops rings and clears camera timers; GO keys are ignored while the
  volume slider has focus; Esc does nothing in the projection window; Google Fonts load
  non-blocking (theatre Wi-Fi must never stall the engine).
- **Presenter**: song + cast + character, NOW with progress, the GO card, THEN, the whole queue,
  BLACKOUT and MENU buttons. Nothing else.
- Restore point before this sprint: git tag `restore-sept18-line-by-line`.

## THE LINE-BY-LINE BUILD (David, Sept 18 — the spec; 65 cues after Sept 19)
- **1** prologue = the falling pages wind down (one GO, no phone); on her verse-2 line the phone
  rises and she sends her text (auto); READ 9:44, his typing bubble, it stops; then she opens the
  Memories — four cards, the BEAR (M2) last, she drifts back up to it; cutoff = phone away.
- **2** 2.1 the roll then his lock screen; 2.2 = ONE ~50 s piece (three drafts → “home safe?” →
  Delivered → her typing bubble); 2.3 her call; 2.4 hang up. Same-night compression kept.
- **3** era-center only for her; Jamie's three calls (Whitfield ×2, Rob — he dials, per the
  script) with return rolls; hang-up on the downbeat of 4.
- **4** her Stelmyer call (dial → connect → end), then his notifications. **5** calendar only (the dedication is CUT). **6** his lock screen,
  Christmas wallpaper, whole song. **7** the FaceTime arc (ring → V2 → Call Ended → black).
- **8** calendar only: engagement → wedding → engagement on the singers' lines; **8.4 = INTERMISSION**
  (the falling pages; holds until 9.1). **9** notifications only. **10** “break a leg” before her first note, two
  rejection emails, black, the bell-tone FLASHBACK to NOVEMBER 2023 (his long text), return.
- **11** timeline only (one cue). **12** THE DRIVE on CARPLAY: Apple Maps on the dash for the whole
  song, time-based (`mapsdrive`, `dur` seconds to arrival — tune in tech), the dash clock runs with it.
- **13** two beats: her text lands (5:05 AM — before dawn means before the 5:24 sunrise) and he
  swipes it away; on his last line, Find My → Share My Location → Share Indefinitely (it was OFF
  before the song; never shown turning off). Her Ohio is **Mount Orab, OH** (forty miles east of
  Cincinnati, per the script — confirmed by David, Sept 19). 4.8 keeps “SONNY READ IT.” (David’s call).
- **Continuity law (Sept 19)**: her Friday thread (1.2) carries Thursday — the flight text from
  13.2 verbatim, “landed?”, “I read it. please call me”, “I’m not angry. just talk to me” — because
  his last day is June 11; nothing in it may imply he moved out earlier. Calls connect at 0:00.
  Her contact for him is “Jamie 💙” through June 2024 (7.1). The drive is dated Nov 6 2021 (after
  the Oct 16 move-in) — if the licensed script's drive contains the move-in invitation, David must
  re-date it; never fill that from memory.
- **14** era flips with the singer; her one animation (his “home safe?” lands, she opens it,
  types, never sends); his last verse rolls to JUNE 2026 and holds; FINAL BLACKOUT = true black.
- Instrumental passages auto-play from one GO using `{op:'pause', ms}` beats — tunable in tech.
- Assets: M24, M15, M3a, M2 (now THE BEAR), M4 (Song 1), M23 (Song 6), V2 (Song 7), plus loop-only
  photos (S00-LOOP-…). CUT: M1, M7/M7b, M12.
- **Never quote the script in chat.** Trigger fragments live only in `cues.js`, short.
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
