#!/usr/bin/env python
"""
Dev server for yygarchive.org to render templates on the fly.
"""

import argparse
import json
from pathlib import Path

from flask import Flask, abort, send_from_directory
from jinja2 import Environment, FileSystemLoader

app = Flask(__name__)
env = Environment(loader=FileSystemLoader("templates"), autoescape=True, auto_reload=True)


@app.route("/")
def index():
    p = Path("static/games.json")
    games = json.loads(p.read_text(encoding="utf-8")) if p.exists() else []
    initial_games = sorted(games, key=lambda g: g["downloads"], reverse=True)[:50]
    return env.get_template("index.html").render(initial_games_json=json.dumps(initial_games), canonical_path="/")


@app.route("/about")
def about():
    return env.get_template("about.html").render(canonical_path="/about")


@app.route("/game/<int:game_id>")
def game(game_id):
    p = Path("static/games.json")
    if not p.exists():
        abort(404)
    games = {g["id"]: g for g in json.loads(p.read_text(encoding="utf-8"))}
    g = games.get(game_id)
    if g is None:
        abort(404)
    return env.get_template("game.html").render(game=g, canonical_path=f"/game/{game_id}")


@app.errorhandler(404)
def page_not_found(e):
    return send_from_directory("static", "404.html"), 404


@app.route("/<path:filename>")
def static_files(filename):
    if (Path("static") / filename).exists():
        return send_from_directory("static", filename)
    return send_from_directory(".", filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    print(f"Dev server running at http://localhost:{args.port}/")
    app.run(debug=True, port=args.port)
