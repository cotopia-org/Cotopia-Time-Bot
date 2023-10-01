
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from urllib.parse import quote



# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

CREDENTIALS_FILE = 'gcal/credentials.json'

def get_calendar_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('gcal/token.json'):
        creds = Credentials.from_authorized_user_file('gcal/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = Flow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES, redirect_uri='http://127.0.0.1:8000/goauth')
            # creds = flow.run_local_server(port=3010, redirect_uri_trailing_slash=False, open_browser=False)
            url = flow.authorization_url()
            print(url[0])
            print(quote(url[0]))
        # Save the credentials for the next run
    #     with open('gcal/token.json', 'w') as token:
    #         token.write(creds.to_json())

    # service = build('calendar', 'v3', credentials=creds)
    return url

def get_token():
    flow = Flow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES, redirect_uri='http://127.0.0.1:8000/goauth')
    code = "4/0AfJohXnmwQ0NBmI2-qCLiF72aDYAxaOpZXGRp1Pe-lIVBIELkZaqjk5OU_pubYi9zI0cSw"
    token = flow.fetch_token(code=code)
    return token

# print(get_token())

get_calendar_service()