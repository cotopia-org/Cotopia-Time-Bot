from db import PGConnect

pgc = PGConnect()
conn = pgc.conn
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
