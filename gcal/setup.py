from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import psycopg2

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

CREDENTIALS_FILE = 'gcal/credentials.json'

THE_FLOW = Flow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES, redirect_uri='http://127.0.0.1:8000/goauth')


def get_calendar_service(discord_guild: int, discord_id: int, the_code: str):
    creds = None
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
    cur = conn.cursor()
    cur.execute("SELECT google_token FROM person WHERE discord_guild = %s AND discord_id = %s;",
                 (discord_guild, discord_id))
    try:
        result = cur.fetchone()[0]
    except:
        result = None


    if (result != None):
        creds = Credentials.from_authorized_user_info(result, SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            creds = Credentials.from_authorized_user_info(get_token(code=the_code), SCOPES)

        # Save the credentials for the next run
        cur.execute("UPDATE person SET google_token = %s WHERE discord_guild = %s AND discord_id = %s;",
                     (creds.to_json(), discord_guild, discord_id))

        conn.commit()
        cur.close()
        conn.close()

    service = build('calendar', 'v3', credentials=creds)
    return service


def get_token(code: str):
    token = THE_FLOW.fetch_token(code=code)
    return token