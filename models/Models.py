from peewee import *

import settings

db = PostgresqlDatabase(
    database=settings.DATABASE,
    user=settings.DATABASE_USER,
    password=settings.DATABASE_PASSWORD,
    host=settings.DATABASE_HOST,
    port=settings.DATABASE_PORT)


class BaseModel(Model):
    """A base model that will use our Postgresql database"""

    class Meta:
        database = db


class Book(BaseModel):
    name = CharField()


db.create_tables([Book])
