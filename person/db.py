from psycopg2.extensions import cursor
import psycopg2

class Person():

    # checks database, if person exists, just returns the id
    # if not, adds and returns the id
    def add_person(discord_guild: int, discord_id: int):
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
            conn.commit()
            cur.close()
            conn.close()
            return result[0]
        else:
            cur.execute("INSERT INTO person (discord_guild, discord_id) VALUES (%s, %s) RETURNING id;",
                        (discord_guild, discord_id))
            result = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()
            return result[0]


    def get_person(cur: cursor, discord_guild: int, discord_id: int):
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


    def get_email(cur: cursor, discord_guild: int, discord_id: int):
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


    def get_trc20_addr(cur: cursor, discord_guild: int, discord_id: int):
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

