import psycopg2

def add_pairid_to_db(start: int, stop: int):
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
    cur = conn.cursor()
#     cur.execute("UPDATE discord_event SET pairid = %s WHERE id = %s;", (start, stop))
#     cur.execute("UPDATE discord_event SET pairid = %s WHERE id = %s;", (stop, start))

    cur.execute("SELECT epoch From discord_event WHERE id = ANY(ARRAY[%s, %s]) ORDER BY id;", (start, stop))
    epochs = cur.fetchall()

    print (epochs)

    duration = epochs[1][0] - epochs[0][0]
    print (duration)
#     cur.execute("UPDATE discord_event SET duration = %s WHERE id = %s", (duration, start))
#     cur.execute("UPDATE discord_event SET duration = %s WHERE id = %s", (duration, start))

    conn.commit()
    cur.close()
    conn.close()



add_pairid_to_db(186, 187)