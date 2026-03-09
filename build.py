#!/usr/bin/env python
"""
Static site generator for yygarchive.org.
"""

import argparse
import json
import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


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

    for src in Path("static").iterdir():
        shutil.copy(src, out / src.name)

    for name in ["games.json", "CNAME", "404.html"]:
        src = Path(name)
        if src.exists():
            shutil.copy(src, out / name)

    env = Environment(loader=FileSystemLoader("templates"), autoescape=True)

    index_tmpl = env.get_template("index.html")
    (out / "index.html").write_text(index_tmpl.render(), encoding="utf-8")
    print("Built index.html")

    about_tmpl = env.get_template("about.html")
    (out / "about.html").write_text(about_tmpl.render(), encoding="utf-8")
    print("Built about.html")

    n_games = args.limit if args.limit else (None if args.all else 0)
    if n_games != 0:
        games_json = Path("games.json")
        if not games_json.exists():
            print("Warning: games.json not found, skipping game pages")
            return

        games = json.loads(games_json.read_text(encoding="utf-8"))
        subset = games if args.all else games[:n_games]

        games_dir = out / "game"
        games_dir.mkdir()
        game_tmpl = env.get_template("game.html")

        for i, game in enumerate(subset, 1):
            (games_dir / f'{game["id"]}.html').write_text(
                game_tmpl.render(game=game), encoding="utf-8"
            )
            if i % 1000 == 0:
                print(f"  {i}/{len(subset)} game pages…")

        print(f"Built {len(subset)} game pages → _site/game/<id>.html")


if __name__ == "__main__":
    main()
