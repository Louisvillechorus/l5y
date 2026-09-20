#!/bin/sh
# EVERY GATE, ONE COMMAND. Run this before anything reaches David. (David, Sept 20: repeatable.)
set -e
cd "$(dirname "$0")"
export CHROMIUM_PATH=${CHROMIUM_PATH:-/opt/pw-browsers/chromium}
python3 build.py
# REGENERATE THE GATES' INPUT. audit_teleports.py reads book.json; qa_all never rebuilt it, so the
# teleport gate spent an unknown time grading a stale show (68 cues, no bows) and reporting CLEAN.
python3 extract_book.py || { echo 'extract_book.py FAILED — book.json is stale, gates would lie'; exit 1; }
fail=0
for g in qc_notes.py qc_livepath.py qc_legibility.py audit_teleports.py qc_census.py; do
  [ -f "$g" ] || continue
  printf '\n===== %s =====\n' "$g"
  python3 "$g" || fail=1
done
printf '\n'
[ $fail -eq 0 ] && echo 'ALL GATES CLEAN' || echo 'GATES FAILED — nothing ships'
exit $fail
