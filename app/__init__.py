import os
from random import randint

from flask import Flask, abort, redirect, render_template, request, url_for

from .models import Game, GameIndex


def create_app(test_config=None):
    # Initial logic from https://flask.palletsprojects.com/en/stable/tutorial/factory/
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "sandbox.sqlite"),
    )
    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
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

        if query:
            results = (
                Game.select(Game, GameIndex.rank().alias("score"))
                .join(GameIndex, on=(GameIndex.rowid == Game.id))
                .where(GameIndex.match(query))
            )
        else:
            abort(400, description="No search terms provided")

        results = list(results)  # convert to list for templating

        return render_template("search.html", results=results, query=query)

    @app.route("/developer/<developer_name>")
    def developer(developer_name):
        results = Game.select().where(Game.developer == developer_name)
        results = list(results)
        return render_template(
            "developer.html", results=results, developer_name=developer_name
        )

    @app.route("/top")
    def top():
        results = Game.select().order_by(Game.downloads.desc()).limit(1000)

        return render_template("search.html", results=results)

    @app.route("/game/<int:game_id>")
    def game(game_id):
        game = Game.get(Game.id == game_id)
        if game is None:
            abort(404)
        return render_template("game.html", game=game)

    @app.route("/random")
    def random():
        count = Game.select().count()
        if count == 0:
            abort(500)
        random_index = randint(0, count - 1)
        game = Game.select().order_by(Game.id).offset(random_index).limit(1).first()
        return redirect(url_for("game", game_id=game.id))

    return app
