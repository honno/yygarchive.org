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
    return env.get_template("index.html").render()


@app.route("/about")
def about():
    return env.get_template("about.html").render()


@app.route("/game/<int:game_id>")
def game(game_id):
    p = Path("games.json")
    if not p.exists():
        abort(404)
    games = {g["id"]: g for g in json.loads(p.read_text(encoding="utf-8"))}
    g = games.get(game_id)
    if g is None:
        abort(404)
    return env.get_template("game.html").render(game=g)


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
