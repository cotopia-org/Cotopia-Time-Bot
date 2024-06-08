import psycopg2
from os import getenv

from dotenv import load_dotenv

class PGConnect():
    load_dotenv()
    conn = psycopg2.connect(
    host=getenv('DB_HOST'),
    dbname=getenv('DB_NAME'),
    user=getenv('DB_USER'),
    password=getenv('DB_PASSWORD'),
    port=getenv('DB_PORT'),
)