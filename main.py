import asyncio
import datetime
import json
import time
from os import getenv

import discord
import requests
from discord.ext import commands
from dotenv import load_dotenv

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

logger = settings.logging.getLogger("bot")

the_zombie = {}
last_profile_update = {}


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
    async def insight(ctx):
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

        job_manager_jwt = "empty"
        jm_username = str(d["discord_id"]) + "@" + str(d["discord_guild"]) + ".discord"
        load_dotenv()
        jm_password = getenv("DBUPW") + "@!"
        timebotsecret = getenv("TIME_BOT_SECRET")

        payload = {
            "timebotsecret": timebotsecret,
            "username": jm_username,
            "password": jm_password,
        }
        jm_url = "https://jobs-api.cotopia.social/timebotlogin"
        r = requests.post(url=jm_url, params=payload)
        if r.status_code == 200:
            job_manager_jwt = r.json()

        # link = "http://127.0.0.1:8000/login?t=" + token
        link = (
            "https://insight.cotopia.social/login?t="
            + token
            + "&jmt="
            + job_manager_jwt
        )

        now = datetime.datetime.now()
        expires_at = now + datetime.timedelta(0, 3600)
        expires_at_string = expires_at.strftime("%H:%M:%S")

        await ctx.send(
            f"[Use this link to open Cotopia Insight.\n(valid until {expires_at_string})]({link})",
            ephemeral=True,
        )

    @bot.hybrid_command()
    async def salary(ctx):
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
        link = (
            "http://tooljet.cotopia.social/applications/3bc09968-15c0-4279-bb3d-04b70eb8c199/contract?access="
            + token
        )

        now = datetime.datetime.now()
        expires_at = now + datetime.timedelta(0, 3600)
        expires_at_string = expires_at.strftime("%H:%M:%S")

        await ctx.send(
            f"[Use this link to open Cotopia Salary App.\n(valid until {expires_at_string})]({link})",
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
    async def server_log(ctx):
        if ctx.author.id == 592386692569366559:
            global the_zombie
            # global last_brief_ask
            global last_profile_update

            await ctx.send("the_zombie: \n" + str(the_zombie), ephemeral=True)
            # await ctx.send("last_brief_ask: \n" + str(last_brief_ask), ephemeral=True)
            await ctx.send(
                "last_profile_update: \n" + str(last_profile_update), ephemeral=True
            )
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
