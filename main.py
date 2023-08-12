import settings
import discord
from discord.ext import commands

from persiantools.jdatetime import JalaliDate
from persiantools.jdatetime import JalaliDateTime
import pytz
import asyncio
import datetime
import typing

import log_processor
import raw_logger
import report
import zombie_hunter


logger = settings.logging.getLogger("bot")

the_zombie = None

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
        if message.author == bot.user:
            return
        
        # cancelling the zombie
        global the_zombie
        if (message.author == the_zombie):
            task, = [task for task in asyncio.all_tasks() if task.get_name() == "dc zombie"]
            task.cancel()
            await message.channel.send("Well well you are not a zombie " + message.author.mention + "!")
            the_zombie = None

        

    @bot.event
    async def on_voice_state_update(member, before, after):

        # cancelling the zombie
        global the_zombie
        if (member == the_zombie):
            task, = [task for task in asyncio.all_tasks() if task.get_name() == "dc zombie"]
            task.cancel()
            
            guild = member.guild
            
            await guild.system_channel.send("Well well you are not a zombie " + member.mention + "!")
            the_zombie = None

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



    @bot.event
    async def on_raw_reaction_add(payload):
        
        global the_zombie
        # cancelling the zombie
        if (payload.member == the_zombie):
            channel = bot.get_channel(payload.channel_id)
            task, = [task for task in asyncio.all_tasks() if task.get_name() == "dc zombie"]
            task.cancel()
            the_zombie = None
            await channel.send("Well well you are not a zombie " + payload.member.mention + "!")

       

    @bot.event
    async def on_presence_update(before, after):
        pass

    @bot.hybrid_command(description="Replies with pong!")
    async def ping(ctx):
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
        
        
        thereport = report.make_report(str(member), start_epoch, end_epoch)
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
        
        
        thereport = report.make_report(str(member), start_epoch, end_epoch)
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
            the_zombie = None
            zombie_hunter.record_hunt(reporter=str(ctx.author), zombie=str(member))
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
                the_zombie = member

                await ctx.send("You reported " + member.mention + " as a zombie!")
                await ctx.guild.system_channel.send(member.mention+" you have been called a zombie. Show up in 3 minutes or you would be disconnected!")
                task1 = asyncio.create_task(dc_user(), name="dc zombie")
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

        thereport = report.make_raw_file(str(member), int(start_epoch), int(end_epoch))


        await ctx.send(file=discord.File(thereport))


    @bot.hybrid_command(description="جدول مدت سشن های تمام شده در امروز")
    async def today(ctx):

        log_processor.renew_pendings()

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
        
        the_board = report.make_board(start_epoch, end_epoch)

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
        
        the_board = report.make_board(start_epoch, end_epoch)

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
        
        the_board = report.make_board(start_epoch, end_epoch)

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
        status = report.get_status(str(member))
        await ctx.send(member.mention + "'s current status: \n" + status)



    bot.run(settings.DISCORD_API_SECRET, root_logger=True)



if __name__ == "__main__":
    run()
