from typing import List

import discord
from discord.components import SelectOption

from db import PGConnect

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
        pgc = PGConnect()
        conn = pgc.conn
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
        calsys_dropdown = CalSysDropdown()
        self.add_item(calsys_dropdown)
