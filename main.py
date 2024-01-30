import json
import sqlite3
from typing import Optional

import settings
import discord
from discord.ext import commands

from persiantools.jdatetime import JalaliDate
from persiantools.jdatetime import JalaliDateTime
import pytz
import time

import asyncio
import datetime
import typing

import log_processor
import raw_logger
import report
import zombie_hunter
# import briefing.briefing as briefing
# from briefing.brief_modal import BriefModal
from person import MySettingsModal, Person
from gcal import calcal as GCalSetup
import auth
from server import Server
from talk_with import TalkWithView
from board.the_text import gen_dirooz_board, update_dirooz_board, gen_inmaah_board, update_inmaah_board

logger = settings.logging.getLogger("bot")

the_zombie = {}
# last_brief_ask = {}
last_profile_update = {}
temp_channels = []
temp_messages = {}


def today_g():
    the_string = datetime.datetime.today().strftime('%Y-%m-%d')
    slices = the_string.split("-")
    dic = {"y": int(slices[0]), "m": int(slices[1]), "d": int(slices[2])}
    return dic
    
def today_jalali():
    the_string = str(JalaliDate.today())
    slices = the_string.split("-")
    dic = {"y": int(slices[0]), "m": int(slices[1]), "d": int(slices[2])}
    return dic

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
    
    @bot.event
    async def on_guild_join(guild):
        # Updating server table
        server = Server()
        banner = None
        icon = None
        if (guild.banner != None):
            banner = str(guild.banner)
        if (guild.icon != None):
            icon = str(guild.icon)
        server.setter(guild_id = guild.id, unavailable = guild.unavailable, banner = banner,
                      icon = icon, created_at = guild.created_at, name = guild.name,
                      description = guild.description, member_count = guild.member_count, owner_name = guild.owner.name,
                      preferred_locale = str(guild.preferred_locale))
        
        # Updating person table
        count = 0
        person = Person()
        for i in guild.members:
            if (i.bot == False):
                if (i.avatar == None):
                    person.add_person(guild.id, i.id, i.name)
                else:
                    person.add_person(guild.id, i.id, i.name, str(i.avatar))
                
                count = count + 1
        
        print(f"Updated {count} profiles!")
    
    @bot.event
    async def on_member_join(member):
        # Updating person table
        guild = member.guild
        count = 0
        person = Person()
        for i in guild.members:
            if (i.bot == False):
                if (i.avatar == None):
                    person.add_person(guild.id, i.id, i.name)
                else:
                    person.add_person(guild.id, i.id, i.name, str(i.avatar))
                
                count = count + 1
        
        print(f"Updated {count} profiles!")
    


    @bot.event
    async def on_message(message):
        # print("this is on_message. the server is:")
        # print(message.guild.id)

        if message.author == bot.user:
            return
        
        # cancelling the zombie
        global the_zombie
        if (message.guild.id in the_zombie):
            if (message.author == the_zombie[message.guild.id]):
                task, = [task for task in asyncio.all_tasks() if task.get_name() == f"dc zombie {message.guild.id}"]
                task.cancel()
                await message.channel.send("Well well you are not a zombie " + message.author.mention + "!")
                the_zombie[message.guild.id] = None
        
        # RECORDING BRIEF
        # try:
        #     replied_to = await message.channel.fetch_message(message.reference.message_id)
        #     if (replied_to.author == bot.user):
        #         if ("Reply to this message to submit a brief." in replied_to.content):
        #             if (message.author in replied_to.mentions):
        #                 briefing.write_to_db(brief=message.content, doer=str(message.author), driver=str(message.guild.id))
        #                 em = discord.Embed(title=f"#brief",
        #                                             description=message.content, color=discord.Color.blue())
        #                 em.set_author(name=str(JalaliDate.today()))
        #                 channel = message.guild.system_channel
        #                 if (channel == None):
        #                     channel = message.guild.text_channels[0]
        #                 webhook = await channel.create_webhook(name=message.author.name)
        #                 if (message.author.nick == None):
        #                     the_name = message.author.name
        #                 else:
        #                     the_name = message.author.nick
        #                 await webhook.send(
        #                     embed=em, username=the_name, avatar_url=message.author.avatar)
        #                 webhooks = await channel.webhooks()
        #                 for w in webhooks:
        #                     await w.delete()
        #                 await replied_to.delete()
        #                 await message.delete()
        #                 try:
        #                     task, = [task for task in asyncio.all_tasks() if task.get_name() ==
        #                              f"ask for brief {str(message.author)}@{message.guild.id}"]
        #                     task.cancel()
        #                 except:
        #                     print("Asking for brief was not canceled! Don't panic tho.")

        # except:
        #     print("the message is not relevant!")

        
    @bot.event
    async def on_voice_state_update(member, before, after):

        # Ignoring Bots
        if (member.bot):
            return
        
        # deleting temp channels
        # func that does the job after a while
        task_del_chan = None
        async def del_temp_chan(channel):
            print("del_temp_chan been called!")
            print("the channel is:  " + str(channel))
            await asyncio.sleep(180)    # 3 minutes
            global temp_channels
            if (len(channel.members) == 0):
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
                    msg = await temp_messages[channel].channel.fetch_message(temp_messages[channel].id)
                    print("trying to delete text:   ")
                    print(msg)
                    await msg.delete()
                    del temp_messages[channel]
                    print("message was removed")
                except Exception as e:
                    print("Sorry couldn't delete the /talk_with message!")
                    print(e)
                
        # calling the  del_temp_chan(channel) func
        global temp_channels
        if (before.channel in temp_channels):
            if (len(before.channel.members) == 0):
                task_del_chan = asyncio.create_task(del_temp_chan(before.channel),
                                                    name=f"deleting temp channel {before.channel.id}")
                await task_del_chan
                

        guild = member.guild
        print("this is on_voice_state_update. the server is:")
        print(guild.id)


        # cancelling the zombie
        global the_zombie
        if (guild.id in the_zombie):
            if (member == the_zombie[guild.id]):
                task, = [task for task in asyncio.all_tasks() if task.get_name() == f"dc zombie {guild.id}"]
                task.cancel()
                try:
                    await guild.system_channel.send("Well well you are not a zombie " + member.mention + "!")
                except:
                    await guild.text_channels[0].send("Well well you are not a zombie " + member.mention + "!")
                the_zombie[guild.id] = None

        # when user joins voice
        if (before.channel is None):
            await update_dirooz_board(guild=guild)
            await update_inmaah_board(guild=guild)
        
        # When user leaves voice channel
        if (after.channel is None):
            # Update user profile
            try:
                global last_profile_update
                if (f"{member.id}@{member.guild.id}" in last_profile_update):
                    pass
                else:
                    last_profile_update[f"{member.id}@{member.guild.id}"] = datetime.datetime.today().strftime('%Y-%m-%d')

                if (last_profile_update[f"{member.id}@{member.guild.id}"] != datetime.datetime.today().strftime('%Y-%m-%d')):
                    keyword = member.guild.name
                    person = Person()
                    person.set_avatar(member.guild.id, member.id, str(member.avatar), member.name)
                    cal = GCalSetup.get_processed_events(member.guild.id, member.id, keyword)
                    person.set_cal(member.guild.id, member.id, json.dumps(cal))
                    last_profile_update[f"{member.id}@{member.guild.id}"] = datetime.datetime.today().strftime('%Y-%m-%d')
            except:
                print("could not get cal!")
            # cancelling asking for brief
            # try:
            #     task, = [task for task in asyncio.all_tasks() if task.get_name() == f"ask for brief {str(member)}@{guild.id}"]
            #     task.cancel()
            # except:
            #     print("Asking for brief was not canceled! Don't panic tho.")
        
        # When user joins a /talk_with channel
        global temp_messages
        if (after.channel in temp_messages):
            talk_with_msg = await temp_messages[after.channel].channel.fetch_message(temp_messages[after.channel].id)
            talk_with_text = talk_with_msg.content
            if (member.mention + ":   :hourglass_flowing_sand: pending" in talk_with_text):
                c2 = talk_with_text.replace(
                    member.mention + ":   :hourglass_flowing_sand: pending",
                    member.mention + ":   :green_circle: joined `" + datetime.datetime.now().strftime('%H:%M:%S') + "`",
                    1)
            elif (member.mention + ":   :red_circle: declined `" in talk_with_text):
                c2 = talk_with_text.replace(
                    member.mention + ":   :red_circle: declined",
                    member.mention + ":   :green_circle: joined",
                    1)
                # now we need to update the timestamp
                split = c2.split(member.mention + ":   :green_circle: joined `", 1)
                d0 = split[0]
                d1 = member.mention + ":   :green_circle: joined `"
                d2 = datetime.datetime.now().strftime('%H:%M:%S') + "`"
                d3 = split[1].split("`", 1)[1]
                c2 = d0 + d1 + d2 + d3
            elif (member.mention + ":   :orange_circle: will join in 5 mins `" in talk_with_text):
                c2 = talk_with_text.replace(
                    member.mention + ":   :orange_circle: will join in 5 mins",
                    member.mention + ":   :green_circle: joined",
                    1)
                # now we need to update the timestamp
                split = c2.split(member.mention + ":   :green_circle: joined `", 1)
                d0 = split[0]
                d1 = member.mention + ":   :green_circle: joined `"
                d2 = datetime.datetime.now().strftime('%H:%M:%S') + "`"
                d3 = split[1].split("`", 1)[1]
                c2 = d0 + d1 + d2 + d3
            elif (member.mention + ":   :orange_circle: will join in 15 mins `" in talk_with_text):
                c2 = talk_with_text.replace(
                    member.mention + ":   :orange_circle: will join in 15 mins",
                    member.mention + ":   :green_circle: joined",
                    1)
                # now we need to update the timestamp
                split = c2.split(member.mention + ":   :green_circle: joined `", 1)
                d0 = split[0]
                d1 = member.mention + ":   :green_circle: joined `"
                d2 = datetime.datetime.now().strftime('%H:%M:%S') + "`"
                d3 = split[1].split("`", 1)[1]
                c2 = d0 + d1 + d2 + d3
            else:
                c2 = "farghi nakarde ke baba"
            
            if (c2 != "farghi nakarde ke baba"):
                await talk_with_msg.edit(content = c2)

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
                "mobile_status": str(member.mobile_status)
            }
        except:
            extra = {"NOTE": "ERROR on making note!"}
        
        await log_processor.record(member, before, after, extra)
        raw_logger.record(member, before, after)


                    
        
    @bot.event
    async def on_raw_reaction_add(payload):
        print("this is on_raw_reaction_add. the server is:")
        print(payload.guild_id)
        
        
        global the_zombie
        # cancelling the zombie
        if (payload.guild_id in the_zombie):
            if (payload.member == the_zombie[payload.guild_id]):
                channel = bot.get_channel(payload.channel_id)
                task, = [task for task in asyncio.all_tasks() if task.get_name() == f"dc zombie {payload.guild_id}"]
                task.cancel()
                the_zombie[payload.guild_id] = None
                await channel.send("Well well you are not a zombie " + payload.member.mention + "!")
  

    @bot.event
    async def on_presence_update(before, after):
        pass


    @bot.hybrid_command(description="Replies with pong!")
    async def ping(ctx):
        print("this is ping. the server is:")
        print(ctx.guild.id)
        await ctx.send("Your Discord ID is " + str(ctx.author.id), ephemeral=True)

    @bot.hybrid_command(description="Generates report. default date: current month")
    async def viewstats(ctx, member: discord.Member,
                        start_yyyy: typing.Optional[int]=1971, start_mm: typing.Optional[int]=1, start_dd: typing.Optional[int]=1,
                        end_yyyy: typing.Optional[int]=2037, end_mm: typing.Optional[int]=1, end_dd: typing.Optional[int]=29):

        now = today_g()

        # I want to set today as default end value, but passing it in Args didnt work. So I do this:
        if (end_yyyy == 2037 and end_mm == 12 and end_dd == 29):
            end_epoch = datetime.datetime(
                year=now["y"], month=now["m"], day=now["d"], hour=23, minute=59, second=59).strftime('%s')
        else:
            try:
                end_epoch = datetime.datetime(
                    year=end_yyyy, month=end_mm, day=end_dd, hour=23, minute=59, second=59).strftime('%s')
            except:
                await ctx.send("Please enter a valid date!", ephemeral=True)
                return
        

        if (start_yyyy == 1971 and start_mm == 1 and start_dd == 1):
            start_epoch = datetime.datetime(
                year=now["y"], month=now["m"], day=1, hour=0, minute=0, second=0).strftime('%s')
        else:
            try:
                start_epoch = datetime.datetime(
                    year=start_yyyy, month=start_mm, day=start_dd, hour=0, minute=0, second=0).strftime('%s')
            except:
                await ctx.send("Please enter a valid date!", ephemeral=True)
                return
        

        if (int(start_epoch) >= int(end_epoch)):
            await ctx.send("**Start Date** should be before **End Date**! Try Again!", ephemeral=True)
            return
        # max int value in postgres is 	-2147483648 to 2147483647
        elif (int(end_epoch) > 2147400000):
            await ctx.send("**End Date** is too far in the future! Try Again!", ephemeral=True)
            return
        elif (int(start_epoch) < 0):
            await ctx.send("I wasn't even born back then! Try Again!", ephemeral=True)
            return
        
        print("start epoch: " + str(start_epoch))
        print("end epoch: " + str(end_epoch))
        
        
        thereport = report.make_report(driver=str(ctx.guild.id), doer=str(member), start_epoch=start_epoch, end_epoch=end_epoch)
        discordDate_from = "<t:" + thereport["From"] + ":D>"
        discordDate_to = "<t:" + thereport["To"] + ":D>"
        text = ("Report for " + member.mention + "\n" + 
                "From: " + discordDate_from + "\n" +
                "To: " + discordDate_to + "\n" +
                "------------------------------\n")

        for line in thereport:
            if (line == "User"):
                pass
            elif (line == "From"):
                pass
            elif (line == "To"):
                pass
            else:
                text = text + str(line)+": "+str(thereport[line]) + "\n"
            

        await ctx.send(text, ephemeral=True)

    
    @bot.hybrid_command(description="گزارش ایجاد می کند. تاریخ پیش فرض: ماه جاری")
    async def viewgozaresh(ctx, member: discord.Member,
                        start_ssss: typing.Optional[int]=1349, start_mm: typing.Optional[int]=1, start_rr: typing.Optional[int]=1,
                        end_ssss: typing.Optional[int]=1415, end_mm: typing.Optional[int]=12, end_rr: typing.Optional[int]=29):

        
        now = today_jalali()        

        # I want to set today as default end value, but passing it in Args didnt work. So I do this:
        if (end_ssss == 1415 and end_mm == 12 and end_rr == 29):
            end_epoch = JalaliDateTime(
                year=now["y"], month=now["m"], day=now["d"], hour=23, minute=59, second=59,
                tzinfo=pytz.timezone("Asia/Tehran")).to_gregorian().strftime('%s')
        else:
            try:
                end_epoch = JalaliDateTime(
                    year=end_ssss, month=end_mm, day=end_rr, hour=23, minute=59, second=59,
                    tzinfo=pytz.timezone("Asia/Tehran")).to_gregorian().strftime('%s')
            except:
                await ctx.send("Please enter a valid date!", ephemeral=True)
                return

         
        if (start_ssss == 1349 and start_mm == 1 and start_rr == 1):
            start_epoch = JalaliDateTime(
                year=now["y"], month=now["m"], day=1, hour=0, minute=0, second=0,
                tzinfo=pytz.timezone("Asia/Tehran")).to_gregorian().strftime('%s')
        else:
            try:
                start_epoch = JalaliDateTime(
                    year=start_ssss, month=start_mm, day=start_rr, hour=0, minute=0, second=0,
                    tzinfo=pytz.timezone("Asia/Tehran")).to_gregorian().strftime('%s')
            except:
                await ctx.send("Please enter a valid date!", ephemeral=True)
                return


        
        if (int(start_epoch) >= int(end_epoch)):
            await ctx.send("**Start Date** should be before **End Date**! Try Again!", ephemeral=True)
            return
        # max int value in postgres is 	-2147483648 to 2147483647
        elif (int(end_epoch) > 2147400000):
            await ctx.send("**End Date** is too far in the future! Try Again!", ephemeral=True)
            return
        elif (int(start_epoch) < 0):
            await ctx.send("I wasn't even born back then! Try Again!", ephemeral=True)
            return

        
        print("start epoch: " + str(start_epoch))
        print("end epoch: " + str(end_epoch))
        
        
        thereport = report.make_report(driver=str(ctx.guild.id), doer=str(member), start_epoch=start_epoch, end_epoch=end_epoch)
        discordDate_from = JalaliDateTime.fromtimestamp(int(thereport["From"]), pytz.timezone("Asia/Tehran")).strftime("%c")
        discordDate_to = JalaliDateTime.fromtimestamp(int(thereport["To"]), pytz.timezone("Asia/Tehran")).strftime("%c")
        text = ("Report for " + member.mention + "\n" + 
                "From: " + discordDate_from + "\n" +
                "To: " + discordDate_to + "\n" +
                "------------------------------\n")

        for line in thereport:
            if (line == "User"):
                pass
            elif (line == "From"):
                pass
            elif (line == "To"):
                pass
            else:
                text = text + str(line)+": "+str(thereport[line]) + "\n"
            

        await ctx.send(text, ephemeral=True)


    @bot.hybrid_command(description="If someone is in not deafen and doesn't answer, report them as a zombie!")
    async def zombie(ctx, member: discord.Member):
        
        # func that does the job after a while
        task1 = None
        async def dc_user():
            await asyncio.sleep(180)    # 3 minutes
            global the_zombie
            the_zombie[ctx.guild.id] = None
            zombie_hunter.record_hunt(driver=str(ctx.guild.id), reporter=str(ctx.author), zombie=str(member))
            await member.move_to(None, reason="You have been reported a zombie and didn't respond!")
            try:
                await ctx.guild.system_channel.send(member.mention+"'s session terminated because they acted like a :zombie:!")
            except:
                await ctx.guild.text_channels[0].send(member.mention+"'s session terminated because they acted like a :zombie:!")
            


        # repoting the zombie!
        if (ctx.author != member):

            try:
                members_channel = member.voice.channel
            except:
                members_channel = None

            if (members_channel != None and member.voice.self_deaf == False):

                global the_zombie
                the_zombie[ctx.guild.id] = member

                await ctx.send("You reported " + member.mention + " as a zombie!", ephemeral=True)
                try:
                    await ctx.guild.system_channel.send(member.mention+" you have been called a zombie. Show up in 3 minutes or you would be disconnected!")
                except:
                    await ctx.guild.text_channels[0].send(member.mention+" you have been called a zombie. Show up in 3 minutes or you would be disconnected!")
                task1 = asyncio.create_task(dc_user(), name=f"dc zombie {ctx.guild.id}")
                await task1

            
            else:
                await ctx.send("Well obviously " + member.mention + " is NOT a zombie!", ephemeral=True)


        # reporting yourself!
        else:
            await ctx.send("You can not name yourself a zombie! Take a break!", ephemeral=True)
            

    @bot.hybrid_command(description="داده خام یک کاربر در یک بازه زمانی. تاریخ پیش فرض: ماه جاری")
    async def rawdata(ctx, member: discord.Member,
                        start_ssss: typing.Optional[int]=1349, start_mm: typing.Optional[int]=1, start_rr: typing.Optional[int]=1,
                        end_ssss: typing.Optional[int]=1415, end_mm: typing.Optional[int]=12, end_rr: typing.Optional[int]=29):
        

        now = today_jalali()        

        # I want to set today as default end value, but passing it in Args didnt work. So I do this:
        if (end_ssss == 1415 and end_mm == 12 and end_rr == 29):
            end_epoch = JalaliDateTime(
                year=now["y"], month=now["m"], day=now["d"], hour=23, minute=59, second=59,
                tzinfo=pytz.timezone("Asia/Tehran")).to_gregorian().strftime('%s')
        else:
            try:
                end_epoch = JalaliDateTime(
                    year=end_ssss, month=end_mm, day=end_rr, hour=23, minute=59, second=59,
                    tzinfo=pytz.timezone("Asia/Tehran")).to_gregorian().strftime('%s')
            except:
                await ctx.send("Please enter a valid date!", ephemeral=True)
                return

         
        if (start_ssss == 1349 and start_mm == 1 and start_rr == 1):
            start_epoch = JalaliDateTime(
                year=now["y"], month=now["m"], day=1, hour=0, minute=0, second=0,
                tzinfo=pytz.timezone("Asia/Tehran")).to_gregorian().strftime('%s')
        else:
            try:
                start_epoch = JalaliDateTime(
                    year=start_ssss, month=start_mm, day=start_rr, hour=0, minute=0, second=0,
                    tzinfo=pytz.timezone("Asia/Tehran")).to_gregorian().strftime('%s')
            except:
                await ctx.send("Please enter a valid date!", ephemeral=True)
                return


        
        if (int(start_epoch) >= int(end_epoch)):
            await ctx.send("**Start Date** should be before **End Date**! Try Again!", ephemeral=True)
            return
        # max int value in postgres is 	-2147483648 to 2147483647
        elif (int(end_epoch) > 2147400000):
            await ctx.send("**End Date** is too far in the future! Try Again!", ephemeral=True)
            return
        elif (int(start_epoch) < 0):
            await ctx.send("I wasn't even born back then! Try Again!", ephemeral=True)
            return

        
        print("start epoch: " + str(start_epoch))
        print("end epoch: " + str(end_epoch))

        thereport = report.make_raw_file(driver=str(ctx.guild.id), doer=str(member), start_epoch=int(start_epoch), end_epoch=int(end_epoch))


        await ctx.send(file=discord.File(thereport))


    @bot.hybrid_command(description="جدول مدت سشن های تمام شده در امروز")
    async def emrooz(ctx):

        log_processor.renew_pendings(driver=str(ctx.guild.id))

        now = today_jalali()
        start_epoch = int(
                JalaliDateTime(
                    year=now["y"], month=now["m"], day=now["d"], hour=0, minute=0, second=0,
                    tzinfo=pytz.timezone("Asia/Tehran")).to_gregorian().strftime('%s')
        )
        end_epoch = int(
                JalaliDateTime(
                    year=now["y"], month=now["m"], day=now["d"], hour=23, minute=59, second=59,
                    tzinfo=pytz.timezone("Asia/Tehran")).to_gregorian().strftime('%s')
        )
        
        the_board = report.make_board(driver=str(ctx.guild.id), start_epoch=start_epoch, end_epoch=end_epoch)

        title_date = JalaliDate.fromtimestamp(start_epoch)
        # discordDate_to = JalaliDateTime.fromtimestamp(end_epoch, pytz.timezone("Asia/Tehran")).strftime("%c")

        text = ("Net Session Hours of " +
        str(title_date) +
        "\n------------------------------\n")
        for l in the_board:
            text = text + str(l[1]) + " | " + l[0] + "\n"

        await ctx.send(text)


    @bot.hybrid_command(description="جدول مدت سشن های دیروز")
    async def dirooz(ctx):
        now = today_jalali()
        start_epoch = int(
                JalaliDateTime(
                    year=now["y"], month=now["m"], day=now["d"]-1, hour=0, minute=0, second=0,
                    tzinfo=pytz.timezone("Asia/Tehran")).to_gregorian().strftime('%s')
        )
        end_epoch = int(
                JalaliDateTime(
                    year=now["y"], month=now["m"], day=now["d"]-1, hour=23, minute=59, second=59,
                    tzinfo=pytz.timezone("Asia/Tehran")).to_gregorian().strftime('%s')
        )
        
        the_board = report.make_board(driver=str(ctx.guild.id), start_epoch=start_epoch, end_epoch=end_epoch)

        title_date = JalaliDate.fromtimestamp(start_epoch)
        # discordDate_to = JalaliDateTime.fromtimestamp(end_epoch, pytz.timezone("Asia/Tehran")).strftime("%c")

        text = ("Net Session Hours of " +
        str(title_date) +
        "\n------------------------------\n")
        for l in the_board:
            text = text + str(l[1]) + " | " + l[0] + "\n"

        await ctx.send(text)
    

    @bot.hybrid_command(description="جدول مدت سشن های این ماه")
    async def inmaah(ctx):

        log_processor.renew_pendings(driver=str(ctx.guild.id))

        now = today_jalali()
        start_epoch = int(
                JalaliDateTime(
                    year=now["y"], month=now["m"], day=1, hour=0, minute=0, second=0,
                    tzinfo=pytz.timezone("Asia/Tehran")).to_gregorian().strftime('%s')
        )
        end_epoch = int(
                JalaliDateTime(
                    year=now["y"], month=now["m"], day=now["d"], hour=23, minute=59, second=59,
                    tzinfo=pytz.timezone("Asia/Tehran")).to_gregorian().strftime('%s')
        )
        
        the_board = report.make_board(driver=str(ctx.guild.id), start_epoch=start_epoch, end_epoch=end_epoch)

        title_date = JalaliDate.fromtimestamp(start_epoch).strftime("%Y/%m")
        # discordDate_to = JalaliDateTime.fromtimestamp(end_epoch, pytz.timezone("Asia/Tehran")).strftime("%c")

        text = ("Net Session Hours of " +
        str(title_date) +
        "\n------------------------------\n")
        for l in the_board:
            text = text + str(l[1]) + " | " + l[0] + "\n"

        await ctx.send(text)
    


    @bot.hybrid_command(description="Session durations of current day")
    async def today(ctx):

        log_processor.renew_pendings(driver=str(ctx.guild.id))

        now = today_g()
        start_epoch = int(
                datetime.datetime(
                    year=now["y"], month=now["m"], day=now["d"], hour=0, minute=0, second=0,
                    tzinfo=pytz.timezone("Asia/Tehran")).strftime('%s')
        )
        end_epoch = int(
                datetime.datetime(
                    year=now["y"], month=now["m"], day=now["d"], hour=23, minute=59, second=59,
                    tzinfo=pytz.timezone("Asia/Tehran")).strftime('%s')
        )
        
        the_board = report.make_board(driver=str(ctx.guild.id), start_epoch=start_epoch, end_epoch=end_epoch)

        title_date = datetime.date.fromtimestamp(start_epoch)
        
        # discordDate_to = JalaliDateTime.fromtimestamp(end_epoch, pytz.timezone("Asia/Tehran")).strftime("%c")

        text = ("Net Session Hours of " +
        str(title_date) +
        "\n------------------------------\n")
        for l in the_board:
            text = text + str(l[1]) + " | " + l[0] + "\n"

        await ctx.send(text)


    @bot.hybrid_command(description="Session durations of last day")
    async def yesterday(ctx):
        now = today_g()
        start_epoch = int(
                datetime.datetime(
                    year=now["y"], month=now["m"], day=now["d"]-1, hour=0, minute=0, second=0,
                    tzinfo=pytz.timezone("Asia/Tehran")).strftime('%s')
        )
        end_epoch = int(
                datetime.datetime(
                    year=now["y"], month=now["m"], day=now["d"]-1, hour=23, minute=59, second=59,
                    tzinfo=pytz.timezone("Asia/Tehran")).strftime('%s')
        )
        
        the_board = report.make_board(driver=str(ctx.guild.id), start_epoch=start_epoch, end_epoch=end_epoch)

        title_date = datetime.date.fromtimestamp(start_epoch)
        # discordDate_to = JalaliDateTime.fromtimestamp(end_epoch, pytz.timezone("Asia/Tehran")).strftime("%c")

        text = ("Net Session Hours of " +
        str(title_date) +
        "\n------------------------------\n")
        for l in the_board:
            text = text + str(l[1]) + " | " + l[0] + "\n"

        await ctx.send(text)
    

    @bot.hybrid_command(description="Session durations of current month")
    async def thismonth(ctx):

        log_processor.renew_pendings(driver=str(ctx.guild.id))

        now = today_g()
        start_epoch = int(
                datetime.datetime(
                    year=now["y"], month=now["m"], day=1, hour=0, minute=0, second=0,
                    tzinfo=pytz.timezone("Asia/Tehran")).strftime('%s')
        )
        end_epoch = int(
                datetime.datetime(
                    year=now["y"], month=now["m"], day=now["d"], hour=23, minute=59, second=59,
                    tzinfo=pytz.timezone("Asia/Tehran")).strftime('%s')
        )
        
        the_board = report.make_board(driver=str(ctx.guild.id), start_epoch=start_epoch, end_epoch=end_epoch)

        title_date = datetime.date.fromtimestamp(start_epoch).strftime("%Y/%m")
        # discordDate_to = JalaliDateTime.fromtimestamp(end_epoch, pytz.timezone("Asia/Tehran")).strftime("%c")

        text = ("Net Session Hours of " +
        str(title_date) +
        "\n------------------------------\n")
        for l in the_board:
            text = text + str(l[1]) + " | " + l[0] + "\n"

        await ctx.send(text)


    @bot.hybrid_command()
    async def status(ctx, member: discord.Member):
        status = report.get_status(driver=str(ctx.guild.id), doer=str(member))
        await ctx.send(member.mention + "'s current status: \n" + status)

    
    @bot.hybrid_command()
    async def makeboard(ctx,
                        start_ssss: typing.Optional[int]=1349, start_mm: typing.Optional[int]=1, start_rr: typing.Optional[int]=1,
                        end_ssss: typing.Optional[int]=1415, end_mm: typing.Optional[int]=12, end_rr: typing.Optional[int]=29):
        now = today_jalali()        

        # I want to set today as default end value, but passing it in Args didnt work. So I do this:
        if (end_ssss == 1415 and end_mm == 12 and end_rr == 29):
            end_epoch = JalaliDateTime(
                year=now["y"], month=now["m"], day=now["d"], hour=23, minute=59, second=59,
                tzinfo=pytz.timezone("Asia/Tehran")).to_gregorian().strftime('%s')
        else:
            try:
                end_epoch = JalaliDateTime(
                    year=end_ssss, month=end_mm, day=end_rr, hour=23, minute=59, second=59,
                    tzinfo=pytz.timezone("Asia/Tehran")).to_gregorian().strftime('%s')
            except:
                await ctx.send("Please enter a valid date!", ephemeral=True)
                return

         
        if (start_ssss == 1349 and start_mm == 1 and start_rr == 1):
            start_epoch = JalaliDateTime(
                year=now["y"], month=now["m"], day=1, hour=0, minute=0, second=0,
                tzinfo=pytz.timezone("Asia/Tehran")).to_gregorian().strftime('%s')
        else:
            try:
                start_epoch = JalaliDateTime(
                    year=start_ssss, month=start_mm, day=start_rr, hour=0, minute=0, second=0,
                    tzinfo=pytz.timezone("Asia/Tehran")).to_gregorian().strftime('%s')
            except:
                await ctx.send("Please enter a valid date!", ephemeral=True)
                return


        
        if (int(start_epoch) >= int(end_epoch)):
            await ctx.send("**Start Date** should be before **End Date**! Try Again!", ephemeral=True)
            return
        # max int value in postgres is 	-2147483648 to 2147483647
        elif (int(end_epoch) > 2147400000):
            await ctx.send("**End Date** is too far in the future! Try Again!", ephemeral=True)
            return
        elif (int(start_epoch) < 0):
            await ctx.send("I wasn't even born back then! Try Again!", ephemeral=True)
            return
        
        print("start epoch: " + str(start_epoch))
        print("end epoch: " + str(end_epoch))

        log_processor.renew_pendings(driver=str(ctx.guild.id))
        the_board = report.make_board(driver=str(ctx.guild.id), start_epoch=start_epoch, end_epoch=end_epoch)


        discordDate_from = JalaliDateTime.fromtimestamp(int(start_epoch), pytz.timezone("Asia/Tehran")).strftime("%c")
        discordDate_to = JalaliDateTime.fromtimestamp(int(end_epoch), pytz.timezone("Asia/Tehran")).strftime("%c")

        text = ("Net Session Hours\n" +
        "From:  " + str(discordDate_from) + "\n"
        "To:  " + str(discordDate_to) +
        "\n------------------------------\n")
        for l in the_board:
            string = str(l)
            string = string.replace("('", "")
            string = string.replace("',", " :")
            string = string.replace(")", "")
            text = text + string + "\n"

        await ctx.send(text)


    # @bot.tree.command()
    # async def brief(interaction: discord.Interaction):
    #     brief_modal = BriefModal()
    #     brief_modal.user = interaction.user
    #     brief_modal.driver = interaction.guild_id
    #     await interaction.response.send_modal(brief_modal)
    
    
    @bot.tree.command()
    async def my_settings(interaction: discord.Interaction):
        my_settings_modal = MySettingsModal()
        my_settings_modal.user = interaction.user
        my_settings_modal.driver = interaction.guild_id
        my_settings_modal.connect_to_db()
        my_settings_modal.load_defualts()
        await interaction.response.send_modal(my_settings_modal)
    

    @bot.hybrid_command()
    async def connect_google_calendar(ctx):
        g_redirect_url = GCalSetup.gen_GOAuth_URL()
        link = "https://time-api.cotopia.social/gcal?u=" + g_redirect_url + "&a=" + str(ctx.author.id) + "&b=" + str(ctx.guild.id) + "&c=" + str(ctx.author.name)
        # link = "http://127.0.0.1:8000/gcal?u=" + g_redirect_url + "&a=" + str(ctx.author.id) + "&b=" + str(ctx.guild.id) + "&c=" + str(ctx.author.name)
        person = Person()
        token = person.get_google_token(ctx.guild.id, ctx.author.id)
        if (token == None):
            await ctx.send("   ‌ ‌  \n⬇️   Please follow the link below to give access to your Google Calendar   ⬇️\n\n" + link,
                            ephemeral=True)
        else:
            await ctx.send("You already did this before!", ephemeral=True)
    

    @bot.hybrid_command()
    async def gcal_status(ctx):
        all_members = ctx.guild.members
        person = Person()
        gave_gcal_access = person.list_of_tokeners(ctx.guild.id)
        result = ""
        for each in all_members:
            if(each.bot == False):
                if (each.id in gave_gcal_access):
                    # result[each.name] = True
                    result = result + "✅ " + each.name + "\n" 
                else:
                    # result[each.name] = False
                    result = result + "❌ " + each.name + "\n" 
        
        await ctx.send(result)

    @bot.hybrid_command()
    async def dashboard(ctx):
        d = {}
        d['discord_guild'] = ctx.guild.id
        d['discord_id'] = ctx.author.id
        d['discord_name'] = ctx.author.name
        roles = ctx.author.roles
        roles_list = []
        for r in roles:
            roles_list.append(r.name)
        d['discord_roles'] = roles_list

        token = auth.create_token(d)

        # link = "http://127.0.0.1:8000/login?t=" + token
        link = "https://time-bot.cotopia.social/login?t=" + token

        now = datetime.datetime.now()
        expires_at = now + datetime.timedelta(0,3600)
        expires_at_string = expires_at.strftime("%H:%M:%S")

        await ctx.send(f"[Use this link to open your time-bot dashboard.\n(valid until {expires_at_string})]({link})",
                       ephemeral=True)



    @bot.hybrid_command()
    async def update_info(ctx):
        guild = ctx.guild
        # Updating server table
        server = Server()
        banner = None
        icon = None
        if (guild.banner != None):
            banner = str(guild.banner)
        if (guild.icon != None):
            icon = str(guild.icon)
        server.setter(guild_id = guild.id, unavailable = guild.unavailable, banner = banner,
                      icon = icon, created_at = guild.created_at, name = guild.name,
                      description = guild.description, member_count = guild.member_count, owner_name = guild.owner.name,
                      preferred_locale = str(guild.preferred_locale))
        # Updating person table
        count = 0
        person = Person()
        for i in guild.members:
            if (i.bot == False):
                if (i.avatar == None):
                    person.add_person(guild.id, i.id, i.name)
                else:
                    person.add_person(guild.id, i.id, i.name, str(i.avatar))
                
                count = count + 1
        
        await ctx.send(f"Updated {count} profiles!")


    @bot.hybrid_command()
    async def talk_with(ctx, member: discord.Member, description: str | None = None,
                        member3: discord.Member | None = None, member4: discord.Member |None = None):
        category = discord.utils.get(ctx.guild.categories, name="MEETINGS")
        if category is None:
            category = await ctx.guild.create_category('MEETINGS')

        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(connect=False),
            ctx.author: discord.PermissionOverwrite(connect=True),
            member: discord.PermissionOverwrite(connect=True)
        }
        
        text = "Hey " + member.mention + ",\n" + ctx.author.mention + " wants to talk with you."
        members = []
        members.append(ctx.author)
        members.append(member)

        if (member3 != None):
            split = text.split(",\n", 1)
            text = split[0] + ", " + member3.mention + ",\n" + split[1]
            members.append(member3)
            overwrites[member3] = discord.PermissionOverwrite(connect=True, view_channel=True)
        if (member4 != None):
            split = text.split(",\n", 1)
            text = split[0] + ", " + member4.mention + ",\n" + split[1]
            members.append(member4)
            overwrites[member4] = discord.PermissionOverwrite(connect=True, view_channel=True)
        
        channel = await ctx.guild.create_voice_channel(name=ctx.author.name + "'s meeting",
                                                       category=category, overwrites=overwrites)
        try:
            await ctx.author.move_to(channel)
            author_moved = True
        except:
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
            the_table = the_table + "\n" + m.mention + ":   :hourglass_flowing_sand: pending"
        view.members_str = members_str

        if (description != None):
            text = text + "\n\nDescription:\n" + description

        the_message = await ctx.send(text + "\n\n" + channel.jump_url, view=view)


        global temp_messages
        temp_messages[channel] = the_message
        print("temp_messages:   ")
        print(temp_messages)

        event_note = {}
        event_note["members"] = members_str
        event_note["channel"] = {
            "name": channel.name,
            "id": channel.id
        }
        note = json.dumps(event_note)
        log_processor.write_event_to_db(driver=ctx.guild.id,
                                        epoch=rightnow(),
                                        kind="ASK FOR TALK",
                                        doer=str(ctx.author),
                                        isPair=False,
                                        note=note)
        
        # Now lets edit the message with what habibi wants
        await the_message.edit(content = the_message.content + the_table + "\n--------------------")
        if (author_moved):
            talk_with_msg = await ctx.channel.fetch_message(the_message.id)
            c1 = talk_with_msg.content
            c2 = c1.replace(
                ctx.author.mention + ":   :hourglass_flowing_sand: pending",
                ctx.author.mention + ":   :green_circle: joined `" + datetime.datetime.now().strftime('%H:%M:%S') + "`",
                1)
            await talk_with_msg.edit(content = c2)
        
        # Handling No Response
        async def write_no_response(msg_id: int):
            await asyncio.sleep(180)    # 3 minutes
            talk_with_msg = await ctx.channel.fetch_message(msg_id)
            c1 = talk_with_msg.content
            c2 = c1.replace(
                ":   :hourglass_flowing_sand: pending",
                ":   :interrobang: no response")
            await talk_with_msg.edit(content = c2)

        task_edit_msg= asyncio.create_task(
            write_no_response(the_message.id),
            name=f"editing talk_with msg with no response {the_message.id} at {ctx.guild.id}")
        await task_edit_msg

            

    @bot.hybrid_command()
    async def server_log(ctx):
        if (ctx.author.id == 592386692569366559):
            global the_zombie
            # global last_brief_ask
            global last_profile_update
            global temp_channels
            global temp_messages
            await ctx.send("the_zombie: \n" + str(the_zombie), ephemeral=True)
            # await ctx.send("last_brief_ask: \n" + str(last_brief_ask), ephemeral=True)
            await ctx.send("last_profile_update: \n" + str(last_profile_update), ephemeral=True)
            await ctx.send("temp_channels: \n" + str(temp_channels), ephemeral=True)
            await ctx.send("temp_messages: \n" + str(temp_messages), ephemeral=True)
        else:
            await ctx.send("Sorry you connot see this!", ephemeral=True)
    
    @bot.hybrid_command()
    async def free_time(ctx, member: discord.Member):
        await ctx.send(member.mention + "'s  free time for this week :\nSat       : none\nSun      : none\nMon     : 9-17\nTues     : 9-10,12-17\nWed     : 12-17\nThurs  : 9-17\nFri        : 9-10, 12-17\n")

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
