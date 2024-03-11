import psycopg2

conn = psycopg2.connect(
    host="localhost",
    dbname="postgres",
    user="postgres",
    password="Tp\ZS?gfLr|]'a",
    port=5432,
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
