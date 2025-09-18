import os

from flask import Flask, request, render_template, redirect, url_for
from peewee import fn

from .models import *


def create_app(test_config=None):
    # Initial logic from https://flask.palletsprojects.com/en/stable/tutorial/factory/
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'sandbox.sqlite'),
    )
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    if app.debug:
        app.jinja_env.auto_reload = True
        app.config["TEMPLATES_AUTO_RELOAD"] = True

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/about")
    def about():
        return render_template("about.html")

    @app.route("/search")
    def search():
        query = request.args.get("query")
        by = request.args.get("by")

        where_clause = Game.developer.contains(by) if by else GameIndex.match(query)
        results = (Game
                   .select(Game, GameIndex.rank().alias("score"))
                   .join(GameIndex, on=(Game.id == GameIndex.rowid))
                   .where(where_clause)
                   .order_by(GameIndex.rank()))

        return render_template("search.html", results=results, by=by)

    @app.route("/top")
    def top():
        results = (Game
                   .select()
                   .order_by(Game.downloads.desc())
                   .limit(1000)
        )

        return render_template("search.html", results=results)


    @app.route("/game/<game_id>")
    def game(game_id):
        game = Game.get(Game.id == int(game_id))
        return render_template("game.html", game=game)

    @app.route("/random")
    def random():
        game = (Game
                   .select()
                   .order_by(fn.Random())
                   .limit(1)
                   .get()
        )
        return redirect(url_for("game", game_id=game.id))

    return app
