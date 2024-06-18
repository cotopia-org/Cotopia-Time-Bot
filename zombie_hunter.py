import json
import time
from os import getenv

import psycopg2
from dotenv import load_dotenv


# returns epoch of NOW: int
def rightnow():
    epoch = int(time.time())
    return epoch


# 🚗
def record_hunt(driver: str, reporter: str, zombie: str):

    load_dotenv()
    conn = psycopg2.connect(
        host=getenv("DB_HOST"),
        dbname=getenv("DB_NAME"),
        user=getenv("DB_USER"),
        password=getenv("DB_PASSWORD"),
        port=getenv("DB_PORT"),
    )
    cur = conn.cursor()

    notedic = {"the_zombie": zombie}
    note = json.dumps(notedic)
    cur.execute(
        "INSERT INTO discord_event (driver, epoch, kind, doer, isPair, note) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;",
        (driver, rightnow(), "REPORTED ZOMBIE", reporter, False, note),
    )
    id_of_added_rows = {"reporter": cur.fetchone()[0]}

    notedic = {"reporter": reporter}
    note = json.dumps(notedic)
    cur.execute(
        "INSERT INTO discord_event (driver, epoch, kind, doer, isPair, note) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;",
        (driver, rightnow(), "BECAME ZOMBIE", zombie, False, note),
    )
    id_of_added_rows.update({"zombie": cur.fetchone()[0]})

    conn.commit()
    cur.close()
    conn.close()
    return id_of_added_rows
