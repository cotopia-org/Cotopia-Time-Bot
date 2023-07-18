import settings
import discord
from discord.ext import commands

import asyncio
import datetime
import typing

import log_processor
import raw_logger
import report


logger = settings.logging.getLogger("bot")

the_zombie = None


def run():

    

    intents = discord.Intents.default()
    intents.message_content = True
    intents.presences = True
    intents.members = True
    intents.reactions = True

    bot = commands.Bot(command_prefix="/", intents=intents)

    def today():
        the_string = datetime.datetime.today().strftime('%Y-%m-%d')
        slices = the_string.split("-")
        dic = {"y": int(slices[0]), "m": int(slices[1]), "d": int(slices[2])}
        return dic

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


        
        log_processor.record(member, before, after)
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

    @bot.hybrid_command()
    async def ping(ctx):
        await ctx.send("pong")

    @bot.hybrid_command()
    async def viewstats(ctx, member: discord.Member,
                        start_yyyy: typing.Optional[int]=today()["y"], start_mm: typing.Optional[int]=today()["m"]-1, start_dd: typing.Optional[int]=today()["d"],
                        end_yyyy: typing.Optional[int]=today()["y"], end_mm: typing.Optional[int]=today()["m"], end_dd: typing.Optional[int]=today()["d"]):

        start_epoch = datetime.datetime(
            year=start_yyyy, month=start_mm, day=start_dd, hour=0, minute=0).strftime('%s')
        end_epoch = datetime.datetime(
            year=end_yyyy, month=end_mm, day=end_dd, hour=0, minute=0).strftime('%s')
        

        if (int(start_epoch) >= int(end_epoch)):
            await ctx.send("**Start Date** should be before **End Date**! Try Again!")
            return
        # max int value in postgres is 	-2147483648 to 2147483647
        elif (int(end_epoch) > 2147400000):
            await ctx.send("**End Date** is too far in the future! Try Again!")
            return
        
        
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




    @bot.hybrid_command()
    async def zombie(ctx, member: discord.Member):
        
        # func that does the job after a while
        task1 = None
        async def dc_user():
            await asyncio.sleep(180)    # 3 minutes
            global the_zombie
            the_zombie = None
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




    bot.run(settings.DISCORD_API_SECRET, root_logger=True)




if __name__ == "__main__":
    run()
