import discord

from .cal_sys_dropdown import CalSysView
from .email_modal import EmailModal
from .timezone_dropdown import TimeZoneView
from .wallet_modal import WalletModal


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
        wallet_modal = WalletModal()
        wallet_modal.guild_id = interaction.guild.id
        wallet_modal.user = interaction.user
        wallet_modal.load_defualts(user_wallet=self.wallet)
        await interaction.response.send_modal(wallet_modal)

    @discord.ui.button(label="✏️ Time Zone", style=discord.ButtonStyle.secondary)
    async def edit_timezone(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        view = TimeZoneView()
        await interaction.response.send_message(
            "Select Your Time Zone:", view=view, ephemeral=True
        )

    @discord.ui.button(label="✏️ Calendar System", style=discord.ButtonStyle.secondary)
    async def edit_cal_sys(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        view = CalSysView()
        await interaction.response.send_message(
            "Select Your Calendar System:", view=view, ephemeral=True
        )
