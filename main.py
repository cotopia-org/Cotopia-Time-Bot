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
        log_processor.process(member, before, after)
        raw_logger.record(member, before, after)
        
        m = member.guild.get_member(member.id)
        print("is_on_mobile():    " + str(m.is_on_mobile()))
        print("raw_status:    " + m.raw_status)
        print("status:    " + str(m.status))
        print("web_status:    " + str(m.web_status))
        print("desktop_status:    " + str(m.desktop_status))
        print("mobile_status:    " + str(m.mobile_status))

    @bot.event
    async def on_presence_update(before, after):
        pass

    @bot.hybrid_command()
    async def ping(ctx):
        await ctx.send("pong")

    bot.run(settings.DISCORD_API_SECRET, root_logger=True)

if __name__ == "__main__":
    run()