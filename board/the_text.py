import time
from os import getenv

import discord
import psycopg2
import pytz
from dotenv import load_dotenv
from persiantools.jdatetime import JalaliDate, JalaliDateTime, timedelta

import log_processor
import report

from .schedule import get_schedules


# returns epoch of NOW: int
def rightnow():
    epoch = int(time.time())
    return epoch


async def gen_dirooz_board(guild):
    # get the channel
    category = discord.utils.get(guild.categories, name="JOBS")
    if category is None:
        category = await guild.create_category("JOBS")
    da_channel = discord.utils.get(guild.text_channels, name="📊-status")
    if da_channel is None:
        da_channel = await guild.create_text_channel(
            category=category, name="📊-status"
        )

    # make the board
    dirooz = JalaliDate.today() - timedelta(days=1)
    start_dt = JalaliDateTime(
        year=dirooz.year,
        month=dirooz.month,
        day=dirooz.day,
    )
    localized_start_dt = pytz.timezone("Asia/Tehran").localize(dt=start_dt)
    start_epoch = int(localized_start_dt.timestamp())
    end_epoch = start_epoch + 86400

    the_board = report.make_board(
        driver=str(guild.id), start_epoch=start_epoch, end_epoch=end_epoch
    )

    # get schedules
    schedules = get_schedules(
        start_epoch=start_epoch, end_epoch=end_epoch, guild_id=guild.id
    )

    title_date = JalaliDate.fromtimestamp(start_epoch)
    updated_on = JalaliDateTime.now().strftime("%H:%M")

    text = (
        "LEADERBOARD OF "
        + str(title_date)
        + "\n`updated on "
        + updated_on
        + "`\n------------------------------\n"
    )
    for line in the_board:
        try:
            percent = line[1] / schedules[line[0]] * 100
            percent = int(round(percent, 0))
            percent_text = f"{percent}% of {schedules[line[0]]} hours"
        except:  # noqa: E722
            percent_text = "schedule's not available!"
        text = text + str(line[1]) + f" | <@{line[0]}>   ({percent_text})\n"

    # send the text
    msg = await da_channel.send(text + "‌")

    # record to db
    load_dotenv()
    conn = psycopg2.connect(
        host=getenv("DB_HOST"),
        dbname=getenv("DB_NAME"),
        user=getenv("DB_USER"),
        password=getenv("DB_PASSWORD"),
        port=getenv("DB_PORT"),
    )
    cursor = conn.cursor()
    cursor.execute(
        """   CREATE TABLE IF NOT EXISTS dirooz_boards(
                                guild_id BIGINT NOT NULL,
                                channel_id BIGINT NOT NULL,
                                msg_id BIGINT NOT NULL,
                                last_update BIGINT NOT NULL); """
    )
    cursor.execute(f"DELETE FROM dirooz_boards WHERE guild_id = {guild.id};")
    cursor.execute(
        f"""     INSERT INTO dirooz_boards VALUES
                                ({guild.id}, {da_channel.id}, {msg.id}, {rightnow()});"""
    )
    conn.commit()
    cursor.close()
    conn.close()


async def update_dirooz_board(guild):
    # get msg from db
    load_dotenv()
    conn = psycopg2.connect(
        host=getenv("DB_HOST"),
        dbname=getenv("DB_NAME"),
        user=getenv("DB_USER"),
        password=getenv("DB_PASSWORD"),
        port=getenv("DB_PORT"),
    )
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM dirooz_boards WHERE guild_id = {guild.id};")
    db_msg = cursor.fetchone()

    # check if it's outdated
    last_update = JalaliDate.fromtimestamp(db_msg[3])

    if JalaliDate.today().day == last_update.day:
        print("no need to update dirooz board")
        conn.commit()
        cursor.close()
        conn.close()
        return
    else:
        # get the msg object
        channel = guild.get_channel(db_msg[1])
        message = await channel.fetch_message(db_msg[2])

        # make the board
        dirooz = JalaliDate.today() - timedelta(days=1)
        start_dt = JalaliDateTime(
            year=dirooz.year,
            month=dirooz.month,
            day=dirooz.day,
        )
        localized_start_dt = pytz.timezone("Asia/Tehran").localize(dt=start_dt)
        start_epoch = int(localized_start_dt.timestamp())
        end_epoch = start_epoch + 86400

        the_board = report.make_board(
            driver=str(guild.id), start_epoch=start_epoch, end_epoch=end_epoch
        )

        # get schedules
        schedules = get_schedules(
            start_epoch=start_epoch, end_epoch=end_epoch, guild_id=guild.id
        )

        title_date = JalaliDate.fromtimestamp(start_epoch)
        updated_on = JalaliDateTime.now().strftime("%H:%M")

        text = (
            "LEADERBOARD OF "
            + str(title_date)
            + "\n`updated on "
            + updated_on
            + "`\n------------------------------\n"
        )
        for line in the_board:
            try:
                percent = line[1] / schedules[line[0]] * 100
                percent = int(round(percent, 0))
                percent_text = f"{percent}% of {schedules[line[0]]} hours"
            except:  # noqa: E722
                percent_text = "schedule's not available!"
            text = text + str(line[1]) + f" | <@{line[0]}>   ({percent_text})\n"

        # send edit
        await message.edit(content=text + "‌")
        # update db
        cursor.execute(
            f"UPDATE dirooz_boards SET last_update = {rightnow()} WHERE guild_id = {guild.id};"
        )
        conn.commit()
        cursor.close()
        conn.close()


async def gen_inmaah_board(guild):
    # get the channel
    category = discord.utils.get(guild.categories, name="JOBS")
    if category is None:
        category = await guild.create_category("JOBS")
    da_channel = discord.utils.get(guild.text_channels, name="📊-status")
    if da_channel is None:
        da_channel = await guild.create_text_channel(
            category=category, name="📊-status"
        )

    # make the board
    log_processor.renew_pendings(driver=str(guild.id))

    emrooz = JalaliDate.today()
    start_dt = JalaliDateTime(
        year=emrooz.year,
        month=emrooz.month,
        day=1,
        hour=0,
        minute=0,
        second=0,
    )
    localized_start_dt = pytz.timezone("Asia/Tehran").localize(dt=start_dt)
    start_epoch = int(localized_start_dt.timestamp())

    end_dt = start_dt + timedelta(days=32)
    end_dt = JalaliDateTime(
        year=end_dt.year,
        month=end_dt.month,
        day=1,
        hour=0,
        minute=0,
        second=0,
    )
    localized_end_dt = pytz.timezone("Asia/Tehran").localize(dt=end_dt)
    end_epoch = int(localized_end_dt.timestamp()) + 1

    the_board = report.make_board(
        driver=str(guild.id), start_epoch=start_epoch, end_epoch=end_epoch
    )

    # get schedules
    schedules = get_schedules(
        start_epoch=start_epoch, end_epoch=end_epoch, guild_id=guild.id
    )

    title_date = JalaliDate.fromtimestamp(start_epoch).strftime("%Y/%m")
    updated_on = JalaliDateTime.now().strftime("%H:%M")

    text = (
        "LEADERBOARD OF "
        + str(title_date)
        + "\n`updated on "
        + updated_on
        + "`\n------------------------------\n"
    )
    for line in the_board:
        try:
            percent = line[1] / schedules[line[0]] * 100
            percent = int(round(percent, 0))
            percent_text = f"{percent}% of {schedules[line[0]]} hours"
        except:  # noqa: E722
            percent_text = "schedule's not available!"
        text = text + str(line[1]) + f" | <@{line[0]}>   ({percent_text})\n"

    # send the text
    msg = await da_channel.send(text + "‌")

    # record to db
    load_dotenv()
    conn = psycopg2.connect(
        host=getenv("DB_HOST"),
        dbname=getenv("DB_NAME"),
        user=getenv("DB_USER"),
        password=getenv("DB_PASSWORD"),
        port=getenv("DB_PORT"),
    )
    cursor = conn.cursor()
    cursor.execute(
        """   CREATE TABLE IF NOT EXISTS inmaah_boards(
                                guild_id BIGINT NOT NULL,
                                channel_id BIGINT NOT NULL,
                                msg_id BIGINT NOT NULL,
                                last_update BIGINT NOT NULL); """
    )
    cursor.execute(f"DELETE FROM inmaah_boards WHERE guild_id = {guild.id};")
    cursor.execute(
        f"""     INSERT INTO inmaah_boards VALUES
                                ({guild.id}, {da_channel.id}, {msg.id}, {rightnow()});"""
    )
    conn.commit()
    cursor.close()
    conn.close()


async def update_inmaah_board(guild):
    # get msg from db
    load_dotenv()
    conn = psycopg2.connect(
        host=getenv("DB_HOST"),
        dbname=getenv("DB_NAME"),
        user=getenv("DB_USER"),
        password=getenv("DB_PASSWORD"),
        port=getenv("DB_PORT"),
    )
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM inmaah_boards WHERE guild_id = {guild.id};")
    db_msg = cursor.fetchone()

    # check if it's outdated
    last_update = db_msg[3]

    if rightnow() - last_update < 3600:
        print("no need to update inmaah board")
        conn.commit()
        cursor.close()
        conn.close()
        return
    else:
        # get the msg object
        channel = guild.get_channel(db_msg[1])
        message = await channel.fetch_message(db_msg[2])

        # make the board
        log_processor.renew_pendings(driver=str(guild.id))

        emrooz = JalaliDate.today()
        start_dt = JalaliDateTime(
            year=emrooz.year,
            month=emrooz.month,
            day=1,
            hour=0,
            minute=0,
            second=0,
        )
        localized_start_dt = pytz.timezone("Asia/Tehran").localize(dt=start_dt)
        start_epoch = int(localized_start_dt.timestamp())

        end_dt = start_dt + timedelta(days=32)
        end_dt = JalaliDateTime(
            year=end_dt.year,
            month=end_dt.month,
            day=1,
            hour=0,
            minute=0,
            second=0,
        )
        localized_end_dt = pytz.timezone("Asia/Tehran").localize(dt=end_dt)
        end_epoch = int(localized_end_dt.timestamp()) + 1

        the_board = report.make_board(
            driver=str(guild.id), start_epoch=start_epoch, end_epoch=end_epoch
        )

        # get schedules
        schedules = get_schedules(
            start_epoch=start_epoch, end_epoch=end_epoch, guild_id=guild.id
        )

        title_date = JalaliDate.fromtimestamp(start_epoch).strftime("%Y/%m")
        updated_on = JalaliDateTime.now().strftime("%H:%M")

        text = (
            "LEADERBOARD OF "
            + str(title_date)
            + "\n`updated on "
            + updated_on
            + "`\n------------------------------\n"
        )
        for line in the_board:
            try:
                percent = line[1] / schedules[line[0]] * 100
                percent = int(round(percent, 0))
                percent_text = f"{percent}% of {schedules[line[0]]} hours"
            except:  # noqa: E722
                percent_text = "schedule's not available!"
            text = text + str(line[1]) + f" | <@{line[0]}>   ({percent_text})\n"

        # send edit
        await message.edit(content=text + "‌")
        # update db
        cursor.execute(
            f"UPDATE inmaah_boards SET last_update = {rightnow()} WHERE guild_id = {guild.id};"
        )
        conn.commit()
        cursor.close()
        conn.close()
