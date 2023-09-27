from typing import Optional
import discord
from discord.interactions import Interaction
from discord.utils import MISSING
import psycopg2
from . import db

class MySettingsModal(discord.ui.Modal, title="Settings"):

    conn = None
    cur = None

    def connect_to_db(self):
        self.conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
        self.cur = self.conn.cursor()    

    email = discord.ui.TextInput(
        style = discord.TextStyle.short,
        label = "Your email",
        placeholder = "me@gmail.com",
    )

    trc20_wallet_addr = discord.ui.TextInput(
        style = discord.TextStyle.short,
        label = "Your TRC20 Wallet Address",
        placeholder = " TRC2034c276example45DaE400ecA3deCc"
    )

    async def on_submit(self, interaction: discord.Interaction):
        if (self.email.default != self.email.value):
            db.set_email(cur=self.cur, discord_guild=self.driver, discord_id=self.user.id,
                          name=self.user.name, email=self.email.value)
        if (self.trc20_wallet_addr.default != self.trc20_wallet_addr.value):
            db.set_trc20_addr(cur=self.cur, discord_guild=self.driver,
                               discord_id=self.user.id, name=self.user.name,
                                 addr=self.trc20_wallet_addr.value)
        self.commit_db()
        await interaction.response.send_message(f"Your settings were submitted {self.user.mention}!", ephemeral=True)
    
    def load_defualts(self):
        self.email.default = db.get_email(
            cur=self.cur, discord_guild=self.driver, discord_id=self.user.id)
        self.trc20_wallet_addr.default = db.get_trc20_addr(
            cur=self.cur, discord_guild=self.driver, discord_id=self.user.id)
        
    def commit_db(self):
        self.conn.commit()
        self.cur.close()
        self.conn.close()


