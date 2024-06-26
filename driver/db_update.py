from os import getenv

import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(
    host=getenv("DB_HOST"),
    dbname=getenv("DB_NAME"),
    user=getenv("DB_USER"),
    password=getenv("DB_PASSWORD"),
    port=getenv("DB_PORT"),
)
cur = conn.cursor()
cur.execute(
    "ALTER TABLE brief ADD COLUMN driver VARCHAR(255) DEFAULT '1125764070935638086';"
)
cur.execute(
    "ALTER TABLE discord_event ADD COLUMN driver VARCHAR(255) DEFAULT '1125764070935638086';"
)
cur.execute(
    "ALTER TABLE pending_event ADD COLUMN driver VARCHAR(255) DEFAULT '1125764070935638086';"
)
conn.commit()
cur.close()
conn.close()
