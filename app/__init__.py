import os

from flask import Flask, request, render_template

from .models import *


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'sandbox.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

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

    return app
