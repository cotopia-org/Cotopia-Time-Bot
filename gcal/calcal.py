
from urllib.parse import quote


client = Oauth(
    credentials_path='gcal/credentials.json',
    scopes=['https://www.googleapis.com/auth/calendar'],
    redirect_uri='http://127.0.0.1:8000/goauth'
)



def gen_GOAuth_URL():
    oauth_consent_url = client.get_authorization_url()
    return quote(oauth_consent_url)

def gen_user_creds(code: str, state: str):
    session_credentials = client.on_auth_callback(code=code, state=state)
    return session_credentials

def store_user_creds():
    pass

def get_user_creds_from_db():
    pass

session_credentials=gen_user_creds(code="4/0AfJohXlBmxon7ofW7_xez-PJvjvrrX6yFYQ0G7KP-ogshQo8Yq__HO7ssxBsRETV6J2zmw", state="wzaqsanpu67rQssf9pYF7Oc7wz2h7i")
print(session_credentials)
session = Session(session_credentials=session_credentials)
print(session)

events_list = session.events.list()
print(events_list)

