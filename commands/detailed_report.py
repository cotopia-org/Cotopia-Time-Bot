import datetime
from typing import Optional

import pytz
from discord import Member
from discord.ext import commands
from persiantools.jdatetime import JalaliDate, JalaliDateTime

import report
from person import Person


@commands.hybrid_command(description="Generates report. default date: current month")
async def viewstats(
    ctx,
    member: Member,
    start_yyyy: Optional[int] = 1971,
    start_mm: Optional[int] = 1,
    start_dd: Optional[int] = 1,
    end_yyyy: Optional[int] = 2037,
    end_mm: Optional[int] = 1,
    end_dd: Optional[int] = 29,
):
    today = datetime.date.today()

    # I want to set today as default end value, but passing it in Args didnt work. So I do this:
    if end_yyyy == 2037 and end_mm == 12 and end_dd == 29:
        end_epoch = datetime.datetime(
            year=today.year,
            month=today.month,
            day=today.day,
            hour=23,
            minute=59,
            second=59,
        ).strftime("%s")
    else:
        try:
            end_epoch = datetime.datetime(
                year=end_yyyy,
                month=end_mm,
                day=end_dd,
                hour=23,
                minute=59,
                second=59,
            ).strftime("%s")
        except:  # noqa: E722
            await ctx.send("Please enter a valid date!", ephemeral=True)
            return

    if start_yyyy == 1971 and start_mm == 1 and start_dd == 1:
        start_epoch = datetime.datetime(
            year=today.year, month=today.month, day=1, hour=0, minute=0, second=0
        ).strftime("%s")
    else:
        try:
            start_epoch = datetime.datetime(
                year=start_yyyy,
                month=start_mm,
                day=start_dd,
                hour=0,
                minute=0,
                second=0,
            ).strftime("%s")
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

    thereport = report.make_report(
        driver=str(ctx.guild.id),
        doer=str(member.id),
        start_epoch=start_epoch,
        end_epoch=end_epoch,
    )
    discordDate_from = "<t:" + thereport["From"] + ":D>"
    discordDate_to = "<t:" + thereport["To"] + ":D>"
    text = (
        "Report for "
        + member.mention
        + "\n"
        + "From: "
        + discordDate_from
        + "\n"
        + "To: "
        + discordDate_to
        + "\n"
        + "------------------------------\n"
    )

    for line in thereport:
        if line == "User":
            pass
        elif line == "From":
            pass
        elif line == "To":
            pass
        else:
            text = text + str(line) + ": " + str(thereport[line]) + "\n"

    await ctx.send(text, ephemeral=True)


@commands.hybrid_command(description="گزارش ایجاد می کند. تاریخ پیش فرض: ماه جاری")
async def viewgozaresh(
    ctx,
    member: Member,
    start_ssss: Optional[int] = 1349,
    start_mm: Optional[int] = 1,
    start_rr: Optional[int] = 1,
    end_ssss: Optional[int] = 1415,
    end_mm: Optional[int] = 12,
    end_rr: Optional[int] = 29,
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

    thereport = report.make_report(
        driver=str(ctx.guild.id),
        doer=str(member.id),
        start_epoch=start_epoch,
        end_epoch=end_epoch,
    )
    discordDate_from = JalaliDateTime.fromtimestamp(
        int(thereport["From"]), pytz.timezone(tz)
    ).strftime("%c")
    discordDate_to = JalaliDateTime.fromtimestamp(
        int(thereport["To"]), pytz.timezone(tz)
    ).strftime("%c")
    text = (
        "Report for "
        + member.mention
        + "\n"
        + "From: "
        + discordDate_from
        + "\n"
        + "To: "
        + discordDate_to
        + "\n"
        + "------------------------------\n"
    )

    for line in thereport:
        if line == "User":
            pass
        elif line == "From":
            pass
        elif line == "To":
            pass
        else:
            text = text + str(line) + ": " + str(thereport[line]) + "\n"

    await ctx.send(text, ephemeral=True)


async def setup(bot):
    bot.add_command(viewgozaresh)
    bot.add_command(viewstats)
