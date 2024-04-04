import datetime
from typing import Optional

import pytz
from discord import File, Member
from discord.ext import commands
from persiantools.jdatetime import JalaliDateTime

import log_processor
import report
from person import Person


@commands.hybrid_command(
    description="Generates a file containing all the events in the db for the given member in given period of time. Default date is current month."
)
async def raw_data(
    ctx,
    member: Member,
    start_yyyy: Optional[int] = 4141,
    start_mm: Optional[int] = 1,
    start_dd: Optional[int] = 1,
    end_yyyy: Optional[int] = 4242,
    end_mm: Optional[int] = 12,
    end_dd: Optional[int] = 29,
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
    # print(now)

    # I wanted to set now as default end value, but passing it in Args didnt work. So I do this:
    if end_yyyy == 4242 and end_mm == 12 and end_dd == 29:
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
                )
                user_input = pytz.timezone(tz).localize(user_input)
                # print(f"END user input: {user_input}")
                end_epoch = int(user_input.timestamp()) + 1
            elif calsys == "Jalali":
                user_input = JalaliDateTime(
                    year=end_yyyy,
                    month=end_mm,
                    day=end_dd,
                    hour=23,
                    minute=59,
                    second=59,
                )
                user_input = pytz.timezone(tz).localize(user_input)
                # print(f"END user input: {user_input}")
                end_epoch = int(user_input.timestamp()) + 1
        except:  # noqa: E722
            await ctx.send(
                f"Please enter a valid end date!\nYour calendar system is {calsys}.",
                ephemeral=True,
            )
            return

    # I wanted to set start of the month as default end value, but passing it in Args didnt work. So I do this:
    if start_yyyy == 4141 and start_mm == 1 and start_dd == 1:
        start_dt = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_epoch = int(start_dt.timestamp())
    else:
        try:
            if calsys == "Gregorian":
                user_input = datetime.datetime(
                    year=start_yyyy,
                    month=start_mm,
                    day=start_dd,
                )
                user_input = pytz.timezone(tz).localize(user_input)
                # print(f"START user input: {user_input}")
                start_epoch = int(user_input.timestamp())
            elif calsys == "Jalali":
                user_input = JalaliDateTime(
                    year=start_yyyy,
                    month=start_mm,
                    day=start_dd,
                )
                user_input = pytz.timezone(tz).localize(user_input)
                # print(f"START user input: {user_input}")
                start_epoch = int(user_input.timestamp())
        except:  # noqa: E722
            await ctx.send(
                f"Please enter a valid start date!\nYour calendar system is {calsys}.",
                ephemeral=True,
            )
            return

    if int(start_epoch) >= int(end_epoch):
        await ctx.send(
            f"**Start Date** should be before **End Date**! Try Again!\nYour calendar system is {calsys}.",
            ephemeral=True,
        )
        return
    # max int value in postgres is 	-2147483648 to 2147483647
    elif int(end_epoch) > 2147400000:
        await ctx.send(
            f"**End Date** is too far in the future! Try Again!\nYour calendar system is {calsys}.",
            ephemeral=True,
        )
        return
    elif int(start_epoch) < 0:
        await ctx.send(
            f"I wasn't even born back then! Try Again!\nYour calendar system is {calsys}.",
            ephemeral=True,
        )
        return

    # print("start epoch: " + str(start_epoch))
    # print("end epoch: " + str(end_epoch))

    thereport = report.make_raw_file(
        driver=str(ctx.guild.id),
        doer=str(member.id),
        start_epoch=int(start_epoch),
        end_epoch=int(end_epoch),
        asker_id=ctx.author.id,
    )

    await ctx.send(file=File(thereport))


async def setup(bot):
    bot.add_command(raw_data)
