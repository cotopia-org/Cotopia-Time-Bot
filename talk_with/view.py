import discord
import datetime
import time
import json


import log_processor


# returns epoch of NOW: int
def rightnow():
    epoch = int(time.time())
    return epoch

class TalkWithView(discord.ui.View):

    def __init__(self, *, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.members = []
        self.members_str = []
        self.interacted = []
        self.author_id = None
        self.voice_channel = None

    @discord.ui.button(label="decline",
                       style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if (interaction.user in self.members):


            if(interaction.user.id == self.author_id):
                # Author declined her own meeting
                # deleting everything
                await interaction.response.send_message(
                    """
You have declined your own talking request!
The request is cancelled!
The temp voice channel will be deleted.
You and all other members in the temp voice channel, will be disconnected from all voice channels!
                    """,
                    ephemeral=True)
                await self.voice_channel.delete()
                await interaction.message.delete()
            

            if (interaction.user not in self.interacted):
                c1 = interaction.message.content
                c2 = c1.replace(
                    interaction.user.mention + ":   :hourglass_flowing_sand: pending",
                    interaction.user.mention + ":   :red_circle: declined `" + datetime.datetime.now().strftime('%H:%M:%S') + "`",
                    1)
                try:
                    await interaction.response.edit_message(content = c2)
                except:
                    print("could not edit talk_with message!")
                
                self.interacted.append(interaction.user)
                event_note = {
                    "members": self.members_str,
                    "channel": {
                        "name": self.voice_channel.name,
                        "id": self.voice_channel.id
                    },
                    "message": interaction.message.content
                }
                log_processor.write_event_to_db(driver=interaction.guild.id,
                                                epoch=rightnow(),
                                                kind="DECLINE TALK",
                                                doer=str(interaction.user),
                                                isPair=False,
                                                note=json.dumps(event_note))
            else:
                try:
                    await interaction.response.send_message("You've already reacted to this!", ephemeral=True)
                except:
                    print("could not response with You've already reacted to this!")
            

        else:
            await interaction.response.send_message("You're not even invited! :unamused:", ephemeral=True)
    
    @discord.ui.button(label="I'll join in 5 mins")
    async def fivemins(self, interaction: discord.Interaction, button: discord.ui.Button):
        if (interaction.user in self.members):
            if (interaction.user not in self.interacted):
                c1 = interaction.message.content
                c2 = c1.replace(
                    interaction.user.mention + ":   :hourglass_flowing_sand: pending",
                    interaction.user.mention + ":   :orange_circle: will join in 5 mins `" + datetime.datetime.now().strftime('%H:%M:%S') + "`",
                    1)
                await interaction.response.edit_message(content = c2)
                self.interacted.append(interaction.user)
            else:
                await interaction.response.send_message("You've already reacted to this!", ephemeral=True)
        else:
            await interaction.response.send_message("You're not even invited! :unamused:", ephemeral=True)
    
    @discord.ui.button(label="I'll join in 15 mins")
    async def fifteenmins(self, interaction: discord.Interaction, button: discord.ui.Button):
        if (interaction.user in self.members):
            if (interaction.user not in self.interacted):
                c1 = interaction.message.content
                c2 = c1.replace(
                    interaction.user.mention + ":   :hourglass_flowing_sand: pending",
                    interaction.user.mention + ":   :orange_circle: will join in 15 mins `" + datetime.datetime.now().strftime('%H:%M:%S') + "`",
                    1)
                await interaction.response.edit_message(content = c2)
                self.interacted.append(interaction.user)
            else:
                await interaction.response.send_message("You've already reacted to this!", ephemeral=True)
        else:
            await interaction.response.send_message("You're not even invited! :unamused:", ephemeral=True)
    


