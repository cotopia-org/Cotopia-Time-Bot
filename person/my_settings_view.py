import discord

class SettingsView(discord.ui.View):
    @discord.ui.button(label="✏️ Email", style=discord.ButtonStyle.secondary)
    async def edit_email(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        pass
    @discord.ui.button(label="✏️ TRC20 Wallet", style=discord.ButtonStyle.secondary)
    async def edit_wallet(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        pass
    @discord.ui.button(label="✏️ Time Zone", style=discord.ButtonStyle.secondary)
    async def edit_timezone(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        pass
    @discord.ui.button(label="✏️ Calendar System", style=discord.ButtonStyle.secondary)
    async def edit_cal_sys(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        pass