import psycopg2

conn = psycopg2.connect(
    host="localhost",
    dbname="discord_bot_db",
    user="cotopia",
    password="123123",
    port=5432,
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
cur.execute("ALTER TABLE person ADD COLUMN discord_avatar VARCHAR(255) NULL;")
conn.commit()
cur.close()
conn.close()
