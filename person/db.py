from os import getenv

import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import cursor

from server import Server


class Person:

    # checks database, if person exists, just returns the id
    # if not, adds and returns the id
    def add_person(
        self,
        discord_guild: int,
        discord_id: int,
        discord_name: str,
        discord_avatar: str | None = None,
    ):
        load_dotenv()
        conn = psycopg2.connect(
            host=getenv("DB_HOST"),
            dbname=getenv("DB_NAME"),
            user=getenv("DB_USER"),
            password=getenv("DB_PASSWORD"),
            port=getenv("DB_PORT"),
        )
        cur = conn.cursor()
        cur.execute(
            """
                    SELECT id FROM person
                    WHERE discord_guild = %s
                    AND discord_id = %s
                    ;""",
            (discord_guild, discord_id),
        )
        result = cur.fetchone()
        if result:
            # person already exists
            print("person already exists")
            cur.execute(
                "UPDATE person SET discord_name = %s, discord_avatar =%s  WHERE id = %s;",
                (discord_name, discord_avatar, result[0]),
            )
            conn.commit()
            cur.close()
            conn.close()
            return result[0]
        else:
            cur.execute(
                """
                        INSERT INTO person (discord_guild, discord_id, discord_name, discord_avatar)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id
                        ;""",
                (discord_guild, discord_id, discord_name, discord_avatar),
            )
            result = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()
            return result[0]

    def get_person(self, cur: cursor, discord_guild: int, discord_id: int):
        cur.execute(
            """
                    SELECT id FROM person
                    WHERE discord_guild = %s
                    AND discord_id = %s
                    ;""",
            (discord_guild, discord_id),
        )
        result = cur.fetchone()
        if result is None:
            return None
        else:
            return result[0]

    def get_email(self, cur: cursor, discord_guild: int, discord_id: int):
        cur.execute(
            """
                    SELECT email FROM person
                    WHERE discord_guild = %s
                    AND discord_id = %s
                    ;""",
            (discord_guild, discord_id),
        )

        result = cur.fetchone()
        if result is None:
            return None
        else:
            return result[0]

    def get_trc20_addr(self, cur: cursor, discord_guild: int, discord_id: int):
        cur.execute(
            """
                    SELECT trc20_addr FROM person
                    WHERE discord_guild = %s
                    AND discord_id = %s
                    ;""",
            (discord_guild, discord_id),
        )

        result = cur.fetchone()
        if result is None:
            return None
        else:
            return result[0]

    def set_email(
        self, cur: cursor, discord_guild: int, discord_id: int, name: str, email: str
    ):
        person_id = self.get_person(cur, discord_guild, discord_id)
        if person_id is None:
            cur.execute(
                "INSERT INTO person (discord_guild, discord_id, discord_name, email) VALUES (%s, %s, %s, %s);",
                (discord_guild, discord_id, name, email),
            )
        else:
            cur.execute(
                "UPDATE person SET email = %s WHERE id = %s;", (email, person_id)
            )

    def set_trc20_addr(
        self, cur: cursor, discord_guild: int, discord_id: int, name: str, addr: str
    ):
        person_id = self.get_person(cur, discord_guild, discord_id)
        if person_id is None:
            cur.execute(
                "INSERT INTO person (discord_guild, discord_id, discord_name, trc20_addr) VALUES (%s, %s, %s, %s);",
                (discord_guild, discord_id, name, addr),
            )
        else:
            cur.execute(
                "UPDATE person SET trc20_addr = %s WHERE id = %s;", (addr, person_id)
            )

    def set_google_token(self, person_id: int, creds_json: str):
        load_dotenv()
        conn = psycopg2.connect(
            host=getenv("DB_HOST"),
            dbname=getenv("DB_NAME"),
            user=getenv("DB_USER"),
            password=getenv("DB_PASSWORD"),
            port=getenv("DB_PORT"),
        )
        cur = conn.cursor()
        cur.execute(
            "UPDATE person SET google_token = %s WHERE id = %s;",
            (creds_json, person_id),
        )
        conn.commit()
        cur.close()
        conn.close()

    def get_google_token(self, discord_guild: int, discord_id: int):
        load_dotenv()
        conn = psycopg2.connect(
            host=getenv("DB_HOST"),
            dbname=getenv("DB_NAME"),
            user=getenv("DB_USER"),
            password=getenv("DB_PASSWORD"),
            port=getenv("DB_PORT"),
        )
        cur = conn.cursor()
        cur.execute(
            """
                    SELECT google_token FROM person
                    WHERE discord_guild = %s
                    AND discord_id = %s
                    ;""",
            (discord_guild, discord_id),
        )
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if result is None:
            return None
        else:
            return result[0]

    def list_of_tokeners(self, discord_guild: int):
        load_dotenv()
        conn = psycopg2.connect(
            host=getenv("DB_HOST"),
            dbname=getenv("DB_NAME"),
            user=getenv("DB_USER"),
            password=getenv("DB_PASSWORD"),
            port=getenv("DB_PORT"),
        )
        cur = conn.cursor()
        cur.execute(
            "SELECT discord_id FROM person WHERE discord_guild = %s AND google_token IS NOT NULL;",
            [discord_guild],
        )
        fetch = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        result = []
        for f in fetch:
            result.append(f[0])
        return result

    def set_cal(self, discord_guild: int, discord_id: int, cal: str):
        load_dotenv()
        conn = psycopg2.connect(
            host=getenv("DB_HOST"),
            dbname=getenv("DB_NAME"),
            user=getenv("DB_USER"),
            password=getenv("DB_PASSWORD"),
            port=getenv("DB_PORT"),
        )
        cur = conn.cursor()
        cur.execute(
            "UPDATE person SET calendar = %s WHERE discord_guild = %s AND discord_id = %s;",
            (cal, discord_guild, discord_id),
        )
        conn.commit()
        cur.close()
        conn.close()

    def get_cal(self, discord_guild: int, discord_id: int):
        load_dotenv()
        conn = psycopg2.connect(
            host=getenv("DB_HOST"),
            dbname=getenv("DB_NAME"),
            user=getenv("DB_USER"),
            password=getenv("DB_PASSWORD"),
            port=getenv("DB_PORT"),
        )
        cur = conn.cursor()
        cur.execute(
            """
                    SELECT calendar FROM person
                    WHERE discord_guild = %s
                    AND discord_id = %s
                    ;""",
            (discord_guild, discord_id),
        )
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if result is None:
            return None
        else:
            return result[0]

    def get_cal_by_name(self, discord_guild: int, discord_name: str):
        load_dotenv()
        conn = psycopg2.connect(
            host=getenv("DB_HOST"),
            dbname=getenv("DB_NAME"),
            user=getenv("DB_USER"),
            password=getenv("DB_PASSWORD"),
            port=getenv("DB_PORT"),
        )
        cur = conn.cursor()
        cur.execute(
            """
                    SELECT calendar FROM person
                    WHERE discord_guild = %s
                    AND discord_name = %s
                    ;""",
            (discord_guild, discord_name),
        )
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if result is None:
            return None
        else:
            return result[0]

    def set_avatar(self, discord_guild: int, discord_id: int, avatar: str, name: str):
        load_dotenv()
        conn = psycopg2.connect(
            host=getenv("DB_HOST"),
            dbname=getenv("DB_NAME"),
            user=getenv("DB_USER"),
            password=getenv("DB_PASSWORD"),
            port=getenv("DB_PORT"),
        )
        cur = conn.cursor()
        cur.execute(
            "UPDATE person SET discord_avatar = %s, discord_name = %s WHERE discord_guild = %s AND discord_id = %s;",
            (avatar, name, discord_guild, discord_id),
        )
        conn.commit()
        cur.close()
        conn.close()

    def get_person_info(self, discord_guild: int, discord_name: str):
        load_dotenv()
        conn = psycopg2.connect(
            host=getenv("DB_HOST"),
            dbname=getenv("DB_NAME"),
            user=getenv("DB_USER"),
            password=getenv("DB_PASSWORD"),
            port=getenv("DB_PORT"),
        )
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM person WHERE discord_guild = %s AND discord_name = %s",
            (discord_guild, discord_name),
        )
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        if result is None:
            return None

        info = {}
        info["id"] = result[0]
        info["active"] = result[7]
        info["created_at"] = result[1]
        info["discord_guild"] = str(result[2])
        info["discord_id"] = str(result[3])
        info["discord_name"] = result[4]
        info["email"] = result[5]
        info["trc20_addr"] = result[6]
        if result[8] is None:
            info["has_google_token"] = False
        else:
            info["has_google_token"] = True
        if result[9] is None:
            info["has_calendar"] = False
        else:
            info["has_calendar"] = True
        info["discord_avatar"] = result[10]
        info["timezone"] = result[11]
        info["calendar_system"] = result[12]

        return info

    def get_person_info_by_id(self, discord_guild: int, discord_id: int):
        load_dotenv()
        conn = psycopg2.connect(
            host=getenv("DB_HOST"),
            dbname=getenv("DB_NAME"),
            user=getenv("DB_USER"),
            password=getenv("DB_PASSWORD"),
            port=getenv("DB_PORT"),
        )
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM person WHERE discord_guild = %s AND discord_id = %s",
            (discord_guild, discord_id),
        )
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        if result is None:
            return None

        server = Server()
        try:
            server_info = server.getter(guild_id=str(result[2]))
        except:  # noqa: E722
            server_info = {}
            server_info["discord_name"] = "N/A"
            server_info["discord_icon"] = "N/A"

        info = {}
        info["id"] = result[0]
        info["active"] = result[7]
        info["created_at"] = result[1]
        info["discord_guild"] = str(result[2])
        info["guild_name"] = server_info["discord_name"]
        info["guild_icon"] = server_info["discord_icon"]
        info["discord_id"] = str(result[3])
        info["discord_name"] = result[4]
        info["email"] = result[5]
        info["trc20_addr"] = result[6]
        if result[8] is None:
            info["has_google_token"] = False
        else:
            info["has_google_token"] = True
        if result[9] is None:
            info["has_calendar"] = False
        else:
            info["has_calendar"] = True
        info["discord_avatar"] = result[10]
        info["timezone"] = result[11]
        info["calendar_system"] = result[12]

        return info

    def set_timezone(self, discord_guild: int, discord_id: int, timezone: str):
        load_dotenv()
        conn = psycopg2.connect(
            host=getenv("DB_HOST"),
            dbname=getenv("DB_NAME"),
            user=getenv("DB_USER"),
            password=getenv("DB_PASSWORD"),
            port=getenv("DB_PORT"),
        )
        cur = conn.cursor()
        cur.execute(
            "UPDATE person SET timezone = %s WHERE discord_guild = %s AND discord_id = %s;",
            (timezone, discord_guild, discord_id),
        )
        conn.commit()
        cur.close()
        conn.close()

    def get_timezone(self, discord_guild: int, discord_id: int):
        load_dotenv()
        conn = psycopg2.connect(
            host=getenv("DB_HOST"),
            dbname=getenv("DB_NAME"),
            user=getenv("DB_USER"),
            password=getenv("DB_PASSWORD"),
            port=getenv("DB_PORT"),
        )
        cur = conn.cursor()
        cur.execute(
            """
                    SELECT timezone FROM person
                    WHERE discord_guild = %s
                    AND discord_id = %s
                    ;""",
            (discord_guild, discord_id),
        )
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if result is None:
            return "Asia/Tehran"
        else:
            return result[0]

    def set_cal_system(self, discord_guild: int, discord_id: int, cal_system: str):
        load_dotenv()
        conn = psycopg2.connect(
            host=getenv("DB_HOST"),
            dbname=getenv("DB_NAME"),
            user=getenv("DB_USER"),
            password=getenv("DB_PASSWORD"),
            port=getenv("DB_PORT"),
        )
        cur = conn.cursor()
        cur.execute(
            "UPDATE person SET cal_system = %s WHERE discord_guild = %s AND discord_id = %s;",
            (cal_system, discord_guild, discord_id),
        )
        conn.commit()
        cur.close()
        conn.close()

    def get_cal_system(self, discord_guild: int, discord_id: int):
        load_dotenv()
        conn = psycopg2.connect(
            host=getenv("DB_HOST"),
            dbname=getenv("DB_NAME"),
            user=getenv("DB_USER"),
            password=getenv("DB_PASSWORD"),
            port=getenv("DB_PORT"),
        )
        cur = conn.cursor()
        cur.execute(
            """
                    SELECT cal_system FROM person
                    WHERE discord_guild = %s
                    AND discord_id = %s
                    ;""",
            (discord_guild, discord_id),
        )
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if result is None:
            return "Jalali"
        else:
            return result[0]

    def get_locale(self, discord_guild: int, discord_id: int):
        person_locale = {}
        person_locale["timezone"] = "Asia/Tehran"
        person_locale["cal_system"] = "Jalali"
        load_dotenv()
        conn = psycopg2.connect(
            host=getenv("DB_HOST"),
            dbname=getenv("DB_NAME"),
            user=getenv("DB_USER"),
            password=getenv("DB_PASSWORD"),
            port=getenv("DB_PORT"),
        )
        cur = conn.cursor()
        cur.execute(
            """
                    SELECT timezone, cal_system FROM person
                    WHERE discord_guild = %s
                    AND discord_id = %s
                    ;""",
            (discord_guild, discord_id),
        )
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if result is None:
            return person_locale
        else:
            person_locale["timezone"] = result[0]
            person_locale["cal_system"] = result[1]
            return person_locale
