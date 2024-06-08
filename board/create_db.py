from db import PGConnect


def create_db():
    pgc = PGConnect()
    conn = pgc.conn
    cursor = conn.cursor()

    cursor.execute(
        """   CREATE TABLE IF NOT EXISTS dirooz_boards(
                                guild_id BIGINT NOT NULL,
                                channel_id BIGINT NOT NULL,
                                msg_id BIGINT NOT NULL,
                                last_update BIGINT NOT NULL); """
    )

    print("dirooz_boards created @postgres")

    cursor.execute(
        """   CREATE TABLE IF NOT EXISTS inmaah_boards(
                                guild_id BIGINT NOT NULL,
                                channel_id BIGINT NOT NULL,
                                msg_id BIGINT NOT NULL,
                                last_update BIGINT NOT NULL); """
    )

    print("inmaah_boards created @postgres")

    conn.commit()
    cursor.close()
    conn.close()


create_db()
