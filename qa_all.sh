#!/bin/sh
# EVERY GATE, ONE COMMAND. Run this before anything reaches David. (David, Sept 20: repeatable.)
set -e
cd "$(dirname "$0")"
export CHROMIUM_PATH=${CHROMIUM_PATH:-/opt/pw-browsers/chromium}
python3 build.py
# REGENERATE THE GATES' INPUT. audit_teleports.py reads book.json; qa_all never rebuilt it, so the
# teleport gate spent an unknown time grading a stale show (68 cues, no bows) and reporting CLEAN.
python3 extract_book.py || { echo 'extract_book.py FAILED — book.json is stale, gates would lie'; exit 1; }
# REGENERATE THE BIBLE TOO (D-058). a_confirm_survives_bible asks whether bible.json is NEWER than
# the build it describes, and qa_all rebuilt the show on line one — so without this the Bible was
# stale by construction on every single run and the note could never pass inside the gate it is
# gated by. The two renderers read the same bible.json, so the DOCX and the PDF cannot drift, and
# the PDF is half of what ships; regenerating it here is what makes "one command" true.
python3 build_bible_data.py || { echo 'build_bible_data.py FAILED — the Bible is stale'; exit 1; }
node build_bible_docx.js  || { echo 'build_bible_docx.js FAILED — the DOCX is stale'; exit 1; }
python3 build_bible_pdf.py || { echo 'build_bible_pdf.py FAILED — the PDF is stale'; exit 1; }
fail=0
for g in qc_notes.py qc_livepath.py qc_legibility.py audit_teleports.py qc_census.py; do
  [ -f "$g" ] || continue
  printf '\n===== %s =====\n' "$g"
  python3 "$g" || fail=1
done
printf '\n'
[ $fail -eq 0 ] && echo 'ALL GATES CLEAN' || echo 'GATES FAILED — nothing ships'
exit $fail
