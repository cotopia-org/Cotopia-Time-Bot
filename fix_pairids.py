import psycopg2
import asyncio


def get_next_session_end_id(doer: str, row_id: int):
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
    cur = conn.cursor()

    cur.execute("""
                SELECT * FROM discord_event
                WHERE id > %s
                AND doer = %s
                AND kind = 'SESSION ENDED'
                ORDER BY id
                ;""", (row_id, doer))
    
    data = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

    print("get_next_session_end_id: " + str(data[0]))

    return data[0]

def get_next_talking_end_id(doer: str, row_id: int):
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
    cur = conn.cursor()

    cur.execute("""
                SELECT * FROM discord_event
                WHERE id > %s
                AND doer = %s
                AND kind = 'TALKING STOPPED'
                ORDER BY id
                ;""", (row_id, doer))
    
    data = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

    print("get_next_talking_end_id: " + str(data[0]))

    return data[0]

def get_next_pausing_end_id(doer: str, row_id: int):
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
    cur = conn.cursor()

    cur.execute("""
                SELECT * FROM discord_event
                WHERE id > %s
                AND doer = %s
                AND kind = 'SESSION RESUMED'
                ORDER BY id
                ;""", (row_id, doer))
    
    data = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

    print("get_next_pausing_end_id: " + str(data[0]))

    return data[0]

def get_correct_pairid (doer: str, kind: str, row_id: int):

    next_session_end = get_next_session_end_id(doer=doer, row_id=row_id)

    if (kind == "TALKING STARTED"):
        next_talking_end = get_next_talking_end_id(doer=doer, row_id=row_id)
        return min(next_session_end, next_talking_end)
    elif (kind == "SESSION PAUSED"):
        next_pausing_end = get_next_pausing_end_id(doer=doer, row_id=row_id)
        return min(next_pausing_end, next_session_end)
    else:
        return -1

def fix_pairid(doer: str, kind: str, row_id: int):

    correct_pairid = get_correct_pairid(doer=doer, kind=kind, row_id=row_id)
    print("correct_pairid: " + str(correct_pairid))

    print(f"fixing row {row_id} where doer is {doer} and kind is {kind}")

    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
    cur = conn.cursor()

    cur.execute("UPDATE discord_event SET pairid = %s WHERE id = %s", (correct_pairid, row_id))

    conn.commit()
    cur.close()
    conn.close()

def get_talking_starts(doer: str):
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
    cur = conn.cursor()

    cur.execute("""
                SELECT * FROM discord_event
                WHERE doer = %s
                AND kind = 'TALKING STARTED'
                ORDER BY id
                ;""", [doer])
    
    data = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return data

def get_pausing_starts(doer: str):
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
    cur = conn.cursor()

    cur.execute("""
                SELECT * FROM discord_event
                WHERE doer = %s
                AND kind = 'SESSION PAUSED'
                ORDER BY id
                ;""", [doer])
    
    data = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return data

async def main(doer: str):

    for line in get_pausing_starts(doer=doer):
        print("_________________________________________________")
        print(line)
        print("_________________________________________________")
        fix_pairid(doer=line[4], kind=line[3], row_id=line[0])


    for row in get_talking_starts(doer=doer):
        print("_________________________________________________")
        print(row)
        print("_________________________________________________")
        fix_pairid(doer=row[4], kind=row[3], row_id=row[0])
    
# asyncio.run(main("kharrati"))
# asyncio.run(main("armanhr"))
# asyncio.run(main("mahdirasti#3738"))
# asyncio.run(main("m.habibi"))
# asyncio.run(main("ajabimahdi"))
# asyncio.run(main("navid.madadi"))
# asyncio.run(main("imebneali"))
# asyncio.run(main("mamreez_tn#5785"))