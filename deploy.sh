#!/bin/bash
# Rebuilds and publishes both the public and private recipe sites.
# Public: namsicklz/recipes -> GitHub Pages (no shopping-list feature).
# Private: namsicklz/recipes-private -> Cloudflare Worker (full feature, real webhook).
# Run by the com.nixhomeserver.recipes-deploy LaunchAgent whenever a recipe
# note changes in the vault; safe to also run by hand any time.
set -euo pipefail

cd "$(dirname "$0")"

# --- Public build ---
python3 build.py
if [ -n "$(git status --porcelain)" ]; then
  git add -A
  git commit -m "Rebuild recipe site"
  git push
  echo "Public site updated and pushed."
else
  echo "Public site: no changes."
fi

# --- Private build ---
python3 build.py --private
rsync -a --delete --exclude .git docs-private/ ../recipes-private/
cd ../recipes-private
if [ -n "$(git status --porcelain)" ]; then
  git add -A
  git commit -m "Rebuild private recipe site"
  git push
  echo "Private site updated and pushed."
else
  echo "Private site: no changes."
fi
