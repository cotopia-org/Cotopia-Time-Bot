import sqlite3

conn = sqlite3.connect('thebot.db')

c = conn.cursor()

# c.execute("""CREATE TABLE timelogs (
#                 epoch integer,
#                 user text,
#                 event text
#                 )""")

conn.commit()

conn.close()