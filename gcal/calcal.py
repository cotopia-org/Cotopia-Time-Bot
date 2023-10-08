from datetime import datetime
from urllib.parse import quote
from . import calapi_chngd as api
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request


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


def get_user_creds(discord_guild: int, discord_id: int):
    creds = None
    conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres",
                        password="Tp\ZS?gfLr|]'a", port=5432)
    cur = conn.cursor()
    cur.execute("SELECT google_token FROM person WHERE discord_guild = %s AND discord_id = %s;",
                 (discord_guild, discord_id))
    try:
        token = cur.fetchone()[0]
    except:
        token = None

    # Token exists
    if (token != None):
        creds = Credentials.from_authorized_user_info(token)
        print("token found!")
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        # If token exists and needs refreshing
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            print("token refreshed!")
            # Save the credentials for the next run
            cur.execute("UPDATE person SET google_token = %s WHERE discord_guild = %s AND discord_id = %s;",
                        (creds.to_json(), discord_guild, discord_id))

        # If we need a new token
        else:
            conn.commit()
            cur.close()
            conn.close()
            print("Need to make a new token!")
            raise Exception("Need to make a new token!")
    
    conn.commit()
    cur.close()
    conn.close()
    the_dict = json.loads(creds.to_json())
    try:
        the_dict["expiry"] = datetime.strptime(the_dict["expiry"], '%Y-%m-%dT%H:%M:%SZ')
    except:
        # When the creds.refresh(Request()) is called, time format is diffrent and has milliseconds.
        the_dict["expiry"] = datetime.strptime(the_dict["expiry"], '%Y-%m-%dT%H:%M:%S.%fZ')

    return the_dict


def get_session(discord_guild: int, discord_id: int):
    session = api.Session(session_credentials =
                          get_user_creds(discord_guild, discord_id))
    return session

def get_events_list(discord_guild: int, discord_id: int):
    session = get_session(discord_guild, discord_id)
    events_list = session.events.list()
    return events_list


def get_keyword_events(discord_guild: int, discord_id: int, keyword: str, checking_last_n_events=100):

    events_list = get_events_list(discord_guild, discord_id)
    event_items = events_list["items"]
    event_items = event_items[-checking_last_n_events:]

    result = []
    recheck = []

    for i in event_items:
        try:
            if (keyword.casefold() in i["summary"].casefold()):
                result.append(i)
        except:
            # It had no summary
            recheck.append(i)

    # check if the events in recheck are related to events in result
    # and if so, append them to result
    # example: if cancel one day of a recurring event, the original event stays the same
    # but a cancelation event will be added and if the id of the original event is somthing like
    # 'id': '70sjie9i68r32bb3cdj3gb9k65ijcbb2c4pjgb9p6hijap1h6th38o9n6k'
    # the id of the cancelation event would be something like
    # 'id': '70sjie9i68r32bb3cdj3gb9k65ijcbb2c4pjgb9p6hijap1h6th38o9n6k_20231025T053000Z'  
    for r in recheck:
        for a in result:
            if (a["id"] in r["id"]):
                result.append(r)
                break

    j = json.dumps(result)

    return j