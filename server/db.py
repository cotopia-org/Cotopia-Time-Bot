import psycopg2
from datetime import datetime


class Server():

    def setter(self, guild_id: int, unavailable: bool, banner: str,
               icon: str, created_at: datetime, name: str,
               description: str, member_count: int, owner_name: str,
               preferred_locale: str, note: str | None = None):
        
        conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                            password="Tp\ZS?gfLr|]'a", port=5432)
        cur = conn.cursor()
        cur.execute(f"SELECT id FROM server WHERE discord_guild_id = {guild_id};")
        result = cur.fetchone()
        if result:
            # server already exists
            print("server already exists")
            cur.execute("""
                        UPDATE server SET discord_unavailable = %s,
                        discord_banner = %s,
                        discord_icon = %s,
                        discord_created_at = %s,
                        discord_name = %s,
                        discord_description = %s,
                        discord_member_count = %s,
                        discord_owner_name = %s,
                        discord_preferred_locale = %s,
                        note = %s
                        WHERE id = %s;""",
                        (unavailable, banner, icon, created_at, name, description,
                         member_count, owner_name, preferred_locale, note, result[0]))
            conn.commit()
            cur.close()
            conn.close()
            return result[0]
        else:
            print("Adding new server to db")
            cur.execute("""
                        INSERT INTO server
                        (discord_guild_id, discord_unavailable, discord_banner,
                        discord_icon, discord_created_at, discord_name,
                        discord_description, discord_member_count, discord_owner_name,
                        discord_preferred_locale, note)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                        ;""",
                        (guild_id, unavailable, banner, icon, created_at, name, description,
                         member_count, owner_name, preferred_locale, note))
            result = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()
            return result[0]
            


    def getter(self, guild_id: str):
        pass