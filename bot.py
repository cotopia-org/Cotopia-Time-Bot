# This example requires the 'message_content' intent.

import discord
import log_processor

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
   log_processor.process(member, before, after)


client.run('MTEyNjAzNzQ2NDMxOTAxMjg4NQ.Ge8WYb.DEdu-Bpd9boEAlsVlMbdK5xEgOEhVhSlyk96GY')
