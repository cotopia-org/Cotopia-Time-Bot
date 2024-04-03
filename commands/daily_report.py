import datetime

import pytz
from discord.ext import commands
from persiantools.jdatetime import JalaliDate

import log_processor
import report
from person import Person


@commands.hybrid_command(description="Session durations of the current day")
async def today(ctx):
    log_processor.renew_pendings(driver=str(ctx.guild.id))
    person = Person()
    locale = person.get_locale(discord_guild=ctx.guild.id, discord_id=ctx.author.id)
    tz = locale["timezone"]
    calsys = locale["cal_system"]

    now = datetime.datetime.now(pytz.timezone(tz))
    start_dt = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_epoch = int(start_dt.timestamp())
    end_epoch = start_epoch + (24 * 3600)

    the_board = report.make_board(
        driver=str(ctx.guild.id), start_epoch=start_epoch, end_epoch=end_epoch
    )

    if calsys == "Gregorian":
        title_date = datetime.date.fromtimestamp(start_epoch)
    elif calsys == "Jalali":
        title_date = JalaliDate.fromtimestamp(start_epoch)

    text = (
        "Net Session Hours of `"
        + str(title_date)
        + "`\n`tz: "
        + tz
        + "`\n------------------------------\n"
    )
    for i in the_board:
        text = text + str(i[1]) + " | <@" + i[0] + ">\n"

    await ctx.send(text)


@commands.hybrid_command(description="Session durations of the previous day")
async def yesterday(ctx):
    person = Person()
    locale = person.get_locale(discord_guild=ctx.guild.id, discord_id=ctx.author.id)
    tz = locale["timezone"]
    calsys = locale["cal_system"]

    now = datetime.datetime.now(pytz.timezone(tz))
    end_dt = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_epoch = int(end_dt.timestamp())
    start_epoch = end_epoch - (24 * 3600)

    the_board = report.make_board(
        driver=str(ctx.guild.id), start_epoch=start_epoch, end_epoch=end_epoch
    )

    if calsys == "Gregorian":
        title_date = datetime.date.fromtimestamp(start_epoch)
    elif calsys == "Jalali":
        title_date = JalaliDate.fromtimestamp(start_epoch)

    text = (
        "Net Session Hours of `"
        + str(title_date)
        + "`\n`tz: "
        + tz
        + "`\n------------------------------\n"
    )
    for i in the_board:
        text = text + str(i[1]) + " | <@" + i[0] + ">\n"

    await ctx.send(text)


async def setup(bot):
    bot.add_command(today)
    bot.add_command(yesterday)
