#
#
#
# This should be run manually, for updating the old database




import psycopg2
import asyncio


async def main():
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
    cur = conn.cursor()

    cur.execute("ALTER TABLE discord_event ADD COLUMN IF NOT EXISTS duration INTEGER Default -1;")

    cur.execute("""
                SELECT * From discord_event
                WHERE pairid IS NOT NULL
                AND kind = ANY(ARRAY['SESSION STARTED', 'TALKING STARTED', 'SESSION PAUSED'])
                ORDER BY id
                """)
    all_rows = cur.fetchall()

    for start in all_rows:
        cur.execute("SELECT * From discord_event WHERE id = %s;", [start[6]])
        end = cur.fetchone()
        duration = end[2] - start[2]
        print(str(start[0]) + " -------> " + str(start[2]) + "||" + str(end[2]) + "||" + str(duration))
        cur.execute("UPDATE discord_event SET duration = %s WHERE id = %s", (duration, start[0]))

    conn.commit()
    cur.close()
    conn.close()


asyncio.run(main())