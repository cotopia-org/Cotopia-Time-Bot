import discord
from discord.ext import commands

import settings

from models.Models import Book

logger = settings.logging.getLogger("bot")


def run():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.presences = True
    intents.members = True
    intents.reactions = True

    # bot = commands.Bot(command_prefix="/", intents=intents)
    # print(Book.select())
    # Book.create(name='SALAM')
    for book in Book.select():
        print(book.name)

    # @bot.event
    # async def on_ready():
    #
    #     logger.info(f"User: {bot.user} (ID: {bot.user.id})")
    #     await bot.tree.sync()
    #
    # @bot.hybrid_command()
    # async def talk_with(ctx, people: commands.Greedy[discord.User]):
    #     for person in people:
    #         print(person)
    #
    # bot.run('MTIxNDU2MTQ1NTEzNjA1NTMxNw.Gm7zsn.f_3gpRHmb2vGJxFjQoACgZ44rGol8tM9MH8NNI', root_logger=True)


if __name__ == "__main__":
    run()
