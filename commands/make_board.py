import datetime
from typing import Optional

import pytz
from discord import Member
from discord.ext import commands
from persiantools.jdatetime import JalaliDateTime

import log_processor
import report
from person import Person


@commands.hybrid_command()
async def make_board(
    ctx,
    start_ssss: typing.Optional[int] = 1349,
    start_mm: typing.Optional[int] = 1,
    start_rr: typing.Optional[int] = 1,
    end_ssss: typing.Optional[int] = 1415,
    end_mm: typing.Optional[int] = 12,
    end_rr: typing.Optional[int] = 29,
):
    emrooz = JalaliDate.today()
    person = Person()
    tz = person.get_timezone(discord_guild=ctx.guild.id, discord_id=ctx.author.id)

    # I want to set today as default end value, but passing it in Args didnt work. So I do this:
    if end_ssss == 1415 and end_mm == 12 and end_rr == 29:
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
    else:
        try:
            end_dt = JalaliDateTime(
                year=end_ssss,
                month=end_mm,
                day=end_rr,
                hour=23,
                minute=59,
                second=59,
            )
            localized_end_dt = pytz.timezone(tz).localize(dt=end_dt)
            end_epoch = int(localized_end_dt.timestamp()) + 1
        except:  # noqa: E722
            await ctx.send("Please enter a valid date!", ephemeral=True)
            return

    if start_ssss == 1349 and start_mm == 1 and start_rr == 1:
        start_dt = JalaliDateTime(year=emrooz.year, month=emrooz.month, day=1)
        localized_start_dt = pytz.timezone(tz).localize(dt=start_dt)
        start_epoch = int(localized_start_dt.timestamp())
    else:
        try:
            start_dt = JalaliDateTime(year=start_ssss, month=start_mm, day=start_rr)
            localized_start_dt = pytz.timezone(tz).localize(dt=start_dt)
            start_epoch = int(localized_start_dt.timestamp())
        except:  # noqa: E722
            await ctx.send("Please enter a valid date!", ephemeral=True)
            return

    if int(start_epoch) >= int(end_epoch):
        await ctx.send(
            "**Start Date** should be before **End Date**! Try Again!",
            ephemeral=True,
        )
        return
    # max int value in postgres is 	-2147483648 to 2147483647
    elif int(end_epoch) > 2147400000:
        await ctx.send(
            "**End Date** is too far in the future! Try Again!", ephemeral=True
        )
        return
    elif int(start_epoch) < 0:
        await ctx.send("I wasn't even born back then! Try Again!", ephemeral=True)
        return

    print("start epoch: " + str(start_epoch))
    print("end epoch: " + str(end_epoch))

    log_processor.renew_pendings(driver=str(ctx.guild.id))
    the_board = report.make_board(
        driver=str(ctx.guild.id), start_epoch=start_epoch, end_epoch=end_epoch
    )

    discordDate_from = JalaliDateTime.fromtimestamp(
        int(start_epoch), pytz.timezone(tz)
    ).strftime("%c")
    discordDate_to = JalaliDateTime.fromtimestamp(
        int(end_epoch), pytz.timezone(tz)
    ).strftime("%c")

    text = (
        "Net Session Hours\n" + "From:  " + str(discordDate_from) + "\n"
        "To:  " + str(discordDate_to) + "\n------------------------------\n"
    )
    for i in the_board:
        text = text + str(i[1]) + " | <@" + i[0] + ">\n"
        # string = str(i)
        # string = string.replace("('", "")
        # string = string.replace("',", " :")
        # string = string.replace(")", "")
        # text = text + string + "\n"

    await ctx.send(text)


async def setup(bot):
    bot.add_command(make_board)
