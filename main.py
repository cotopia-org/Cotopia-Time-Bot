import settings
import discord
from discord.ext import commands

import asyncio
import datetime

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

    bot = commands.Bot(command_prefix="/", intents=intents)

    @bot.event
    async def on_ready():
        logger.info(f"User: {bot.user} (ID: {bot.user.id})")
        await bot.tree.sync()
    
    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return
        global the_zombie
        if (message.author == the_zombie):
            task, = [task for task in asyncio.all_tasks() if task.get_name() == "dc zombie"]
            task.cancel()
            await message.channel.send("Well well you are not a zombie " + message.author.mention + "!")
            the_zombie = None

        

    @bot.event
    async def on_voice_state_update(member, before, after):

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
    async def on_presence_update(before, after):
        pass

    @bot.hybrid_command()
    async def ping(ctx):
        await ctx.send("pong")

    @bot.hybrid_command()
    async def viewstats(ctx, member: discord.Member, start_yyyy: int, start_mm: int, start_dd: int, end_yyyy: int, end_mm: int, end_dd: int):

        start_epoch = datetime.datetime(
            year=start_yyyy, month=start_mm, day=start_dd, hour=0, minute=0).strftime('%s')
        end_epoch = datetime.datetime(
            year=end_yyyy, month=end_mm, day=end_dd, hour=0, minute=0).strftime('%s')
        
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

        global the_zombie
        the_zombie = member
        
        task1 = None
        async def dc_user():
            await asyncio.sleep(20)
            await member.move_to(None, reason="You have been reported a zombie and didn't respond!")
            await ctx.guild.system_channel.send(member.mention+"'s session terminated because they acted like a zombie!")

        

        if (ctx.author != member):
            await ctx.send("You reported " + member.mention + " as a zombie!")
            await ctx.guild.system_channel.send(member.mention+" you have been called a zombie. Show up in 3 minutes or you would be disconnected!")
            task1 = asyncio.create_task(dc_user(), name="dc zombie")
            await task1
        else:
            await ctx.send("You can not name yourself a zombie! Take a break!")

            # task, = [task for task in asyncio.all_tasks() if task.get_name() == "dc zombie"]
            # task.cancel()
            # await ctx.send("Well well you are not a zombie " + member.mention + "!")



    bot.run(settings.DISCORD_API_SECRET, root_logger=True)




if __name__ == "__main__":
    run()
