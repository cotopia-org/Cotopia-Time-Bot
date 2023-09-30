
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import psycopg2

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

CREDENTIALS_FILE = 'gcal/credentials.json'

def get_calendar_service(discord_guild: int, discord_id: int):
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
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=8080, redirect_uri_trailing_slash=False, open_browser=False)

        # Save the credentials for the next run
        cur.execute("UPDATE person SET google_token = %s WHERE discord_guild = %s AND discord_id = %s;",
                     (creds.to_json(), discord_guild, discord_id))

        conn.commit()
        cur.close()
        conn.close()

    service = build('calendar', 'v3', credentials=creds)
    return service

get_calendar_service(10, 11)