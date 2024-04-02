from typing import List

import discord
import psycopg2
from discord.components import SelectOption

from .db import Person


class CalSysDropdown(discord.ui.Select):
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
            SelectOption(label="Jalali", value="Jalali"),
            SelectOption(label="Gregorian", value="Gregorian"),
        ]
        super().__init__(
            # custom_id=custom_id,
            placeholder="Jalali or Gregorian",
            min_values=min_values,
            max_values=max_values,
            options=options,
            disabled=disabled,
            row=row,
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        conn = psycopg2.connect(
            host="localhost",
            dbname="postgres",
            user="postgres",
            password="Tp\ZS?gfLr|]'a",
            port=5432,
        )
        cursor = conn.cursor()
        the_person = Person()
        the_person.set_cal_system(
            discord_guild=interaction.guild.id,
            discord_id=interaction.user.id,
            cal_system=self.values[0],
        )
        conn.commit()
        cursor.close()
        conn.close()
        await interaction.followup.send(
            "Your Calendar System preference saved!", ephemeral=True
        )


class CalSysView(discord.ui.View):
    def __init__(
        self,
        *,
        timeout: float | None = 600,
    ):
        super().__init__(timeout=timeout)
        todo_dropdown = CalSysDropdown()
        self.add_item(todo_dropdown)
