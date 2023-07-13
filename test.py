import psycopg2
import json

conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)

cur = conn.cursor()
cur.execute("SELECT * FROM pending_event")
pendings = cur.fetchall()
for row in pendings:
    print(row)

print("------------------------------------------")

cur.execute("SELECT * FROM discord_event")
main = cur.fetchall()
for row in main:
    print(main)


conn.commit()
cur.close()
conn.close()

