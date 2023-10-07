from urllib.parse import quote
from . import calapi_chngd as api

import sys
sys.path.append("..")
from person import Person

import json
import psycopg2



client = api.Oauth(
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


def store_user_creds(discord_guild: int, discord_id: int, code: str, state: str):
    the_person = Person()
    person_id = the_person.add_person(discord_guild, discord_id)
    creds = gen_user_creds(code, state)
    creds_json = json.dumps(creds)
    the_person.set_google_token(person_id, creds_json)
    return creds_json


def get_user_creds(discord_guild: int, discord_id: int, code: str, state: str):
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
    cur = conn.cursor()
    cur.execute("SELECT google_token FROM person WHERE discord_guild = %s AND discord_id = %s;",
                 (discord_guild, discord_id))
    try:
        result = cur.fetchone()[0]
    except:
        result = None

    conn.commit()
    cur.close()
    conn.close()
    
    if (result != None):
        # Token exists
        return result
    else:
        # No Token in DB
        return store_user_creds(discord_guild, discord_id, code, state)


def get_session(discord_guild: int, discord_id: int, code: str, state: str):
    session = api.Session(session_credentials =
                          get_user_creds(discord_guild, discord_id, code, state))
    return session

def get_events_list(discord_guild: int, discord_id: int, code: str, state: str):
    session = get_session(discord_guild, discord_id, code, state)
    events_list = session.events.list()
    return events_list


def get_cotopia_events(discord_guild: int, discord_id: int):
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
    cur = conn.cursor()
    cur.execute("SELECT google_token FROM person WHERE discord_guild = %s AND discord_id = %s;",
                 (discord_guild, discord_id))
    try:
        result = cur.fetchone()[0]
    except:
        result = None
    
    conn.commit()
    cur.close()
    conn.close()

