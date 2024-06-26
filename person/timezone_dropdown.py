from os import getenv
from typing import List

import discord
import psycopg2
from discord.components import SelectOption
from dotenv import load_dotenv

from .db import Person


class TimeZoneDropdown(discord.ui.Select):
    def __init__(
        self,
        *,
        # custom_id: str = ...,
        placeholder: str | None = None,
        min_values: int = 1,
        max_values: int = 1,
        options: List[SelectOption] = ...,
        disabled: bool = False,
        row: int | None = None,
    ) -> None:
        options = [
            SelectOption(label="Asia/Tehran", value="Asia/Tehran"),
            SelectOption(label="Asia/Dubai", value="Asia/Dubai"),
            SelectOption(label="Asia/Istanbul", value="Asia/Istanbul"),
            SelectOption(label="Africa/Cairo", value="Africa/Cairo"),
            SelectOption(label="Europe/London", value="Europe/London"),
            SelectOption(label="America/Toronto", value="America/Toronto"),
        ]
        super().__init__(
            # custom_id=custom_id,
            placeholder="Time Zone",
            min_values=min_values,
            max_values=max_values,
            options=options,
            disabled=disabled,
            row=row,
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
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
        the_person.set_timezone(
            discord_guild=interaction.guild.id,
            discord_id=interaction.user.id,
            timezone=self.values[0],
        )
        conn.commit()
        cursor.close()
        conn.close()
        await interaction.followup.send(
            "Your Time Zone preference saved!", ephemeral=True
        )


class TimeZoneView(discord.ui.View):
    def __init__(
        self,
        *,
        timeout: float | None = 600,
    ):
        super().__init__(timeout=timeout)
        timezone_dropdown = TimeZoneDropdown()
        self.add_item(timezone_dropdown)
