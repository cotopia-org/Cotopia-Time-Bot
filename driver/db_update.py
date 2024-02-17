import psycopg2

conn = psycopg2.connect(
    host="localhost",
    dbname="postgres",
    user="postgres",
    password="Tp\ZS?gfLr|]'a",
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
