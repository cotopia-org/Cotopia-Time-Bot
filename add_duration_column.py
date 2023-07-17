import psycopg2


async def main():
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
    cur = conn.cursor()

    cur.execute("ALTER TABLE discord_event ADD COLUMN IF NOT EXISTS duration INTEGER Default -1;")

    

    conn.commit()
    cur.close()
    conn.close()