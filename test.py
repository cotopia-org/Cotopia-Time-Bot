import psycopg2

conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
cur = conn.cursor()

cur.execute("UPDATE discord_event SET pairid = 556 WHERE id = 555")

conn.commit()
cur.close()
conn.close()