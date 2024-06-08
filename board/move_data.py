# copy data from sqlite tables to postgres tables

import sqlite3

from db import PGConnect

tables = ["dirooz_boards", "inmaah_boards"]


def copy_to_postgres(table_name: str):
    conn = sqlite3.connect("timeboards.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    data = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()

    pgc = PGConnect()
    conn = pgc.conn
    cursor = conn.cursor()

    for i in data:
        cursor.execute(f"INSERT INTO {table_name} VALUES{i}")

    conn.commit()
    cursor.close()
    conn.close()


for each in tables:
    copy_to_postgres(each)
