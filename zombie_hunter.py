import json
import time

from db import PGConnect


# returns epoch of NOW: int
def rightnow():
    epoch = int(time.time())
    return epoch


# 🚗
def record_hunt(driver: str, reporter: str, zombie: str):

    pgc = PGConnect()
    conn = pgc.conn
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
