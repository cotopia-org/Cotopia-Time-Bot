from db import PGConnect

pgc = PGConnect()
conn = pgc.conn
cur = conn.cursor()
cur.execute("SELECT id, discord_id, discord_name FROM person;")
users = cur.fetchall()

for i in users:
    print(i)

conn.commit()
cur.close()
conn.close()