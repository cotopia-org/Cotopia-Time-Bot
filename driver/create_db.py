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
cur.execute(
    """CREATE TABLE IF NOT EXISTS driver(
            id SERIAL NOT NULL PRIMARY KEY,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            discord_guild BIGINT NULL,
            discord_owner_id BIGINT NULL,
            discord_owner_name VARCHAR(255) NULL,
            locale json NULL,
            email VARCHAR(63) NULL,
            active BOOLEAN DEFAULT TRUE,
            note json NULL
            );"""
)
conn.commit()
cur.close()
conn.close()
