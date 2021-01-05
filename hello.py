from flask import Flask, render_template
from peewee import *

app = Flask(__name__)

db = SqliteDatabase('sandbox.db')

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
        database = db # this model uses the "people.db" database.

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/game/<game_id>")
def hello(game_id):
    game = Game.get(Game.id == int(game_id))
    return render_template("game.html", game=game)
