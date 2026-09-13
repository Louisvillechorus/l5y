# PUNCHLIST — vertical-TV review, Sept 13 2026

Product of a full review of the portrait build: every one of the 187 cues rendered at
1080×1920 and inspected, plus a complete animated walk (zero JS errors). Mechanism
problems were fixed the same night (list below). Everything else here is a **decision
for David** — mostly content and iOS-fidelity calls on screens that were approved in
build 27P. Nothing in this file blocks running the show.

## Fixed in this build (no action needed)
- Blackout never ended within a song: **8.2–8.8 (the whole wedding sequence) and 14.12
  (the final image) rendered black in playback.** A `device` cue now ends the blackout.
- Era stamps that wrapped to a second line hidden behind the phone (songs 3, 7, 14) —
  portrait stamps now auto-fit one line.
- Touch/tap gesture dots landed off-target (or offscreen) under the portrait scale and
  rotated feeds — placement now maps back into layout space (`dotPos`).
- Song 6 MacBook under the 10-ft type floor on the vertical TV — scaled 1.7×; the
  Schmuel prose and mail content now clear it.
- The Schmuel document never scrolled to follow the typing — cues 6.4–6.6 produced no
  visible change. The sheet now follows the caret, lines land one-by-one.
- QC upgrades: legibility walk now runs at both aspects (`qc_legibility.py 1080x1920`),
  book.json extraction is reproducible (`extract_book.py`).

## 1 · Meta-text printed on screens (realism-law family — keep or kill per instance)
The law: phones never announce; meta lives in the Cue Bible. Each of these is doing
dramaturgical work on the glass. Decide which earn an exception, then we restage the
keepers as real phone behavior.
- `WALLPAPER — …` caption on lock screens: 1.1, 2.1, 3.1+, 4.1, 5.1, 11.6, 13.1, 14.1.
  (Dies naturally once real wallpaper images land — part of the assets pipeline.)
- `search cleared` caption after backspacing Google: 5.13, 10.13.
- `DRAFTS · NEVER SENT` label inside the thread: 12.7–12.10 (persists after the draft is gone).
- Voicemail `✓ Saved — will not be deleted automatically`: 14.8, 14.9. Also
  `Voicemail (0:47) — unplayed` notification: 9.12.
- `READ 9:44 AM — he never answered` under an INCOMING bubble on Jamie's phone: 14.10.
  Double violation (receipts never appear on the receiver's side + narration). The beat
  belongs to Cathy's POV or to silence.
- DND schedule notes `“so we actually sleep” — created together`: 4.13, 9.11.
- Contact renames staged with strikethrough old names / `Added just now`: 13.5, 14.2.
- Notes header `Edited March 24 — 11 weeks ago` (relative time is narration): 13.14.
- Battery row `Messages — top conversation: R.H. EDITS`: 13.10.
- Photos caption prefixed `her caption: …`: 12.6.

## 2 · Newest-first & time math (the audit family David catches instantly)
- Inbox order: Messages 1.9/1.10 (Wednesday row above today's), 2.2 (Rob 11:12 below
  Cathy 10:42); Mail 14.5 (2:50 lawyer below 2:31 U-MOVE), 1.17.
- Notification stacks oldest-first: 4.3/4.4; stale `now` stamp sorted under morning
  items: 3.9–3.13.
- Clock vs. content: 1.14 (Read 9:42 while clock 9:41 — canon wants READ 9:44), 5.5
  (12:04 sent while clock 11:20), 14.6 (clock frozen 2:40 across 2:50 and 4:12 events),
  7.10/7.11 (clock frozen during the call), 9.12 (past-midnight `Today` stamps).
- Stale thread preview 1.9 (`please just call me` vs. latest `I still have your ring`).
- Like counts: 3.2→3.3 jumps 3→47 on a `just now` post; 11.8 (3-year-old memory gains
  43 likes in one cue); 10.10 raw `4212` (Facebook shows `4.2K`).

## 3 · Threads have history
- 1.11 the five-year Jamie thread visibly begins May 12, 2026 (blank void above).
- 7.1 same pattern in Ohio; 3.14 Jamie 💙 thread opens with today as first-ever message.
- 11.2 Elise thread OPENS on the dramatic Feb 2025 exchange (it must sit mid-history).
- 13.2 R.H. EDITS opens fully empty until 13.3 pours history in.
- 14.8 exactly one voicemail in the tab (mundane neighbors would make "kept" read as kept).

## 4 · Canon conflicts (storyline vs. screens)
- 1.4 memories ladder: June 12, 2021 "nine months" post predates the Sept 3, 2021 meeting.
- 12.7–12.9 stamp NOVEMBER 2021 with move-in drafts, but canon movers-in is October 2021.
- 6.2 "Estimated delivery: Thursday, December 18" — Dec 18, 2022 was a Sunday.

## 5 · iOS chrome fidelity (polish; group into one restyling pass)
- Keyboard sliver: a clipped row of key-tops peeks above the bezel wherever the keyboard
  is "down" (songs 1, 2, 4, 5, 7, 9, 11, 13, 14). One engine fix — say the word.
- Dynamic Island appears/disappears between lock and unlocked frames (1.3, 5.1, 14.1);
  status-bar time shown on lock screens.
- QuickType bar always suggests `"I" / I don't / I'm` regardless of typed text.
- Emoji used as system glyphs: call/FaceTime controls (3.7, 7.6), contact buttons (13.5,
  14.2), Music shuffle (14.7), IG/mac icons.
- Desktop Google homepage on a phone: 5.12, 10.4–10.8.
- 9.4–9.9 the Instagram thread renders as iMessage (blue bubbles, `iMessage` placeholder,
  `Delivered`) — needs an IG register or a different staging.
- FB action row struck by the home indicator: 5.2, 10.11, 12.4, 12.5.
- Maps: route line drawn over the instruction banner; puck off the route (12.1, 12.11).
- Misc: `Not Delivered` should be red (5.5+), missing `Delivered` receipts in 7.x,
  dangling time separators before sends (1.12, 2.8, 3.14, 5.6, 7.2), redacted dotted
  phone numbers (9.10, 14.2), Messages in grid AND dock (9.16), `Silence Notifications`
  on a contact card (9.10), mac apps rendered single-pane (6.x), legacy notification
  layout (13.8), 2.1 empty lock screen despite three unreads (the unlock is unmotivated).

## 6 · No action (capture artifacts)
- 6.1 "dim" era stamp and 9.1 dimmed canvas — screenshots caught mid-fade; live
  playback is fine.
