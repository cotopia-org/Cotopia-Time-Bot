import settings
import discord
from discord.ext import commands

import log_processor
import raw_logger


logger = settings.logging.getLogger("bot")

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
        guild = message.guild
        # print(guild)
        if message.author == bot.user:
            return

        if message.content.startswith('📜'):
            async for member in guild.fetch_members(limit=150):
                # print(member.name)
                await message.channel.send(member)

    @bot.event
    async def on_voice_state_update(member, before, after):

        # print("before:  "+ str(before))
        # print("after:  "+ str(after))

        log_processor.record(member, before, after)
        raw_logger.record(member, before, after)

        # m = member.guild.get_member(member.id)
        # print("is_on_mobile():    " + str(m.is_on_mobile()))
        # print("raw_status:    " + m.raw_status)
        # print("status:    " + str(m.status))
        # print("web_status:    " + str(m.web_status))
        # print("desktop_status:    " + str(m.desktop_status))
        # print("mobile_status:    " + str(m.mobile_status))

    @bot.event
    async def on_presence_update(before, after):
        pass

    @bot.hybrid_command()
    async def ping(ctx):
        await ctx.send("pong")

    @bot.hybrid_command()
    async def viewstats(ctx):
        guild = ctx.guild
        view = discord.ui.View()
        async for member in guild.fetch_members(limit=150):
            b = discord.ui.Button(label=str(member))
            view.add_item(b)
        
        await ctx.send(view=view)

    # @bot.hybrid_command()
    # async def week0(ctx):
    #     await ctx.send(file=discord.File("./plogs/reports/LunaBot🌙#9997.txt"))
    #     await ctx.send(file=discord.File("./plogs/reports/ajabimahdi.txt"))
    #     await ctx.send(file=discord.File("./plogs/reports/armanhr.txt"))
    #     await ctx.send(file=discord.File("./plogs/reports/imebneali.txt"))
    #     await ctx.send(file=discord.File("./plogs/reports/kharrati.txt"))
    #     await ctx.send(file=discord.File("./plogs/reports/m.habibi.txt"))
    #     await ctx.send(file=discord.File("./plogs/reports/mamreez_tn#5785.txt"))
    #     await ctx.send(file=discord.File("./plogs/reports/navid.madadi.txt"))

    bot.run(settings.DISCORD_API_SECRET, root_logger=True)

if __name__ == "__main__":
    run()