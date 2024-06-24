from os import getenv

import discord
import psycopg2
from dotenv import load_dotenv

from .db import Person


class WalletModal(discord.ui.Modal, title="TRC20 Wallet"):

    trc20_wallet_addr = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Your TRC20 Wallet Address",
        placeholder="TRC2034c276example45DaE400ecA3deCc",
        required=False,
    )

    async def on_submit(self, interaction: discord.Interaction):
        if self.trc20_wallet_addr.default != self.trc20_wallet_addr.value:
            if self.check_addr(self.trc20_wallet_addr.value):
                load_dotenv()
                conn = psycopg2.connect(
                    host=getenv("DB_HOST"),
                    dbname=getenv("DB_NAME"),
                    user=getenv("DB_USER"),
                    password=getenv("DB_PASSWORD"),
                    port=getenv("DB_PORT"),
                )
                cursor = conn.cursor()

                the_person = Person()
                the_person.set_trc20_addr(
                    cur=cursor,
                    discord_guild=self.guild_id,
                    discord_id=self.user.id,
                    name=self.user.name,
                    addr=self.trc20_wallet_addr.value,
                )
                conn.commit()
                cursor.close()
                conn.close()
                await interaction.response.send_message(
                    f"Your wallet address were submitted {self.user.mention}!",
                    ephemeral=True,
                )
            else:
                # invalid address input
                await interaction.response.send_message(
                    "Invalid address input! Try agin!", ephemeral=True
                )
        else:
            await interaction.response.send_message("Nothing changed!", ephemeral=True)

    def load_defualts(self, user_wallet):
        self.trc20_wallet_addr.default = user_wallet

    def check_addr(self, addr: str):
        if " " not in addr:
            return True
        else:
            return False
