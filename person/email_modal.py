import re
from os import getenv

import discord
import psycopg2
from dotenv import load_dotenv

from .db import Person


class EmailModal(discord.ui.Modal, title="Email"):
    # def __init__(
    #     self, *, title: str = ..., timeout: float | None = None, custom_id: str = ...
    # ) -> None:
    #     super().__init__(title=title, timeout=timeout, custom_id=custom_id)
    #     self.user = None
    #     self.guild_id = 0

    email = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Your email",
        placeholder="me@gmail.com",
        required=False,
    )

    async def on_submit(self, interaction: discord.Interaction):
        if self.email.default != self.email.value:
            if self.check_email(self.email.value):
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
                the_person.set_email(
                    cur=cursor,
                    discord_guild=self.guild_id,
                    discord_id=self.user.id,
                    name=self.user.name,
                    email=self.email.value,
                )
                conn.commit()
                cursor.close()
                conn.close()
                await interaction.response.send_message(
                    f"Your email were submitted {self.user.mention}!", ephemeral=True
                )
            else:
                # invalid email input
                await interaction.response.send_message(
                    "Invalid email input! Try agin!", ephemeral=True
                )
        else:
            await interaction.response.send_message("Nothing changed!", ephemeral=True)

    def load_defualts(self, user_email):
        self.email.default = user_email

    def check_email(self, email: str):
        if email == "":
            return True
        pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
        if re.fullmatch(pattern, email):
            return True
        else:
            return False
