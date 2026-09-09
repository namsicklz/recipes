# Recipes

A static recipe site, generated from the recipe notes in my Obsidian vault, meant to be pulled up on a phone or tablet while cooking.

Live site: https://namsicklz.github.io/recipes/

## How it works

`build.py` reads every recipe note from `~/Vault/02 - Personal/Recipes/`, follows the category groupings in that folder's `Recipes.md` index, and generates a plain static site into `docs/` — a home page with searchable, categorized recipe cards, and one page per recipe. No backend, no database, no login; GitHub Pages just serves the `docs/` folder as-is.

The vault is the source of truth. This repo only ever contains the generated output plus the generator itself — nothing else from the vault gets pulled in.

## Updating the site

Whenever a recipe is added or edited in the vault:

```bash
cd ~/recipes
python3 build.py
git add docs
git commit -m "Update recipes"
git push
```

GitHub Pages picks up the change automatically within a minute or two.
