import psycopg2

conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
cur = conn.cursor()

cur.execute("""
                SELECT * From discord_event
                WHERE epoch > 1689702404
                ORDER BY id
                """)

data = cur.fetchall()

for row in data:
    print(row)
