import psycopg2

conn = psycopg2.connect(
    host="localhost",
    dbname="discord_bot_db",
    user="cotopia",
    password="123123",
    port=5432,
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
