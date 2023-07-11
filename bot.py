# This example requires the 'message_content' intent.

import discord
import log_processor
import raw_logger

intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    guild = message.guild
    # print(guild)
    if message.author == client.user:
        return

    if message.content.startswith('📜'):
        async for member in guild.fetch_members(limit=150):
            # print(member.name)
            await message.channel.send(member)    

@client.event
async def on_voice_state_update(member, before, after):
   log_processor.process(member, before, after)
   raw_logger.record(member, before, after)

   m = member.guild.fetch_members
   print (m)

   member = (await member.guild.query_members([member.id], presences=True))[0]
   m = member.guild.get_member(member.id)
   print("is_on_mobile():    " + str(m.is_on_mobile()))
   print("raw_status:    " + m.raw_status)
   print("status:    " + str(m.status))
   print("web_status:    " + str(m.web_status))
   print("desktop_status:    " + str(m.desktop_status))
   print("mobile_status:    " + str(m.mobile_status))
#    await guild.system_channel.send('SESSION PAUSED')

@client.event
async def on_presence_update(before, after):
    # print("it works")
    pass




client.run('MTEyNzQ3MzQzMzg4MjY3MzI2Mw.GIF-ZA.yNj9icp1DGzEkd4DOztjkjbMpuCToNz4lVhYRg')
