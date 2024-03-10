from asyncio import sleep


async def play_ring_voice(discord, bot, ctx, member, voice='assets/sounds/ring3.mp3'):
    # play ring alarm when user sent the command

    if member.voice is not None:

        if not member.voice.self_deaf:
            voice_channel = member.voice.channel
            print(voice_channel)

            await voice_channel.connect()
            voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
            voice_client.play(discord.FFmpegPCMAudio(voice))
            while voice_client.is_playing():
                await sleep(1)
            await voice_client.disconnect()

    return 'Ok'
