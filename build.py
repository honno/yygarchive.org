#!/usr/bin/env python
"""
Static site generator for yygarchive.org.
"""

import argparse
import json
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

SITE_URL = "https://yygarchive.org"
SITEMAP_SCHEMA_URL = "http://www.sitemaps.org/schemas/sitemap/0.9"
SITEMAP_CHUNK_SIZE = 50_000  # i.e. the limit of urls per sitemap so google search console is happy


def add_url(element: ET.Element, loc: str, **kw) -> None:
    url = ET.SubElement(element, "url")
    ET.SubElement(url, "loc").text = loc
    for k, v in kw.items():
        ET.SubElement(url, k).text = v


def build_sitemaps(games: list, out: Path) -> None:
    child_names = []

    pages_name = "sitemap_pages.xml"
    urlset = ET.Element("urlset", {"xmlns": SITEMAP_SCHEMA_URL})
    add_url(urlset, f"{SITE_URL}/", priority="1.0")
    add_url(urlset, f"{SITE_URL}/about")
    ET.indent(urlset, space="  ", level=0)
    ET.ElementTree(urlset).write(out / pages_name, encoding="utf-8", xml_declaration=True)
    child_names.append(pages_name)

    for i, offset in enumerate(range(0, len(games), SITEMAP_CHUNK_SIZE), start=1):
        name = f"sitemap_games_{i}.xml"
        urlset = ET.Element("urlset", {"xmlns": SITEMAP_SCHEMA_URL})
        for game in games[offset : offset + SITEMAP_CHUNK_SIZE]:
            add_url(urlset, f"{SITE_URL}/game/{game['id']}")
        ET.indent(urlset, space="  ", level=0)
        ET.ElementTree(urlset).write(out / name, encoding="utf-8", xml_declaration=True)
        child_names.append(name)

    sitemapindex = ET.Element("sitemapindex", {"xmlns": SITEMAP_SCHEMA_URL})
    for name in child_names:
        sitemap = ET.SubElement(sitemapindex, "sitemap")
        ET.SubElement(sitemap, "loc").text = f"{SITE_URL}/{name}"
    ET.indent(sitemapindex, space="  ", level=0)
    ET.ElementTree(sitemapindex).write(out / "sitemap.xml", encoding="utf-8", xml_declaration=True)


def main():
    parser = argparse.ArgumentParser(description="Build yygarchive.org static site")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--limit", type=int, metavar="N", help="Build index + N game pages")
    group.add_argument("--all", action="store_true", help="Build all game pages")
    args = parser.parse_args()

    out = Path("_site")
    if out.exists():
        shutil.rmtree(out)
    out.mkdir()

    static_path = Path("static")

    for src in static_path.iterdir():
        shutil.copy(src, out / src.name)
    print("Copied files in static/")

    shutil.copy("CNAME", out / "CNAME")

    games_json = static_path / "games.json"
    games = json.loads(games_json.read_text(encoding="utf-8"))

    # Pre-render top 50 games
    initial_games = sorted(games, key=lambda g: g["downloads"], reverse=True)[:50]

    env = Environment(loader=FileSystemLoader("templates"), autoescape=True)

    index_tmpl = env.get_template("index.html")
    (out / "index.html").write_text(index_tmpl.render(initial_games_json=json.dumps(initial_games), canonical_path="/"), encoding="utf-8")
    print("Built index.html")

    about_tmpl = env.get_template("about.html")
    (out / "about.html").write_text(about_tmpl.render(canonical_path="/about"), encoding="utf-8")
    print("Built about.html")

    n_games = args.limit if args.limit else (None if args.all else 0)
    if n_games != 0:
        subset = games if args.all else games[:n_games]

        games_dir = out / "game"
        games_dir.mkdir()
        game_tmpl = env.get_template("game.html")

        for i, game in enumerate(subset, 1):
            (games_dir / f'{game["id"]}.html').write_text(game_tmpl.render(game=game, canonical_path=f"/game/{game['id']}"), encoding="utf-8" )
            if i % 1000 == 0:
                print(f"  {i}/{len(subset)} game pages…")

        print(f"Built {len(subset)} game pages → _site/game/<id>.html")

    build_sitemaps(games, out)
    print("Built sitemaps")


if __name__ == "__main__":
    main()
