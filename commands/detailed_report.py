import datetime
from typing import Optional

import pytz
from discord import Member
from discord.ext import commands
from persiantools.jdatetime import JalaliDate, JalaliDateTime

import log_processor
import report
from person import Person


@commands.hybrid_command(
    description="Generates detailed report of a member. default date: current month"
)
async def detailed_report(
    ctx,
    member: Member,
    start_yyyy: Optional[int] = 4141,
    start_mm: Optional[int] = 41,
    start_dd: Optional[int] = 41,
    end_yyyy: Optional[int] = 4242,
    end_mm: Optional[int] = 42,
    end_dd: Optional[int] = 42,
):
    log_processor.renew_pendings(driver=str(ctx.guild.id))
    person = Person()
    locale = person.get_locale(discord_guild=ctx.guild.id, discord_id=ctx.author.id)
    tz = locale["timezone"]
    calsys = locale["cal_system"]

    if calsys == "Gregorian":
        now = datetime.datetime.now(pytz.timezone(tz))
    elif calsys == "Jalali":
        now = JalaliDateTime.now(pytz.timezone(tz))

    # I wanted to set now as default end value, but passing it in Args didnt work. So I do this:
    if end_yyyy == 4242 and end_mm == 42 and end_dd == 42:
        end_epoch = int(now.timestamp()) + 1
    else:
        try:
            if calsys == "Gregorian":
                user_input = datetime.datetime(
                    year=end_yyyy,
                    month=end_mm,
                    day=end_dd,
                    hour=23,
                    minute=59,
                    second=59,
                    tzinfo=pytz.timezone(tz),
                )
                print(f"END user input: {user_input}")
                end_epoch = int(user_input.timestamp()) + 1
            elif calsys == "Jalali":
                user_input = JalaliDateTime(
                    year=end_yyyy,
                    month=end_mm,
                    day=end_dd,
                    hour=23,
                    minute=59,
                    second=59,
                    tzinfo=pytz.timezone(tz),
                )
                print(f"END user input: {user_input}")
                end_epoch = int(user_input.timestamp()) + 1
        except:  # noqa: E722
            await ctx.send("Please enter a valid end date!", ephemeral=True)
            return

    # I wanted to set start of the month as default end value, but passing it in Args didnt work. So I do this:
    if start_yyyy == 4141 and start_mm == 41 and start_dd == 41:
        start_dt = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_epoch = int(start_dt.timestamp())
    else:
        try:
            if calsys == "Gregorian":
                user_input = datetime.datetime(
                    year=start_yyyy,
                    month=start_mm,
                    day=start_dd,
                    tzinfo=pytz.timezone(tz),
                )
                print(f"START user input: {user_input}")
                start_epoch = int(user_input.timestamp())
            elif calsys == "Jalali":
                user_input = JalaliDateTime(
                    year=start_yyyy,
                    month=start_mm,
                    day=start_dd,
                    tzinfo=pytz.timezone(tz),
                )
                print(f"START user input: {user_input}")
                start_epoch = int(user_input.timestamp())
        except:  # noqa: E722
            await ctx.send("Please enter a valid start date!", ephemeral=True)
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

    if calsys == "Gregorian":
        reportDate_from = datetime.datetime.fromtimestamp(
            start_epoch, tz=pytz.timezone(tz)
        ).strftime("%Y/%m/%d")
        reportDate_to = datetime.datetime.fromtimestamp(
            end_epoch, tz=pytz.timezone(tz)
        ).strftime("%Y/%m/%d")
    elif calsys == "Jalali":
        reportDate_to = JalaliDateTime.fromtimestamp(
            start_epoch, tz=pytz.timezone(tz)
        ).strftime("%Y/%m/%d")
        reportDate_from = JalaliDateTime.fromtimestamp(
            end_epoch, tz=pytz.timezone(tz)
        ).strftime("%Y/%m/%d")
    
    text = (
        "Report for "
        + member.mention
        + "\n"
        + "From: `"
        + reportDate_from
        + "`\n"
        + "To: `"
        + reportDate_to
        + "`\n"
        + "`tz: "
        + tz
        + "`\n------------------------------\n"
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
    bot.add_command(detailed_report)
