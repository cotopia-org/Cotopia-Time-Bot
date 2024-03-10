import psycopg2

conn = psycopg2.connect(
    host="localhost",
    dbname="discord_bot_db",
    user="cotopia",
    password="123123",
    port=5432,
)
cur = conn.cursor()
