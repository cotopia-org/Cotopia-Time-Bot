import datetime

import pytz
from discord.ext import commands
from persiantools.jdatetime import JalaliDateTime, timedelta

import log_processor
import report
from person import Person


@commands.hybrid_command(description="Session durations of current month")
async def thismonth(ctx):
    log_processor.renew_pendings(driver=str(ctx.guild.id))
    person = Person()
    locale = person.get_locale(discord_guild=ctx.guild.id, discord_id=ctx.author.id)
    tz = locale["timezone"]
    calsys = locale["cal_system"]

    if calsys == "Gregorian":
        now = datetime.datetime.now(pytz.timezone(tz))
    elif calsys == "Jalali":
        now = JalaliDateTime.now(pytz.timezone(tz))

    start_dt = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start_epoch = int(start_dt.timestamp())
    end_epoch = int(now.timestamp()) + 1

    the_board = report.make_board(
        driver=str(ctx.guild.id), start_epoch=start_epoch, end_epoch=end_epoch
    )

    if calsys == "Gregorian":
        title_date = datetime.datetime.fromtimestamp(
            start_epoch, tz=pytz.timezone(tz)
        ).strftime("%Y/%m")
    elif calsys == "Jalali":
        title_date = JalaliDateTime.fromtimestamp(
            start_epoch, tz=pytz.timezone(tz)
        ).strftime("%Y/%m")

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


@commands.hybrid_command(description="Session durations of previous month")
async def lastmonth(ctx):
    person = Person()
    locale = person.get_locale(discord_guild=ctx.guild.id, discord_id=ctx.author.id)
    tz = locale["timezone"]
    calsys = locale["cal_system"]

    if calsys == "Gregorian":
        now = datetime.datetime.now(pytz.timezone(tz))
    elif calsys == "Jalali":
        now = JalaliDateTime.now(pytz.timezone(tz))

    end_dt = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_epoch = int(end_dt.timestamp())
    if calsys == "Gregorian":
        last_month_day = end_dt - datetime.timedelta(days=2)
    elif calsys == "Jalali":
        last_month_day = end_dt - timedelta(days=2)
    start_dt = last_month_day.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start_epoch = int(start_dt.timestamp())

    the_board = report.make_board(
        driver=str(ctx.guild.id), start_epoch=start_epoch, end_epoch=end_epoch
    )

    if calsys == "Gregorian":
        title_date = datetime.datetime.fromtimestamp(
            start_epoch, tz=pytz.timezone(tz)
        ).strftime("%Y/%m")
    elif calsys == "Jalali":
        title_date = JalaliDateTime.fromtimestamp(
            start_epoch, tz=pytz.timezone(tz)
        ).strftime("%Y/%m")

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
    bot.add_command(thismonth)
    bot.add_command(lastmonth)
