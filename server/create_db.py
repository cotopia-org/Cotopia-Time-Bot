import psycopg2


conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS server(
            id SERIAL NOT NULL PRIMARY KEY,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            discord_guild_id BIGINT NULL,
            discord_unavailable BOOLEAN DEFAULT FALSE,
            active BOOLEAN DEFAULT TRUE,
            discord_banner VARCHAR(255) NULL,
            discord_icon VARCHAR(255) NULL,
            discord_created_at TIMESTAMPTZ DEFAULT NULL,
            discord_name VARCHAR(255) NULL,
            discord_description VARCHAR(255) NULL,
            discord_member_count INT NULL,
            discord_owner_name VARCHAR(127) NULL,
            discord_preferred_locale VARCHAR(63) NULL,
            note json NULL
            );""")
conn.commit()
cur.close()
conn.close()
