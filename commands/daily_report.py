from discord.ext import commands


@commands.hybrid_command(description="Replies with pong!")
async def test_test(ctx):
    print("this is ping. the server is:")
    print(ctx.guild.id)
    await ctx.send("Your Discord ID is " + str(ctx.author.id), ephemeral=True)

async def setup(bot):
    bot.add_command(test_test)