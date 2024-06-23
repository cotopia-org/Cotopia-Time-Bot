import datetime

import requests
from discord import Member
from discord.ext import commands

import auth


@commands.hybrid_command()
async def schedule(ctx):
    d = {}
    d["discord_guild"] = ctx.guild.id
    d["discord_id"] = ctx.author.id
    d["discord_name"] = ctx.author.name
    roles = ctx.author.roles
    roles_list = []
    for r in roles:
        roles_list.append(r.name)
    d["discord_roles"] = roles_list

    token = auth.create_token(d)

    # link = "http://127.0.0.1:8000/login?t=" + token
    link = (
        "http://tooljet.cotopia.social/applications/e61ce10d-580e-4167-98a3-719dbfb85f5a/home?access="
        + token
    )

    now = datetime.datetime.now()
    expires_at = now + datetime.timedelta(0, 3600)
    expires_at_string = expires_at.strftime("%H:%M:%S")

    await ctx.send(
        f"[Use this link to open Cotopia Schedule App.\n(valid until {expires_at_string})]({link})",
        ephemeral=True,
    )


@commands.hybrid_command(description="Shows @member total shceduled time!")
async def scheduled_time(
    ctx,
    member: Member,
    start_yyyy_mm_dd: str,
    end_yyyy_mm_dd: str,
):
    REQUEST_URL = "http://tooljet.cotopia.social:8084/total_hours"
    params = {
        "id_server": ctx.guild.id,
        "id_discord": member.id,
        "start_date": start_yyyy_mm_dd,
        "end_date": end_yyyy_mm_dd,
    }
    r = requests.get(url=REQUEST_URL, params=params)
    if r.status_code == 200:
        text = f"Scheduled Time of {member.mention}\nFrom: {start_yyyy_mm_dd}\nTo: {end_yyyy_mm_dd}\n"
        text = text + "**" + str(r.json()["total_duration_hours"]) + " Hours**"
        await ctx.send(text)
    else:
        await ctx.send(
            r.json()["error"],
            ephemeral=True,
        )


async def setup(bot):
    bot.add_command(schedule)
    bot.add_command(scheduled_time)
