from os import getenv

import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(
    host=getenv("DB_HOST"),
    dbname=getenv("DB_NAME"),
    user=getenv("DB_USER"),
    password=getenv("DB_PASSWORD"),
    port=getenv("DB_PORT"),
)
cur = conn.cursor()
# cur.execute("""CREATE TABLE IF NOT EXISTS person(
#             id SERIAL NOT NULL PRIMARY KEY,
#             created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
#             discord_guild BIGINT NULL,
#             discord_id BIGINT NULL,
#             discord_name VARCHAR(255) NULL,
#             email VARCHAR(63) NULL,
#             trc20_addr VARCHAR(127) NULL,
#             active BOOLEAN DEFAULT TRUE,
#             google_token json NULL,
#             note json NULL
#             );""")
# cur.execute("ALTER TABLE person ADD COLUMN discord_avatar VARCHAR(255) NULL;")
cur.execute(
    "ALTER TABLE person ADD COLUMN timezone VARCHAR(255) DEFAULT 'Asia/Tehran';"
)
cur.execute("ALTER TABLE person ADD COLUMN cal_system VARCHAR(255) DEFAULT 'Jalali';")
conn.commit()
cur.close()
conn.close()
