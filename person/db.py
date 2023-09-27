from psycopg2.extensions import cursor
import psycopg2


# def already_exists(cur: cursor, discord_guild: int, discord_id: int):
#     cur.execute("""
#                 SELECT id FROM person
#                 WHERE discord_guild = %s
#                 AND discord_id = %s
#                 ;"""
#                 , (discord_guild, discord_id))
    
#     return cur.fetchone()

# def add_person(cur: cursor, discord_guild: int, discord_id: int):
#     return

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

def set_email(cur: cursor, discord_guild: int, discord_id: int, name: str, email: str):
    person_id = get_person(cur, discord_guild, discord_id)
    if (person_id == None):
        cur.execute("INSERT INTO person (discord_guild, discord_id, discord_name, email) VALUES (%s, %s, %s, %s);",
                 (discord_guild, discord_id, name, email))
    else:
        cur.execute("UPDATE person SET email = %s WHERE id = %s;", (email, person_id))

def set_trc20_addr(cur: cursor, discord_guild: int, discord_id: int, name: str, addr: str):
    person_id = get_person(cur, discord_guild, discord_id)
    if (person_id == None):
        cur.execute("INSERT INTO person (discord_guild, discord_id, discord_name, trc20_addr) VALUES (%s, %s, %s, %s);",
                 (discord_guild, discord_id, name, addr))
    else:
        cur.execute("UPDATE person SET trc20_addr = %s WHERE id = %s;", (addr, person_id))