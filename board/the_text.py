import sqlite3
import discord

from persiantools.jdatetime import JalaliDateTime
from persiantools.jdatetime import JalaliDate
import pytz
import time

import report
import log_processor


def today_jalali():
    the_string = str(JalaliDate.today())
    slices = the_string.split("-")
    dic = {"y": int(slices[0]), "m": int(slices[1]), "d": int(slices[2])}
    return dic

# returns epoch of NOW: int
def rightnow():
    epoch = int(time.time())
    return epoch

async def gen_dirooz_board(guild):
    # get the channel
    category = discord.utils.get(guild.categories, name="JOBS")
    if category is None:
        category = await guild.create_category("JOBS")
    da_channel = discord.utils.get(guild.text_channels, name="status")
    if da_channel is None:
        da_channel = await guild.create_text_channel(category=category, name="status")
    
    # make the board
    now = today_jalali()
    start_epoch = int(
                JalaliDateTime(
                    year=now["y"], month=now["m"], day=now["d"]-1, hour=0, minute=0, second=0,
                    tzinfo=pytz.timezone("Asia/Tehran")).to_gregorian().strftime('%s')
        )
    end_epoch = int(
                JalaliDateTime(
                    year=now["y"], month=now["m"], day=now["d"]-1, hour=23, minute=59, second=59,
                    tzinfo=pytz.timezone("Asia/Tehran")).to_gregorian().strftime('%s')
        )
        
    the_board = report.make_board(driver=str(guild.id), start_epoch=start_epoch, end_epoch=end_epoch)

    title_date = JalaliDate.fromtimestamp(start_epoch)

    text = ("Net Session Hours of " + str(title_date) + "\n------------------------------\n")
    for l in the_board:
        text = text + str(l[1]) + " | " + l[0] + "\n"
    
    # send the text
    msg = await da_channel.send(text)

    # record to db
    conn = sqlite3.connect("timeboards.db")
    cursor = conn.cursor()
    cursor.execute(
        """   CREATE TABLE IF NOT EXISTS dirooz_boards(
                                guild_id INT NOT NULL,
                                channel_id INT NOT NULL,
                                msg_id INT NOT NULL,
                                last_update INT NOT NULL); """)
    cursor.execute(f"DELETE FROM dirooz_boards WHERE guild_id = {guild.id};")
    cursor.execute(f"""     INSERT INTO dirooz_boards VALUES
                                ({guild.id}, {da_channel.id}, {msg.id}, {rightnow()});""")
    conn.commit()
    cursor.close()
    conn.close()


async def update_dirooz_board(guild):
    # get msg from db
    conn = sqlite3.connect("timeboards.db")
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
        now = today_jalali()
        start_epoch = int(
                JalaliDateTime(
                    year=now["y"], month=now["m"], day=now["d"]-1, hour=0, minute=0, second=0,
                    tzinfo=pytz.timezone("Asia/Tehran")).to_gregorian().strftime('%s')
        )
        end_epoch = int(
                JalaliDateTime(
                    year=now["y"], month=now["m"], day=now["d"]-1, hour=23, minute=59, second=59,
                    tzinfo=pytz.timezone("Asia/Tehran")).to_gregorian().strftime('%s')
        )
        
        the_board = report.make_board(driver=str(guild.id), start_epoch=start_epoch, end_epoch=end_epoch)

        title_date = JalaliDate.fromtimestamp(start_epoch)

        text = ("Net Session Hours of " + str(title_date) + "\n------------------------------\n")
        for l in the_board:
            text = text + str(l[1]) + " | " + l[0] + "\n"

        # send edit
        await message.edit(content=text)
        # update db
        cursor.execute(f"UPDATE dirooz_boards SET last_update = {rightnow()} WHERE guild_id = {guild.id};")
        conn.commit()
        cursor.close()
        conn.close()
    
async def gen_inmaah_board(guild):
     # get the channel
    category = discord.utils.get(guild.categories, name="JOBS")
    if category is None:
        category = await guild.create_category("JOBS")
    da_channel = discord.utils.get(guild.text_channels, name="status")
    if da_channel is None:
        da_channel = await guild.create_text_channel(category=category, name="status")
    
    # make the board
    log_processor.renew_pendings(driver=str(guild.id))

    now = today_jalali()
    start_epoch = int(
                JalaliDateTime(
                    year=now["y"], month=now["m"], day=1, hour=0, minute=0, second=0,
                    tzinfo=pytz.timezone("Asia/Tehran")).to_gregorian().strftime('%s')
        )
    end_epoch = int(
                JalaliDateTime(
                    year=now["y"], month=now["m"], day=now["d"], hour=23, minute=59, second=59,
                    tzinfo=pytz.timezone("Asia/Tehran")).to_gregorian().strftime('%s')
        )
        
    the_board = report.make_board(driver=str(guild.id), start_epoch=start_epoch, end_epoch=end_epoch)

    title_date = JalaliDate.fromtimestamp(start_epoch).strftime("%Y/%m")

    text = ("Net Session Hours of " + str(title_date) + "\n------------------------------\n")
    for l in the_board:
        text = text + str(l[1]) + " | " + l[0] + "\n"
    
    # send the text
    msg = await da_channel.send(text)

    # record to db
    conn = sqlite3.connect("timeboards.db")
    cursor = conn.cursor()
    cursor.execute(
        """   CREATE TABLE IF NOT EXISTS inmaah_boards(
                                guild_id INT NOT NULL,
                                channel_id INT NOT NULL,
                                msg_id INT NOT NULL,
                                last_update INT NOT NULL); """)
    cursor.execute(f"DELETE FROM inmaah_boards WHERE guild_id = {guild.id};")
    cursor.execute(f"""     INSERT INTO inmaah_boards VALUES
                                ({guild.id}, {da_channel.id}, {msg.id}, {rightnow()});""")
    conn.commit()
    cursor.close()
    conn.close()


async def update_inmaah_board(guild):
    # get msg from db
    conn = sqlite3.connect("timeboards.db")
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

        now = today_jalali()
        start_epoch = int(
                JalaliDateTime(
                    year=now["y"], month=now["m"], day=1, hour=0, minute=0, second=0,
                    tzinfo=pytz.timezone("Asia/Tehran")).to_gregorian().strftime('%s')
        )
        end_epoch = int(
                JalaliDateTime(
                    year=now["y"], month=now["m"], day=now["d"], hour=23, minute=59, second=59,
                    tzinfo=pytz.timezone("Asia/Tehran")).to_gregorian().strftime('%s')
        )
        
        the_board = report.make_board(driver=str(guild.id), start_epoch=start_epoch, end_epoch=end_epoch)

        title_date = JalaliDate.fromtimestamp(start_epoch).strftime("%Y/%m")

        text = ("Net Session Hours of " + str(title_date) + "\n------------------------------\n")
        for l in the_board:
            text = text + str(l[1]) + " | " + l[0] + "\n"
        
        # send edit
        await message.edit(content=text)
        # update db
        cursor.execute(f"UPDATE inmaah_boards SET last_update = {rightnow()} WHERE guild_id = {guild.id};")
        conn.commit()
        cursor.close()
        conn.close()