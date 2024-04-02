import discord

class SettingsView(discord.ui.View):
    def __init__(self, *, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.email = ""
        self.wallet = ""

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