import datetime

import pytz
from discord.ext import commands
from persiantools.jdatetime import JalaliDate, JalaliDateTime

import log_processor
import report
from person import Person


@commands.hybrid_command(description="جدول مدت سشن های این ماه")
async def inmaah(ctx):
    log_processor.renew_pendings(driver=str(ctx.guild.id))

    emrooz = JalaliDate.today()
    person = Person()
    tz = person.get_timezone(discord_guild=ctx.guild.id, discord_id=ctx.author.id)

    start_dt = JalaliDateTime(year=emrooz.year, month=emrooz.month, day=1)
    localized_start_dt = pytz.timezone(tz).localize(dt=start_dt)
    start_epoch = int(localized_start_dt.timestamp())

    end_dt = JalaliDateTime(
        year=emrooz.year,
        month=emrooz.month,
        day=emrooz.day,
        hour=23,
        minute=59,
        second=59,
    )
    localized_end_dt = pytz.timezone(tz).localize(dt=end_dt)
    end_epoch = int(localized_end_dt.timestamp()) + 1

    the_board = report.make_board(
        driver=str(ctx.guild.id), start_epoch=start_epoch, end_epoch=end_epoch
    )

    title_date = JalaliDate.fromtimestamp(start_epoch).strftime("%Y/%m")
    # discordDate_to = JalaliDateTime.fromtimestamp(end_epoch, pytz.timezone(tz)).strftime("%c")

    text = (
        "Net Session Hours of " + str(title_date) + "\n------------------------------\n"
    )
    for i in the_board:
        text = text + str(i[1]) + " | <@" + i[0] + ">\n"

    await ctx.send(text)


@commands.hybrid_command(description="Session durations of current month")
async def thismonth(ctx):
    log_processor.renew_pendings(driver=str(ctx.guild.id))

    today = datetime.date.today()
    person = Person()
    tz = person.get_timezone(discord_guild=ctx.guild.id, discord_id=ctx.author.id)

    start_dt = datetime.datetime(year=today.year, month=today.month, day=1)
    localized_start_dt = pytz.timezone(tz).localize(dt=start_dt)
    start_epoch = int(localized_start_dt.timestamp())

    end_dt = datetime.datetime(
        year=today.year,
        month=today.month,
        day=today.day,
        hour=23,
        minute=59,
        second=59,
    )
    localized_end_dt = pytz.timezone(tz).localize(dt=end_dt)
    end_epoch = int(localized_end_dt.timestamp()) + 1

    the_board = report.make_board(
        driver=str(ctx.guild.id), start_epoch=start_epoch, end_epoch=end_epoch
    )

    title_date = datetime.date.fromtimestamp(start_epoch).strftime("%Y/%m")
    # discordDate_to = JalaliDateTime.fromtimestamp(end_epoch, pytz.timezone(tz)).strftime("%c")

    text = (
        "Net Session Hours of " + str(title_date) + "\n------------------------------\n"
    )
    for i in the_board:
        text = text + str(i[1]) + " | <@" + i[0] + ">\n"

    await ctx.send(text)


async def setup(bot):
    bot.add_command(inmaah)
    bot.add_command(thismonth)
