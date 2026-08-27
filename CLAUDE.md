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

## Song 7 is special
Song 7 will be **one prerecorded FaceTime** (Jamie half-attending at his desk, writing). Do not build elaborate cueing inside 7; keep the FaceTime frame and the log; the video content is produced separately.

## Workflow law
1. **Verify before delivering.** Playwright harness must pass: state-integrity (all cues), POV/timeline, legibility QC, `audit_teleports.py` (no register appears without navigation), zero JS errors — plus a screenshot review of anything visually changed. Never hand David anything unverified.
2. Rebuild = splice `cues.js` into `FALLBACK_SHOW`, emit `L5Y-Show-STANDALONE.html`, `node --check` the script.
3. Regenerate the Cue Bible (`build_bible_data.py` → `build_bible_docx.js` → PDF) whenever cue content changes. The Bible carries: ON SCREEN verbatim, PLAYS mechanics, SOUND, PHONES state, gold dramaturgy notes.
4. Ship: STANDALONE + Bible PDF; push to this repo so the team URL stays current.
5. David's notes are punch lists: fix **every** item, then QA beyond the list in the same spirit. Proactive taste is expected; sloppiness anywhere invalidates polish everywhere.
