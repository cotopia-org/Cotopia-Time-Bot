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
from person import Person, my_settings_view
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
        for cmd_file in settings.CMDS_DIR.glob("*.py"):
            if cmd_file.name != "__init__.py":
                await bot.load_extension(f"commands.{cmd_file.name[:-3]}")
        
        await bot.tree.sync()


    @bot.event
    async def on_guild_join(guild):
        # Updating server table
        server = Server()
        banner = None
        icon = None
        if guild.banner is not None:
            banner = str(guild.banner)
        if guild.icon is not None:
            icon = str(guild.icon)
        server.setter(
            guild_id=guild.id,
            unavailable=guild.unavailable,
            banner=banner,
            icon=icon,
            created_at=guild.created_at,
            name=guild.name,
            description=guild.description,
            member_count=guild.member_count,
            owner_name=guild.owner.name,
            preferred_locale=str(guild.preferred_locale),
        )

        # Updating person table
        count = 0
        person = Person()
        for i in guild.members:
            if i.bot is False:
                if i.avatar is None:
                    person.add_person(guild.id, i.id, i.name)
                else:
                    person.add_person(guild.id, i.id, i.name, str(i.avatar))

                count = count + 1

        print(f"Updated {count} profiles!")

        await gen_inmaah_board(guild=guild)
        await gen_dirooz_board(guild=guild)

    @bot.event
    async def on_member_join(member):
        # Updating person table
        guild = member.guild
        count = 0
        person = Person()
        for i in guild.members:
            if i.bot is False:
                if i.avatar is None:
                    person.add_person(guild.id, i.id, i.name)
                else:
                    person.add_person(guild.id, i.id, i.name, str(i.avatar))

                count = count + 1

        print(f"Updated {count} profiles!")

    @bot.event
    async def on_message(message):

        if message.author == bot.user:
            return

        # cancelling the zombie
        global the_zombie
        if message.guild.id in the_zombie:
            if message.author == the_zombie[message.guild.id]:
                (task,) = [
                    task
                    for task in asyncio.all_tasks()
                    if task.get_name() == f"dc zombie {message.guild.id}"
                ]
                task.cancel()
                await message.channel.send(
                    "Well well you are not a zombie " + message.author.mention + "!"
                )
                the_zombie[message.guild.id] = None

    @bot.event
    async def on_voice_state_update(member, before, after):

        # Ignoring Bots
        if member.bot:
            return

        # deleting temp channels
        # func that does the job after a while
        task_del_chan = None

        async def del_temp_chan(channel):
            print("del_temp_chan been called!")
            print("the channel is:  " + str(channel))
            await asyncio.sleep(180)  # 3 minutes
            global temp_channels
            if len(channel.members) == 0:
                try:
                    print("trying to delete channel:    ")
                    print(channel)
                    await channel.delete()
                    temp_channels.remove(channel)
                    print("channel was removed")
                except Exception as e:
                    print("Sorry couldn't delete the temp channel!")
                    print(e)
                try:
                    global temp_messages
                    # msg = temp_messages[channel]
                    msg = await temp_messages[channel].channel.fetch_message(
                        temp_messages[channel].id
                    )
                    print("trying to edit text:   ")
                    print(msg)
                    msg_content = msg.content
                    # getting the status part
                    status_part = msg_content.split("--------------------")[1]
                    # getting the author mention
                    author_mention = msg_content.split(">,\n")[1]
                    author_mention = author_mention.split(" wants to talk with you.")[0]
                    # calculating the duration of the meeting
                    msg_created_at = msg.created_at.timestamp()
                    duration = (
                        rightnow() - msg_created_at - 180
                    )  # minus 180 seconds, time of waiting before deleting voice channel
                    duration = round((duration / 60), 1)
                    #
                    # await msg.delete()
                    # editing the message
                    new_content = (
                        author_mention
                        + "'s meeting ended!\n"
                        + "Duration: "
                        + str(duration)
                        + " minutes"
                        + "\n--------------------"
                        + status_part
                        + "--------------------"
                    )
                    await msg.edit(content=new_content, view=None)
                    del temp_messages[channel]
                    print("message was edited")
                except Exception as e:
                    print("Sorry couldn't edit the /talk_with message!")
                    print(e)

        # calling the  del_temp_chan(channel) func
        global temp_channels
        if before.channel in temp_channels:
            if len(before.channel.members) == 0:
                task_del_chan = asyncio.create_task(
                    del_temp_chan(before.channel),
                    name=f"deleting temp channel {before.channel.id}",
                )
                await task_del_chan

        guild = member.guild
        print("this is on_voice_state_update. the server is:")
        print(guild.id)

        # cancelling the zombie
        global the_zombie
        if guild.id in the_zombie:
            if member == the_zombie[guild.id]:
                (task,) = [
                    task
                    for task in asyncio.all_tasks()
                    if task.get_name() == f"dc zombie {guild.id}"
                ]
                task.cancel()
                try:
                    await guild.system_channel.send(
                        "Well well you are not a zombie " + member.mention + "!"
                    )
                except:  # noqa: E722
                    await guild.text_channels[0].send(
                        "Well well you are not a zombie " + member.mention + "!"
                    )
                the_zombie[guild.id] = None

        # when user joins voice
        if before.channel is None:
            pass

        # When user leaves voice channel
        if after.channel is None:
            # Update user profile
            try:
                global last_profile_update
                if f"{member.id}@{member.guild.id}" in last_profile_update:
                    pass
                else:
                    last_profile_update[f"{member.id}@{member.guild.id}"] = (
                        datetime.datetime.today().strftime("%Y-%m-%d")
                    )

                if last_profile_update[
                    f"{member.id}@{member.guild.id}"
                ] != datetime.datetime.today().strftime("%Y-%m-%d"):
                    keyword = member.guild.name
                    person = Person()
                    person.set_avatar(
                        member.guild.id, member.id, str(member.avatar), member.name
                    )
                    cal = GCalSetup.get_processed_events(
                        member.guild.id, member.id, keyword
                    )
                    person.set_cal(member.guild.id, member.id, json.dumps(cal))
                    last_profile_update[f"{member.id}@{member.guild.id}"] = (
                        datetime.datetime.today().strftime("%Y-%m-%d")
                    )
            except:  # noqa: E722
                print("could not get cal!")

        # When user joins a /talk_with channel
        global temp_messages
        if after.channel in temp_messages:
            talk_with_msg = await temp_messages[after.channel].channel.fetch_message(
                temp_messages[after.channel].id
            )
            talk_with_text = talk_with_msg.content
            if (
                member.mention + ":   :hourglass_flowing_sand: pending"
                in talk_with_text
            ):
                c2 = talk_with_text.replace(
                    member.mention + ":   :hourglass_flowing_sand: pending",
                    member.mention
                    + ":   :green_circle: joined `"
                    + datetime.datetime.now().strftime("%H:%M:%S")
                    + "`",
                    1,
                )
            elif member.mention + ":   :red_circle: declined `" in talk_with_text:
                c2 = talk_with_text.replace(
                    member.mention + ":   :red_circle: declined",
                    member.mention + ":   :green_circle: joined",
                    1,
                )
                # now we need to update the timestamp
                split = c2.split(member.mention + ":   :green_circle: joined `", 1)
                d0 = split[0]
                d1 = member.mention + ":   :green_circle: joined `"
                d2 = datetime.datetime.now().strftime("%H:%M:%S") + "`"
                d3 = split[1].split("`", 1)[1]
                c2 = d0 + d1 + d2 + d3
            elif (
                member.mention + ":   :orange_circle: will join in 5 mins `"
                in talk_with_text
            ):
                c2 = talk_with_text.replace(
                    member.mention + ":   :orange_circle: will join in 5 mins",
                    member.mention + ":   :green_circle: joined",
                    1,
                )
                # now we need to update the timestamp
                split = c2.split(member.mention + ":   :green_circle: joined `", 1)
                d0 = split[0]
                d1 = member.mention + ":   :green_circle: joined `"
                d2 = datetime.datetime.now().strftime("%H:%M:%S") + "`"
                d3 = split[1].split("`", 1)[1]
                c2 = d0 + d1 + d2 + d3
            elif (
                member.mention + ":   :orange_circle: will join in 15 mins `"
                in talk_with_text
            ):
                c2 = talk_with_text.replace(
                    member.mention + ":   :orange_circle: will join in 15 mins",
                    member.mention + ":   :green_circle: joined",
                    1,
                )
                # now we need to update the timestamp
                split = c2.split(member.mention + ":   :green_circle: joined `", 1)
                d0 = split[0]
                d1 = member.mention + ":   :green_circle: joined `"
                d2 = datetime.datetime.now().strftime("%H:%M:%S") + "`"
                d3 = split[1].split("`", 1)[1]
                c2 = d0 + d1 + d2 + d3
            else:
                c2 = "farghi nakarde ke baba"

            if c2 != "farghi nakarde ke baba":
                await talk_with_msg.edit(content=c2)

        #####
        #####
        #####
        # Sending the event
        #####
        #####
        #####
        try:
            extra = {
                "is_on_mobile": member.is_on_mobile(),
                "raw_status": str(member.raw_status),
                "status": str(member.status),
                "web_status": str(member.web_status),
                "desktop_status": str(member.desktop_status),
                "mobile_status": str(member.mobile_status),
            }
        except:  # noqa: E722
            extra = {"NOTE": "ERROR on making note!"}

        await log_processor.record(member, before, after, extra)
        raw_logger.record(member, before, after)

        # updating boards
        # updating inmaah first, so pendings are renewed for dirooz report
        await update_inmaah_board(guild=guild)
        await update_dirooz_board(guild=guild)

    @bot.event
    async def on_raw_reaction_add(payload):
        print("this is on_raw_reaction_add. the server is:")
        print(payload.guild_id)

        global the_zombie
        # cancelling the zombie
        if payload.guild_id in the_zombie:
            if payload.member == the_zombie[payload.guild_id]:
                channel = bot.get_channel(payload.channel_id)
                (task,) = [
                    task
                    for task in asyncio.all_tasks()
                    if task.get_name() == f"dc zombie {payload.guild_id}"
                ]
                task.cancel()
                the_zombie[payload.guild_id] = None
                await channel.send(
                    "Well well you are not a zombie " + payload.member.mention + "!"
                )

    @bot.event
    async def on_presence_update(before, after):
        pass

    @bot.hybrid_command(description="Replies with pong!")
    async def ping(ctx):
        print("this is ping. the server is:")
        print(ctx.guild.id)
        await ctx.send("Your Discord ID is " + str(ctx.author.id), ephemeral=True)

    @bot.hybrid_command(
        description="If someone is in not deafen and doesn't answer, report them as a zombie!"
    )
    async def zombie(ctx, member: discord.Member):
        # func that does the job after a while
        task1 = None

        async def dc_user():
            await asyncio.sleep(180)  # 3 minutes
            global the_zombie
            the_zombie[ctx.guild.id] = None
            zombie_hunter.record_hunt(
                driver=str(ctx.guild.id),
                reporter=str(ctx.author.id),
                zombie=str(member.id),
            )
            await member.move_to(
                None, reason="You have been reported a zombie and didn't respond!"
            )
            try:
                await ctx.guild.system_channel.send(
                    member.mention
                    + "'s session terminated because they acted like a :zombie:!"
                )
            except:  # noqa: E722
                await ctx.guild.text_channels[0].send(
                    member.mention
                    + "'s session terminated because they acted like a :zombie:!"
                )

        # repoting the zombie!
        if ctx.author != member:

            try:
                members_channel = member.voice.channel
            except:  # noqa: E722
                members_channel = None

            if members_channel is not None and member.voice.self_deaf is False:

                global the_zombie
                the_zombie[ctx.guild.id] = member

                await ctx.send(
                    "You reported " + member.mention + " as a zombie!", ephemeral=True
                )
                try:
                    await ctx.guild.system_channel.send(
                        member.mention
                        + " you have been called a zombie. Show up in 3 minutes or you would be disconnected!"
                    )
                except:  # noqa: E722
                    await ctx.guild.text_channels[0].send(
                        member.mention
                        + " you have been called a zombie. Show up in 3 minutes or you would be disconnected!"
                    )
                task1 = asyncio.create_task(dc_user(), name=f"dc zombie {ctx.guild.id}")
                await task1

            else:
                await ctx.send(
                    "Well obviously " + member.mention + " is NOT a zombie!",
                    ephemeral=True,
                )

        # reporting yourself!
        else:
            await ctx.send(
                "You can not name yourself a zombie! Take a break!", ephemeral=True
            )

   
  
    @bot.hybrid_command()
    async def status(ctx, member: discord.Member):
        status = report.get_status(driver=str(ctx.guild.id), doer=str(member.id))
        await ctx.send(member.mention + "'s current status: \n" + status)

    @bot.hybrid_command()
    async def makeboard(
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

    @bot.hybrid_command()
    async def my_settings(ctx):
        person = Person()
        person_info = person.get_person_info_by_id(
            discord_guild=ctx.guild.id, discord_id=ctx.author.id
        )
        if person_info is None:
            print("person info not found!")
            await ctx.send("Someting went wrong! Try again!", ephemeral=True)
            if ctx.author.avatar is None:
                person.add_person(
                    discord_guild=ctx.guild.id,
                    discord_id=ctx.author.id,
                    discord_name=ctx.author.name,
                )
            else:
                person.add_person(
                    discord_guild=ctx.guild.id,
                    discord_id=ctx.author.id,
                    discord_name=ctx.author.name,
                    discord_avatar=str(ctx.author.avatar),
                )
        else:
            view = my_settings_view.SettingsView()
            view.email = ""
            view.wallet = ""
            email = "-"
            wallet = "-"
            if person_info["email"] is not None and person_info["email"] != "":
                email = person_info["email"]
                view.email = email
            if (
                person_info["trc20_addr"] is not None
                and person_info["trc20_addr"] != ""
            ):
                wallet = person_info["trc20_addr"]
                view.wallet = wallet
            text = (
                "Email:   `"
                + email
                + "`\n"
                + "TRC20 Wallet:   `"
                + wallet
                + "`\nTime Zone:   `"
                + person_info["timezone"]
                + "`\nCalendar System:   `"
                + person_info["calendar_system"]
                + "`\n"
            )
            await ctx.send(text, view=view, ephemeral=True)

    @bot.hybrid_command()
    async def connect_google_calendar(ctx):
        g_redirect_url = GCalSetup.gen_GOAuth_URL()
        link = (
            "https://time-api.cotopia.social/gcal?u="
            + g_redirect_url
            + "&a="
            + str(ctx.author.id)
            + "&b="
            + str(ctx.guild.id)
            + "&c="
            + str(ctx.author.name)
        )
        # link = "http://127.0.0.1:8000/gcal?u=" + g_redirect_url + "&a=" + str(ctx.author.id) + "&b=" + str(ctx.guild.id) + "&c=" + str(ctx.author.name)
        person = Person()
        token = person.get_google_token(ctx.guild.id, ctx.author.id)
        if token is None:
            await ctx.send(
                "   ‌ ‌  \n⬇️   Please follow the link below to give access to your Google Calendar   ⬇️\n\n"
                + link,
                ephemeral=True,
            )
        else:
            await ctx.send("You already did this before!", ephemeral=True)

    @bot.hybrid_command()
    async def gcal_status(ctx):
        all_members = ctx.guild.members
        person = Person()
        gave_gcal_access = person.list_of_tokeners(ctx.guild.id)
        result = ""
        for each in all_members:
            if each.bot is False:
                if each.id in gave_gcal_access:
                    # result[each.name] = True
                    result = result + "✅ " + each.name + "\n"
                else:
                    # result[each.name] = False
                    result = result + "❌ " + each.name + "\n"

        await ctx.send(result)

    @bot.hybrid_command()
    async def dashboard(ctx):
        d = {}
        d["discord_guild"] = ctx.guild.id
        d["discord_id"] = ctx.author.id
        d["discord_name"] = ctx.author.name
        roles = ctx.author.roles
        roles_list = []
        for r in roles:
            roles_list.append(r.name)
        d["discord_roles"] = roles_list

        token = auth.create_token(d)

        # link = "http://127.0.0.1:8000/login?t=" + token
        link = "https://time-bot.cotopia.social/login?t=" + token

        now = datetime.datetime.now()
        expires_at = now + datetime.timedelta(0, 3600)
        expires_at_string = expires_at.strftime("%H:%M:%S")

        await ctx.send(
            f"[Use this link to open your time-bot dashboard.\n(valid until {expires_at_string})]({link})",
            ephemeral=True,
        )

    @bot.hybrid_command()
    async def update_info(ctx):
        guild = ctx.guild
        # Updating server table
        server = Server()
        banner = None
        icon = None
        if guild.banner is not None:
            banner = str(guild.banner)
        if guild.icon is not None:
            icon = str(guild.icon)
        server.setter(
            guild_id=guild.id,
            unavailable=guild.unavailable,
            banner=banner,
            icon=icon,
            created_at=guild.created_at,
            name=guild.name,
            description=guild.description,
            member_count=guild.member_count,
            owner_name=guild.owner.name,
            preferred_locale=str(guild.preferred_locale),
        )
        # Updating person table
        count = 0
        person = Person()
        for i in guild.members:
            if i.bot is False:
                if i.avatar is None:
                    person.add_person(guild.id, i.id, i.name)
                else:
                    person.add_person(guild.id, i.id, i.name, str(i.avatar))

                count = count + 1

        await ctx.send(f"Updated {count} profiles!")

    @bot.hybrid_command()
    async def talk_with(
        ctx,
        member: discord.Member,
        description: str | None = None,
        member3: discord.Member | None = None,
        member4: discord.Member | None = None,
    ):

        category = discord.utils.get(ctx.guild.categories, name="MEETINGS")
        if category is None:
            category = await ctx.guild.create_category("MEETINGS")

        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(connect=False),
            ctx.author: discord.PermissionOverwrite(connect=True),
            member: discord.PermissionOverwrite(connect=True),
        }

        text = (
            "Hey "
            + member.mention
            + ",\n"
            + ctx.author.mention
            + " wants to talk with you."
        )
        members = []
        members.append(ctx.author)
        members.append(member)

        # send bot to their channels and play ring voice

        if member3 is not None:
            split = text.split(",\n", 1)
            text = split[0] + ", " + member3.mention + ",\n" + split[1]
            members.append(member3)
            overwrites[member3] = discord.PermissionOverwrite(
                connect=True, view_channel=True
            )

        if member4 is not None:
            split = text.split(",\n", 1)
            text = split[0] + ", " + member4.mention + ",\n" + split[1]
            members.append(member4)
            overwrites[member4] = discord.PermissionOverwrite(
                connect=True, view_channel=True
            )

        channel = await ctx.guild.create_voice_channel(
            name=ctx.author.name + "'s meeting",
            category=category,
            overwrites=overwrites,
        )
        try:
            await ctx.author.move_to(channel)
            author_moved = True
        except:  # noqa: E722
            print("user is not connected to voice.")
            author_moved = False

        view = TalkWithView()
        view.author_id = ctx.author.id
        view.voice_channel = channel

        global temp_channels
        temp_channels.append(channel)
        print("temp_channels:   ")
        print(temp_channels)

        view.members = members

        members_str = []
        the_table = "\n\n--------------------"
        for m in members:
            members_str.append(str(m))
            the_table = (
                the_table + "\n" + m.mention + ":   :hourglass_flowing_sand: pending"
            )
        view.members_str = members_str

        if description is not None:
            text = text + "\n\nDescription:\n" + description

        the_message = await ctx.send(text + "\n\n" + channel.jump_url, view=view)

        # play ring alarm when user sent the command

        await play_ring_voice(discord, bot, ctx, member)
        if member3 is not None and member3.voice.channel != member.voice.channel:
            # send bot to their channels and play ring voice
            await play_ring_voice(discord, bot, ctx, member3)

        if member4 is not None and member4.voice.channel != member.voice.channel:
            # send bot to their channels and play ring voice
            await play_ring_voice(discord, bot, ctx, member4)

        global temp_messages
        temp_messages[channel] = the_message
        print("temp_messages:   ")
        print(temp_messages)

        event_note = {}
        event_note["members"] = members_str
        event_note["channel"] = {"name": channel.name, "id": channel.id}
        note = json.dumps(event_note)
        log_processor.write_event_to_db(
            driver=ctx.guild.id,
            epoch=rightnow(),
            kind="ASK FOR TALK",
            doer=str(ctx.author.id),
            isPair=False,
            note=note,
        )

        # Now lets edit the message with what habibi wants
        await the_message.edit(
            content=the_message.content + the_table + "\n--------------------"
        )

        if author_moved:
            talk_with_msg = await ctx.channel.fetch_message(the_message.id)
            c1 = talk_with_msg.content
            c2 = c1.replace(
                ctx.author.mention + ":   :hourglass_flowing_sand: pending",
                ctx.author.mention
                + ":   :green_circle: joined `"
                + datetime.datetime.now().strftime("%H:%M:%S")
                + "`",
                1,
            )
            await talk_with_msg.edit(content=c2)

        # Handling No Response
        async def write_no_response(msg_id: int):
            await asyncio.sleep(180)  # 3 minutes
            talk_with_msg = await ctx.channel.fetch_message(msg_id)
            c1 = talk_with_msg.content
            c2 = c1.replace(
                ":   :hourglass_flowing_sand: pending", ":   :interrobang: no response"
            )
            await talk_with_msg.edit(content=c2)

        task_edit_msg = asyncio.create_task(
            write_no_response(the_message.id),
            name=f"editing talk_with msg with no response {the_message.id} at {ctx.guild.id}",
        )
        await task_edit_msg

    @bot.hybrid_command()
    async def server_log(ctx):
        if ctx.author.id == 592386692569366559:
            global the_zombie
            # global last_brief_ask
            global last_profile_update
            global temp_channels
            global temp_messages
            await ctx.send("the_zombie: \n" + str(the_zombie), ephemeral=True)
            # await ctx.send("last_brief_ask: \n" + str(last_brief_ask), ephemeral=True)
            await ctx.send(
                "last_profile_update: \n" + str(last_profile_update), ephemeral=True
            )
            await ctx.send("temp_channels: \n" + str(temp_channels), ephemeral=True)
            await ctx.send("temp_messages: \n" + str(temp_messages), ephemeral=True)
        else:
            await ctx.send("Sorry you connot see this!", ephemeral=True)

    @bot.hybrid_command()
    async def create_dirooz_board(ctx):
        await gen_dirooz_board(guild=ctx.guild)
        await ctx.send("Done!", ephemeral=True)

    @bot.hybrid_command()
    async def create_inmaah_board(ctx):
        await gen_inmaah_board(guild=ctx.guild)
        await ctx.send("Done!", ephemeral=True)

    bot.run(settings.DISCORD_API_SECRET, root_logger=True)


if __name__ == "__main__":
    run()
