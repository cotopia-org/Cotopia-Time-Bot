from psycopg2.extensions import cursor
import psycopg2

class Person():

    # checks database, if person exists, just returns the id
    # if not, adds and returns the id
    def add_person(self, discord_guild: int, discord_id: int, discord_name: str):
        conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                            password="Tp\ZS?gfLr|]'a", port=5432)
        cur = conn.cursor()
        cur.execute("""
                    SELECT id FROM person
                    WHERE discord_guild = %s
                    AND discord_id = %s
                    ;"""
                    , (discord_guild, discord_id))
        result = cur.fetchone()
        if result:
            # person already exists
            print("person already exists")
            cur.execute("UPDATE person SET discord_name = %s WHERE id = %s;", (discord_name, result[0]))
            conn.commit()
            cur.close()
            conn.close()
            return result[0]
        else:
            cur.execute("INSERT INTO person (discord_guild, discord_id, discord_name) VALUES (%s, %s, %s) RETURNING id;",
                        (discord_guild, discord_id, discord_name))
            result = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()
            return result[0]


    def get_person(self, cur: cursor, discord_guild: int, discord_id: int):
        cur.execute("""
                    SELECT id FROM person
                    WHERE discord_guild = %s
                    AND discord_id = %s
                    ;"""
                    , (discord_guild, discord_id))
        result = cur.fetchone()
        if(result == None):
            return None
        else:
            return result[0]


    def get_email(self, cur: cursor, discord_guild: int, discord_id: int):
        cur.execute("""
                    SELECT email FROM person
                    WHERE discord_guild = %s
                    AND discord_id = %s
                    ;"""
                    , (discord_guild, discord_id))
        
        result = cur.fetchone()
        if(result == None):
            return None
        else:
            return result[0]


    def get_trc20_addr(self, cur: cursor, discord_guild: int, discord_id: int):
        cur.execute("""
                    SELECT trc20_addr FROM person
                    WHERE discord_guild = %s
                    AND discord_id = %s
                    ;"""
                    , (discord_guild, discord_id))
        
        result = cur.fetchone()
        if(result == None):
            return None
        else:
            return result[0]


    def set_email(self, cur: cursor, discord_guild: int, discord_id: int, name: str, email: str):
        person_id = self.get_person(cur, discord_guild, discord_id)
        if (person_id == None):
            cur.execute("INSERT INTO person (discord_guild, discord_id, discord_name, email) VALUES (%s, %s, %s, %s);",
                    (discord_guild, discord_id, name, email))
        else:
            cur.execute("UPDATE person SET email = %s WHERE id = %s;", (email, person_id))


    def set_trc20_addr(self, cur: cursor, discord_guild: int, discord_id: int, name: str, addr: str):
        person_id = self.get_person(cur, discord_guild, discord_id)
        if (person_id == None):
            cur.execute("INSERT INTO person (discord_guild, discord_id, discord_name, trc20_addr) VALUES (%s, %s, %s, %s);",
                    (discord_guild, discord_id, name, addr))
        else:
            cur.execute("UPDATE person SET trc20_addr = %s WHERE id = %s;", (addr, person_id))
    

    def set_google_token(self, person_id: int, creds_json: str):
        conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                            password="Tp\ZS?gfLr|]'a", port=5432)
        cur = conn.cursor()
        cur.execute("UPDATE person SET google_token = %s WHERE id = %s;", (creds_json, person_id))
        conn.commit()
        cur.close()
        conn.close()


    def list_of_tokeners(self, discord_guild: int):
        conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                            password="Tp\ZS?gfLr|]'a", port=5432)
        cur = conn.cursor()
        cur.execute("SELECT discord_id FROM person WHERE discord_guild = %s AND google_token IS NOT NULL;",
                    [discord_guild])
        fetch = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        result = []
        for f in fetch:
            result.append(f[0])
        return result
    

    def set_cal(self, discord_guild: int, discord_id: int, cal: str):
        conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                            password="Tp\ZS?gfLr|]'a", port=5432)
        cur = conn.cursor()
        cur.execute("UPDATE person SET calendar = %s WHERE discord_guild = %s AND discord_id = %s;",
                    (cal, discord_guild, discord_id))
        conn.commit()
        cur.close()
        conn.close()


    def get_cal(sel, discord_guild: int, discord_id: int):
        conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                            password="Tp\ZS?gfLr|]'a", port=5432)
        cur = conn.cursor()
        cur.execute("""
                    SELECT calendar FROM person
                    WHERE discord_guild = %s
                    AND discord_id = %s
                    ;"""
                    , (discord_guild, discord_id))
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if(result == None):
            return None
        else:
            return result[0]
