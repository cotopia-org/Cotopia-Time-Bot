from discord.interactions import Interaction
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
import briefing


logger = settings.logging.getLogger("bot")

class BriefModal(discord.ui.Modal, title="Submit your brief!"):
    brief = discord.ui.TextInput(
        style = discord.TextStyle.long,
        label = "Your Brief",
        required = True,
        placeholder = "What are you going to do in this session?"
    )

    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.guild.system_channel
        embed = discord.Embed(title=f"Brief of {str(JalaliDate.today())}",
                               description=self.brief.value, color=discord.Color.blue())
        embed.set_author(name=str(self.user))
        await channel.send(embed=embed)
        briefing.write_to_db(brief=self.brief.value, doer=str(self.user), driver=str(self.driver))
        try:
            task, = [task for task in asyncio.all_tasks() if task.get_name() == f"ask for brief {str(self.user)}@{self.driver}"]
            task.cancel() 
        except:
            print("No briefing tasks were canceled!")
        await interaction.response.send_message(f"Your brief was submited {self.user.mention}!", ephemeral=True)

the_zombie = {}
last_brief_ask = {}

def today():
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
        try:
            replied_to = await message.channel.fetch_message(message.reference.message_id)
            if (replied_to.author == bot.user):
                if ("Reply to this message to submit a brief." in replied_to.content):
                    if (message.author in replied_to.mentions):
                        briefing.write_to_db(brief=message.content, doer=str(message.author), driver=str(message.guild.id))
                        em = discord.Embed(title=f"Brief of {str(JalaliDate.today())}",
                                                    description=message.content, color=discord.Color.blue())
                        em.set_author(name=str(message.author))
                        channel = message.guild.system_channel
                        await channel.send(embed=em)
                        await replied_to.delete()
                        await message.delete()

        except:
            print("the message is not relevant!")

        

    @bot.event
    async def on_voice_state_update(member, before, after):

        guild = member.guild

        # func that does the job after a while
        task2 = None
        async def ask_for_brief():
            await asyncio.sleep(900)    # 15 minutes
            await guild.system_channel.send(
                "Welcome " + member.mention + "!\nWhat are you going to do today?\nReply to this message to submit a brief."
            )


        print("this is on_voice_state_update. the server is:")
        print(guild.id)

        # cancelling the zombie
        global the_zombie
        if (guild.id in the_zombie):
            if (member == the_zombie[guild.id]):
                task, = [task for task in asyncio.all_tasks() if task.get_name() == f"dc zombie {guild.id}"]
                task.cancel()         
                await guild.system_channel.send("Well well you are not a zombie " + member.mention + "!")
                the_zombie[guild.id] = None

        extra = {
            "is_on_mobile": member.is_on_mobile(),
            "raw_status": str(member.raw_status),
            "status": str(member.status),
            "web_status": str(member.web_status),
            "desktop_status": str(member.desktop_status),
            "mobile_status": str(member.mobile_status)
        }
        
        log_processor.record(member, before, after, extra)
        raw_logger.record(member, before, after)

        # ASKING FOR BRIEF
        global last_brief_ask

        def get_previous_ask(doer: str):
            try:
                return rightnow() - last_brief_ask[doer + "@" + str(guild.id)]
            except:
                return 1000000000
        
        def just_asked(doer: str):
            if (get_previous_ask(doer) < 900): # 15 minutes
                return True
            else:
                return False
        
        if (before.channel is None):
            if (briefing.should_record_brief(driver=str(guild.id), doer=str(member))):
                if (just_asked(str(member)) == False):
                    # Ask 15 minutes later
                    last_brief_ask[str(member) + "@" + str(guild.id)] = rightnow() + 900
                    task2 = asyncio.create_task(ask_for_brief(), name=f"ask for brief {str(member)}@{guild.id}")
                    await task2
                    # await guild.system_channel.send(
                    #     "Welcome " + member.mention + "!\nWhat are you going to do today?\nReply to this message to submit a brief.")
        



    @bot.event
    async def on_raw_reaction_add(payload):
        print("this is on_raw_reaction_add. the server is:")
        print(payload.guild_id)
        
        
        global the_zombie
        # cancelling the zombie
        if (payload.guild.id in the_zombie):
            if (payload.member == the_zombie[payload.guild.id]):
                channel = bot.get_channel(payload.channel_id)
                task, = [task for task in asyncio.all_tasks() if task.get_name() == f"dc zombie {payload.guild.id}"]
                task.cancel()
                the_zombie[payload.guild.id] = None
                await channel.send("Well well you are not a zombie " + payload.member.mention + "!")

       

    @bot.event
    async def on_presence_update(before, after):
        pass

    @bot.hybrid_command(description="Replies with pong!")
    async def ping(ctx):
        print("this is ping. the server is:")
        print(ctx.guild.id)
        await ctx.send("pong")

    @bot.hybrid_command(description="Generates report. default date: current month")
    async def viewstats(ctx, member: discord.Member,
                        start_yyyy: typing.Optional[int]=1971, start_mm: typing.Optional[int]=1, start_dd: typing.Optional[int]=1,
                        end_yyyy: typing.Optional[int]=2037, end_mm: typing.Optional[int]=1, end_dd: typing.Optional[int]=29):

        now = today()

        # I want to set today as default end value, but passing it in Args didnt work. So I do this:
        if (end_yyyy == 2037 and end_mm == 12 and end_dd == 29):
            end_epoch = datetime.datetime(
                year=now["y"], month=now["m"], day=now["d"], hour=23, minute=59, second=59).strftime('%s')
        else:
            try:
                end_epoch = datetime.datetime(
                    year=end_yyyy, month=end_mm, day=end_dd, hour=23, minute=59, second=59).strftime('%s')
            except:
                await ctx.send("Please enter a valid date!")
                return
        

        if (start_yyyy == 1971 and start_mm == 1 and start_dd == 1):
            start_epoch = datetime.datetime(
                year=now["y"], month=now["m"], day=1, hour=0, minute=0, second=0).strftime('%s')
        else:
            try:
                start_epoch = datetime.datetime(
                    year=start_yyyy, month=start_mm, day=start_dd, hour=0, minute=0, second=0).strftime('%s')
            except:
                await ctx.send("Please enter a valid date!")
                return
        

        if (int(start_epoch) >= int(end_epoch)):
            await ctx.send("**Start Date** should be before **End Date**! Try Again!")
            return
        # max int value in postgres is 	-2147483648 to 2147483647
        elif (int(end_epoch) > 2147400000):
            await ctx.send("**End Date** is too far in the future! Try Again!")
            return
        elif (int(start_epoch) < 0):
            await ctx.send("I wasn't even born back then! Try Again!")
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
            

        await ctx.send(text)

    
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
                await ctx.send("Please enter a valid date!")
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
                await ctx.send("Please enter a valid date!")
                return


        
        if (int(start_epoch) >= int(end_epoch)):
            await ctx.send("**Start Date** should be before **End Date**! Try Again!")
            return
        # max int value in postgres is 	-2147483648 to 2147483647
        elif (int(end_epoch) > 2147400000):
            await ctx.send("**End Date** is too far in the future! Try Again!")
            return
        elif (int(start_epoch) < 0):
            await ctx.send("I wasn't even born back then! Try Again!")
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
            

        await ctx.send(text)



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
            await ctx.guild.system_channel.send(member.mention+"'s session terminated because they acted like a :zombie:!")
            


        # repoting the zombie!
        if (ctx.author != member):

            try:
                members_channel = member.voice.channel
            except:
                members_channel = None

            if (members_channel != None and member.voice.self_deaf == False):

                global the_zombie
                the_zombie[ctx.guild.id] = member

                await ctx.send("You reported " + member.mention + " as a zombie!")
                await ctx.guild.system_channel.send(member.mention+" you have been called a zombie. Show up in 3 minutes or you would be disconnected!")
                task1 = asyncio.create_task(dc_user(), name=f"dc zombie {ctx.guild.id}")
                await task1

            
            else:
                await ctx.send("Well obviously " + member.mention + " is NOT a zombie!")


        # reporting yourself!
        else:
            await ctx.send("You can not name yourself a zombie! Take a break!")
            

    

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
                await ctx.send("Please enter a valid date!")
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
                await ctx.send("Please enter a valid date!")
                return


        
        if (int(start_epoch) >= int(end_epoch)):
            await ctx.send("**Start Date** should be before **End Date**! Try Again!")
            return
        # max int value in postgres is 	-2147483648 to 2147483647
        elif (int(end_epoch) > 2147400000):
            await ctx.send("**End Date** is too far in the future! Try Again!")
            return
        elif (int(start_epoch) < 0):
            await ctx.send("I wasn't even born back then! Try Again!")
            return

        
        print("start epoch: " + str(start_epoch))
        print("end epoch: " + str(end_epoch))

        thereport = report.make_raw_file(driver=str(ctx.guild.id), doer=str(member), start_epoch=int(start_epoch), end_epoch=int(end_epoch))


        await ctx.send(file=discord.File(thereport))


    @bot.hybrid_command(description="جدول مدت سشن های تمام شده در امروز")
    async def today(ctx):

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
            string = str(l)
            string = string.replace("('", "")
            string = string.replace("',", " :")
            string = string.replace(")", "")
            text = text + string + "\n"

        await ctx.send(text)



    @bot.hybrid_command(description="جدول مدت سشن های دیروز")
    async def yesterday(ctx):
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
            string = str(l)
            string = string.replace("('", "")
            string = string.replace("',", " :")
            string = string.replace(")", "")
            text = text + string + "\n"

        await ctx.send(text)
    
    @bot.hybrid_command(description="جدول مدت سشن های این ماه")
    async def thismonth(ctx):

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
            string = str(l)
            string = string.replace("('", "")
            string = string.replace("',", " :")
            string = string.replace(")", "")
            text = text + string + "\n"

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
                await ctx.send("Please enter a valid date!")
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
                await ctx.send("Please enter a valid date!")
                return


        
        if (int(start_epoch) >= int(end_epoch)):
            await ctx.send("**Start Date** should be before **End Date**! Try Again!")
            return
        # max int value in postgres is 	-2147483648 to 2147483647
        elif (int(end_epoch) > 2147400000):
            await ctx.send("**End Date** is too far in the future! Try Again!")
            return
        elif (int(start_epoch) < 0):
            await ctx.send("I wasn't even born back then! Try Again!")
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


    @bot.tree.command()
    async def brief(interaction: discord.Interaction):
        brief_modal = BriefModal()
        brief_modal.user = interaction.user
        brief_modal.driver = interaction.guild_id
        await interaction.response.send_modal(brief_modal)



    bot.run(settings.DISCORD_API_SECRET, root_logger=True)



if __name__ == "__main__":
    run()
