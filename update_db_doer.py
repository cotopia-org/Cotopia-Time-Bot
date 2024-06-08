from db import PGConnect

users = {}
pgc = PGConnect()
conn = pgc.conn
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
