from flask import Flask, request, render_template

from .models import *

__all__ = "app"

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search")
def search():
    query = request.args.get("query")
    results = (Game
               .select(Game, GameIndex.rank().alias("score"))
               .join(GameIndex, on=(Game.id == GameIndex.rowid))
               .where(GameIndex.match(query))
               .order_by(GameIndex.rank()))

    return render_template("search.html", results=results[:100])

@app.route("/game/<game_id>")
def game(game_id):
    game = Game.get(Game.id == int(game_id))
    return render_template("game.html", game=game)
