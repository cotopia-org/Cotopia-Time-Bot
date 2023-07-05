# This example requires the 'message_content' intent.

import discord

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')


@client.event
async def on_voice_state_update(member, before, after):
    guild = member.guild
    if guild.system_channel is not None:
            to_send = f'Welcome {member.mention} to the voice channel: {after.channel.name}!'
            await guild.system_channel.send(to_send)
    print("someone is here!")
    print(member)
    print(before)
    print(after)


client.run('MTEyNjAzNzQ2NDMxOTAxMjg4NQ.Ge8WYb.DEdu-Bpd9boEAlsVlMbdK5xEgOEhVhSlyk96GY')
