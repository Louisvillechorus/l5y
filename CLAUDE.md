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
Meet Sept 3 2021 · movers-in Oct 2021 (Sat Oct 16) · proposal June 12 2023 (the rowboat) · **wedding May 18 2024** (the only shared date) · Ohio summers 2024, 2025 & 2026 (she is in Ohio when he leaves — "what time does your flight land") · pier birthday July 19 2025 (he visits and leaves early) · Cathy's Stelmyer call May 9 2025 · Elise/R.H. affair seeded May 2024 → Feb 2025 ("for you I'm always up") → April 2026 · **his last day is Thursday June 11 2026**: before dawn with Elise (song 13), the afternoon he packs, writes the pad and leaves the ring on the table (song 14), breakup email "Some practical things" (lawyer at 2:50, her at 4:12 — he told the lawyer first) · **she reads the pad Friday June 12 2026, 9:41 AM** (song 1); her final text READ 9:44, never answered; the ring only reaches her with the note, so nothing before Thursday can mention it · **she finishes it — “safe 😊 tonight was amazing” — and sends it at 11:51; we hear the send and the bubble STAYS LIT (David, Sept 21 — “the last thing we should see before the blackout is the text”; this reverses Sept 20’s baked-in `screenoff`, which reversed “still typing”)**; the show's last image is her text, held through the whole of his last verse, then a slow fade to true black, then the end screen. Whitfield is his literary AGENT (Linda; agency never named — he saved her office number as "Ms. Whitfield (office)"); The Atlantic Monthly prints his chapter; Random House is Elise's house; Stelmyer's agency is never named. Jamie escalates by silence and administration (accounts, movers, lawyers); Cathy escalates by asking. His ghosts are cowardice; hers are courage. He cannot delete anything about her (Cancel, every time) except the two sharing buttons he does press: Stop Sharing and Leave Playlist.

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
**2022** nine months in — the bear (M2, Jamie giving it to her; caption “nine months in. he brought a bear 🧸”) · **2023** the proposal, June 12 (the rowboat day
The Next Ten Minutes returns to) · **2024** married three weeks, 600 miles apart (Ohio is forty
miles east of Cincinnati per the script) · **2025** Ohio round two, day one — Cathy in the dressing-room mirror (M26; caption “Ohio round 2 day 1”). The couch (M15) is CUT from the whole show (David, Sept 19). She stays on the bear (memgo i:3). The pier (M1, July 19, 2025) is Song 3's post only — it can never be a June 12
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
- **LEFT CLEARS, RIGHT OPENS (David, Sept 21, with a reference shot — 13.2)**: on a real iPhone you swipe a
  notification RIGHT to open it; to get rid of one you swipe LEFT and the card slides off its own **Clear**
  button. `notifDismiss` pulls the card left, reveals Clear on its trailing edge, holds it long enough to
  read, and only then takes the card away. He is not opening her text; he is clearing it. Proof:
  `a_swipe_left_clear` (D-070).
- **No touch dots (cut by David).** The blue finger circles are gone everywhere. Taps read
  the way a real screen recording reads: the beat, the control's own pressed state (icon
  press animation, iOS pressed-gray on rows and buttons via `hover`/`btnHover`), then the
  transition. The `hover`/`tap`/`btnHover`/`btnTap` ops remain as timing + pressed-state beats.
- **Preshow**: the house card (title + the two-handed clock) renders at song 1 · cue 0.
- **THE ENDING (David, Sept 21 — supersedes the Sept 20 shape)**: **14.5 is CUT** — his last verse carries no
  screen event, because her text is still on it. **14.6 is a SLOW curtain** (`{op:'curtain',fade:3500}`): nothing
  drops and nothing cuts, because an ordinary curtain drops the phone first and that would take her text away
  BEFORE the black did. Everything on stage fades together to true black. Then **14.7** is the end screen.
  Proof: `a_ending_on_her_text` (D-072).
- **BOWS (David, Sept 20)**: 14.6 is the curtain, then **14.7 `{op:'bows'}`** brings the title card and the
  photo bed back at a faster rate (a print every 0.9–1.5 s against a 15–20 s fall, so it can never go
  blank and never ends). The operator's questionnaire no longer arms itself 2.6 s after the curtain —
  it waits for the bows and for the operator to leave the show, and never arms in the projection window.
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
- **PAPER (David, Sept 19 night: the crumple is CUT)**: the sheets are flat matte off-white with a
  whisper of grain and quiet torn edges. The generator (`paperTex`) stays in the engine but is
  inert; real scans in `assets/paper/` (embedded by build.py as `window.L5Y_PAPER`) would show
  through `--pp` if David ever wants texture back. The strip is 14.4vw wide — everything on the
  right side big (month 4.6vw, YEAR 9.6vw, the number 20vw), in Poppins to match the pad.
  **THE CARD (David, Sept 19 night — his own mockup, “this is the move”)**: the center pad is a SQUARE sheet,
  96vh × 94vh, and every card is that same size (the house pages too — the falling photos must read behind
  them). The face is **Poppins**: the word YEAR at 28vh directly over the NUMERAL at 54vh, both weight 800,
  hard black, and one foot row under a rule — **month │ event**, 5.2vh weight 600, split by a vertical pipe.
  `fitPad()` shrinks any element wider than the sheet, so no month or foot line can ever run off.
  **THE INK HAS GRIT** (`#inkgrit`): a low-amplitude displacement roughens the glyph CONTOUR so the type sits
  in the paper, with only a whisper of interior mottle — the fill stays hard black (a fine interior screen
  greys the letter out at 25 ft and is wrong). A page in flight drops the filter (16 filtered clones cost frames).
  **THE HOUSE PAGES LEAVE THE BED ROOM (David, Sept 20: "the preshow and home screens are too large right
  now, we won't be able to see the falling photos behind them")**: the title page, the performer page and
  the bows card scale to `--hsc:.66` and the money minute to `.78` (the QR must still scan — verified by
  decoding the rendered card down to 600 px wide), so a house page covers ~30% of the stage instead of 69%
  and the photographs read around and behind it. The whole card scales as one — sheet, understack, torn
  edge and type — so the mockup's proportions are untouched and only the footprint changes. The
  INTERMISSION band is unscaled: it is already a strip with 70% of the stage open above and below. The DATE
  cards are unscaled too — nothing falls behind them. Proof: `a_house_leaves_bed` (D-066). This caps D-012:
  the house pages are still LANDSCAPE and still tracked edge to edge, they just no longer take the width.
  **MEASURE IN ONE SPACE (the corollary that bit immediately)**: `clientWidth` is a LAYOUT width and a
  `Range` rect is a SCREEN rect, so under a scaled card every fit read 34% short and the title ran off the
  paper. `fitPad` divides the ink back out by the DECLARED `--hsc` (never by a measured transform — during
  a morph or a tear the pad carries a transient one, and measuring it made the 1.2 glide jump), and the QA
  that grades the fit does the same.
  **THE TITLE PAGE IS ITSELF A DATE CARD** (David, Sept 19 night — his second mockup): THE LAST over a huge
  **5** over YEARS, with *Redline Performing Arts* at the foot. No act number, no author credit.
  **INTERMISSION is ONE WORD on a wide torn BAND** across the middle of the stage (`.pad.inter .sheet` insets
  to a strip) — never split across lines. Photos fall behind both; the photo files are still outstanding.
- **THE OPERATOR'S GATE (David, Sept 19 night — “think of it like choosing your ingredients”)**: `#gatewrap`
  is a FULL-SCREEN MODAL over everything (z-index 300, opaque). While `body.needgate` is set NOTHING is
  clickable and NO key does anything — the keydown handler returns first — so there is no play, no recipe and
  no work-around until tonight is chosen: (1) cast, (2) preshow performer (Gayle King · Kenneth Bailey ·
  Taylor Thomas · Elijah Pahls · none), (3) both read back with “is this right?”, (4) **a SECOND person
  confirms**, and only then do the Start buttons exist. Stored as `l5y_perf`, synced to the projection window;
  a `?view=projection` window is never gated. **ONE WINDOW ASKS, AND NO WINDOW IS A DEAD END (David,
  Sept 21: "I just loaded the cue url and it appears to take me to the projection screen instead of the
  start screen")**: a window opened while another window of the same origin has the show up becomes that
  show's silent projector — that is the design and it stays. What was wrong is that a tab left open from an
  EARLIER session answered "the show is live" for ever, so every later load was swallowed, with no gate, no
  explanation and no key that did anything. The owner now reports how long it has been idle (`LAST_ACT`,
  stamped by advance/prev/hardRender/blackout/start) and an owner idle past 45 minutes (`GATE_IDLE_MS` —
  longer than any gap in a performance, intermission included) is treated as a leftover: the new window
  keeps the questions and the old tab is NEVER stood down from here (blacking out a real presenter
  mid-show would be far worse than one extra questionnaire). And **Shift+G (`gateRetake`) takes the
  questions back on ANY window**, checked before the `started` guard so it works in a dead one; it is not
  a GO key, so it cannot fire a cue by accident. Proof: `a_gate_recoverable` (D-067).
  **Cue 1.0** turns the pad to the performer's name; “none” leaves
  the title page up so that GO is a harmless no-op, and 1.1 tears whatever page is on top either way.
- **THE FINAL CURTAIN LOCKS (David, Sept 19 night; amended Sept 20)**: the `curtain` op sets `SHOW_OVER` —
  `prev()` does nothing (there is no rewind past the end). The questionnaire NO LONGER arms itself 2.6 s
  later in both windows (the audience would have seen it during the final blackout): `gateArmWatch` waits
  for the bows and for the operator to come off the show, and never arms in a projection window. Starting again from the gate resets to the top of the show and clears the saved position.
- **THE INTERMISSION IS THREE CUES (David, Sept 19 night)**: 8.4 the torn INTERMISSION band · **8.5 THE MONEY
  MINUTE** — “THE NEXT 5 YEARS” over Redline's QR code, fired when the speaker picks up the handheld mic ·
  8.6 the same band again when the ask is over. The QR (`assets/img/qr-next5.png`, embedded by build.py as
  `window.L5Y_IMG`) prints ONTO the paper with `mix-blend-mode:multiply` and **carries no ink grit** — a
  filtered QR does not scan. **THE CODE IS DAVID'S, INSTALLED SEPT 21 (D-029)**: it decodes to
  https://givebutter.com/friends-of-rpa-xgna4k — the Redline donation page. Flattened onto white, because the
  card prints it with `multiply` and transparency would carry the dark stage through. The proof does not take
  anyone's word for it: `a_qr` decodes the image the BUILD embedded, then renders 8.5 and decodes the card the
  way a phone across the room sees it — it scans down to 400 px wide of the whole 1920×1080 frame.
- **TIME ONLY EVER CHANGES ON THE CALENDAR** (`eraRoll`), and every roll rides the TIME WARP MUSIC
  (`assets/sfx/timewarp.mp3`, David's file, `warpStart`: in on the first page, out as the last settles,
  stopped on a scrub): forward = pages tear off and fall;
  backward = pages rise and settle. Long journeys skip months (≤16 pages). **EVERY ROLL LASTS EXACTLY 6 s** (David, Sept 19 — the
  Time Warp music, five clock ticks; the pages share the 6 s whatever their number). The phone never rolls; a dated `clock` op rolls the era, then `device` docks it
  and the phone rises already at the new time. `stamp` is now the calendar's FOOT line.
- **THE SCENE NAME IS HELD (David, Sept 21: “some moments where the typing of the day description disappears
  too quickly for the audience to read… at least 2-3 seconds fully typed”)**: `typeFoot` finishes typing and
  then waits `FOOT_DWELL_()` (2.4 s) before ANYTHING else in the cue runs — the next op could dock the
  calendar and raise the phone in the same breath. All 21 typed lines measure 2.3-2.5 s fully typed.
  Proof: `a_foot_dwell` (D-068).
- **COMING HOME, THE TYPE DOES NOT PAINT (David, Sept 21 — D-073)**: the era morph is a FLIP, and on the
  homeward leg the type’s “old box” can be measured after the card has already taken its centre layout, so
  the words flew at full card size across a strip-width sheet and hung off the paper until fitPad caught up
  (“it fixes itself as the warp happens”). The paper still morphs; the words sit out the journey and fade up
  as it lands (`#era.morphing.homing`). Docking is unaffected. A morph whose type cannot be measured at all
  is now instant rather than half-flipped.
- **YEAR 1…5**, never real years on stage: Year N = years since the night they met (Sept 3);
  the real dates stay in cues.js (`yearN()` derives the label). The wedding is May · Year 3.
- **The phone only comes up when it is used.** Calendar-only songs: 5, **6**, 8 (three moves), 11.
- **Preshow / intermission (David, Sept 19 night — the falling pages are CUT, “too cartoonlike”)**:
  the calendar pad sits center-stage, STILL. Before the show its top page reads the title
  (Redline Performing Arts / The Last Five Years); at the break it reads Intermission (Act Two).
  **Prologue** = one GO: the title page tears off and falls (`tearTop`), the era beneath it —
  JUNE · YEAR 5 — holds through the whole prologue. 9.1 tears the Intermission page the same way,
  then rolls. Nothing else moves, nothing sounds. **Curtain** (`curtain` op) = true black.
- **THE CAMERA (David, Sept 19 night — CALM; supersedes everything above)**: the screen SUPPORTS
  a live musical; it is not a show of its own. The frame is a window into the phone (never
  phone-sized): the docked strip owns the right 15% (`ERA_ZONE`), the screen fills the rest edge
  to edge (`camRest`, `CAM_FILL`=3.6×), anchored to the TOP of the register (a thread opens at its
  top — the name, the history; Find My's card sits at the BOTTOM), with feathers where it leaves
  the frame. A thread rests at its top until she has typed in it, then at its foot for good
  (`st.camBottom`). The camera never pans to an app icon (the app opens 400 ms later), never moves
  on the unlock, and rests only when the REGISTER changes (`wasApp!==st.app`); a Find My sheet
  rises into a frame that already holds it. **THE FOLLOW RULE**: a push (`camPush`) moves the camera ONLY when its target is not
  already in frame; when it is, the camera holds. When it must move it pans at the current zoom if
  the target fits, and re-zooms only when it must. Every move is one slow glide (1.4 s,
  ease-in-out). No drift. Nothing moves while a receipt changes or a bubble lands in frame. The MacBook (song 7) and the dash (song 12) fill
  the frame natively. The presenter preview is a 16:9 frame running the same camera.
- **A HEAD UNIT IS NEVER WHITE (David, Sept 21: “12.2 there’s a random white flash before the navigation
  starts”)**: not a flash, a fade — the Maps layer fades up over `.app`, the phone’s white page, which is
  right on a phone and wrong in a car, so for the length of the fade the dash was a white screen with the
  navigation ghosted on it. `.carplay .app` carries the dash ground. Proof: `a_dash_never_white` (D-069).
- **CARPLAY (song 12)**: the drive plays on the dash — `dev:'carplay'`, a landscape head unit
  (sidebar: clock, signal, recent apps, home; Maps with the maneuver card and the trip card over the
  map, the same live route model as the phone). The dash clock rides with the trip.
- **THE SUBJECT LAW (David, Sept 20 — the family rule behind every framing note)**: content may
  leave the frame with feathers, but the SUBJECT of a cue — whatever the camera was last aimed at —
  sits WHOLE inside the reading window when the glide settles. `qc_notes_subject.py` wraps `camPush`,
  records each cue's last target and asserts it. Two exceptions, both honest: a subject TALLER than
  the window (a memory photograph is 2221 px in a 1080 px window; fitting it would mean 58% black
  bars and break the fill law) is judged on its TOP edge — flush, and the eye drifts down into it;
  and a transient pressed-state class the control itself removes before the glide lands is not a
  camera fault. **ONE SCALE PER REGISTER**: every iPhone register rests at 3.39× (`camFill`), never
  seven different sizes for the same screen. **NO CUE LEAVES BLACK DOWN THE SIDES** — `camPush` may
  not zoom out below the resting fill. **NOTIFICATIONS**: one or two cards on the lock screen are
  framed together and both read whole (David: Rob's text matters more than the time); three or more
  and the newest card is the subject, the older ones cascading off the bottom as they do on a real
  lock screen — at 3.39× five cards are 1829 px in a 1080 px frame, so "every card whole" is
  arithmetically impossible and the clock is what gives way first.
- **MEASURE THE TYPE, NOT THE BOX (Sept 20, the hard-won one)**: `scrollWidth` on a `display:block`
  line can never report less than its own box, so a fit-to-width silently no-ops for anything
  narrower — and a QA that measures the same way will happily confirm it. `fitPad` and its probe both
  measure the ink with a `Range`. Any future "does it fill?" check does the same.
- **THE SOUND LAW (David, Sept 19 night; amended Sept 20)**: the screen makes ONLY the sounds a real iPhone makes
  with its volume up, and QUIETLY (default 0.35, trims ≤ .7). Send, receive, the lock-screen tone,
  mail, the FaceTime ring / accept / end, **and the UNLOCK — David, Sept 20: we hear it at 13.3 and
  everywhere else a phone is unlocked** (`unlock` is in `SFX_KEEP_`; the licensed set has no
  `unlock.caf`, so the synthesised tick plays until David drops one in). **The low-battery chime is
  CUT entirely (David, Sept 20)** — op, synth, sample and census entry all removed. **NO RINGTONES (David)**: an incoming call BUZZES — the
  phone vibrating on the table (`assets/sfx/vibrate.mp3`, David's licensed file). NO paper sounds, NO
  ambience, NO taps and NO swipes; **the unlock IS audible and the ringback is David's own recording
  (both Sept 20, superseding this line)**; **KEYBOARD CLICKS ARE ON for every typing beat (David, Sept 19
  night — “the haptics back in”): the real key_press_click per key, key_press_modifier on the space bar,
  key_press_delete on every backspace (typos, the wipes), all at the .35 trim; a cue mutes them with `keys:false`**;
  any notification/bubble may be silenced with `snd:false`. A noise every five
  seconds is a trope — sound is color and context, never a beat of its own.
- **SOUND FILES (David, Sept 19 — the licensed iOS set)**: the real system sounds live in `assets/sfx/`
  (SentMessage, ReceivedMessage, sms-received1 = the lock-screen text tone, new-mail, mail-sent,
  key_press_*, Tock, lock, Swish, vc~ringing = the FaceTime ring, vc~ended, vc~invitation-accepted,
  Reflection.m4r = the ringtone, ct-* call tones). build.py embeds them into the STANDALONE and
  docs (never into index.html); the engine decodes Core Audio Format itself (`cafDecode`: lpcm
  and ima4) and plays the mapped sample (`SFX_MAP_`, `sample`); the synthesized sounds in `sfx()`
  remain the fallback, so a missing file never silences a beat. Paper (tear, settle, flutter,
  rustle) stays synthesized. The ringback is David's licensed recording (Sept 20), not a synth tone.
  Sound plays only from the window the operator clicked Start in; a window we opened ourselves
  (`?view=projection`) is silent unless its checkbox says otherwise; speaker button → volume popover.
  **THE LOW-BATTERY CHIME IS CUT (David, Sept 20: "let's lose the low battery thing, entirely just cut
  that sound")** — the op branch, the synthesised tone, the `low_power.caf` sample and the census entry
  are all gone. His 9% before dawn at 13.1 is still state; it just makes no sound.
  **THE RINGBACK IS REAL (David, Sept 20)**: his licensed recording, `assets/sfx/ringback.mp3`, trimmed
  to the single 2.01 s burst of North American ringback (440 + 480 Hz) with the dead air off both ends,
  played EXACTLY TWICE with 0.92 s between — two tight rings, wherever anyone dials out. The synthesised
  pair remains the fallback. **A `{op:'notif', tone:'…'}`** names a custom text tone for that contact,
  the way you set one for the person you cannot miss: Linda Whitfield's text at 4.8 arrives on its own
  tone, distinct from the bank alert and from the mail.
- **THE TYPE IS EMBEDDED (David, Sept 19 night)**: `fetch_fonts.py` pulls the latin woff2 subsets into
  `assets/fonts/` and build.py inlines them as base64 `@font-face` in the STANDALONE and docs, so the
  projection machine never waits on — or goes without — theatre Wi-Fi. Before this, a machine with no
  internet ran the whole show in fallback Georgia/Courier. The Google Fonts `<link>` stays for `index.html`.
- **THE OPERATOR CAN MOVE (David, Sept 20)**: the Menu is no longer a dead end. `☰ Menu` (or `J`, or
  `Esc`) opens **#jump** — the running order on the left, that song's cues with their triggers on the
  right, the live cue marked NOW; click or arrow-and-Enter to land on any cue (a scrub via
  `hardRender`, not a GO). It swallows every key while open, so GO can never fire behind it, and
  **Esc never un-starts the show again**. Presenter only — `body.jumping.v-presenter`, never
  broadcast, so the house never sees the operator think.
- **OPERATOR SAFETY (Sept 19 review)**: one `setBlackout()` for key, button and the other window;
  a RELOADED presenter resumes at the saved cue (`l5y_pos`, reload only, 3 h); resize never cancels
  a running cue; `hardRender` stops rings and clears camera timers; GO keys are ignored while the
  volume slider has focus; Esc does nothing in the projection window; Google Fonts load
  non-blocking (theatre Wi-Fi must never stall the engine).
- **THE PRESENTER IS THE CUE SHEET (David, Sept 19 night)**: the operator has a SECOND MONITOR showing the
  audience view, so the presenter carries NO projection preview — the whole window is the cue sheet and
  every element is scaled up (the GO line is `clamp(30px,4.1vw,80px)`). The WHAT HAPPENS paragraph under
  NEXT GO is CUT; THEN moves up under the GO card and is larger, in gold. What is left: song + cast +
  character, NOW with progress, the GO card, THEN, the whole queue, BLACKOUT and MENU. Nothing else.
- Restore point before this sprint: git tag `restore-sept18-line-by-line`.

## THE LINE-BY-LINE BUILD (David, Sept 18 — the spec; 68 cues after Sept 21)
- **1** prologue = the title page tears off (one GO, no phone); on her verse-2 line the phone rises
  and she sends her text (auto, ~50 s — SLOW by direction, Sept 19 night: she reads the list, she
  reads his name and the history, she types slowly, she waits before Send; every pause is tunable);
  READ 9:44, his typing bubble, it stops; then she opens the Memories — four cards (~26 s, slow), the
  BEAR (M2) last, she drifts back up to it; cutoff = phone away.
- **2** 2.1 the roll then his lock screen; 2.2 = ONE ~50 s piece (three drafts → “home safe?” →
  Delivered → her typing bubble); 2.3 her call; 2.4 hang up. Same-night compression kept.
- **3** the LAKE BED (`{op:'bed',file:'lake.mp3'}` on 3.1, fades in 5 s; `stop` on 3.10, fades out 5 s — David's licensed lake ambience, quiet; a `bed` is by cue only and dies with its song or the curtain). **THE LAKE IS HERS (David, Sept 19 night)**: it ducks out (2 s) on 3.2, 3.5 and 3.8 as his phone comes up and returns (4 s) on 3.4 and 3.7 with the roll home to her — never under a Whitfield/Rob call. Era-center only for her; Jamie's three calls (Whitfield ×2, Rob — he dials, per the
  script) with return rolls; hang-up on the downbeat of 4. **NO WARP INTO MOVING TOO FAST (David, Sept 21:
  “we’re going to operate as if he sings that song right after he gets off the phone with rob”)**: 3.10 does
  not date the clock, so nothing tears and SEPTEMBER · YEAR 1 holds through the hang-up; 4.3 comes home to
  8:16 the same evening, so the win streak belongs to the night he called Rob. The only roll left in 4 is
  Cathy’s May 2025 call, which David pinned himself.
- **4** her Stelmyer call (dial → connect → end), then his notifications. **5** calendar only (the dedication is CUT). **6 is CALENDAR ONLY
  (David, Sept 20: "I think we've cut 6.2, the only thing visible on Schmuel is the date, so just cut
  that one. No background with christmas needed") — 6.2 and the Christmas lock screen are gone; the
  date is the whole of Schmuel.** **7** the FaceTime arc (ring → V2 → Call Ended → black).
- **8** calendar only: engagement → wedding → engagement on the singers' lines; **8.4 = INTERMISSION**
  (the falling pages; holds until 9.1). **9** notifications only. **10** “break a leg” before her first note, two
  rejection emails, black, the bell-tone FLASHBACK to NOVEMBER 2023 (his long text), return.
- **9** (dramaturg pass, Sept 19): one device, one era (Fri Oct 18 2024 = OCTOBER · YEAR 4, “five months
  married”, the wedding portrait M4 as his wallpaper); the stack is only what a real phone shows —
  Instagram COMMENTS preview text (a stranger's DM never does; a request says “wants to send you a
  message”), the book's growth arrives from Linda Whitfield (Goodreads pushes nothing like it),
  Elise is “Elise (Random House)”, the clock ticks 11:22 → 11:25 → 11:29 across the number. **PAIGE.TURNER
  (David, Sept 21) lands on 9.3 as a COMMENT, not a DM**: a stranger’s direct message shows no preview text on
  a real iPhone — which is exactly why lit.with.lena on the same cue can only say “wants to send you a
  message” — and her line has to be read to land. She arrives second, so she is the top card of the two. 9.2,
  9.4, 9.5, 9.6 carry `confirm:true` (⚠CONFIRM) until David ticks them on the worksheet; the
  attribution “— Elise” was removed from the 9.5 trigger (the score does not name her). Her
  interpolation has no cue — David's call whether the phone drops on her lines.
- **11** timeline only (one cue). **12** THE DRIVE on CARPLAY, IN REAL TIME (David, Sept 19 — “driving 500 mph” was cut): `rate:1`,
  `startAt:.5` (David, Sept 20 — at rate:1 the two things this line used to ask for are arithmetically
  incompatible: four miles ahead IS four minutes twenty-four at 58 mph). The banner opens 2.1 miles out
  and the Delaware Memorial Bridge maneuver lands at 2:12, mid-song; `seconds = (.51 − startAt) × 214 ÷
  58.4 × 3600`. On I-95 past Wilmington, the miles fall at highway speed, the dash clock runs 5:53 onward; she never arrives in
  the song. (`dur` mode still exists for a compressed trip.)
- **13** two beats: her text lands (5:05 AM — before dawn means before the 5:24 sunrise), holds 4 s so the
  house can read it, and he swipes it away over 1.9 s — deliberate, not a flick (David, Sept 20); on his last line the **whole phone** is on stage so we see him unlock it, then Find My → **Me** →
  **“Use This iPhone as My Location”** — sharing was always ON and stays ON; only the reporting device
  changes, iPad → iPhone, the classic cover-up (David, Sept 20). We never see the iPad made the source. **THE CAMERA GOES
  TO THE ROW (David, Sept 21: “we just need to see ‘sharing location from Jamie’s iPad’ on the screen for
  longer — just change the camera zoom effect there”)**: the whole beat is one word changing on one row, so
  `camPush('.fmshare')` takes the camera to the row itself and BOTH findmy ops name the same selector, so the
  follow rule holds the camera still and the house watches the word change in place — 4.0 s settled on each.
  Proof: `a_share_row_held` (D-071). Her Ohio is **Mount Orab, OH** (forty miles east of
  Cincinnati, per the script — confirmed by David, Sept 19). 4.8 keeps “SONNY READ IT.” (David’s call).
- **Continuity law (Sept 19)**: her Friday thread (1.2) carries Thursday — the flight text from
  13.2 verbatim, “landed?”, “I read it. please call me”, “I’m not angry. just talk to me” — because
  his last day is June 11; nothing in it may imply he moved out earlier. Calls connect at 0:00.
  Her contact for him is “Jamie 💙” through June 2024 (7.1). The drive is dated Nov 6 2021 (after
  the Oct 16 move-in) — if the licensed script's drive contains the move-in invitation, David must
  re-date it; never fill that from memory.
- **14** era flips with the singer; her one animation (his “home safe?” lands, she opens it, types at the
  `slow` pace, **SENDS — Delivered — and the bubble holds eight seconds and never goes away**). His last
  verse has NO CUE: her text is the picture for all of it. 14.6 fades the whole stage to true black over
  3.5 s; 14.7 is the end screen. (David, Sept 21.)
- Instrumental passages auto-play from one GO using `{op:'pause', ms}` beats — tunable in tech.
- Assets: M24, M25, M26, M3a, M2 (THE BEAR), M4 (Songs 1 and 9), M23 (Song 6), V2 (Song 7), plus loop-only
  photos (S00-LOOP-…). CUT: M1, M7/M7b, M12, M15.
- **Never quote the script in chat.** Script fragments live only in `cues.js`, short.
- **Sound**: the ringback is David's own licensed recording (`assets/sfx/ringback.mp3`), trimmed to
  the single 2.01 s burst of real North American ringback (440 + 480 Hz), played EXACTLY TWICE with
  0.92 s between — two tight rings. A `{op:'notif', tone:'…'}` names a custom text tone for that
  contact, the way you set one for the person you cannot miss: Linda Whitfield's "SONNY READ IT"
  at 4.8 arrives on its own tone, distinct from the bank alert and from the mail.
- **LINES LAW (supreme; scoped by David, Sept 20)**: a `trig:` has two halves and they are
  governed differently.
  **The SCRIPT FRAGMENT** — the quoted words the singer actually sings, normally in curly
  quotes before the em dash — comes ONLY from the licensed script. Never write, fix, or fill
  one from memory; anything unchecked carries a ⚠CONFIRM flag; `apply_lines.py` +
  `L5Y-Lines-Worksheet.docx` are the reconciliation path. That half is untouchable.
  **THE OPERATOR'S STAGE NOTE** — everything after the em dash ("— he hangs up", "— Find My,
  the location device swapped"), and all of `what:` and `hold:` — is OUR writing, not the
  script's. It must be kept TRUE to what the cue actually does, and it is rewritten as soon as
  the cue changes. David, Sept 20: "I would've never approved something that required me to
  edit a worksheet to make a change here." A stage note that describes the old behaviour is a
  bug, not a protected line.

## THE NOTES REGISTER (David, Sept 20 — "trackable, traceable, fixable, provable, repeatable")
`notes.json` holds every note David has given: an ID, the cues it touches, a `family` (so the same
logic is swept everywhere it applies, not only where he caught it), a status, and the NAME OF THE
ASSERTION THAT PROVES IT. Each proof is an `a_*` function in a `qc_notes_*.py` probe file.
`qc_notes.py` runs them all on the live path and prints a line per note, with each probe's own
runtime and the five slowest named; **a note marked `fixed` whose proof is missing or failing fails
the gate.** `--only D-001,D-005` checks one thing in seconds and `--fast` skips the show-wide sweeps
(measured: `a_maybe_cathy` 84 s, `a_13_to_14` 48 s, the subject law ~20 min) — **neither can close a
loop**, only the full gate can. Nothing is "done" because it was edited — it is
done when its probe passes. Never mark one fixed without a probe.

**THE CLOSURE LAW (David, Sept 20 — "always and forever amen")**: QA → fix → QA → fix → QA → no fix
necessary → QA → no fix necessary → CLOSE. A note goes `open` → `fixed` → `closed`, and `closed`
requires **two consecutive clean runs on two DIFFERENT builds** (`clean` counter + `last_build` hash
in notes.json; a pass on the same artifact does not count twice, so a loop can never be closed by
re-running the gate). Any failure resets the counter to zero. A `closed` note whose probe later
fails is reported as a REGRESSION and fails the whole gate — closure is not permanent absolution.

## Workflow law
1. **Verify before delivering.** Playwright harness must pass: state-integrity (all cues), POV/timeline, legibility QC, `audit_teleports.py` (no register appears without navigation), **`qc_census.py` (the live census: every sound and every camera move of the whole show, by cue — the sound law and the follow rule are checked HERE; any cue with more than three moves must justify itself)**, **`qc_notes.py` (David's register: every note he has given, proved by its own assertion)**, **`qc_livepath.py` (the operator's GO path: every cue fired via advance(), shell chrome + reading window asserted against settled truth — settled-render sweeps cannot see live-swap bugs)**, zero JS errors — plus a screenshot review of anything visually changed. Never hand David anything unverified.
2. Rebuild = splice `cues.js` into `FALLBACK_SHOW`, emit `L5Y-Show-STANDALONE.html`, `node --check` the script.
3. Regenerate the Cue Bible whenever cue content changes: `extract_book.py` → `build_bible_data.py` → `build_bible_docx.js` (DOCX) + `build_bible_pdf.py` (PDF, headless Chromium). Both render the same `bible.json`, so they cannot drift. The Bible carries: ON SCREEN verbatim, PLAYS mechanics, SOUND, PHONES state, gold dramaturgy notes.
4. Ship: STANDALONE + Bible PDF; push to this repo so the team URL stays current.
5. David's notes are punch lists: fix **every** item, then QA beyond the list in the same spirit. Proactive taste is expected; sloppiness anywhere invalidates polish everywhere.
