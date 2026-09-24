#!/usr/bin/env python3
"""
Builds a static recipe site (into docs/) from the recipe notes in the Obsidian
vault at VAULT_RECIPES_DIR. Re-run this any time recipes are added or edited
in the vault, then commit + push docs/ to publish the update.

Usage: python3 build.py
"""

import re
import shutil
from pathlib import Path

VAULT_RECIPES_DIR = Path("/Users/nixhomeserver/Vault/02 - Personal/Recipes")
INDEX_FILE = VAULT_RECIPES_DIR / "Recipes.md"
OUT_DIR = Path(__file__).parent / "docs"
RECIPES_OUT_DIR = OUT_DIR / "recipes"

WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")

CATEGORY_ICONS = {
    "Mains — Chicken": "🍗",
    "Mains — Beef": "🥩",
    "Mains — Pork": "🥓",
    "Mains — Seafood": "🦐",
    "Mains — Vegetarian": "🌱",
    "Sides": "🥔",
    "Salads": "🥗",
    "Soups & Stews": "🍲",
    "Wraps & Handhelds": "🌯",
    "Sauces, Dips, Dressings & Spice Blends": "🧂",
    "Desserts & Baking": "🍰",
    "Breakfast": "🥞",
    "Drinks": "🥤",
    "Uncategorized / thin": "📋",
    "Other": "📋",
}

HEADING_ICONS = [
    ("ingredients", "🧂"),
    ("instructions", "👩‍🍳"),
    ("method", "👩‍🍳"),
    ("directions", "👩‍🍳"),
    ("nutrition", "📊"),
    ("chef", "💡"),
    ("tip", "💡"),
    ("storage", "🧊"),
    ("serving", "🍽️"),
    ("variation", "🔀"),
    ("note", "📝"),
    ("what it is", "ℹ️"),
    ("what it includes", "ℹ️"),
]


def slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return parts[2].lstrip("\n")
    return text


def inline_md(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<em>\1</em>", text)
    text = WIKILINK_RE.sub(lambda m: f'<a href="{slugify(m.group(1))}.html">{m.group(1)}</a>', text)
    return text


def heading_icon(text: str) -> str:
    lower = text.lower()
    for keyword, icon in HEADING_ICONS:
        if lower.startswith(keyword):
            return icon + " "
    return ""


def try_meta_badges(stripped: str):
    """A line like '**Serves:** 4 · **Prep:** 10 min' becomes a badge row."""
    if "·" not in stripped:
        return None
    segments = [s.strip() for s in stripped.split("·")]
    badges = []
    for seg in segments:
        m = re.match(r"^\*\*(.+?):?\*\*:?\s*(.*)$", seg)
        if not m or not m.group(2).strip():
            return None
        label = m.group(1).strip().rstrip(":")
        value = m.group(2).strip()
        badges.append((label, value))
    return badges


def md_to_html(body: str):
    lines = body.split("\n")
    html = []
    list_stack = []
    table_rows = []
    in_table = False

    def close_lists():
        while list_stack:
            html.append(f"</{list_stack.pop()}>")

    def flush_table():
        nonlocal in_table, table_rows
        if not table_rows:
            in_table = False
            return
        html.append("<table>")
        header = table_rows[0]
        html.append("<thead><tr>" + "".join(f"<th>{inline_md(c.strip())}</th>" for c in header) + "</tr></thead>")
        html.append("<tbody>")
        for row in table_rows[1:]:
            html.append("<tr>" + "".join(f"<td>{inline_md(c.strip())}</td>" for c in row) + "</tr>")
        html.append("</tbody></table>")
        table_rows = []
        in_table = False

    seen_h1 = False
    title = None
    lead = None
    seen_body_block = False

    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()

        is_table_row = stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") >= 2
        is_sep_row = bool(re.match(r"^\|[\s:-]+\|$", stripped)) if is_table_row else False

        if is_table_row:
            in_table = True
            if is_sep_row:
                continue
            cells = [c for c in stripped.strip("|").split("|")]
            table_rows.append(cells)
            continue
        elif in_table:
            flush_table()

        if not stripped:
            close_lists()
            continue

        if stripped == "---":
            close_lists()
            html.append("<hr>")
            continue

        h_match = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if h_match:
            close_lists()
            level = len(h_match.group(1))
            raw_text = h_match.group(2)
            if level == 1 and not seen_h1:
                seen_h1 = True
                title = raw_text
                continue
            text = inline_md(raw_text)
            tag = f"h{min(level + 1, 4)}"
            html.append(f"<{tag}>{heading_icon(raw_text)}{text}</{tag}>")
            seen_body_block = True
            continue

        ol_match = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        ul_match = re.match(r"^[-*]\s+(.*)$", stripped)

        if ol_match:
            if not list_stack or list_stack[-1] != "ol":
                close_lists()
                list_stack.append("ol")
                html.append("<ol>")
            html.append(f"<li>{inline_md(ol_match.group(2))}</li>")
            seen_body_block = True
            continue

        if ul_match:
            if not list_stack or list_stack[-1] != "ul":
                close_lists()
                list_stack.append("ul")
                html.append("<ul>")
            html.append(f"<li>{inline_md(ul_match.group(1))}</li>")
            seen_body_block = True
            continue

        close_lists()

        badges = try_meta_badges(stripped)
        if badges:
            spans = "".join(
                f'<span class="badge"><strong>{label}</strong> {inline_md(value)}</span>'
                for label, value in badges
            )
            html.append(f'<div class="meta-badges">{spans}</div>')
            seen_body_block = True
            continue

        if lead is None and not seen_body_block:
            lead = f'<p class="lead">{inline_md(stripped)}</p>'
        else:
            html.append(f"<p>{inline_md(stripped)}</p>")
        seen_body_block = True

    if in_table:
        flush_table()
    close_lists()

    body_html = (lead or "") + "\n".join(html)
    return body_html, title


def parse_index():
    """Returns list of (category_name, [recipe_names]) in vault-file order."""
    text = INDEX_FILE.read_text()
    text = strip_frontmatter(text)
    categories = []
    current = None
    for raw in text.split("\n"):
        line = raw.strip()
        if line.startswith("## "):
            heading = line[3:].strip()
            if heading == "Notes on this migration":
                break
            current = (heading, [])
            categories.append(current)
        elif line.startswith("- ") and current is not None:
            m = WIKILINK_RE.search(line)
            if m:
                current[1].append(m.group(1))
    categories = [c for c in categories if c[1]]
    return categories


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Nicholls' Family Recipes</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{css_path}style.css">
</head>
<body>
<header class="topbar">
<a class="back" href="{css_path}index.html">&larr; All recipes</a>
</header>
<main class="page recipe-page">
<article class="recipe-card">
<h1>{title}</h1>
{content}
</article>
</main>
</body>
</html>
"""

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Nicholls' Family Recipes</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
</head>
<body>
<header class="topbar sticky">
<div class="topbar-inner">
<h1>Nicholls' Family Recipes</h1>
<span class="count-pill">{total} recipes</span>
</div>
<div class="controls">
<input id="search" type="search" placeholder="Search recipes..." autocomplete="off">
<select id="cat-jump" aria-label="Jump to category">
<option value="">Jump to category…</option>
{cat_options}
</select>
</div>
</header>
<main class="page">
<div id="sections">
{sections}
</div>
</main>
<script src="search.js"></script>
</body>
</html>
"""


def build():
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    RECIPES_OUT_DIR.mkdir(parents=True)

    categories = parse_index()

    recipe_files = {p.stem: p for p in VAULT_RECIPES_DIR.glob("*.md") if p.name != "Recipes.md"}
    built_slugs = set()

    for stem, path in recipe_files.items():
        raw = path.read_text()
        body = strip_frontmatter(raw)
        content_html, title = md_to_html(body)
        title = title or stem
        slug = slugify(stem)
        built_slugs.add(slug)
        html = PAGE_TEMPLATE.format(title=title, css_path="../", content=content_html)
        (RECIPES_OUT_DIR / f"{slug}.html").write_text(html)

    sections_html = []
    cat_options = []
    linked_slugs = set()
    total = 0

    for cat_name, names in categories:
        items = []
        for name in sorted(names):
            slug = slugify(name)
            linked_slugs.add(slug)
            if slug not in built_slugs:
                continue
            items.append(f'<li><a class="recipe-link" href="recipes/{slug}.html">{name}</a></li>')
        if items:
            cat_slug = slugify(cat_name)
            icon = CATEGORY_ICONS.get(cat_name, "🍴")
            total += len(items)
            cat_options.append(f'<option value="#{cat_slug}">{icon} {cat_name} ({len(items)})</option>')
            sections_html.append(
                f'<section class="category" id="{cat_slug}">'
                f'<h2>{icon} {cat_name} <span class="cat-count">{len(items)}</span></h2>'
                f'<ul class="recipe-list">' + "".join(items) + "</ul></section>"
            )

    orphans = [s for s in recipe_files if slugify(s) not in linked_slugs]
    if orphans:
        items = "".join(
            f'<li><a class="recipe-link" href="recipes/{slugify(s)}.html">{s}</a></li>'
            for s in sorted(orphans)
        )
        icon = CATEGORY_ICONS["Other"]
        total += len(orphans)
        cat_options.append(f'<option value="#other">{icon} Other ({len(orphans)})</option>')
        sections_html.append(
            f'<section class="category" id="other"><h2>{icon} Other <span class="cat-count">{len(orphans)}</span></h2>'
            f'<ul class="recipe-list">{items}</ul></section>'
        )

    index_html = INDEX_TEMPLATE.format(
        sections="\n".join(sections_html),
        cat_options="\n".join(cat_options),
        total=total,
    )
    (OUT_DIR / "index.html").write_text(index_html)

    shutil.copy(Path(__file__).parent / "assets" / "style.css", OUT_DIR / "style.css")
    shutil.copy(Path(__file__).parent / "assets" / "search.js", OUT_DIR / "search.js")

    print(f"Built {len(built_slugs)} recipe pages and {len(sections_html)} sections into {OUT_DIR}")


if __name__ == "__main__":
    build()
