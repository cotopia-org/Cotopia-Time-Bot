from datetime import datetime

from peewee import *
from playhouse.postgres_ext import JSONField

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


class Brief(BaseModel):
    ts = TimestampField(default=datetime.now, null=False)
    epoch = IntegerField()
    doer = CharField()
    content = TextField()
    driver = CharField(default='1125764070935638086')


class DiroozBoard(BaseModel):
    guild_id = BigIntegerField(null=False)
    channel_id = BigIntegerField(null=False)
    msg_id = BigIntegerField(null=False)
    last_update = BigIntegerField(null=False)


class DiscordEvent(BaseModel):
    ts = TimestampField(default=datetime.now, null=False)
    epoch = IntegerField()
    doer = CharField()
    kind = CharField()
    isPair = BooleanField(default=False)
    pairId = IntegerField()
    isValid = BooleanField(default=True)
    note = JSONField()
    duration = IntegerField(default=-1)
    driver = CharField(default='1125764070935638086')


class Idle(BaseModel):
    guild_id = BigIntegerField(null=False)
    member_id = BigIntegerField(null=False)


class InMaahBoard(BaseModel):
    guild_id = BigIntegerField(null=False)
    channel_id = BigIntegerField(null=False)
    msg_id = BigIntegerField(null=False)
    last_update = BigIntegerField(null=False)


class JobEvent(BaseModel):
    guild_id = BigIntegerField(null=False)
    discord_id = BigIntegerField(null=False)
    start_epoch = BigIntegerField(null=False)
    end_epoch = BigIntegerField(null=False)
    duration = IntegerField()
    isJob = BooleanField(default=True)
    job_id = IntegerField()
    brief_id = IntegerField()
    title = CharField()


class JobPending(BaseModel):
    guild_id = BigIntegerField(null=False)
    discord_id = BigIntegerField(null=False)
    event_id = IntegerField(null=False)


class JobPost(BaseModel):
    guild_id = BigIntegerField(null=False)
    channel_id = BigIntegerField(null=False)
    post_id = BigIntegerField(null=False)
    job_id = IntegerField(null=False)
    author_id = BigIntegerField(default=-1, null=False)


class PendingEvent(BaseModel):
    ts = TimestampField(default=datetime.now, null=False)
    doer = CharField()
    kind = CharField()
    pendingId = IntegerField()
    driver = CharField(default='1125764070935638086')


class Person(BaseModel):
    created_at = TimestampField(default=datetime.now, null=False)
    discord_guild = BigIntegerField()
    discord_id = BigIntegerField()
    discord_name = CharField()
    email = CharField()
    trc20_addr = CharField()
    active = BooleanField(default=True)
    google_token = JSONField()
    calendar = JSONField()
    discord_avatar = CharField()


class Server(BaseModel):
    created_at = TimestampField(default=datetime.now, null=False)
    discord_created_at = TimestampField(default=datetime.now, null=False)
    discord_guild_id = BigIntegerField()
    discord_unavailable = BooleanField(default=False)
    active = BooleanField(default=False)
    discord_name = CharField()
    discord_banner = CharField()
    discord_icon = CharField()
    discord_description = CharField()
    discord_owner_name = CharField()
    discord_member_count = IntegerField()
    discord_preferred_locale = IntegerField()
    note = JSONField()


class StatusText(BaseModel):
    guild_id = BigIntegerField(null=False)
    channel_id = BigIntegerField(null=False)
    msg_id = BigIntegerField(null=False)


db.create_tables(
    [Brief, DiroozBoard, DiscordEvent, Idle, JobEvent, JobPending, JobPost, PendingEvent, Person, Server, StatusText])
