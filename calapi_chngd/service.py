import google.oauth2.credentials
from apiclient.discovery import build

class Service():

    def __init__(self, session_credentials):
        self.session_credentials = session_credentials
        self.service = None
        if session_credentials:
            credentials = google.oauth2.credentials.Credentials(
                **session_credentials)
            self.service = build(
                                'calendar', 'v3', credentials=credentials)
