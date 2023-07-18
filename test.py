import psycopg2
import report
import time
import datetime
import asyncio


# def epoch_generator(year: int, month: int, day: int):
#     ts= datetime.datetime(year=year, month=month, day=day, hour=0, minute=0).strftime('%s')
#     return ts


# print(epoch_generator(2023, int("07"), int("07")))

# datetime_object = datetime.fromtimestamp(1689424634)
# print(datetime_object)




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


    # if message.content.startswith(":zombie:"):
            # await message.author.move_to(None, reason="You have been reported a zombie and didn't respond!")
            # await guild.kick(message.author, reason="You have been reported a zombie and didn't respond!")
            # async for member in guild.fetch_members(limit=150):
            #     print(member.name)
            #     await message.channel.send(member)


 # m = member.guild.get_member(member.id)
        # print("is_on_mobile():    " + str(m.is_on_mobile()))
        # print("raw_status:    " + m.raw_status)
        # print("status:    " + str(m.status))
        # print("web_status:    " + str(m.web_status))
        # print("desktop_status:    " + str(m.desktop_status))
        # print("mobile_status:    " + str(m.mobile_status))



# guild = ctx.guild
#         view = discord.ui.View()
#         async for member in guild.fetch_members(limit=150):
#             b = discord.ui.Button(label=str(member))
#             view.add_item(b)
        
#         await ctx.send(view=view)



def today():
        the_string = datetime.datetime.today().strftime('%Y-%m-%d')
        slices = the_string.split("-")
        dic = {"y": int(slices[0]), "m": int(slices[1]), "d": int(slices[2])}
        return dic

print(today())

