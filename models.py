from peewee import Model, IntegerField, CharField, DateField, FloatField, TextField
from playhouse.sqlite_ext import SqliteExtDatabase, FTSModel, SearchField, RowIDField

__all__ = ["Game", "GameIndex"]

db = SqliteExtDatabase("sandbox.db")

class Game(Model):
    id = IntegerField(primary_key=True)
    slug = CharField()
    title = CharField()
    developer = CharField()
    date = DateField()
    category = CharField()
    description = TextField()
    tags = TextField()
    rating = FloatField()
    nratings = IntegerField()
    downloads = IntegerField()
    version = IntegerField()
    dl_url = CharField()

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

