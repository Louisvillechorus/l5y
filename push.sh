#!/bin/bash
# One-time: create an empty repo on github.com (no README), then:
#   ./push.sh https://github.com/YOURUSER/l5y-second-screen.git
set -e
git remote remove origin 2>/dev/null || true
git remote add origin "$1"
git branch -M main
git push -u origin main
echo "Now enable Pages: repo Settings → Pages → main /docs. Team URL: https://YOURUSER.github.io/REPO/"
