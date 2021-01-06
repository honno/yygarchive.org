from flask import Flask, request, render_template
from peewee import Model, IntegerField, CharField, DateField, FloatField
from playhouse.sqlite_ext import SqliteExtDatabase, FTSModel, SearchField, RowIDField

app = Flask(__name__)

db = SqliteExtDatabase("sandbox.db")

class Game(Model):
    id = IntegerField(primary_key=True)
    slug = CharField()
    title = CharField()
    developer = CharField()
    date = DateField()
    category = CharField()
    description = CharField()
    tags = CharField()
    rating = FloatField()
    nratings = IntegerField()
    downloads = IntegerField()
    version = IntegerField()

    class Meta:
        database = db

class GameIndex(FTSModel):
    rowid = RowIDField()
    slug = SearchField()
    title = SearchField()
    description = SearchField()
    developer = SearchField()
    category = SearchField()
    tags = SearchField()

    class Meta:
        database = db

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
