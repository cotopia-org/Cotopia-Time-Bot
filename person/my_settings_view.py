import discord

from .email_modal import EmailModal


class SettingsView(discord.ui.View):
    def __init__(self, *, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.email = ""
        self.wallet = ""

    @discord.ui.button(label="✏️ Email", style=discord.ButtonStyle.secondary)
    async def edit_email(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        email_modal = EmailModal()
        email_modal.guild_id = interaction.guild.id
        email_modal.user = interaction.user
        email_modal.load_defualts(user_email=self.email)
        await interaction.response.send_modal(email_modal)

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
