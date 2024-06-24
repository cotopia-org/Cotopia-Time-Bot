from os import getenv

import psycopg2
from dotenv import load_dotenv

users = {}

load_dotenv()
conn = psycopg2.connect(
    host=getenv("DB_HOST"),
    dbname=getenv("DB_NAME"),
    user=getenv("DB_USER"),
    password=getenv("DB_PASSWORD"),
    port=getenv("DB_PORT"),
)
cur = conn.cursor()
cur.execute("SELECT id, discord_id, discord_name FROM person;")
users = cur.fetchall()


for i in users:
    cur.execute("UPDATE brief SET doer = %s WHERE doer = %s", (str(i[1]), i[2]))
    cur.execute("UPDATE discord_event SET doer = %s WHERE doer = %s", (str(i[1]), i[2]))
    cur.execute("UPDATE pending_event SET doer = %s WHERE doer = %s", (str(i[1]), i[2]))


conn.commit()
cur.close()
conn.close()
