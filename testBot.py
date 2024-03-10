import asyncio
import datetime
import json
import time
import typing

import discord
import pytz
from discord.ext import commands
from persiantools.jdatetime import JalaliDate, JalaliDateTime, timedelta

import auth
import log_processor
import raw_logger
import report
import settings
import zombie_hunter
from board.the_text import (
    gen_dirooz_board,
    gen_inmaah_board,
    update_dirooz_board,
    update_inmaah_board,
)
from gcal import calcal as GCalSetup
from person import MySettingsModal, Person
from server import Server
from talk_with import TalkWithView
from utils.utils import play_ring_voice

logger = settings.logging.getLogger("bot")

the_zombie = {}
last_profile_update = {}
temp_channels = []
temp_messages = {}


# returns epoch of NOW: int
def rightnow():
    epoch = int(time.time())
    return epoch


def run():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.presences = True
    intents.members = True
    intents.reactions = True

    bot = commands.Bot(command_prefix="/", intents=intents)

    @bot.event
    async def on_ready():
        logger.info(f"User: {bot.user} (ID: {bot.user.id})")
        await bot.tree.sync()

    @bot.hybrid_command()
    async def test(ctx, member: discord.Member, member2: discord.Member):
        await play_ring_voice(discord, bot, ctx, member)
        await play_ring_voice(discord, bot, ctx, member2)
        await ctx.send('Hello', ephemeral=True)

    bot.run('MTIxNDUyODIzNDQ4MjMxMTE4OA.GUeQOK.y6aGzmlKBp1IyUyPVguXn87O0DAalYOudQguQY', root_logger=True)


if __name__ == "__main__":
    run()
