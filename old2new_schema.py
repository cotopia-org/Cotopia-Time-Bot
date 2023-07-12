import psycopg2
import json

conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)

cur = conn.cursor()
cur2 = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS discord_event(
            id SERIAL NOT NULL PRIMARY KEY,
            ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            epoch integer null,
            kind varchar(255) null,
            doer varchar(255) null,
            isPair boolean DEFAULT FALSE,
            pairID integer null,
            isValid boolean DEFAULT TRUE,
            note json null
);
""")
            
# cur.execute("""INSERT INTO discord_event (kind, isPair) VALUES ('Hello World', True);
# """)

# username = "m.habibi"
# filename = "m.habibi.txt"
# with open(filename) as file:
#     while line := file.readline():
#         pieces = line.split("   ")

#         epoch = int(pieces[0])
#         kind = str(pieces[1])
#         doer = username
#         if kind == "CHANEL CHANGED":
#             isPair = False
#         else:
#             isPair = True
#         notedic = {"channel": str(pieces[2]).strip()}
#         note = json.dumps(notedic)

#         cur.execute("INSERT INTO discord_event (epoch, kind, doer, isPair, note) VALUES (%s, %s, %s, %s, %s);",
#                     (epoch, kind, doer, isPair, note))

cur.execute("""SELECT COUNT id FROM discord_event WHERE isPair = TRUE AND doer = 'm.habibi' AND kind = 'SESSION STARTED';
""")
cur2.execute("""SELECT COUNT id FROM discord_event WHERE isPair = TRUE AND doer = 'm.habibi' AND kind = 'SESSION ENDED';
""")


print(cur.fetchone())
# for i in cur.fetchall():
#     print(i.index())             

conn.commit()
cur.close()
cur2.close()
conn.close()