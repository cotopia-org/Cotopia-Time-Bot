import psycopg2

conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
cur = conn.cursor()

cur.execute("""
                SELECT id, epoch, kind, doer, ispair, pairid, duration FROM discord_event
                WHERE kind = ANY(ARRAY['SESSION PAUSED', 'SESSION RESUMED'])
                ORDER BY id
                """)

data = cur.fetchall()

for row in data:
    print(row)
