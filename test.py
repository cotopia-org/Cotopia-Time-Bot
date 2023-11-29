import psycopg2


def get_pendings(driver: str, doer: str):
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
    cur = conn.cursor()

    cur.execute(f"SELECT * FROM pending_event WHERE driver = '{driver}' AND doer = '{doer}'")
    current_pendings = cur.fetchall()

    conn.commit()
    cur.close()
    conn.close()

    result = []
    if (current_pendings == None):
        return result
    else:
        for i in current_pendings:
            result.append(i[3])
        return result



# print(get_pendings(driver="1125764070935638086", doer="kharrati"))

print("SESSION STARTED" in get_pendings(driver="1125764070935638086", doer="kharrati"))